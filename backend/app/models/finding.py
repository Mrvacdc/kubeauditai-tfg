from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Finding(Base, TimestampMixin):
    """
    Resultado de un control CIS dentro de una auditoría.

    Puede representar controles PASS, FAIL o WARN.
    """

    __tablename__ = "findings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    audit_id: Mapped[int] = mapped_column(
        ForeignKey("audits.id"),
        nullable=False,
        index=True,
    )

    control_id: Mapped[int] = mapped_column(
        ForeignKey("cis_controls.id"),
        nullable=False,
        index=True,
    )

    result: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    evidence_sanitized: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    evidence_hash: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
    )

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    audit: Mapped["Audit"] = relationship(
        back_populates="findings",
    )

    control: Mapped["CisControl"] = relationship(
        back_populates="findings",
    )

    recommendations: Mapped[List["Recommendation"]] = relationship(
        back_populates="finding",
        cascade="all, delete-orphan",
    )
