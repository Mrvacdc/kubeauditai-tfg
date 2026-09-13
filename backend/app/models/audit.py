from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Audit(Base, TimestampMixin):
    """
    Auditoría ejecutada sobre un clúster Kubernetes.

    Puede provenir de una ejecución real de kube-bench o de la carga
    controlada de un resultado JSON para fines de demostración.
    """

    __tablename__ = "audits"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    cluster_id: Mapped[int] = mapped_column(
        ForeignKey("clusters.id"),
        nullable=False,
        index=True,
    )

    executed_by_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
    )

    execution_mode: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="uploaded_json",
    )

    benchmark_version: Mapped[Optional[str]] = mapped_column(
        String(80),
        nullable=True,
    )

    benchmark_profile: Mapped[Optional[str]] = mapped_column(
        String(80),
        nullable=True,
    )

    kubernetes_version: Mapped[Optional[str]] = mapped_column(
        String(80),
        nullable=True,
    )

    kubernetes_distribution: Mapped[Optional[str]] = mapped_column(
        String(80),
        nullable=True,
    )

    kube_bench_version: Mapped[Optional[str]] = mapped_column(
        String(80),
        nullable=True,
    )

    audit_scope: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    duration_seconds: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    failure_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    total_controls: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    passed_controls: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_controls: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    warning_controls: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    compliance_percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=0,
    )

    raw_result_location: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    cluster: Mapped["Cluster"] = relationship(
        back_populates="audits",
    )

    executed_by: Mapped[Optional["User"]] = relationship(
        back_populates="audits",
    )

    findings: Mapped[List["Finding"]] = relationship(
        back_populates="audit",
        cascade="all, delete-orphan",
    )
