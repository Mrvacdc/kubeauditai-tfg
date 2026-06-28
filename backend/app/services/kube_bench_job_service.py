import ast
import json
import time
import uuid
from typing import Any

from kubernetes import client
from kubernetes.client import ApiClient
from kubernetes.client.exceptions import ApiException

from app.core.config import get_settings
from app.services.kubernetes_client_service import (
    KubernetesConnectionError,
    build_api_client_from_kubeconfig,
)


class KubeBenchJobError(Exception):
    """
    Error controlado durante la ejecución de kube-bench como Job.
    """
    pass

def extract_json_from_logs(logs: str) -> dict[str, Any]:
    """
    Extrae resultado de kube-bench desde logs.

    Soporta:
    - JSON válido con comillas dobles.
    - Representación Python tipo dict con comillas simples.
    - Texto antes o después del contenido principal.
    """
    if not logs or not str(logs).strip():
        raise KubeBenchJobError("kube-bench produced empty logs.")

    text = str(logs).strip()

    def is_kube_bench_payload(value: Any) -> bool:
        return isinstance(value, dict) and (
            "Controls" in value
            or "controls" in value
            or "Totals" in value
            or "totals" in value
        )

    # Caso 1: JSON puro válido
    try:
        parsed = json.loads(text)
        if is_kube_bench_payload(parsed):
            return parsed
    except json.JSONDecodeError:
        pass

    # Caso 2: dict Python convertido a string, ejemplo {'Controls': [...]}
    try:
        parsed = ast.literal_eval(text)
        if is_kube_bench_payload(parsed):
            return parsed
    except (ValueError, SyntaxError):
        pass

    # Caso 3: hay texto antes/después, buscamos desde cada llave
    decoder = json.JSONDecoder()

    for index, char in enumerate(text):
        if char != "{":
            continue

        candidate = text[index:]

        try:
            parsed, _ = decoder.raw_decode(candidate)
            if is_kube_bench_payload(parsed):
                return parsed
        except json.JSONDecodeError:
            pass

        try:
            parsed = ast.literal_eval(candidate)
            if is_kube_bench_payload(parsed):
                return parsed
        except (ValueError, SyntaxError):
            pass

    preview_start = text[:300].replace("\n", "\\n")
    preview_end = text[-300:].replace("\n", "\\n")

    raise KubeBenchJobError(
        "Unable to locate valid kube-bench JSON object in logs. "
        f"Log length={len(text)}. "
        f"Start preview={preview_start}. "
        f"End preview={preview_end}."
    )


def ensure_namespace(api_client: ApiClient, namespace: str) -> None:
    """
    Crea el namespace si no existe.
    """
    core_v1 = client.CoreV1Api(api_client)

    try:
        core_v1.read_namespace(name=namespace)
    except ApiException as exc:
        if exc.status != 404:
            raise KubeBenchJobError(
                f"Unable to read namespace {namespace}: {exc.reason}"
            ) from exc

        namespace_body = client.V1Namespace(
            metadata=client.V1ObjectMeta(name=namespace)
        )

        core_v1.create_namespace(body=namespace_body)


