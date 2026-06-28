from sqlalchemy.orm import Session, joinedload

from app.models.audit import Audit
from app.models.finding import Finding
from app.models.recommendation import Recommendation
from app.services.recommendation_engine import (
    build_rationale,
    build_recommendation_text,
    build_recommendation_title,
    infer_priority,
)
from app.core.config import get_settings
from app.services.deepseek_service import (
    DeepSeekRecommendationError,
    generate_recommendation_with_deepseek,
)


VALID_RECOMMENDATION_STATUSES = {"PENDING", "APPLIED", "DISMISSED"}


class RecommendationServiceError(Exception):
    pass


def generate_recommendations_for_audit(
    db: Session,
    audit_id: int,
    source: str = "auto",
    limit: int | None = None,
) -> tuple[list[Recommendation], int, int, int]:
    """
    Genera recomendaciones para findings FAIL/WARN de una auditoría.

    Es idempotente:
    - Si ya existe recomendación para finding_id + source=rule_engine, la actualiza.
    - Si no existe, la crea.
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

        title = payload["title"]
        recommendation_text = payload["recommendation_text"]
        rationale = payload["rationale"]
        priority = payload["priority"]
        recommendation_source = payload["source"]

        existing = (
            db.query(Recommendation)
            .filter(
                Recommendation.finding_id == finding.id,
                Recommendation.source == recommendation_source,
            )
            .first()
        )

        if existing:
            if existing.status in {"APPLIED", "DISMISSED"}:
                skipped += 1
                recommendations.append(existing)
                continue

            existing.title = title
            existing.recommendation_text = recommendation_text
            existing.rationale = rationale
            existing.priority = priority
            existing.status = "PENDING"

            db.add(existing)
            recommendations.append(existing)
            updated += 1
            continue

        recommendation = Recommendation(
            finding_id=finding.id,
            title=title,
            recommendation_text=recommendation_text,
            rationale=rationale,
            priority=priority,
            status="PENDING",
            source=recommendation_source,
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
        query = query.filter(Recommendation.status == status.upper())

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
) -> Recommendation:
    normalized_status = status.upper()

    if normalized_status not in VALID_RECOMMENDATION_STATUSES:
        raise RecommendationServiceError(
            f"Invalid status. Allowed values: {', '.join(sorted(VALID_RECOMMENDATION_STATUSES))}"
        )

    recommendation = get_recommendation_by_id(
        db=db,
        recommendation_id=recommendation_id,
    )

    if not recommendation:
        raise RecommendationServiceError("Recommendation not found")

    recommendation.status = normalized_status

    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)

    return recommendation


def build_recommendation_payload(
    finding: Finding,
    source: str = "auto",
) -> dict[str, str]:
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

    # source=auto
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


def build_rule_engine_payload(finding: Finding) -> dict[str, str]:
    return {
        "title": build_recommendation_title(finding)[:255],
        "recommendation_text": build_recommendation_text(finding),
        "rationale": build_rationale(finding),
        "priority": infer_priority(finding),
        "source": "rule_engine",
    }
