from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class ClusterCreate(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    description: Optional[str] = None
    api_server: HttpUrl
    namespace_target: Optional[str] = None

    connection_mode: str = Field(
        default="kubeconfig",
        pattern="^(kubeconfig|service_account)$",
    )

    credential_reference: Optional[str] = Field(
        default=None,
        description=(
            "Referencia segura a credenciales. Para demo puede ser una ruta local "
            "a un kubeconfig protegido. No debe contener tokens ni secretos en texto plano."
        ),
    )


class ClusterRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    api_server: str
    namespace_target: Optional[str]
    connection_mode: str
    credential_reference: Optional[str]
    ca_certificate_fingerprint: Optional[str]
    kubernetes_version: Optional[str]
    last_connection_status: Optional[str]
    last_connection_checked_at: Optional[datetime]
    registered_by_user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class ClusterConnectionTestResponse(BaseModel):
    cluster_id: int
    status: str
    message: str
    kubernetes_version: Optional[str] = None