def build_kube_bench_job(
    job_name: str,
    namespace: str,
    image: str,
) -> client.V1Job:
    """
    Construye un Job de kube-bench compatible con kind para demo.

    Notas:
    - host_pid=True permite inspeccionar procesos del nodo.
    - hostPath monta directorios del nodo necesarios para los controles CIS.
    - --exit-code 0 evita que el Job falle solo porque kube-bench encuentre controles FAIL.
    """
    labels = {
        "app": "kubeaudit",
        "component": "kube-bench",
        "job-name": job_name,
    }

    volume_mounts = [
        client.V1VolumeMount(
            name="var-lib-etcd",
            mount_path="/var/lib/etcd",
            read_only=True,
        ),
        client.V1VolumeMount(
            name="etc-kubernetes",
            mount_path="/etc/kubernetes",
            read_only=True,
        ),
        client.V1VolumeMount(
            name="etc-systemd",
            mount_path="/etc/systemd",
            read_only=True,
        ),
        client.V1VolumeMount(
            name="lib-systemd",
            mount_path="/lib/systemd",
            read_only=True,
        ),
        client.V1VolumeMount(
            name="srv-kubernetes",
            mount_path="/srv/kubernetes",
            read_only=True,
        ),
        client.V1VolumeMount(
            name="etc-cni-netd",
            mount_path="/etc/cni/net.d",
            read_only=True,
        ),
        client.V1VolumeMount(
            name="opt-cni-bin",
            mount_path="/opt/cni/bin",
            read_only=True,
        ),
        client.V1VolumeMount(
            name="etc-passwd",
            mount_path="/etc/passwd",
            read_only=True,
        ),
        client.V1VolumeMount(
            name="etc-group",
            mount_path="/etc/group",
            read_only=True,
        ),
    ]

    volumes = [
        client.V1Volume(
            name="var-lib-etcd",
            host_path=client.V1HostPathVolumeSource(path="/var/lib/etcd"),
        ),
        client.V1Volume(
            name="etc-kubernetes",
            host_path=client.V1HostPathVolumeSource(path="/etc/kubernetes"),
        ),
        client.V1Volume(
            name="etc-systemd",
            host_path=client.V1HostPathVolumeSource(path="/etc/systemd"),
        ),
        client.V1Volume(
            name="lib-systemd",
            host_path=client.V1HostPathVolumeSource(path="/lib/systemd"),
        ),
        client.V1Volume(
            name="srv-kubernetes",
            host_path=client.V1HostPathVolumeSource(path="/srv/kubernetes"),
        ),
        client.V1Volume(
            name="etc-cni-netd",
            host_path=client.V1HostPathVolumeSource(path="/etc/cni/net.d"),
        ),
        client.V1Volume(
            name="opt-cni-bin",
            host_path=client.V1HostPathVolumeSource(path="/opt/cni/bin"),
        ),
        client.V1Volume(
            name="etc-passwd",
            host_path=client.V1HostPathVolumeSource(path="/etc/passwd"),
        ),
        client.V1Volume(
            name="etc-group",
            host_path=client.V1HostPathVolumeSource(path="/etc/group"),
        ),
    ]

    container = client.V1Container(
        name="kube-bench",
        image=image,
        image_pull_policy="IfNotPresent",
        command=["kube-bench"],
        args=[
            "--json",
            "--exit-code",
            "0",
        ],
        security_context=client.V1SecurityContext(
            privileged=True,
            run_as_user=0,
        ),
        volume_mounts=volume_mounts,
    )

    pod_spec = client.V1PodSpec(
        restart_policy="Never",
        host_pid=True,
        containers=[container],
        volumes=volumes,
        tolerations=[
            client.V1Toleration(
                key="node-role.kubernetes.io/control-plane",
                operator="Exists",
                effect="NoSchedule",
            ),
            client.V1Toleration(
                key="node-role.kubernetes.io/master",
                operator="Exists",
                effect="NoSchedule",
            ),
        ],
    )

    pod_template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels=labels),
        spec=pod_spec,
    )

    job_spec = client.V1JobSpec(
        template=pod_template,
        backoff_limit=0,
        ttl_seconds_after_finished=300,
    )

    return client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(
            name=job_name,
            namespace=namespace,
            labels=labels,
        ),
        spec=job_spec,
    )


def wait_for_job_completion(
    api_client: ApiClient,
    namespace: str,
    job_name: str,
    timeout_seconds: int,
) -> str:
    """
    Espera a que el Job termine y devuelve el nombre del Pod asociado.
    """
    batch_v1 = client.BatchV1Api(api_client)
    core_v1 = client.CoreV1Api(api_client)

    deadline = time.time() + timeout_seconds
    pod_name = None

    while time.time() < deadline:
        pods = core_v1.list_namespaced_pod(
            namespace=namespace,
            label_selector=f"job-name={job_name}",
        )

        if pods.items:
            pod_name = pods.items[0].metadata.name

        job = batch_v1.read_namespaced_job(
            name=job_name,
            namespace=namespace,
        )

        if job.status.succeeded and job.status.succeeded >= 1:
            if not pod_name:
                raise KubeBenchJobError(
                    "kube-bench Job completed but no Pod was found."
                )
            return pod_name

        if job.status.failed and job.status.failed >= 1:
            if pod_name:
                pod = core_v1.read_namespaced_pod(
                    name=pod_name,
                    namespace=namespace,
                )

                container_statuses = pod.status.container_statuses or []
                reasons = []

                for status in container_statuses:
                    state = status.state
                    if state and state.terminated:
                        reasons.append(
                            f"{status.name}: exit_code={state.terminated.exit_code}, "
                            f"reason={state.terminated.reason}"
                        )

                reason_text = "; ".join(reasons) if reasons else "unknown reason"
                raise KubeBenchJobError(
                    f"kube-bench Job failed: {reason_text}"
                )

            raise KubeBenchJobError("kube-bench Job failed and no Pod was found.")

        time.sleep(2)

    raise KubeBenchJobError(
        f"Timed out waiting for kube-bench Job after {timeout_seconds} seconds."
    )


