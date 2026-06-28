import logging
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings

from app.db.session import SessionLocal, get_db
from app.models.user import User
from app.schemas.audit import AuditDetailRead, AuditRead, AuditUploadResponse
from app.security.dependencies import get_current_user, require_roles
from app.services.audit_log_service import create_audit_log
from app.services.audit_service import (
    build_audit_upload_response,
    create_audit_from_parsed_kube_bench,
    get_audit_by_id,
    list_audits,
    run_kube_bench_and_create_audit,
)
from app.services.cluster_service import get_cluster_by_id
from app.services.kube_bench_parser import (
    KubeBenchParseError,
    load_json_content,
    parse_kube_bench_json,
)
from app.services.kube_bench_job_service import KubeBenchJobError
from app.services.recommendation_service import generate_recommendations_for_audit

router = APIRouter(prefix="/audits", tags=["Audits"])

logger = logging.getLogger(__name__)



def generate_recommendations_for_audit_background(
    audit_id: int,
    user_id: int,
    source: str,
    client_ip: str | None,
    user_agent: str | None,
) -> None:
    """
    Genera recomendaciones con IA en segundo plano usando una sesión DB propia.
    """
    db = SessionLocal()

    try:
        recommendations, created, updated, skipped = generate_recommendations_for_audit(
            db=db,
            audit_id=audit_id,
            source=source,
        )

        create_audit_log(
            db=db,
            user_id=user_id,
            action="RECOMMENDATIONS_GENERATED",
            entity_type="Audit",
            entity_id=str(audit_id),
            ip_address=client_ip,
            user_agent=user_agent,
            detail=(
                f"Generated recommendations for audit_id={audit_id}; "
                f"source={source}; "
                f"created={created}; "
                f"updated={updated}; "
                f"skipped={skipped}; "
                f"total={len(recommendations)}"
            ),
        )

        db.commit()

        logger.info(
            "Recommendations generated for audit_id=%s source=%s; created=%s; updated=%s; skipped=%s; total=%s",
            audit_id,
            source,
            created,
            updated,
            skipped,
            len(recommendations),
        )

    except Exception as exc:
        db.rollback()

        logger.exception(
            "Recommendation generation failed for audit_id=%s source=%s: %s",
            audit_id,
            source,
            exc,
        )

        try:
            create_audit_log(
                db=db,
                user_id=user_id,
                action="RECOMMENDATIONS_GENERATION_FAILED",
                entity_type="Audit",
                entity_id=str(audit_id),
                ip_address=client_ip,
                user_agent=user_agent,
                detail=(
                    f"Recommendation generation failed for audit_id={audit_id}; "
                    f"source={source}; "
                    f"error={exc}"
                ),
            )
            db.commit()
        except Exception:
            db.rollback()
            logger.exception(
                "Unable to write recommendation failure audit log for audit_id=%s",
                audit_id,
            )

    finally:
        db.close()


@router.get("", response_model=list[AuditRead])
def get_audits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lista auditorías registradas.
    """
    return list_audits(db)

@router.post(
    "/run-kube-bench",
    response_model=AuditUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
def run_kube_bench_audit(
    request: Request,
    background_tasks: BackgroundTasks,
    cluster_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "DEVOPS", "SRE", "SECURITY")),
):
    """
    Ejecuta kube-bench como Job dentro del clúster Kubernetes registrado.

    Este endpoint corresponde al modo real de auditoría contra el clúster.
    """
    cluster = get_cluster_by_id(db, cluster_id)

    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found",
        )

    recommendation_source = settings.RECOMMENDATION_SOURCE or "deepseek"

    try:
        audit = run_kube_bench_and_create_audit(
            db=db,
            cluster=cluster,
            current_user=current_user,
        )

    except KubeBenchJobError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="KUBE_BENCH_JOB_EXECUTED",
        entity_type="Audit",
        entity_id=str(audit.id),
        ip_address=client_ip,
        user_agent=user_agent,
        detail=(
            f"kube-bench Job executed for cluster_id={cluster.id}; "
            f"total_controls={audit.total_controls}; "
            f"passed={audit.passed_controls}; "
            f"failed={audit.failed_controls}; "
            f"warn={audit.warning_controls}"
        ),
    )

    background_tasks.add_task(
        generate_recommendations_for_audit_background,
        audit_id=audit.id,
        user_id=current_user.id,
        source=recommendation_source,
        client_ip=client_ip,
        user_agent=user_agent,
    )

    return build_audit_upload_response(audit)

@router.get("/{audit_id}", response_model=AuditDetailRead)
def get_audit_detail(
    audit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Consulta detalle de una auditoría.
    """
    audit = get_audit_by_id(db, audit_id)

    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found",
        )

    return audit


@router.post(
    "/upload",
    response_model=AuditUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_kube_bench_result(
    request: Request,
    cluster_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "DEVOPS", "SRE", "SECURITY")),
):
    """
    Carga un archivo JSON de kube-bench y registra una auditoría.

    Este endpoint corresponde al modo demo controlado de KubeAudit.
    """
    cluster = get_cluster_by_id(db, cluster_id)

    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found",
        )

    if not file.filename.endswith(".json"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JSON files are allowed",
        )

    raw_content = await file.read()

    try:
        raw_json = load_json_content(raw_content)
        parsed_audit = parse_kube_bench_json(raw_json)

    except KubeBenchParseError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    audit = create_audit_from_parsed_kube_bench(
        db=db,
        cluster_id=cluster.id,
        current_user=current_user,
        parsed_audit=parsed_audit,
        raw_result_location=f"uploaded:{file.filename}",
    )

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="AUDIT_UPLOADED",
        entity_type="Audit",
        entity_id=str(audit.id),
        ip_address=client_ip,
        user_agent=user_agent,
        detail=(
            f"kube-bench JSON uploaded for cluster_id={cluster.id}; "
            f"total_controls={audit.total_controls}; "
            f"passed={audit.passed_controls}; "
            f"failed={audit.failed_controls}; "
            f"warn={audit.warning_controls}"
        ),
    )

    return build_audit_upload_response(audit)
