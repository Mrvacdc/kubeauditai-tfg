from datetime import datetime, timezone

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.audit import Audit
from app.models.cis_control import CisControl
from app.models.cluster import Cluster
from app.models.finding import Finding
from app.models.recommendation import Recommendation
from app.services.dashboard_service import (
    DashboardServiceError,
    get_audit_dashboard_summary,
    get_audit_remediation_plan,
)


class ReportServiceError(Exception):
    pass


def get_audit_or_raise(db: Session, audit_id: int) -> Audit:
    audit = (
        db.query(Audit)
        .filter(Audit.id == audit_id)
        .first()
    )

    if not audit:
        raise ReportServiceError("Audit not found")

    return audit


def build_cluster_info(db: Session, cluster_id: int) -> dict:
    cluster = (
        db.query(Cluster)
        .filter(Cluster.id == cluster_id)
        .first()
    )

    if not cluster:
        return {
            "cluster_id": cluster_id,
            "name": None,
            "environment": None,
            "api_server_url": None,
        }

    return {
        "cluster_id": cluster.id,
        "name": getattr(cluster, "name", None),
        "environment": getattr(cluster, "environment", None),
        "api_server_url": getattr(cluster, "api_server_url", None),
    }


def get_report_findings(
    db: Session,
    audit_id: int,
    limit: int = 50,
) -> list[dict]:
    if limit <= 0:
        raise ReportServiceError("Limit must be greater than 0")

    result_order = case(
        (Finding.result == "FAIL", 1),
        (Finding.result == "WARN", 2),
        (Finding.result == "PASS", 3),
        else_=4,
    )

    rows = (
        db.query(
            Finding.id,
            CisControl.code,
            CisControl.title,
            Finding.result,
            Finding.detail,
            Finding.evidence_sanitized,
            Finding.evidence_hash,
            Finding.detected_at,
        )
        .join(CisControl, CisControl.id == Finding.control_id)
        .filter(
            Finding.audit_id == audit_id,
            Finding.result.in_(["FAIL", "WARN"]),
        )
        .order_by(
            result_order.asc(),
            CisControl.code.asc(),
            Finding.id.asc(),
        )
        .limit(limit)
        .all()
    )

    return [
        {
            "finding_id": finding_id,
            "control_code": control_code,
            "control_title": control_title,
            "result": result,
            "detail": detail,
            "evidence_sanitized": evidence_sanitized,
            "evidence_hash": evidence_hash,
            "detected_at": detected_at,
        }
        for (
            finding_id,
            control_code,
            control_title,
            result,
            detail,
            evidence_sanitized,
            evidence_hash,
            detected_at,
        ) in rows
    ]


def get_audit_json_report(
    db: Session,
    audit_id: int,
    finding_limit: int = 50,
    remediation_limit: int = 20,
) -> dict:
    audit = get_audit_or_raise(db=db, audit_id=audit_id)

    try:
        summary = get_audit_dashboard_summary(
            db=db,
            audit_id=audit_id,
        )

        remediation_plan = get_audit_remediation_plan(
            db=db,
            audit_id=audit_id,
            limit=remediation_limit,
        )
    except DashboardServiceError as exc:
        raise ReportServiceError(str(exc)) from exc

    findings = get_report_findings(
        db=db,
        audit_id=audit_id,
        limit=finding_limit,
    )

    return {
        "generated_at": datetime.now(timezone.utc),
        "audit_id": audit.id,
        "cluster": build_cluster_info(
            db=db,
            cluster_id=audit.cluster_id,
        ),
        "summary": summary,
        "findings": findings,
        "remediation_plan": remediation_plan,
    }


