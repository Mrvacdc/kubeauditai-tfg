from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Cluster(Base, TimestampMixin):
    """
    Clúster Kubernetes auditado por KubeAudit.

    La aplicación no necesita ejecutarse dentro del clúster auditado.
    Se conecta mediante kubeconfig, token restringido o referencia segura
    a credenciales almacenadas fuera de la base de datos.
    """

    __tablename__ = "clusters"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    api_server: Mapped[str] = mapped_column(String(500), nullable=False)

    namespace_target: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)

    connection_mode: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="kubeconfig",
    )

    credential_reference: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    ca_certificate_fingerprint: Mapped[Optional[str]] = mapped_column(
        String(255),
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

    last_connection_status: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    last_connection_checked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    registered_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    registered_by: Mapped["User"] = relationship(
        back_populates="clusters",
    )

    audits: Mapped[List["Audit"]] = relationship(
        back_populates="cluster",
        cascade="all, delete-orphan",
    )
