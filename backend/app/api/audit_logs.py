from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


@router.get("")
def list_audit_logs(
    limit: int = Query(default=50, ge=1, le=200),
    action: Optional[str] = Query(default=None),
    entity_type: Optional[str] = Query(default=None),
    entity_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
):
    """
    Devuelve los eventos de auditoría registrados por KubeAudit.

    Permite filtrar por:
    - action
    - entity_type
    - entity_id
    """

    filters = []
    params = {"limit": limit}

    if action:
        filters.append("action ILIKE :action")
        params["action"] = f"%{action}%"

    if entity_type:
        filters.append("entity_type ILIKE :entity_type")
        params["entity_type"] = entity_type

    if entity_id:
        filters.append("entity_id = :entity_id")
        params["entity_id"] = entity_id

    where_clause = ""
    if filters:
        where_clause = "WHERE " + " AND ".join(filters)

    query = text(
        f"""
        SELECT
            id,
            user_id,
            action,
            entity_type,
            entity_id,
            ip_address,
            detail,
            created_at
        FROM audit_logs
        {where_clause}
        ORDER BY created_at DESC, id DESC
        LIMIT :limit
        """
    )

    rows = db.execute(query, params).mappings().all()

    return {
        "total": len(rows),
        "items": [
            {
                "id": row["id"],
                "user_id": row["user_id"],
                "action": row["action"],
                "entity_type": row["entity_type"],
                "entity_id": row["entity_id"],
                "ip_address": row["ip_address"],
                "detail": row["detail"],
                "created_at": row["created_at"],
            }
            for row in rows
        ],
    }
