from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    action: str,
    user_id: int | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    detail: str | None = None,
) -> AuditLog:
    """
    Registra una acción relevante dentro de KubeAudit.

    No se deben guardar contraseñas, tokens, kubeconfigs ni secretos.
    """
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        ip_address=ip_address,
        user_agent=user_agent,
        detail=detail,
    )

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    return audit_log
