from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.models.audit import Audit
from app.models.cis_control import CisControl
from app.models.cluster import Cluster
from app.models.finding import Finding
from app.models.user import User
from app.schemas.audit import AuditUploadResponse
from app.services.kube_bench_job_service import (
    KubeBenchJobError,
    run_kube_bench_job_from_kubeconfig,
)
from app.services.kube_bench_parser import (
    KubeBenchParseError,
    ParsedAudit,
    parse_kube_bench_json,
)


def extract_image_version(image: str | None) -> str | None:
    """
    Obtiene el tag de una imagen.
    Ejemplo: aquasec/kube-bench:v0.15.6 -> v0.15.6
    """
    if not image:
        return None

    without_digest = image.split("@", 1)[0]
    last_segment = without_digest.rsplit("/", 1)[-1]

    if ":" not in last_segment:
        return None

    return last_segment.rsplit(":", 1)[-1]


def format_audit_scope(values: list[str] | None) -> str | None:
    """
    Convierte los targets detectados por kube-bench en una cadena persistible.
    """
    if not values:
        return None

    cleaned = sorted(
        {str(value).strip() for value in values if value and str(value).strip()}
    )

    if not cleaned:
        return None

    return ",".join(cleaned)


def get_or_create_cis_control(
    db: Session,
    control_code: str,
    title: str,
    category: str | None,
    remediation_reference: str | None,
) -> CisControl:
    """
    Obtiene o crea un control CIS.

    Si el control ya existe, se actualizan algunos campos descriptivos.
    """
    control = (
        db.query(CisControl)
        .filter(CisControl.code == control_code)
        .first()
    )

    if control:
        control.title = title
        control.category = category
        control.remediation_reference = remediation_reference
        db.add(control)
        return control

    control = CisControl(
        code=control_code,
        title=title,
        description=None,
        category=category,
        priority=None,
        priority_source=None,
        remediation_reference=remediation_reference,
    )

    db.add(control)
    db.flush()

    return control


def create_audit_from_parsed_kube_bench(
    db: Session,
    cluster_id: int,
    current_user: User,
    parsed_audit: ParsedAudit,
    raw_result_location: str | None = None,
    execution_mode: str = "uploaded_json",
    started_at: datetime | None = None,
    finished_at: datetime | None = None,
    kubernetes_version: str | None = None,
    kubernetes_distribution: str | None = None,
    kube_bench_version: str | None = None,
    failure_reason: str | None = None,
) -> Audit:
    """
    Crea una auditoría y sus hallazgos a partir de un resultado parseado.
    Además persiste metadata técnica para trazabilidad histórica.
    """
    started_at = started_at or datetime.now(timezone.utc)
    finished_at = finished_at or datetime.now(timezone.utc)

    duration_seconds = max(
        0,
        int((finished_at - started_at).total_seconds()),
    )

    audit = Audit(
        cluster_id=cluster_id,
        executed_by_user_id=current_user.id,
        status="completed",
        execution_mode=execution_mode,
        benchmark_version=parsed_audit.benchmark_version,
        benchmark_profile=parsed_audit.benchmark_profile,
        kubernetes_version=(
            kubernetes_version
            or parsed_audit.detected_kubernetes_version
        ),
        kubernetes_distribution=kubernetes_distribution,
        kube_bench_version=kube_bench_version,
        audit_scope=format_audit_scope(parsed_audit.audit_scope),
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=duration_seconds,
        failure_reason=failure_reason,
        total_controls=parsed_audit.total_controls,
        passed_controls=parsed_audit.passed_controls,
        failed_controls=parsed_audit.failed_controls,
        warning_controls=parsed_audit.warning_controls,
        compliance_percentage=parsed_audit.compliance_percentage,
        raw_result_location=raw_result_location,
    )

    db.add(audit)
    db.flush()

    for parsed_finding in parsed_audit.findings:
        control = get_or_create_cis_control(
            db=db,
            control_code=parsed_finding.control_code,
            title=parsed_finding.title,
            category=parsed_finding.category,
            remediation_reference=parsed_finding.remediation_reference,
        )

        finding = Finding(
            audit_id=audit.id,
            control_id=control.id,
            result=parsed_finding.result,
            detail=parsed_finding.detail,
            evidence_sanitized=parsed_finding.evidence_sanitized,
            evidence_hash=parsed_finding.evidence_hash,
            detected_at=finished_at,
        )

        db.add(finding)

    db.commit()
    db.refresh(audit)

    return audit


def list_audits(db: Session) -> list[Audit]:
    return (
        db.query(Audit)
        .order_by(Audit.created_at.desc())
        .all()
    )


def get_audit_by_id(db: Session, audit_id: int) -> Audit | None:
    return (
        db.query(Audit)
        .options(
            joinedload(Audit.findings).joinedload(Finding.control)
        )
        .filter(Audit.id == audit_id)
        .first()
    )


def build_audit_upload_response(audit: Audit) -> AuditUploadResponse:
    return AuditUploadResponse(
        audit_id=audit.id,
        cluster_id=audit.cluster_id,
        status=audit.status,
        total_controls=audit.total_controls,
        passed_controls=audit.passed_controls,
        failed_controls=audit.failed_controls,
        warning_controls=audit.warning_controls,
        compliance_percentage=audit.compliance_percentage,
    )


def run_kube_bench_and_create_audit(
    db: Session,
    cluster: Cluster,
    current_user: User,
) -> Audit:
    """
    Ejecuta kube-bench como Job dentro del clúster y guarda la auditoría
    con metadata técnica de trazabilidad.
    """
    if cluster.connection_mode != "kubeconfig":
        raise KubeBenchJobError(
            "Only kubeconfig connection mode is supported for kube-bench Job execution."
        )

    if not cluster.credential_reference:
        raise KubeBenchJobError(
            "credential_reference is required to execute kube-bench."
        )

    kube_bench_started_at = datetime.now(timezone.utc)

    raw_json, raw_result_location = run_kube_bench_job_from_kubeconfig(
        kubeconfig_path=cluster.credential_reference,
    )

    kube_bench_finished_at = datetime.now(timezone.utc)

    try:
        parsed_audit = parse_kube_bench_json(raw_json)
    except KubeBenchParseError as exc:
        raise KubeBenchJobError(
            f"kube-bench finished, but the JSON output could not be parsed: {exc}"
        ) from exc

    return create_audit_from_parsed_kube_bench(
        db=db,
        cluster_id=cluster.id,
        current_user=current_user,
        parsed_audit=parsed_audit,
        raw_result_location=raw_result_location,
        execution_mode="kube_bench_job",
        started_at=kube_bench_started_at,
        finished_at=kube_bench_finished_at,
        kubernetes_version=cluster.kubernetes_version,
        kubernetes_distribution=cluster.kubernetes_distribution,
        kube_bench_version=extract_image_version(settings.KUBE_BENCH_IMAGE),
    )
