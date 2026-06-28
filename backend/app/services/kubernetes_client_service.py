from pathlib import Path
from typing import Optional

from kubernetes import client, config
from kubernetes.client import ApiClient
from kubernetes.client.exceptions import ApiException


class KubernetesConnectionError(Exception):
    """
    Error controlado para fallas de conexión con Kubernetes.
    """
    pass


def _validate_kubeconfig_path(kubeconfig_path: str) -> Path:
    """
    Valida que el kubeconfig exista y sea un archivo.

    No imprime ni devuelve el contenido del kubeconfig.
    """
    path = Path(kubeconfig_path).expanduser().resolve()

    if not path.exists():
        raise KubernetesConnectionError(
            f"Kubeconfig file does not exist: {path}"
        )

    if not path.is_file():
        raise KubernetesConnectionError(
            f"Kubeconfig path is not a file: {path}"
        )

    return path


def build_api_client_from_kubeconfig(kubeconfig_path: str) -> ApiClient:
    """
    Construye un ApiClient de Kubernetes usando un kubeconfig local.

    Este método es adecuado para la demo sobre EC2, donde el archivo kubeconfig
    queda almacenado fuera del repositorio y con permisos restringidos.
    """
    path = _validate_kubeconfig_path(kubeconfig_path)

    try:
        return config.new_client_from_config(config_file=str(path))
    except Exception as exc:
        raise KubernetesConnectionError(
            "Unable to load kubeconfig. Verify file format, certificates and permissions."
        ) from exc

def validate_kubernetes_connection(
    connection_mode: str,
    credential_reference: Optional[str],
) -> str:
    """
    Valida conexión contra Kubernetes API y devuelve la versión del clúster.

    Por ahora se implementa kubeconfig. service_account queda reservado
    para una fase posterior o para integración con Secrets Manager.
    """
    if connection_mode == "kubeconfig":
        if not credential_reference:
            raise KubernetesConnectionError(
                "credential_reference is required for kubeconfig connection mode."
            )

        api_client = build_api_client_from_kubeconfig(credential_reference)

    elif connection_mode == "service_account":
        raise KubernetesConnectionError(
            "service_account connection mode is not implemented yet in the MVP."
        )

    else:
        raise KubernetesConnectionError(
            f"Unsupported connection_mode: {connection_mode}"
        )

    try:
        version_api = client.VersionApi(api_client)
        version_info = version_api.get_code()
        return version_info.git_version

    except ApiException as exc:
        raise KubernetesConnectionError(
            f"Kubernetes API returned an error: status={exc.status}, reason={exc.reason}"
        ) from exc

    except Exception as exc:
        raise KubernetesConnectionError(
            "Unable to connect to Kubernetes API. Verify network, credentials and certificates."
        ) from exc
