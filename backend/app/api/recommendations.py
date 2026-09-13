from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.cis_control import CisControl
from app.models.finding import Finding
from app.models.user import User
from app.schemas.recommendation import (
    RecommendationGenerateResponse,
    RecommendationRead,
    RecommendationStatusUpdate,
)
from app.security.dependencies import get_current_user, require_roles
from app.services.audit_log_service import create_audit_log
from app.services.recommendation_service import (
    RecommendationServiceError,
    generate_recommendations_for_audit,
    get_recommendation_by_id,
    list_recommendations,
    update_recommendation_status,
)

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.post("/generate", response_model=RecommendationGenerateResponse)
def generate_recommendations(
    request: Request,
    audit_id: int,
    source: str = "auto",
    limit: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "DEVOPS", "SRE", "SECURITY")),
):
    try:
        recommendations, created, updated, skipped = generate_recommendations_for_audit(
            db=db,
            audit_id=audit_id,
            source=source,
            limit=limit,
        )
    except RecommendationServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="RECOMMENDATIONS_GENERATED",
        entity_type="Audit",
        entity_id=str(audit_id),
        ip_address=client_ip,
        user_agent=user_agent,
        detail=(
            f"Generated recommendations for audit_id={audit_id}; "
            f"created={created}; updated={updated}; skipped={skipped}"
        ),
    )

    return RecommendationGenerateResponse(
        audit_id=audit_id,
        created=created,
        updated=updated,
        skipped=skipped,
        total_recommendations=len(recommendations),
    )


@router.get("", response_model=list[RecommendationRead])
def get_recommendations(
    audit_id: int | None = None,
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_recommendations(
        db=db,
        audit_id=audit_id,
        status=status_filter,
    )


def build_recommendation_review_log_detail(
    db: Session,
    recommendation_id: int,
    finding_id: int,
    previous_status: str,
    new_status: str,
    source: str,
    priority: str,
    reviewer_user_id: int,
) -> str:
    finding_context = (
        db.query(
            CisControl.code,
            CisControl.title,
            Finding.result,
        )
        .join(Finding, Finding.control_id == CisControl.id)
        .filter(Finding.id == finding_id)
        .first()
    )

    base_detail = (
        f"Recommendation review changed from {previous_status} "
        f"to {new_status}; "
        f"recommendation_id={recommendation_id}; "
        f"finding_id={finding_id}; "
        f"source={source}; "
        f"priority={priority}; "
        f"reviewer_user_id={reviewer_user_id}"
    )

    if finding_context:
        control_code, control_title, finding_result = finding_context
        return (
            f"{base_detail}; "
            f"control={control_code}; "
            f"result={finding_result}; "
            f"control_title={control_title}"
        )

    return base_detail


@router.patch("/{recommendation_id}/status", response_model=RecommendationRead)
def patch_recommendation_status(
    request: Request,
    recommendation_id: int,
    payload: RecommendationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "DEVOPS", "SRE", "SECURITY")
    ),
):
    recommendation_before = get_recommendation_by_id(
        db=db,
        recommendation_id=recommendation_id,
    )

    if not recommendation_before:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found",
        )

    previous_status = (
        recommendation_before.review_status
        or recommendation_before.status
        or "PENDING"
    )

    try:
        recommendation = update_recommendation_status(
            db=db,
            recommendation_id=recommendation_id,
            status=payload.status,
            reviewer_user_id=current_user.id,
            decision=payload.decision,
            validation_evidence=payload.validation_evidence,
            manual_recommendation=payload.manual_recommendation,
        )
    except RecommendationServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    log_detail = build_recommendation_review_log_detail(
        db=db,
        recommendation_id=recommendation.id,
        finding_id=recommendation.finding_id,
        previous_status=previous_status,
        new_status=recommendation.review_status,
        source=recommendation.source,
        priority=recommendation.priority,
        reviewer_user_id=current_user.id,
    )

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="RECOMMENDATION_REVIEWED",
        entity_type="Recommendation",
        entity_id=str(recommendation_id),
        ip_address=client_ip,
        user_agent=user_agent,
        detail=log_detail,
    )

    return recommendation
