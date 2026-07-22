"""PathWalk calibration eligibility and release-QA profile checks."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED_WEIGHT_KEYS = {
    "cell_match_rate",
    "protocol_compliance_rate",
    "distraction_recovery_rate",
    "backtrack_accuracy",
}


def load_profile(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_profile(data)
    return data


def validate_profile(profile: dict[str, Any]) -> None:
    if profile.get("primary_purpose") != "ordo_release_qa":
        raise ValueError("PathWalk primary_purpose must be ordo_release_qa")
    weights = profile.get("default_weights") or {}
    if set(weights) != REQUIRED_WEIGHT_KEYS:
        raise ValueError("default_weights keys do not match canonical PathWalk components")
    if abs(sum(float(v) for v in weights.values()) - 1.0) > 1e-9:
        raise ValueError("default_weights must sum to 1.0")
    gates = profile.get("hard_gates") or {}
    if gates.get("per_case_protocol_compliance_rate") != 1.0:
        raise ValueError("protocol compliance hard gate must remain 1.0")
    if gates.get("direct_compiled_access_violations") != 0:
        raise ValueError("direct compiled access hard gate must remain zero")


def calibration_eligibility(summary: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    validate_profile(profile)
    req = profile["calibration_eligibility"]
    checks = {
        "model_versions": int(summary.get("model_versions", 0)) >= int(req["min_model_versions"]),
        "runs_per_model": int(summary.get("min_runs_per_model", 0)) >= int(req["min_runs_per_model"]),
        "scored_cases": int(summary.get("scored_cases", 0)) >= int(req["min_scored_cases"]),
        "nonperfect_completed_cases": int(summary.get("nonperfect_completed_cases", 0)) >= int(req["min_nonperfect_completed_cases"]),
        "hard_or_protocol_failures": int(summary.get("hard_or_protocol_failures", 0)) >= int(req["min_hard_or_protocol_failures"]),
        "component_variance": int(summary.get("weighted_components_with_nonzero_variance", 0)) >= int(req["min_weighted_components_with_nonzero_variance"]),
        "manual_adjudication": bool(summary.get("manual_failure_adjudication_complete")),
        "uncertainty_summary": bool(summary.get("uncertainty_summary_complete")),
    }
    return {
        "eligible": all(checks.values()),
        "checks": checks,
        "decision": "calibration_allowed" if all(checks.values()) else "weights_locked",
    }
