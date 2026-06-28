from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import (
    AuditComparison,
    AuditControlComparison,
    AuditDashboardSummary,
    AuditRemediationPlan,
    ClusterAuditHistory,
)
from app.security.dependencies import require_roles
from app.services.dashboard_service import (
    DashboardServiceError,
    get_audit_comparison,
    get_audit_control_comparison,
    get_audit_dashboard_summary,
    get_audit_remediation_plan,
    get_cluster_audit_history,
)


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/audits/{audit_id}/summary",
    response_model=AuditDashboardSummary,
)
def get_audit_summary(
    audit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "DEVOPS", "SRE", "SECURITY")
    ),
):
    try:
        return get_audit_dashboard_summary(
            db=db,
            audit_id=audit_id,
        )
    except DashboardServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/clusters/{cluster_id}/history",
    response_model=ClusterAuditHistory,
)
def get_cluster_history(
    cluster_id: int,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "DEVOPS", "SRE", "SECURITY")
    ),
):
    try:
        return get_cluster_audit_history(
            db=db,
            cluster_id=cluster_id,
            limit=limit,
        )
    except DashboardServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/audits/compare",
    response_model=AuditComparison,
)
def compare_audits(
    base_audit_id: int,
    target_audit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "DEVOPS", "SRE", "SECURITY")
    ),
):
    try:
        return get_audit_comparison(
            db=db,
            base_audit_id=base_audit_id,
            target_audit_id=target_audit_id,
        )
    except DashboardServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/audits/compare-controls",
    response_model=AuditControlComparison,
)
def compare_audits_by_controls(
    base_audit_id: int,
    target_audit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "DEVOPS", "SRE", "SECURITY")
    ),
):
    try:
        return get_audit_control_comparison(
            db=db,
            base_audit_id=base_audit_id,
            target_audit_id=target_audit_id,
        )
    except DashboardServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/audits/{audit_id}/remediation-plan",
    response_model=AuditRemediationPlan,
)
def get_remediation_plan(
    audit_id: int,
    source: str | None = None,
    priority: str | None = None,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "DEVOPS", "SRE", "SECURITY")
    ),
):
    try:
        return get_audit_remediation_plan(
            db=db,
            audit_id=audit_id,
            source=source,
            priority=priority,
            limit=limit,
        )
    except DashboardServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
