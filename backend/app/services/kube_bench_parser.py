import hashlib
import json
import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any


class KubeBenchParseError(Exception):
    """
    Error controlado para archivos kube-bench inválidos.
    """
    pass


@dataclass
class ParsedFinding:
    control_code: str
    title: str
    category: str | None
    result: str
    detail: str | None
    evidence_sanitized: str | None
    evidence_hash: str | None
    remediation_reference: str | None


@dataclass
class ParsedAudit:
    total_controls: int
    passed_controls: int
    failed_controls: int
    warning_controls: int
    compliance_percentage: Decimal
    benchmark_version: str | None
    detected_kubernetes_version: str | None
    benchmark_profile: str | None
    audit_scope: list[str]
    findings: list[ParsedFinding]


SENSITIVE_PATTERNS = [
    # Bloques PEM completos: deben evaluarse antes que patrones clave-valor.
    re.compile(
        r"-----BEGIN\s+[A-Z0-9 ]*PRIVATE\s+KEY-----.*?-----END\s+[A-Z0-9 ]*PRIVATE\s+KEY-----",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"-----BEGIN\s+CERTIFICATE-----.*?-----END\s+CERTIFICATE-----",
        re.IGNORECASE | re.DOTALL,
    ),

    # Tokens Bearer.
    re.compile(r"Bearer\s+[A-Za-z0-9._\-]+", re.IGNORECASE),

    # Secretos en formato clave-valor, incluyendo nombres compuestos.
    # Ejemplos: aws_secret_access_key=..., api_key=..., client_secret=...
    re.compile(
        r"[A-Za-z0-9_.\-]*(?:token|password|passwd|secret|credential|api[_\-]?key|access[_\-]?key|private[_\-]?key|client[_\-]?secret)[A-Za-z0-9_.\-]*\s*[:=]\s*[^\s,;\"'}]+",
        re.IGNORECASE,
    ),

    # Identificadores AWS Access Key ID, cuando aparecen como valor directo.
    re.compile(r"AKIA[0-9A-Z]{16}", re.IGNORECASE),
    re.compile(r"ASIA[0-9A-Z]{16}", re.IGNORECASE),

    # Patrones específicos originales.
    re.compile(r"token[:=]\s*[A-Za-z0-9._\-]+", re.IGNORECASE),
    re.compile(r"password[:=]\s*\S+", re.IGNORECASE),
    re.compile(r"secret[:=]\s*\S+", re.IGNORECASE),
    re.compile(r"client-key-data[:=]\s*\S+", re.IGNORECASE),
    re.compile(r"client-certificate-data[:=]\s*\S+", re.IGNORECASE),
    re.compile(r"certificate-authority-data[:=]\s*\S+", re.IGNORECASE),
]


def sanitize_evidence(value: Any) -> str | None:
    """
    Sanitiza evidencia técnica para evitar persistir secretos accidentales.

    En esta fase se aplica sanitización básica. En la fase de IA se reforzará
    con validaciones adicionales antes de enviar datos al modelo.
    """
    if value is None:
        return None

    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    else:
        text = str(value)

    for pattern in SENSITIVE_PATTERNS:
        text = pattern.sub("<REDACTED>", text)

    return text.strip()


def hash_evidence(value: str | None) -> str | None:
    """
    Genera hash SHA-256 de la evidencia sanitizada para trazabilidad.
    """
    if not value:
        return None

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_result(status: str | None) -> str:
    """
    Normaliza estados de kube-bench.
    """
    if not status:
        return "WARN"

    status = status.upper().strip()

    if status in {"PASS", "FAIL", "WARN"}:
        return status

    if status in {"INFO", "MANUAL"}:
        return "WARN"

    return "WARN"


def calculate_compliance_percentage(passed: int, total: int) -> Decimal:
    """
    Calcula porcentaje de cumplimiento.

    Fórmula:
    controles aprobados / total de controles evaluados * 100
    """
    if total == 0:
        return Decimal("0.00")

    value = (Decimal(passed) / Decimal(total)) * Decimal(100)
    return value.quantize(Decimal("0.01"))


def collapse_metadata_values(values: set[str]) -> str | None:
    """
    Normaliza un conjunto de valores de metadata de kube-bench.

    Si hay un solo valor lo devuelve directamente. Si hay más de uno,
    los conserva en una lista separada por comas para trazabilidad.
    """
    cleaned = sorted(
        str(value).strip()
        for value in values
        if value is not None and str(value).strip()
    )

    if not cleaned:
        return None

    return ",".join(cleaned)


