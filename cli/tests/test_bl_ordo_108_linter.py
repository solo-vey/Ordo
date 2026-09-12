from __future__ import annotations

from ordo.linter import lint_source


def test_runtime_fields_are_rejected_from_business_state_schema() -> None:
    report = lint_source({
        "ordo": {"version": "0.12", "package": "demo", "control_level": "standard", "execution_mode": "full_runtime"},
        "state": {"schema": {"current_node": {"type": "string"}, "domain_value": {"type": "string"}}},
    })
    assert any(issue["code"] == "RUNTIME_CONTEXT_FIELD_IN_BUSINESS_STATE" for issue in report["issues"])
