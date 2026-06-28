from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.report import AuditJsonReport, ExecutiveSummaryReport
from app.security.dependencies import require_roles
from app.services.report_service import (
    ReportServiceError,
    build_markdown_report,
    get_audit_json_report,
    get_executive_summary_report,
)


router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get(
    "/audits/{audit_id}/json",
    response_model=AuditJsonReport,
)
def get_audit_report_json(
    audit_id: int,
    finding_limit: int = 50,
    remediation_limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "DEVOPS", "SRE", "SECURITY")
    ),
):
    try:
        return get_audit_json_report(
            db=db,
            audit_id=audit_id,
            finding_limit=finding_limit,
            remediation_limit=remediation_limit,
        )
    except ReportServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/audits/{audit_id}/executive-summary",
    response_model=ExecutiveSummaryReport,
)
def get_audit_executive_summary(
    audit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "DEVOPS", "SRE", "SECURITY")
    ),
):
    try:
        return get_executive_summary_report(
            db=db,
            audit_id=audit_id,
        )
    except ReportServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/audits/{audit_id}/markdown")
def get_audit_report_markdown(
    audit_id: int,
    finding_limit: int = 30,
    remediation_limit: int = 15,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "DEVOPS", "SRE", "SECURITY")
    ),
):
    try:
        markdown = build_markdown_report(
            db=db,
            audit_id=audit_id,
            finding_limit=finding_limit,
            remediation_limit=remediation_limit,
        )
    except ReportServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return Response(
        content=markdown,
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Disposition": f'inline; filename="kubeaudit-audit-{audit_id}.md"'
        },
    )