def infer_scope_from_control(control_group: dict[str, Any]) -> str | None:
    """
    Determina el alcance o target evaluado a partir de la metadata del grupo
    de controles de kube-bench.
    """
    node_type = control_group.get("node_type")
    if node_type:
        return str(node_type).strip()

    text = str(control_group.get("text") or control_group.get("desc") or "").lower()

    if "etcd" in text:
        return "etcd"

    if "control plane" in text:
        return "controlplane"

    if "worker" in text or "node" in text:
        return "node"

    if "policies" in text or "policy" in text:
        return "policies"

    return None


def load_json_content(raw_content: bytes) -> dict[str, Any]:
    """
    Carga contenido JSON desde bytes.
    """
    try:
        decoded = raw_content.decode("utf-8")
        return json.loads(decoded)
    except UnicodeDecodeError as exc:
        raise KubeBenchParseError("File must be UTF-8 encoded.") from exc
    except json.JSONDecodeError as exc:
        raise KubeBenchParseError("File is not a valid JSON document.") from exc


def parse_kube_bench_json(raw_data: dict[str, Any]) -> ParsedAudit:
    """
    Parsea un resultado JSON de kube-bench.

    Soporta la estructura habitual:
    {
      "Controls": [
        {
          "tests": [
            {
              "results": [
                {
                  "test_number": "...",
                  "test_desc": "...",
                  "status": "PASS|FAIL|WARN"
                }
              ]
            }
          ]
        }
      ]
    }
    """
    controls = raw_data.get("Controls") or raw_data.get("controls")

    if not isinstance(controls, list):
        raise KubeBenchParseError(
            "Invalid kube-bench JSON: expected 'Controls' list."
        )

    findings: list[ParsedFinding] = []

    passed = 0
    failed = 0
    warnings = 0

    benchmark_versions: set[str] = set()
    detected_versions: set[str] = set()
    audit_scope_values: set[str] = set()

    for control_group in controls:
        if not isinstance(control_group, dict):
            continue

        version = control_group.get("version")
        detected_version = control_group.get("detected_version")
        scope_value = infer_scope_from_control(control_group)

        if version:
            benchmark_versions.add(str(version))

        if detected_version:
            detected_versions.add(str(detected_version))

        if scope_value:
            audit_scope_values.add(scope_value)

        group_text = control_group.get("text") or control_group.get("desc")
        tests = control_group.get("tests", [])

        if not isinstance(tests, list):
            continue

        for test in tests:
            category = test.get("desc") or group_text
            results = test.get("results", [])

            if not isinstance(results, list):
                continue

            for result_item in results:
                control_code = (
                    result_item.get("test_number")
                    or result_item.get("id")
                    or result_item.get("number")
                )

                title = (
                    result_item.get("test_desc")
                    or result_item.get("desc")
                    or "Unnamed CIS control"
                )

                status = normalize_result(result_item.get("status"))

                evidence_raw = {
                    "audit": result_item.get("audit"),
                    "actual_value": result_item.get("actual_value"),
                    "expected_result": result_item.get("expected_result"),
                    "reason": result_item.get("reason"),
                }

                evidence_sanitized = sanitize_evidence(evidence_raw)
                evidence_hash = hash_evidence(evidence_sanitized)

                remediation_reference = result_item.get("remediation")

                if not control_code:
                    control_code = f"unknown-{len(findings) + 1}"

                if status == "PASS":
                    passed += 1
                elif status == "FAIL":
                    failed += 1
                else:
                    warnings += 1

                findings.append(
                    ParsedFinding(
                        control_code=str(control_code),
                        title=str(title),
                        category=str(category) if category else None,
                        result=status,
                        detail=str(title),
                        evidence_sanitized=evidence_sanitized,
                        evidence_hash=evidence_hash,
                        remediation_reference=(
                            str(remediation_reference)
                            if remediation_reference
                            else None
                        ),
                    )
                )

    total = len(findings)

    if total == 0:
        raise KubeBenchParseError(
            "No kube-bench results were found in the uploaded JSON."
        )

    compliance_percentage = calculate_compliance_percentage(
        passed=passed,
        total=total,
    )

    benchmark_version = collapse_metadata_values(benchmark_versions)
    detected_kubernetes_version = collapse_metadata_values(detected_versions)
    audit_scope = sorted(audit_scope_values)

    return ParsedAudit(
        total_controls=total,
        passed_controls=passed,
        failed_controls=failed,
        warning_controls=warnings,
        compliance_percentage=compliance_percentage,
        benchmark_version=benchmark_version,
        detected_kubernetes_version=detected_kubernetes_version,
        benchmark_profile=benchmark_version,
        audit_scope=audit_scope,
        findings=findings,
    )
