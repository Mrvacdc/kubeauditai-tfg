from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session

from app.models.cluster import Cluster
from app.models.user import User
from app.schemas.cluster import ClusterCreate
from app.services.kubernetes_client_service import (
    KubernetesConnectionError,
    validate_kubernetes_connection,
)


def create_cluster(
    db: Session,
    payload: ClusterCreate,
    current_user: User,
) -> Cluster:
    """
    Registra un clúster Kubernetes externo.

    No almacena secretos en texto plano. credential_reference debe ser una
    referencia a un archivo o secreto protegido.
    """
    cluster = Cluster(
        name=payload.name,
        description=payload.description,
        api_server=str(payload.api_server),
        namespace_target=payload.namespace_target,
        connection_mode=payload.connection_mode,
        credential_reference=payload.credential_reference,
        registered_by_user_id=current_user.id,
        last_connection_status="not_checked",
    )

    db.add(cluster)
    db.commit()
    db.refresh(cluster)

    return cluster


def list_clusters(db: Session) -> List[Cluster]:
    return db.query(Cluster).order_by(Cluster.created_at.desc()).all()


def get_cluster_by_id(db: Session, cluster_id: int) -> Cluster | None:
    return db.query(Cluster).filter(Cluster.id == cluster_id).first()


def validate_cluster_connection(
    db: Session,
    cluster: Cluster,
) -> tuple[str, str]:
    """
    Valida conectividad contra Kubernetes API.

    Devuelve:
    - status
    - kubernetes_version o mensaje de error
    """
    try:
        kubernetes_version = validate_kubernetes_connection(
            connection_mode=cluster.connection_mode,
            credential_reference=cluster.credential_reference,
        )

        cluster.kubernetes_version = kubernetes_version
        cluster.last_connection_status = "success"
        cluster.last_connection_checked_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(cluster)

        return "success", kubernetes_version

    except KubernetesConnectionError as exc:
        cluster.last_connection_status = "failed"
        cluster.last_connection_checked_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(cluster)

        return "failed", str(exc)
