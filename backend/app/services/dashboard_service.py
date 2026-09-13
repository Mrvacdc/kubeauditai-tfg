from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.audit import Audit
from app.models.finding import Finding
from app.models.recommendation import Recommendation
from app.models.cis_control import CisControl

class DashboardServiceError(Exception):
    pass


def get_audit_dashboard_summary(
    db: Session,
    audit_id: int,
) -> dict:
    audit = (
        db.query(Audit)
        .filter(Audit.id == audit_id)
        .first()
    )

    if not audit:
        raise DashboardServiceError("Audit not found")

    findings_by_result = [
        {
            "name": result or "UNKNOWN",
            "count": count,
        }
        for result, count in (
            db.query(
                Finding.result,
                func.count(Finding.id),
            )
            .filter(Finding.audit_id == audit_id)
            .group_by(Finding.result)
            .order_by(Finding.result)
            .all()
        )
    ]

    recommendations_by_status = [
        {
            "name": status or "UNKNOWN",
            "count": count,
        }
        for status, count in (
            db.query(
                Recommendation.status,
                func.count(Recommendation.id),
            )
            .join(Finding, Finding.id == Recommendation.finding_id)
            .filter(Finding.audit_id == audit_id)
            .group_by(Recommendation.status)
            .order_by(Recommendation.status)
            .all()
        )
    ]

    recommendations_by_source_status = [
        {
            "source": source or "UNKNOWN",
            "status": status or "UNKNOWN",
            "count": count,
        }
        for source, status, count in (
            db.query(
                Recommendation.source,
                Recommendation.status,
                func.count(Recommendation.id),
            )
            .join(Finding, Finding.id == Recommendation.finding_id)
            .filter(Finding.audit_id == audit_id)
            .group_by(Recommendation.source, Recommendation.status)
            .order_by(Recommendation.source, Recommendation.status)
            .all()
        )
    ]

    recommendations_by_priority_status = [
        {
            "priority": priority or "UNKNOWN",
            "status": status or "UNKNOWN",
            "count": count,
        }
        for priority, status, count in (
            db.query(
                Recommendation.priority,
                Recommendation.status,
                func.count(Recommendation.id),
            )
            .join(Finding, Finding.id == Recommendation.finding_id)
            .filter(Finding.audit_id == audit_id)
            .group_by(Recommendation.priority, Recommendation.status)
            .order_by(Recommendation.priority, Recommendation.status)
            .all()
        )
    ]

    top_failed_controls = [
        {
            "control_code": code,
            "title": title,
            "result": result,
            "count": count,
        }
        for code, title, result, count in (
            db.query(
                CisControl.code,
                CisControl.title,
                Finding.result,
                func.count(Finding.id),
            )
            .join(Finding, Finding.control_id == CisControl.id)
            .filter(
                Finding.audit_id == audit_id,
                Finding.result.in_(["FAIL", "WARN"]),
            )
            .group_by(
                CisControl.code,
                CisControl.title,
                Finding.result,
            )
            .order_by(
                Finding.result.asc(),
                func.count(Finding.id).desc(),
                CisControl.code.asc(),
            )
            .limit(10)
            .all()
        )
    ]

    return {
        "audit_id": audit.id,
        "cluster_id": audit.cluster_id,
        "status": audit.status,
        "total_controls": audit.total_controls or 0,
        "passed_controls": audit.passed_controls or 0,
        "failed_controls": audit.failed_controls or 0,
        "warning_controls": audit.warning_controls or 0,
        "compliance_percentage": float(audit.compliance_percentage or 0),
        "findings_by_result": findings_by_result,
        "recommendations_by_status": recommendations_by_status,
        "recommendations_by_source_status": recommendations_by_source_status,
        "recommendations_by_priority_status": recommendations_by_priority_status,
        "top_failed_controls": top_failed_controls,
    }


