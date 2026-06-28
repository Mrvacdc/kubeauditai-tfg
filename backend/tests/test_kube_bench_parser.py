from decimal import Decimal

import pytest

from app.services.kube_bench_parser import (
    KubeBenchParseError,
    calculate_compliance_percentage,
    parse_kube_bench_json,
    sanitize_evidence,
)


def test_calculate_compliance_percentage():
    result = calculate_compliance_percentage(passed=1, total=3)

    assert result == Decimal("33.33")


def test_parse_kube_bench_json_should_count_results():
    raw_data = {
        "Controls": [
            {
                "id": "1",
                "text": "Control Plane Components",
                "tests": [
                    {
                        "section": "1.1",
                        "desc": "Control Plane Node Configuration Files",
                        "results": [
                            {
                                "test_number": "1.1.1",
                                "test_desc": "Control PASS",
                                "status": "PASS",
                            },
                            {
                                "test_number": "1.1.2",
                                "test_desc": "Control FAIL",
                                "status": "FAIL",
                            },
                            {
                                "test_number": "1.1.3",
                                "test_desc": "Control WARN",
                                "status": "WARN",
                            },
                        ],
                    }
                ],
            }
        ]
    }

    parsed = parse_kube_bench_json(raw_data)

    assert parsed.total_controls == 3
    assert parsed.passed_controls == 1
    assert parsed.failed_controls == 1
    assert parsed.warning_controls == 1
    assert parsed.compliance_percentage == Decimal("33.33")


def test_parse_kube_bench_json_without_controls_should_fail():
    with pytest.raises(KubeBenchParseError) as exc:
        parse_kube_bench_json({"invalid": []})

    assert "expected 'Controls' list" in str(exc.value)


def test_sanitize_evidence_should_redact_sensitive_values():
    raw = "Authorization: Bearer abc.def.ghi token=supersecret password=ExamplePassword123!"

    sanitized = sanitize_evidence(raw)

    assert "abc.def.ghi" not in sanitized
    assert "supersecret" not in sanitized
    assert "ExamplePassword123!" not in sanitized
    assert "<REDACTED>" in sanitized
