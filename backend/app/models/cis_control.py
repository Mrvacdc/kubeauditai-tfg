from typing import List, Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class CisControl(Base, TimestampMixin):
    """
    Control definido por el CIS Kubernetes Benchmark.
    """

    __tablename__ = "cis_controls"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(String(500), nullable=False)

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    category: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)

    severity: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    remediation_reference: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    findings: Mapped[List["Finding"]] = relationship(
        back_populates="control",
    )