def get_cluster_audit_history(
    db: Session,
    cluster_id: int,
    limit: int = 10,
) -> dict:
    if limit <= 0:
        raise DashboardServiceError("Limit must be greater than 0")

    audits = (
        db.query(Audit)
        .filter(Audit.cluster_id == cluster_id)
        .order_by(Audit.created_at.desc())
        .limit(limit)
        .all()
    )

    return {
        "cluster_id": cluster_id,
        "total_audits": len(audits),
        "audits": [
            {
                "audit_id": audit.id,
                "status": audit.status,
                "total_controls": audit.total_controls or 0,
                "passed_controls": audit.passed_controls or 0,
                "failed_controls": audit.failed_controls or 0,
                "warning_controls": audit.warning_controls or 0,
                "compliance_percentage": float(
                    audit.compliance_percentage or 0
                ),
                "created_at": audit.created_at,
            }
            for audit in audits
        ],
    }


def build_audit_comparison_snapshot(audit: Audit) -> dict:
    return {
        "audit_id": audit.id,
        "cluster_id": audit.cluster_id,
        "status": audit.status,
        "total_controls": audit.total_controls or 0,
        "passed_controls": audit.passed_controls or 0,
        "failed_controls": audit.failed_controls or 0,
        "warning_controls": audit.warning_controls or 0,
        "compliance_percentage": float(audit.compliance_percentage or 0),
        "created_at": audit.created_at,
    }


def get_audit_comparison(
    db: Session,
    base_audit_id: int,
    target_audit_id: int,
) -> dict:
    base_audit = (
        db.query(Audit)
        .filter(Audit.id == base_audit_id)
        .first()
    )

    if not base_audit:
        raise DashboardServiceError("Base audit not found")

    target_audit = (
        db.query(Audit)
        .filter(Audit.id == target_audit_id)
        .first()
    )

    if not target_audit:
        raise DashboardServiceError("Target audit not found")

    if base_audit.cluster_id != target_audit.cluster_id:
        raise DashboardServiceError(
            "Audits belong to different clusters and cannot be compared"
        )

    base_snapshot = build_audit_comparison_snapshot(base_audit)
    target_snapshot = build_audit_comparison_snapshot(target_audit)

    compliance_delta = round(
        target_snapshot["compliance_percentage"]
        - base_snapshot["compliance_percentage"],
        2,
    )

    delta = {
        "total_controls": (
            target_snapshot["total_controls"]
            - base_snapshot["total_controls"]
        ),
        "passed_controls": (
            target_snapshot["passed_controls"]
            - base_snapshot["passed_controls"]
        ),
        "failed_controls": (
            target_snapshot["failed_controls"]
            - base_snapshot["failed_controls"]
        ),
        "warning_controls": (
            target_snapshot["warning_controls"]
            - base_snapshot["warning_controls"]
        ),
        "compliance_percentage": compliance_delta,
    }

    if compliance_delta > 0:
        trend_text = "incrementó"
    elif compliance_delta < 0:
        trend_text = "disminuyó"
    else:
        trend_text = "mantuvo"

    summary = (
        f"La auditoría objetivo {trend_text} el cumplimiento en "
        f"{abs(compliance_delta)} puntos porcentuales. "
        f"PASS cambió de {base_snapshot['passed_controls']} a "
        f"{target_snapshot['passed_controls']}, "
        f"FAIL de {base_snapshot['failed_controls']} a "
        f"{target_snapshot['failed_controls']} y "
        f"WARN de {base_snapshot['warning_controls']} a "
        f"{target_snapshot['warning_controls']}."
    )

    if base_snapshot["total_controls"] != target_snapshot["total_controls"]:
        summary += (
            " Nota: las auditorías tienen distinta cantidad total de controles, "
            "por lo que la comparación porcentual debe interpretarse con cautela."
        )

    return {
        "base_audit": base_snapshot,
        "target_audit": target_snapshot,
        "delta": delta,
        "summary": summary,
    }


