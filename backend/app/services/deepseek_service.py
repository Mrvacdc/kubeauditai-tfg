import json
from typing import Any

from openai import OpenAI

from app.core.config import get_settings
from app.models.finding import Finding


class DeepSeekRecommendationError(Exception):
    pass


ALLOWED_PRIORITIES = {"HIGH", "MEDIUM", "LOW"}


def generate_recommendation_with_deepseek(finding: Finding) -> dict[str, str]:
    settings = get_settings()

    if not settings.DEEPSEEK_API_KEY:
        raise DeepSeekRecommendationError("DEEPSEEK_API_KEY is not configured")

    try:
        client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )

        payload = build_prompt_payload(finding)

        last_json_error: Exception | None = None

        for attempt in range(2):
            response = client.chat.completions.create(
                model=settings.DEEPSEEK_MODEL,
                temperature=settings.AI_RECOMMENDATION_TEMPERATURE,
                max_tokens=settings.AI_RECOMMENDATION_MAX_TOKENS,
                response_format={"type": "json_object"},
                extra_body={
                    "thinking": {
                        "type": "disabled"
                    }
                },
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eres un especialista senior en seguridad Kubernetes, "
                            "CIS Benchmark, hardening, DevSecOps y operación SRE. "
                            "Debes generar recomendaciones accionables, prudentes y "
                            "seguras para remediar hallazgos de auditoría. "
                            "Responde exclusivamente en JSON válido, sin markdown, "
                            "sin texto adicional y respetando exactamente el esquema solicitado."
                        ),
                    },
                    {
                        "role": "user",
                        "content": json.dumps(payload, ensure_ascii=False),
                    },
                ],
            )

            content = response.choices[0].message.content

            if not content:
                raise DeepSeekRecommendationError("DeepSeek returned empty content")

            try:
                data = json.loads(content)
                return normalize_deepseek_response(data=data, finding=finding)
            except json.JSONDecodeError as exc:
                last_json_error = exc

                if attempt == 0:
                    continue

                raise DeepSeekRecommendationError(
                    f"DeepSeek returned invalid JSON after retry: {exc}"
                ) from exc

        raise DeepSeekRecommendationError(
            f"DeepSeek returned invalid JSON: {last_json_error}"
        )

    except DeepSeekRecommendationError:
        raise
    except Exception as exc:
        raise DeepSeekRecommendationError(str(exc)) from exc


def build_prompt_payload(finding: Finding) -> dict[str, Any]:
    control = finding.control

    return {
        "task": "Generar una recomendación de remediación para un hallazgo CIS Kubernetes.",
        "language": "es",
        "output_schema": {
            "title": "string",
            "recommendation_text": "string",
            "rationale": "string",
            "priority": "HIGH | MEDIUM | LOW",
            "operational_notes": "string",
        },
        "security_rules": [
            "No inventar evidencia.",
            "No solicitar ni exponer secretos.",
            "No incluir kubeconfigs, tokens, certificados privados ni credenciales.",
            "No recomendar cambios destructivos sin advertencias operativas.",
            "Priorizar acciones verificables y reversibles.",
        ],
        "finding": {
            "finding_id": finding.id,
            "result": finding.result,
            "evidence_sanitized": truncate_text(build_evidence_text(finding), 2500),
        },
        "cis_control": {
            "code": getattr(control, "code", None),
            "title": getattr(control, "title", None),
            "category": getattr(control, "category", None),
            "remediation_reference": truncate_text(
                getattr(control, "remediation_reference", "") or "",
                2500,
            ),
        },
    }


def normalize_deepseek_response(
    data: dict[str, Any],
    finding: Finding,
) -> dict[str, str]:
    title = str(
        data.get("title")
        or f"Remediar control CIS {finding.control.code}"
    ).strip()

    recommendation_text = str(
        data.get("recommendation_text")
        or data.get("recommendation")
        or ""
    ).strip()

    rationale = str(data.get("rationale") or "").strip()

    priority = str(data.get("priority") or "MEDIUM").upper().strip()

    operational_notes = str(data.get("operational_notes") or "").strip()

    if priority not in ALLOWED_PRIORITIES:
        priority = "MEDIUM"

    if not recommendation_text:
        raise DeepSeekRecommendationError(
            "DeepSeek response missing recommendation_text"
        )

    if operational_notes:
        recommendation_text = (
            f"{recommendation_text}\n\n"
            f"Nota operacional:\n{operational_notes}"
        )

    return {
        "title": title[:255],
        "recommendation_text": recommendation_text,
        "rationale": rationale or "Recomendación generada por IA a partir del resultado CIS y la evidencia sanitizada.",
        "priority": priority,
        "source": "deepseek",
    }


def truncate_text(value: str, max_length: int) -> str:
    if len(value) <= max_length:
        return value

    return value[:max_length] + "\n...[TRUNCATED]"


def build_evidence_text(finding: Finding) -> str:
    """
    Construye evidencia sanitizada desde los campos reales del modelo Finding.

    No asume que exista finding.evidence.
    """
    evidence = {
        "audit": getattr(finding, "audit", None),
        "actual_value": getattr(finding, "actual_value", None),
        "expected_result": getattr(finding, "expected_result", None),
        "reason": getattr(finding, "reason", None),
        "result": getattr(finding, "result", None),
    }

    cleaned = {
        key: value
        for key, value in evidence.items()
        if value is not None and str(value).strip() != ""
    }

    return json.dumps(cleaned, ensure_ascii=False, default=str)
