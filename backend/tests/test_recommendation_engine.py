from types import SimpleNamespace

from app.services.recommendation_engine import (
    build_recommendation_text,
    infer_priority,
)


def test_infer_priority_should_return_high_for_fail_api_server():
    finding = SimpleNamespace(
        result="FAIL",
        control=SimpleNamespace(
            code="1.2.15",
            title="Ensure that the --profiling argument is set to false",
            category="API Server",
            remediation_reference="Set --profiling=false",
        ),
        evidence_sanitized=None,
    )

    assert infer_priority(finding) == "HIGH"


def test_infer_priority_should_return_low_for_warn_general_control():
    finding = SimpleNamespace(
        result="WARN",
        control=SimpleNamespace(
            code="5.1.7",
            title="Avoid use of system:masters group",
            category="RBAC and Service Accounts",
            remediation_reference="Review group usage",
        ),
        evidence_sanitized=None,
    )

    assert infer_priority(finding) in {"LOW", "MEDIUM"}


def test_build_recommendation_text_should_include_remediation():
    finding = SimpleNamespace(
        result="FAIL",
        evidence_sanitized="actual_value=test",
        control=SimpleNamespace(
            code="1.2.15",
            title="Ensure that profiling is disabled",
            remediation_reference="Set --profiling=false",
        ),
    )

    text = build_recommendation_text(finding)

    assert "Control CIS: 1.2.15" in text
    assert "Set --profiling=false" in text
    assert "Evidencia sanitizada" in text