def get_audit_remediation_plan(
    db: Session,
    audit_id: int,
    source: str | None = None,
    priority: str | None = None,
    limit: int = 20,
) -> dict:
    if limit <= 0:
        raise DashboardServiceError("Limit must be greater than 0")

    audit = (
        db.query(Audit)
        .filter(Audit.id == audit_id)
        .first()
    )

    if not audit:
        raise DashboardServiceError("Audit not found")

    normalized_source = source.lower() if source else None
    normalized_priority = priority.upper() if priority else None

    if normalized_source is not None and normalized_source not in {
        "deepseek",
        "rule_engine",
    }:
        raise DashboardServiceError(
            "Invalid source. Allowed values: deepseek, rule_engine"
        )

    if normalized_priority is not None and normalized_priority not in {
        "HIGH",
        "MEDIUM",
        "LOW",
    }:
        raise DashboardServiceError(
            "Invalid priority. Allowed values: HIGH, MEDIUM, LOW"
        )

    base_filters = [
        Finding.audit_id == audit_id,
        Recommendation.status == "PENDING",
    ]

    if normalized_source is not None:
        base_filters.append(Recommendation.source == normalized_source)

    if normalized_priority is not None:
        base_filters.append(Recommendation.priority == normalized_priority)

    summary = [
        {
            "priority": priority_value or "UNKNOWN",
            "source": source_value or "UNKNOWN",
            "count": count,
        }
        for priority_value, source_value, count in (
            db.query(
                Recommendation.priority,
                Recommendation.source,
                func.count(Recommendation.id),
            )
            .join(Finding, Finding.id == Recommendation.finding_id)
            .filter(*base_filters)
            .group_by(
                Recommendation.priority,
                Recommendation.source,
            )
            .order_by(
                Recommendation.priority,
                Recommendation.source,
            )
            .all()
        )
    ]

    priority_order = case(
        (Recommendation.priority == "HIGH", 1),
        (Recommendation.priority == "MEDIUM", 2),
        (Recommendation.priority == "LOW", 3),
        else_=4,
    )

    rows = (
        db.query(
            Recommendation.id,
            Finding.id,
            CisControl.code,
            CisControl.title,
            Finding.result,
            Recommendation.priority,
            Recommendation.source,
            Recommendation.status,
            Recommendation.title,
            Recommendation.recommendation_text,
        )
        .join(Finding, Finding.id == Recommendation.finding_id)
        .join(CisControl, CisControl.id == Finding.control_id)
        .filter(*base_filters)
        .order_by(
            priority_order.asc(),
            Recommendation.source.asc(),
            CisControl.code.asc(),
            Recommendation.id.asc(),
        )
        .limit(limit)
        .all()
    )

    items = [
        {
            "recommendation_id": recommendation_id,
            "finding_id": finding_id,
            "control_code": control_code,
            "control_title": control_title,
            "result": result,
            "priority": recommendation_priority,
            "source": recommendation_source,
            "status": status,
            "title": title,
            "recommendation_text": recommendation_text,
        }
        for (
            recommendation_id,
            finding_id,
            control_code,
            control_title,
            result,
            recommendation_priority,
            recommendation_source,
            status,
            title,
            recommendation_text,
        ) in rows
    ]

    total_pending = (
        db.query(func.count(Recommendation.id))
        .join(Finding, Finding.id == Recommendation.finding_id)
        .filter(*base_filters)
        .scalar()
        or 0
    )

    return {
        "audit_id": audit_id,
        "total_pending": total_pending,
        "summary": summary,
        "items": items,
    }


RESULT_PRIORITY_RANK = {
    "PASS": 1,
    "WARN": 2,
    "FAIL": 3,
    "NOT_EVALUATED": 0,
}


def normalize_result(result: str | None) -> str:
    if not result:
        return "NOT_EVALUATED"

    normalized = result.upper()

    if normalized not in {"PASS", "WARN", "FAIL"}:
        return "NOT_EVALUATED"

    return normalized


def is_non_compliant(result: str) -> bool:
    return result in {"FAIL", "WARN"}


def is_pass(result: str) -> bool:
    return result == "PASS"


def get_control_results_for_audit(
    db: Session,
    audit_id: int,
) -> dict[str, dict]:
    rows = (
        db.query(
            Finding.id.label("finding_id"),
            Finding.result.label("result"),
            CisControl.id.label("control_id"),
            CisControl.code.label("control_code"),
            CisControl.title.label("control_title"),
        )
        .join(CisControl, CisControl.id == Finding.control_id)
        .filter(Finding.audit_id == audit_id)
        .all()
    )

    controls: dict[str, dict] = {}

    for row in rows:
        result = normalize_result(row.result)
        existing = controls.get(row.control_code)

        candidate = {
            "control_id": row.control_id,
            "control_code": row.control_code,
            "control_title": row.control_title,
            "finding_id": row.finding_id,
            "result": result,
        }

        if not existing:
            controls[row.control_code] = candidate
            continue

        existing_result_rank = RESULT_PRIORITY_RANK.get(existing["result"], 0)
        candidate_result_rank = RESULT_PRIORITY_RANK.get(result, 0)

        if candidate_result_rank > existing_result_rank:
            controls[row.control_code] = candidate

    return controls


