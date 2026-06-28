from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.schemas.dashboard import AuditDashboardSummary, AuditRemediationPlan


class ReportClusterInfo(BaseModel):
    cluster_id: int
    name: str | None = None
    environment: str | None = None
    api_server_url: str | None = None


class ReportFindingItem(BaseModel):
    finding_id: int
    control_code: str
    control_title: str
    result: str
    detail: str | None = None
    evidence_sanitized: str | None = None
    evidence_hash: str | None = None
    detected_at: datetime | None = None


class AuditJsonReport(BaseModel):
    generated_at: datetime
    audit_id: int
    cluster: ReportClusterInfo
    summary: AuditDashboardSummary
    findings: list[ReportFindingItem]
    remediation_plan: AuditRemediationPlan


class ExecutiveSummaryReport(BaseModel):
    generated_at: datetime
    audit_id: int
    cluster: ReportClusterInfo
    compliance_percentage: float
    total_controls: int
    passed_controls: int
    failed_controls: int
    warning_controls: int
    total_recommendations: int
    pending_recommendations: int
    applied_recommendations: int
    dismissed_recommendations: int
    high_pending_recommendations: int
    summary: str
    notes: list[str]