def get_executive_summary_report(
    db: Session,
    audit_id: int,
) -> dict:
    audit = get_audit_or_raise(db=db, audit_id=audit_id)

    status_counts = dict(
        db.query(
            Recommendation.status,
            func.count(Recommendation.id),
        )
        .join(Finding, Finding.id == Recommendation.finding_id)
        .filter(Finding.audit_id == audit_id)
        .group_by(Recommendation.status)
        .all()
    )

    total_recommendations = sum(status_counts.values())

    high_pending_recommendations = (
        db.query(func.count(Recommendation.id))
        .join(Finding, Finding.id == Recommendation.finding_id)
        .filter(
            Finding.audit_id == audit_id,
            Recommendation.status == "PENDING",
            Recommendation.priority == "HIGH",
        )
        .scalar()
        or 0
    )

    compliance = float(audit.compliance_percentage or 0)
    failed = audit.failed_controls or 0
    warnings = audit.warning_controls or 0
    total = audit.total_controls or 0

    notes = []

    if total > 0:
        notes.append(
            "El porcentaje de cumplimiento se calcula sobre la cantidad total de controles evaluados en la auditoría."
        )

    if failed > 0:
        notes.append(
            "Existen controles en estado FAIL que deberían priorizarse en el plan de remediación."
        )

    if high_pending_recommendations > 0:
        notes.append(
            "El plan contiene recomendaciones pendientes de prioridad HIGH."
        )

    summary = (
        f"La auditoría {audit_id} evaluó {total} controles CIS Kubernetes. "
        f"El cumplimiento general fue de {compliance}%, con "
        f"{audit.passed_controls or 0} controles PASS, "
        f"{failed} controles FAIL y "
        f"{warnings} controles WARN. "
        f"Se registran {total_recommendations} recomendaciones asociadas, "
        f"de las cuales {status_counts.get('PENDING', 0)} permanecen pendientes."
    )

    return {
        "generated_at": datetime.now(timezone.utc),
        "audit_id": audit.id,
        "cluster": build_cluster_info(
            db=db,
            cluster_id=audit.cluster_id,
        ),
        "compliance_percentage": compliance,
        "total_controls": total,
        "passed_controls": audit.passed_controls or 0,
        "failed_controls": failed,
        "warning_controls": warnings,
        "total_recommendations": total_recommendations,
        "pending_recommendations": status_counts.get("PENDING", 0),
        "applied_recommendations": status_counts.get("APPLIED", 0),
        "dismissed_recommendations": status_counts.get("DISMISSED", 0),
        "high_pending_recommendations": high_pending_recommendations,
        "summary": summary,
        "notes": notes,
    }


def build_markdown_report(
    db: Session,
    audit_id: int,
    finding_limit: int = 30,
    remediation_limit: int = 15,
) -> str:
    report = get_audit_json_report(
        db=db,
        audit_id=audit_id,
        finding_limit=finding_limit,
        remediation_limit=remediation_limit,
    )

    summary = report["summary"]
    cluster = report["cluster"]
    findings = report["findings"]
    remediation_plan = report["remediation_plan"]

    lines = [
        f"# Reporte de auditoría KubeAudit - Auditoría {audit_id}",
        "",
        f"**Fecha de generación:** {report['generated_at'].isoformat()}",
        "",
        "## 1. Información del clúster",
        "",
        f"- **Cluster ID:** {cluster['cluster_id']}",
        f"- **Nombre:** {cluster.get('name') or 'N/D'}",
        f"- **Ambiente:** {cluster.get('environment') or 'N/D'}",
        f"- **API Server:** {cluster.get('api_server_url') or 'N/D'}",
        "",
        "## 2. Resumen de cumplimiento",
        "",
        f"- **Estado de auditoría:** {summary['status']}",
        f"- **Total de controles:** {summary['total_controls']}",
        f"- **PASS:** {summary['passed_controls']}",
        f"- **FAIL:** {summary['failed_controls']}",
        f"- **WARN:** {summary['warning_controls']}",
        f"- **Cumplimiento:** {summary['compliance_percentage']}%",
        "",
        "## 3. Recomendaciones por fuente y estado",
        "",
    ]

    for item in summary["recommendations_by_source_status"]:
        lines.append(
            f"- **{item['source']} / {item['status']}:** {item['count']}"
        )

    lines.extend(
        [
            "",
            "## 4. Hallazgos FAIL/WARN principales",
            "",
        ]
    )

    if not findings:
        lines.append("No se registran hallazgos FAIL/WARN.")
    else:
        for finding in findings:
            lines.extend(
                [
                    f"### {finding['control_code']} - {finding['result']}",
                    "",
                    f"**Control:** {finding['control_title']}",
                    "",
                    f"**Detalle:** {finding.get('detail') or 'N/D'}",
                    "",
                    f"**Evidencia sanitizada:** {finding.get('evidence_sanitized') or 'N/D'}",
                    "",
                    f"**Hash de evidencia:** {finding.get('evidence_hash') or 'N/D'}",
                    "",
                    f"**Detectado en:** {finding.get('detected_at') or 'N/D'}",
                    "",                    
                ]
            )

    lines.extend(
        [
            "",
            "## 5. Plan de remediación priorizado",
            "",
            f"**Total pendiente:** {remediation_plan['total_pending']}",
            "",
        ]
    )

    for item in remediation_plan["summary"]:
        lines.append(
            f"- **{item['priority']} / {item['source']}:** {item['count']}"
        )

    lines.append("")

    for item in remediation_plan["items"]:
        lines.extend(
            [
                f"### {item['control_code']} - {item['priority']} - {item['source']}",
                "",
                f"**Recomendación:** {item['title']}",
                "",
                item["recommendation_text"],
                "",
            ]
        )

    lines.extend(
        [
            "",
            "## 6. Nota metodológica",
            "",
            "Este reporte fue generado a partir de los resultados almacenados por KubeAudit, "
            "incluyendo hallazgos CIS Kubernetes, recomendaciones generadas por motor local "
            "y/o proveedor de IA, y estados de remediación registrados en la plataforma.",
            "",
        ]
    )

    return "\n".join(lines)
