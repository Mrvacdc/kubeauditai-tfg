from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class AuditLog(Base, TimestampMixin):
    """
    Registro de acciones relevantes realizadas dentro del sistema.

    Sirve para trazabilidad interna de KubeAudit.
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    action: Mapped[str] = mapped_column(String(120), nullable=False)

    entity_type: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)

    entity_id: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)

    ip_address: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)

    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped[Optional["User"]] = relationship(
        back_populates="audit_logs",
    )
