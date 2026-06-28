import pytest

from app.services.kubernetes_client_service import (
    KubernetesConnectionError,
    validate_kubernetes_connection,
)


def test_kubeconfig_mode_requires_credential_reference():
    with pytest.raises(KubernetesConnectionError) as exc:
        validate_kubernetes_connection(
            connection_mode="kubeconfig",
            credential_reference=None,
        )

    assert "credential_reference is required" in str(exc.value)


def test_unsupported_connection_mode_should_fail():
    with pytest.raises(KubernetesConnectionError) as exc:
        validate_kubernetes_connection(
            connection_mode="unsupported",
            credential_reference="/tmp/fake",
        )

    assert "Unsupported connection_mode" in str(exc.value)
