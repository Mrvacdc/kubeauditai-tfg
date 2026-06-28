from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.cluster import (
    ClusterConnectionTestResponse,
    ClusterCreate,
    ClusterRead,
)
from app.security.dependencies import get_current_user, require_roles
from app.services.audit_log_service import create_audit_log
from app.services.cluster_service import (
    create_cluster,
    get_cluster_by_id,
    list_clusters,
    validate_cluster_connection,
)

router = APIRouter(prefix="/clusters", tags=["Clusters"])


@router.get("", response_model=list[ClusterRead])
def get_clusters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lista los clústeres registrados.
    """
    return list_clusters(db)


@router.post(
    "",
    response_model=ClusterRead,
    status_code=status.HTTP_201_CREATED,
)
def register_cluster(
    payload: ClusterCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "DEVOPS")),
):
    """
    Registra un nuevo clúster Kubernetes externo.

    Solo ADMIN y DEVOPS pueden registrar clústeres.
    """
    cluster = create_cluster(
        db=db,
        payload=payload,
        current_user=current_user,
    )

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CLUSTER_REGISTERED",
        entity_type="Cluster",
        entity_id=str(cluster.id),
        ip_address=client_ip,
        user_agent=user_agent,
        detail=f"Cluster registered: name={cluster.name}",
    )

    return cluster


@router.get("/{cluster_id}", response_model=ClusterRead)
def get_cluster(
    cluster_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Consulta un clúster por ID.
    """
    cluster = get_cluster_by_id(db, cluster_id)

    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found",
        )

    return cluster


@router.post(
    "/{cluster_id}/test",
    response_model=ClusterConnectionTestResponse,
)
def test_cluster_connection(
    cluster_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "DEVOPS", "SRE", "SECURITY")),
):
    """
    Valida conectividad contra la API Server del clúster Kubernetes externo.
    """
    cluster = get_cluster_by_id(db, cluster_id)

    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found",
        )

    status_result, message = validate_cluster_connection(
        db=db,
        cluster=cluster,
    )

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CLUSTER_CONNECTION_TEST",
        entity_type="Cluster",
        entity_id=str(cluster.id),
        ip_address=client_ip,
        user_agent=user_agent,
        detail=f"Cluster connection test result={status_result}",
    )

    if status_result == "failed":
        return ClusterConnectionTestResponse(
            cluster_id=cluster.id,
            status="failed",
            message=message,
            kubernetes_version=None,
        )

    return ClusterConnectionTestResponse(
        cluster_id=cluster.id,
        status="success",
        message="Kubernetes API connection validated successfully.",
        kubernetes_version=message,
    )
