from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RecommendationRead(BaseModel):
    id: int
    finding_id: int
    title: str
    recommendation_text: str
    rationale: Optional[str]
    priority: str
    status: str
    source: str
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
    status: str
