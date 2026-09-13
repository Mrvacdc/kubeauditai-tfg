from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Recommendation(Base, TimestampMixin):
    """
    Recomendación de remediación generada para un finding.

    La prioridad representa una prioridad operativa de remediación, no una
    severidad oficial CIS. El estado de revisión se gestiona mediante
    review_status. El campo status se conserva como espejo de compatibilidad.
    """

    __tablename__ = "recommendations"

    __table_args__ = (
        UniqueConstraint(
            "finding_id",
            "source",
            name="uq_recommendations_finding_source",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    finding_id: Mapped[int] = mapped_column(
        ForeignKey("findings.id"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    recommendation_text: Mapped[str] = mapped_column(Text, nullable=False)

    rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="MEDIUM",
    )

    # Campo legado/espejo para mantener compatibilidad con endpoints y dashboard.
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING",
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="rule_engine",
    )

    # Estado real de revisión humana.
    review_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING",
    )

    reviewed_by_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    review_decision: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    validation_evidence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    manual_recommendation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    model_provider: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)

    model_name: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)

    model_version: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)

    prompt_template: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    finding: Mapped["Finding"] = relationship(
        back_populates="recommendations",
    )