def build_control_comparison_item(
    control_code: str,
    base_control: dict | None,
    target_control: dict | None,
    transition: str,
) -> dict:
    source_control = target_control or base_control or {}

    return {
        "control_id": source_control.get("control_id"),
        "control_code": control_code,
        "control_title": source_control.get("control_title", "N/D"),
        "base_finding_id": base_control.get("finding_id") if base_control else None,
        "target_finding_id": target_control.get("finding_id") if target_control else None,
        "base_result": base_control.get("result") if base_control else "NOT_EVALUATED",
        "target_result": target_control.get("result") if target_control else "NOT_EVALUATED",
        "transition": transition,
    }


def get_audit_control_comparison(
    db: Session,
    base_audit_id: int,
    target_audit_id: int,
) -> dict:
    if base_audit_id == target_audit_id:
        raise DashboardServiceError(
            "Base audit and target audit must be different"
        )

    base_audit = (
        db.query(Audit)
        .filter(Audit.id == base_audit_id)
        .first()
    )

    if not base_audit:
        raise DashboardServiceError("Base audit not found")

    target_audit = (
        db.query(Audit)
        .filter(Audit.id == target_audit_id)
        .first()
    )

    if not target_audit:
        raise DashboardServiceError("Target audit not found")

    if base_audit.cluster_id != target_audit.cluster_id:
        raise DashboardServiceError(
            "Audits belong to different clusters and cannot be compared"
        )

    base_controls = get_control_results_for_audit(
        db=db,
        audit_id=base_audit_id,
    )
    target_controls = get_control_results_for_audit(
        db=db,
        audit_id=target_audit_id,
    )

    all_control_codes = sorted(
        set(base_controls.keys()) | set(target_controls.keys())
    )

    resolved_controls = []
    regressions = []
    new_findings = []
    unchanged_non_compliant = []
    unchanged_passed = []
    removed_controls = []
    newly_evaluated_passed = []

    for control_code in all_control_codes:
        base_control = base_controls.get(control_code)
        target_control = target_controls.get(control_code)

        base_result = (
            base_control["result"]
            if base_control
            else "NOT_EVALUATED"
        )
        target_result = (
            target_control["result"]
            if target_control
            else "NOT_EVALUATED"
        )

        transition = f"{base_result}->{target_result}"

        item = build_control_comparison_item(
            control_code=control_code,
            base_control=base_control,
            target_control=target_control,
            transition=transition,
        )

        if is_non_compliant(base_result) and is_pass(target_result):
            resolved_controls.append(item)
        elif is_pass(base_result) and is_non_compliant(target_result):
            regressions.append(item)
        elif base_result == "NOT_EVALUATED" and is_non_compliant(target_result):
            new_findings.append(item)
        elif is_non_compliant(base_result) and is_non_compliant(target_result):
            unchanged_non_compliant.append(item)
        elif is_pass(base_result) and is_pass(target_result):
            unchanged_passed.append(item)
        elif base_result != "NOT_EVALUATED" and target_result == "NOT_EVALUATED":
            removed_controls.append(item)
        elif base_result == "NOT_EVALUATED" and is_pass(target_result):
            newly_evaluated_passed.append(item)

    return {
        "base_audit_id": base_audit_id,
        "target_audit_id": target_audit_id,
        "cluster_id": base_audit.cluster_id,
        "summary": {
            "total_controls_compared": len(all_control_codes),
            "resolved_count": len(resolved_controls),
            "regression_count": len(regressions),
            "new_finding_count": len(new_findings),
            "unchanged_non_compliant_count": len(unchanged_non_compliant),
            "unchanged_passed_count": len(unchanged_passed),
            "removed_control_count": len(removed_controls),
            "newly_evaluated_passed_count": len(newly_evaluated_passed),
        },
        "resolved_controls": resolved_controls,
        "regressions": regressions,
        "new_findings": new_findings,
        "unchanged_non_compliant": unchanged_non_compliant,
        "unchanged_passed": unchanged_passed,
        "removed_controls": removed_controls,
        "newly_evaluated_passed": newly_evaluated_passed,
    }
