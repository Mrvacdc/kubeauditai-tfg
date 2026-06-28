from app.models.finding import Finding


def infer_priority(finding: Finding) -> str:
    """
    Calcula prioridad de remediación según resultado, sección CIS y categoría.

    Reglas simples:
    - FAIL en control plane, API Server, etcd o kubelet: HIGH
    - FAIL en otros controles: MEDIUM
    - WARN en controles sensibles: MEDIUM
    - WARN general: LOW
    """
    result = finding.result.upper()
    control = finding.control

    code = control.code if control else ""
    title = (control.title or "").lower() if control else ""
    category = (control.category or "").lower() if control else ""

    sensitive_keywords = [
        "api server",
        "etcd",
        "kubelet",
        "authentication",
        "authorization",
        "secret",
        "encryption",
        "audit",
        "certificate",
        "anonymous-auth",
        "rbac",
    ]

    is_sensitive = any(
        keyword in title or keyword in category
        for keyword in sensitive_keywords
    )

    is_control_plane = code.startswith("1.")
    is_etcd = code.startswith("2.")
    is_kubelet = code.startswith("4.2")

    if result == "FAIL" and (is_control_plane or is_etcd or is_kubelet or is_sensitive):
        return "HIGH"

    if result == "FAIL":
        return "MEDIUM"

    if result == "WARN" and is_sensitive:
        return "MEDIUM"

    return "LOW"


def build_recommendation_title(finding: Finding) -> str:
    control = finding.control

    if not control:
        return "Revisar hallazgo de seguridad"

    return f"Remediar control CIS {control.code}: {control.title}"


def build_rationale(finding: Finding) -> str:
    control = finding.control
    result = finding.result.upper()

    if not control:
        return (
            "El hallazgo requiere revisión porque no se encontró información "
            "del control CIS asociado."
        )

    if result == "FAIL":
        return (
            f"El control CIS {control.code} fue evaluado como FAIL. "
            "Esto indica que la configuración observada no cumple con el criterio "
            "esperado por el benchmark y debería ser priorizada para remediación."
        )

    if result == "WARN":
        return (
            f"El control CIS {control.code} fue evaluado como WARN. "
            "Esto suele corresponder a controles manuales, validaciones parciales "
            "o configuraciones que requieren revisión profesional antes de aplicar cambios."
        )

    return (
        f"El control CIS {control.code} requiere revisión según el resultado "
        f"obtenido: {result}."
    )


def build_recommendation_text(finding: Finding) -> str:
    control = finding.control

    if not control:
        return (
            "Revisar el hallazgo detectado y contrastarlo con la documentación "
            "del CIS Kubernetes Benchmark antes de aplicar cambios."
        )

    remediation = control.remediation_reference
    evidence = finding.evidence_sanitized

    parts = [
        f"Control CIS: {control.code}",
        f"Título: {control.title}",
        f"Resultado: {finding.result}",
        "",
        "Acción recomendada:",
    ]

    if remediation:
        parts.append(remediation.strip())
    else:
        parts.append(
            "Revisar la configuración asociada al control y aplicar la remediación "
            "correspondiente según el CIS Kubernetes Benchmark."
        )

    if evidence:
        parts.extend(
            [
                "",
                "Evidencia sanitizada:",
                evidence.strip()[:3000],
            ]
        )

    parts.extend(
        [
            "",
            "Nota operacional:",
            (
                "Antes de aplicar la remediación en un entorno productivo, validar impacto, "
                "realizar backup de manifiestos o configuración afectada, aplicar primero "
                "en ambiente de prueba y documentar el cambio."
            ),
        ]
    )

    return "\n".join(parts)
