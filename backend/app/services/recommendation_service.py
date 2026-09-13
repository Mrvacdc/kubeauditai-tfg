from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
from app.models.audit import Audit
from app.models.finding import Finding
from app.models.recommendation import Recommendation
from app.services.deepseek_service import (
    DeepSeekRecommendationError,
    generate_recommendation_with_deepseek,
)
from app.services.recommendation_engine import (
    build_rationale,
    build_recommendation_text,
    build_recommendation_title,
    infer_priority,
)


VALID_REVIEW_STATUSES = {"PENDING", "APPROVED", "REJECTED", "REPLACED"}
FINAL_REVIEW_STATUSES = {"APPROVED", "REJECTED", "REPLACED"}


class RecommendationServiceError(Exception):
    pass


def normalize_review_status(status: str) -> str:
    normalized = status.upper().strip()

    legacy_mapping = {
        "APPLIED": "APPROVED",
        "DISMISSED": "REJECTED",
    }

    normalized = legacy_mapping.get(normalized, normalized)

    if normalized not in VALID_REVIEW_STATUSES:
        raise RecommendationServiceError(
            f"Invalid status. Allowed values: {', '.join(sorted(VALID_REVIEW_STATUSES))}"
        )

    return normalized


def generate_recommendations_for_audit(
    db: Session,
    audit_id: int,
    source: str = "auto",
    limit: int | None = None,
) -> tuple[list[Recommendation], int, int, int]:
    """
    Genera recomendaciones para findings FAIL/WARN de una auditoría.

    Si una recomendación ya fue revisada por una persona, no se sobrescribe.
    """
    audit = (
        db.query(Audit)
        .options(
            joinedload(Audit.findings).joinedload(Finding.control),
            joinedload(Audit.findings).joinedload(Finding.recommendations),
        )
        .filter(Audit.id == audit_id)
        .first()
    )

    if not audit:
        raise RecommendationServiceError("Audit not found")

    findings_to_process = [
        finding
        for finding in audit.findings
        if finding.result.upper() in {"FAIL", "WARN"}
    ]

    if limit is not None:
        if limit <= 0:
            raise RecommendationServiceError("Limit must be greater than 0")
        findings_to_process = findings_to_process[:limit]

    recommendations: list[Recommendation] = []
    created = 0
    updated = 0
    skipped = 0

    for finding in findings_to_process:
        payload = build_recommendation_payload(finding, source=source)

        title = str(payload["title"])
        recommendation_text = str(payload["recommendation_text"])
        rationale = payload.get("rationale")
        priority = str(payload["priority"])
        recommendation_source = str(payload["source"])

        existing = (
            db.query(Recommendation)
            .filter(
                Recommendation.finding_id == finding.id,
                Recommendation.source == recommendation_source,
            )
            .first()
        )

        if existing:
            existing_review_status = normalize_review_status(
                existing.review_status or existing.status or "PENDING"
            )

            if existing_review_status in FINAL_REVIEW_STATUSES:
                skipped += 1
                recommendations.append(existing)
                continue

            existing.title = title
            existing.recommendation_text = recommendation_text
            existing.rationale = str(rationale) if rationale else None
            existing.priority = priority
            existing.review_status = "PENDING"
            existing.status = "PENDING"
            existing.reviewed_by_user_id = None
            existing.reviewed_at = None
            existing.review_decision = None
            existing.validation_evidence = None
            existing.manual_recommendation = None
            existing.model_provider = payload.get("model_provider")
            existing.model_name = payload.get("model_name")
            existing.model_version = payload.get("model_version")
            existing.prompt_template = payload.get("prompt_template")

            db.add(existing)
            recommendations.append(existing)
            updated += 1
            continue

        recommendation = Recommendation(
            finding_id=finding.id,
            title=title,
            recommendation_text=recommendation_text,
            rationale=str(rationale) if rationale else None,
            priority=priority,
            status="PENDING",
            review_status="PENDING",
            source=recommendation_source,
            reviewed_by_user_id=None,
            reviewed_at=None,
            review_decision=None,
            validation_evidence=None,
            manual_recommendation=None,
            model_provider=payload.get("model_provider"),
            model_name=payload.get("model_name"),
            model_version=payload.get("model_version"),
            prompt_template=payload.get("prompt_template"),
        )

        db.add(recommendation)
        recommendations.append(recommendation)
        created += 1

    db.commit()

    for recommendation in recommendations:
        db.refresh(recommendation)

    return recommendations, created, updated, skipped


