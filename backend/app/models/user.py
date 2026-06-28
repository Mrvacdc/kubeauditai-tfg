from typing import List

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """
    Usuario de KubeAudit.

    Representa a los perfiles que acceden al sistema:
    ADMIN, DEVOPS, SRE o SECURITY.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="SECURITY",
    )

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    clusters: Mapped[List["Cluster"]] = relationship(
        back_populates="registered_by",
        cascade="all, delete-orphan",
    )

    audits: Mapped[List["Audit"]] = relationship(
        back_populates="executed_by",
    )

#    reviewed_recommendations: Mapped[List["Recommendation"]] = relationship(
#        back_populates="reviewed_by",
#    )

    audit_logs: Mapped[List["AuditLog"]] = relationship(
        back_populates="user",
    )
