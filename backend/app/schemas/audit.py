from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class AuditRead(BaseModel):
    id: int
    cluster_id: int
    executed_by_user_id: Optional[int]
    status: str
    execution_mode: str
    benchmark_version: Optional[str]
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    total_controls: int
    passed_controls: int
    failed_controls: int
    warning_controls: int
    compliance_percentage: Decimal
    raw_result_location: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class FindingRead(BaseModel):
    id: int
    audit_id: int
    control_id: int
    result: str
    detail: Optional[str]
    evidence_sanitized: Optional[str]
    evidence_hash: Optional[str]
    detected_at: datetime

    model_config = {
        "from_attributes": True
    }


class CisControlRead(BaseModel):
    id: int
    code: str
    title: str
    description: Optional[str]
    category: Optional[str]
    severity: Optional[str]
    remediation_reference: Optional[str]

    model_config = {
        "from_attributes": True
    }


class FindingDetailRead(BaseModel):
    id: int
    result: str
    detail: Optional[str]
    evidence_sanitized: Optional[str]
    evidence_hash: Optional[str]
    detected_at: datetime
    control: CisControlRead

    model_config = {
        "from_attributes": True
    }


class AuditDetailRead(AuditRead):
    findings: list[FindingDetailRead] = []

    model_config = {
        "from_attributes": True
    }


class AuditUploadResponse(BaseModel):
    audit_id: int
    cluster_id: int
    status: str
    total_controls: int
    passed_controls: int
    failed_controls: int
    warning_controls: int
    compliance_percentage: Decimal