def list_recommendations(
    db: Session,
    audit_id: int | None = None,
    status: str | None = None,
) -> list[Recommendation]:
    query = db.query(Recommendation).join(Finding)

    if audit_id is not None:
        query = query.filter(Finding.audit_id == audit_id)

    if status is not None:
        query = query.filter(
            Recommendation.review_status == normalize_review_status(status)
        )

    return query.order_by(
        Recommendation.priority.asc(),
        Recommendation.created_at.desc(),
    ).all()


def get_recommendation_by_id(
    db: Session,
    recommendation_id: int,
) -> Recommendation | None:
    return (
        db.query(Recommendation)
        .filter(Recommendation.id == recommendation_id)
        .first()
    )


def update_recommendation_status(
    db: Session,
    recommendation_id: int,
    status: str,
    reviewer_user_id: int,
    decision: str | None = None,
    validation_evidence: str | None = None,
    manual_recommendation: str | None = None,
) -> Recommendation:
    review_status = normalize_review_status(status)

    clean_decision = decision.strip() if decision else None
    clean_validation_evidence = (
        validation_evidence.strip() if validation_evidence else None
    )
    clean_manual_recommendation = (
        manual_recommendation.strip() if manual_recommendation else None
    )

    if review_status == "REJECTED" and not clean_decision:
        raise RecommendationServiceError(
            "decision is required when status=REJECTED"
        )

    if review_status == "REPLACED":
        if not clean_decision:
            raise RecommendationServiceError(
                "decision is required when status=REPLACED"
            )
        if not clean_manual_recommendation:
            raise RecommendationServiceError(
                "manual_recommendation is required when status=REPLACED"
            )

    if review_status == "APPROVED" and clean_manual_recommendation:
        raise RecommendationServiceError(
            "manual_recommendation must be empty when status=APPROVED"
        )

    recommendation = get_recommendation_by_id(
        db=db,
        recommendation_id=recommendation_id,
    )

    if not recommendation:
        raise RecommendationServiceError("Recommendation not found")

    recommendation.review_status = review_status

    # Espejo de compatibilidad para dashboard/reportes existentes.
    recommendation.status = review_status

    recommendation.reviewed_by_user_id = reviewer_user_id
    recommendation.reviewed_at = datetime.now(timezone.utc)
    recommendation.review_decision = clean_decision
    recommendation.validation_evidence = clean_validation_evidence
    recommendation.manual_recommendation = (
        clean_manual_recommendation if review_status == "REPLACED" else None
    )

    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)

    return recommendation


def build_recommendation_payload(
    finding: Finding,
    source: str = "auto",
) -> dict[str, str | None]:
    """
    Construye el payload de recomendación.

    source:
    - auto: usa settings.AI_PROVIDER y permite fallback a rule_engine.
    - rule_engine: fuerza motor determinístico.
    - deepseek: fuerza DeepSeek y falla si DeepSeek no responde correctamente.
    """
    settings = get_settings()

    normalized_source = source.lower()

    if normalized_source not in {"auto", "rule_engine", "deepseek"}:
        raise RecommendationServiceError(
            "Invalid source. Allowed values: auto, rule_engine, deepseek"
        )

    if normalized_source == "rule_engine":
        return build_rule_engine_payload(finding)

    if normalized_source == "deepseek":
        try:
            return generate_recommendation_with_deepseek(finding)
        except DeepSeekRecommendationError as exc:
            raise RecommendationServiceError(
                f"DeepSeek recommendation generation failed: {exc}"
            ) from exc

    provider = settings.AI_PROVIDER.lower()

    if provider == "deepseek":
        try:
            return generate_recommendation_with_deepseek(finding)
        except DeepSeekRecommendationError as exc:
            print(
                "[KubeAudit WARNING] DeepSeek failed in auto mode. "
                f"Using rule_engine fallback. Error: {exc}"
            )

    return build_rule_engine_payload(finding)


def build_rule_engine_payload(finding: Finding) -> dict[str, str | None]:
    return {
        "title": build_recommendation_title(finding)[:255],
        "recommendation_text": build_recommendation_text(finding),
        "rationale": build_rationale(finding),
        "priority": infer_priority(finding),
        "source": "rule_engine",
        "model_provider": "KubeAuditAI",
        "model_name": "internal_rule_engine",
        "model_version": "1.0",
        "prompt_template": None,
    }
