from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


VALID_REVIEW_STATUSES = {"PENDING", "APPROVED", "REJECTED", "REPLACED"}


class RecommendationRead(BaseModel):
    id: int
    finding_id: int
    title: str
    recommendation_text: str
    rationale: Optional[str]
    priority: str

    # status se mantiene por compatibilidad y refleja review_status.
    status: str
    review_status: str

    source: str

    reviewed_by_user_id: Optional[int]
    reviewed_at: Optional[datetime]
    review_decision: Optional[str]
    validation_evidence: Optional[str]
    manual_recommendation: Optional[str]

    model_provider: Optional[str]
    model_name: Optional[str]
    model_version: Optional[str]
    prompt_template: Optional[str]

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RecommendationGenerateResponse(BaseModel):
    audit_id: int
    created: int
    updated: int
    skipped: int
    total_recommendations: int


class RecommendationStatusUpdate(BaseModel):
    status: str = Field(
        description="Estado de revisión: PENDING, APPROVED, REJECTED o REPLACED."
    )
    decision: Optional[str] = Field(
        default=None,
        description="Justificación de la decisión tomada por el revisor.",
    )
    validation_evidence: Optional[str] = Field(
        default=None,
        description="Evidencia o criterio usado para validar la recomendación.",
    )
    manual_recommendation: Optional[str] = Field(
        default=None,
        description="Recomendación manual cuando status=REPLACED.",
    )

    @model_validator(mode="after")
    def validate_review_payload(self):
        normalized_status = self.status.upper().strip()

        if normalized_status not in VALID_REVIEW_STATUSES:
            allowed = ", ".join(sorted(VALID_REVIEW_STATUSES))
            raise ValueError(f"Invalid status. Allowed values: {allowed}")

        decision = (self.decision or "").strip()
        manual_recommendation = (self.manual_recommendation or "").strip()

        if normalized_status == "REJECTED" and not decision:
            raise ValueError("decision is required when status=REJECTED")

        if normalized_status == "REPLACED":
            if not decision:
                raise ValueError("decision is required when status=REPLACED")
            if not manual_recommendation:
                raise ValueError(
                    "manual_recommendation is required when status=REPLACED"
                )

        if normalized_status == "APPROVED" and manual_recommendation:
            raise ValueError(
                "manual_recommendation must be empty when status=APPROVED"
            )

        self.status = normalized_status
        return self
