from pydantic import BaseModel
from datetime import datetime


class CountItem(BaseModel):
    name: str
    count: int


class RecommendationSourceStatusItem(BaseModel):
    source: str
    status: str
    count: int


class RecommendationPriorityStatusItem(BaseModel):
    priority: str
    status: str
    count: int


class TopControlItem(BaseModel):
    control_code: str
    title: str
    result: str
    count: int


class AuditDashboardSummary(BaseModel):
    audit_id: int
    cluster_id: int
    status: str

    total_controls: int
    passed_controls: int
    failed_controls: int
    warning_controls: int
    compliance_percentage: float

    findings_by_result: list[CountItem]
    recommendations_by_status: list[CountItem]
    recommendations_by_source_status: list[RecommendationSourceStatusItem]
    recommendations_by_priority_status: list[RecommendationPriorityStatusItem]
    top_failed_controls: list[TopControlItem]


class AuditHistoryItem(BaseModel):
    audit_id: int
    status: str
    total_controls: int
    passed_controls: int
    failed_controls: int
    warning_controls: int
    compliance_percentage: float
    created_at: datetime | None = None


class ClusterAuditHistory(BaseModel):
    cluster_id: int
    total_audits: int
    audits: list[AuditHistoryItem]


class AuditComparisonSnapshot(BaseModel):
    audit_id: int
    cluster_id: int
    status: str
    total_controls: int
    passed_controls: int
    failed_controls: int
    warning_controls: int
    compliance_percentage: float
    created_at: datetime | None = None


class AuditComparisonDelta(BaseModel):
    total_controls: int
    passed_controls: int
    failed_controls: int
    warning_controls: int
    compliance_percentage: float


class AuditComparison(BaseModel):
    base_audit: AuditComparisonSnapshot
    target_audit: AuditComparisonSnapshot
    delta: AuditComparisonDelta
    summary: str


class RemediationPlanSummaryItem(BaseModel):
    priority: str
    source: str
    count: int


class RemediationPlanItem(BaseModel):
    recommendation_id: int
    finding_id: int
    control_code: str
    control_title: str
    result: str
    priority: str
    source: str
    status: str
    title: str
    recommendation_text: str


class AuditRemediationPlan(BaseModel):
    audit_id: int
    total_pending: int
    summary: list[RemediationPlanSummaryItem]
    items: list[RemediationPlanItem]


class ControlComparisonItem(BaseModel):
    control_id: int | None = None
    control_code: str
    control_title: str
    base_finding_id: int | None = None
    target_finding_id: int | None = None
    base_result: str
    target_result: str
    transition: str


class ControlComparisonSummary(BaseModel):
    total_controls_compared: int
    resolved_count: int
    regression_count: int
    new_finding_count: int
    unchanged_non_compliant_count: int
    unchanged_passed_count: int
    removed_control_count: int
    newly_evaluated_passed_count: int


class AuditControlComparison(BaseModel):
    base_audit_id: int
    target_audit_id: int
    cluster_id: int
    summary: ControlComparisonSummary
    resolved_controls: list[ControlComparisonItem]
    regressions: list[ControlComparisonItem]
    new_findings: list[ControlComparisonItem]
    unchanged_non_compliant: list[ControlComparisonItem]
    unchanged_passed: list[ControlComparisonItem]
    removed_controls: list[ControlComparisonItem]
    newly_evaluated_passed: list[ControlComparisonItem]
