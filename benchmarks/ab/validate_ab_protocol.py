from __future__ import annotations

from typing import Any


def validate_protocol(protocol: dict[str, Any], rubric: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []

    design = protocol.get("design") or {}
    arms = design.get("arms") or {}
    if set(arms) != {"A", "B"}:
        issues.append({"path": "design.arms", "message": "exactly A and B arms are required"})

    shared = design.get("shared_controls") or {}
    required_controls = [
        "same_model", "same_input", "same_acceptance_criteria",
        "same_sampling_parameters", "same_retry_policy"
    ]
    for field in required_controls:
        if shared.get(field) is not True:
            issues.append({"path": f"design.shared_controls.{field}", "message": "must be true"})

    if not design.get("blinding", {}).get("scorer_blind_to_arm"):
        issues.append({"path": "design.blinding.scorer_blind_to_arm", "message": "blind scoring is required"})

    if not design.get("counterbalancing", {}).get("enabled"):
        issues.append({"path": "design.counterbalancing.enabled", "message": "counterbalancing is required"})

    dimensions = rubric.get("dimensions") or []
    total_weight = sum(item.get("weight", 0) for item in dimensions)
    if total_weight != 100:
        issues.append({"path": "dimensions", "message": "weights must sum to 100"})

    ids = [item.get("id") for item in dimensions]
    if len(ids) != len(set(ids)):
        issues.append({"path": "dimensions", "message": "dimension ids must be unique"})

    if not rubric.get("critical_failures"):
        issues.append({"path": "critical_failures", "message": "at least one critical failure is required"})

    thresholds = protocol.get("analysis_plan", {}).get("closure_thresholds", {})
    if thresholds.get("minimum_complete_pairs", 0) < 20:
        issues.append({"path": "analysis_plan.closure_thresholds.minimum_complete_pairs", "message": "minimum must be at least 20"})

    return issues
