from typing import Optional

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Recommendation(Base, TimestampMixin):
    """
    Recomendación de remediación generada para un finding.

    En esta fase se genera mediante reglas determinísticas.
    En una fase posterior puede enriquecerse con IA.
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

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    recommendation_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    rationale: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="MEDIUM",
    )

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

    finding: Mapped["Finding"] = relationship(
        back_populates="recommendations",
    )