def read_pod_logs(
    api_client: ApiClient,
    namespace: str,
    pod_name: str,
) -> str:
    """
    Lee logs crudos del Pod de kube-bench.

    Importante:
    Debe devolver el texto tal como lo entrega Kubernetes, no una conversión
    a dict ni str(dict).
    """
    core_v1 = client.CoreV1Api(api_client)

    try:
        logs = core_v1.read_namespaced_pod_log(
            name=pod_name,
            namespace=namespace,
            container="kube-bench",
        )

        if isinstance(logs, bytes):
            return logs.decode("utf-8")

        if isinstance(logs, str):
            return logs

        return json.dumps(logs)

    except ApiException as exc:
        raise KubeBenchJobError(
            f"Unable to read kube-bench Pod logs: status={exc.status}, reason={exc.reason}"
        ) from exc


def cleanup_job(
    api_client: ApiClient,
    namespace: str,
    job_name: str,
) -> None:
    """
    Elimina el Job y sus Pods asociados.
    """
    batch_v1 = client.BatchV1Api(api_client)

    try:
        batch_v1.delete_namespaced_job(
            name=job_name,
            namespace=namespace,
            propagation_policy="Foreground",
        )
    except ApiException as exc:
        if exc.status != 404:
            raise

def read_kube_bench_json_from_logs_with_retry(
    api_client: ApiClient,
    namespace: str,
    pod_name: str,
    retries: int = 10,
    delay_seconds: int = 2,
) -> dict[str, Any]:
    last_error = None
    last_log_length = 0

    for _ in range(retries):
        logs = read_pod_logs(
            api_client=api_client,
            namespace=namespace,
            pod_name=pod_name,
        )

        last_log_length = len(logs or "")

        try:
            return extract_json_from_logs(logs)
        except KubeBenchJobError as exc:
            last_error = exc
            time.sleep(delay_seconds)

    raise KubeBenchJobError(
        f"Unable to parse kube-bench JSON after {retries} attempts. "
        f"Last log length={last_log_length}. "
        f"Last error={last_error}"
    )

def run_kube_bench_job_from_kubeconfig(
    kubeconfig_path: str,
) -> tuple[dict[str, Any], str]:
    """
    Ejecuta kube-bench como Job usando un kubeconfig externo.

    Devuelve:
    - JSON parseado de kube-bench
    - referencia del Job ejecutado
    """
    settings = get_settings()

    try:
        api_client = build_api_client_from_kubeconfig(kubeconfig_path)
    except KubernetesConnectionError as exc:
        raise KubeBenchJobError(str(exc)) from exc

    namespace = settings.KUBE_BENCH_NAMESPACE
    job_name = f"kube-bench-{uuid.uuid4().hex[:8]}"

    ensure_namespace(api_client=api_client, namespace=namespace)

    job = build_kube_bench_job(
        job_name=job_name,
        namespace=namespace,
        image=settings.KUBE_BENCH_IMAGE,
    )

    batch_v1 = client.BatchV1Api(api_client)

    try:
        batch_v1.create_namespaced_job(
            namespace=namespace,
            body=job,
        )

        pod_name = wait_for_job_completion(
            api_client=api_client,
            namespace=namespace,
            job_name=job_name,
            timeout_seconds=settings.KUBE_BENCH_JOB_TIMEOUT_SECONDS,
        )

        logs = read_pod_logs(
            api_client=api_client,
            namespace=namespace,
            pod_name=pod_name,
        )
        
        raw_json = read_kube_bench_json_from_logs_with_retry(
            api_client=api_client,
            namespace=namespace,
            pod_name=pod_name,
            retries=10,
            delay_seconds=2,
        )
        raw_json = extract_json_from_logs(logs)

        return raw_json, f"kubernetes-job:{namespace}/{job_name}"

    except ApiException as exc:
        raise KubeBenchJobError(
            f"Kubernetes API error while running kube-bench: status={exc.status}, reason={exc.reason}"
        ) from exc

    finally:
        if settings.KUBE_BENCH_CLEANUP_JOB:
            cleanup_job(
                api_client=api_client,
                namespace=namespace,
                job_name=job_name,
            )
