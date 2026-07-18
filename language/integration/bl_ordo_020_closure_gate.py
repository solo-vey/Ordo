from __future__ import annotations

from typing import Any


REQUIRED_ANTIPATTERNS = {
    "PROMPT_AS_IMPLEMENTATION",
    "PACKAGE_VALIDATION_WITHOUT_COMPLETENESS_VALIDATION",
    "MANDATORY_BRANCH_SHORT_CIRCUIT",
    "FINAL_LABEL_OVERCLAIM",
    "SCOPE_CONFIRMATION_AS_IMPLEMENTATION_AUTHORIZATION",
    "COMPLEXITY_ROUTING_AND_EXECUTION_IN_ONE_NODE",
}


def evaluate_closure(
    *,
    antipattern_registry: dict[str, Any],
    rule_registry: dict[str, Any],
    activation_profile: dict[str, Any],
    regression_passed: bool,
    integration_passed: bool,
) -> dict[str, Any]:
    issues = []

    active_antipatterns = {
        item["id"] for item in antipattern_registry.get("items", [])
        if item.get("status") == "active"
    }
    if not REQUIRED_ANTIPATTERNS <= active_antipatterns:
        issues.append({
            "code": "ORDO-AP-CLOSE-001",
            "message": "required initial anti-pattern registry coverage is incomplete",
        })

    covered = {
        item["antipattern_id"] for item in rule_registry.get("items", [])
        if item.get("status") == "active"
    }
    if not REQUIRED_ANTIPATTERNS <= covered:
        issues.append({
            "code": "ORDO-AP-CLOSE-002",
            "message": "required anti-pattern detection-rule coverage is incomplete",
        })

    activated = set()
    for context in activation_profile.get("contexts", {}).values():
        activated.update(context.get("enabled_antipatterns", []))
    if not REQUIRED_ANTIPATTERNS <= activated:
        issues.append({
            "code": "ORDO-AP-CLOSE-003",
            "message": "required anti-pattern activation coverage is incomplete",
        })

    if activation_profile.get("policy", {}).get("blocking_finding_blocks_gate") is not True:
        issues.append({
            "code": "ORDO-AP-CLOSE-004",
            "message": "blocking finding enforcement is not active",
        })

    if not regression_passed:
        issues.append({
            "code": "ORDO-AP-CLOSE-005",
            "message": "regression suite failed",
        })

    if not integration_passed:
        issues.append({
            "code": "ORDO-AP-CLOSE-006",
            "message": "end-to-end integration failed",
        })

    return {
        "schema_version": "ordo.bl_ordo_020_closure_gate.v1",
        "status": "passed" if not issues else "blocked",
        "issues": issues,
        "requirements": {
            "initial_antipattern_count": 6,
            "full_rule_coverage": True,
            "full_activation_coverage": True,
            "blocking_enforcement": True,
            "regression_passed": True,
            "integration_passed": True,
        },
    }
