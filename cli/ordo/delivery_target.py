from __future__ import annotations

from typing import Any

ALLOWED_TARGETS = {"engine_runtime", "prompt_only", "both"}
DEFAULT_POLICY = {
    "max_prompt_risk_level": "low",
    "max_prompt_branches": 3,
    "max_prompt_gates": 2,
    "max_prompt_backtrack_points": 1,
    "minimum_prompt_evidence_runs": 3,
    "minimum_prompt_composite_score": 90,
    "minimum_prompt_branch_score": 85,
    "minimum_prompt_backtrack_score": 85,
}
RISK_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}
LOST_PROMPT_GUARANTEES = [
    "mechanical_gate_enforcement",
    "runtime_state_validation",
    "enforced_transition_control",
    "csg_enforced_protection",
    "runtime_evidence_capture_by_default",
]


def recommend_delivery_target(assessment: dict[str, Any], policy: dict[str, Any] | None = None) -> dict[str, Any]:
    policy = {**DEFAULT_POLICY, **(policy or {})}
    reasons: list[str] = []
    risk = str(assessment.get("risk_level", "high")).lower()
    branches = int(assessment.get("branch_count", 0))
    gates = int(assessment.get("gate_count", 0))
    backtracks = int(assessment.get("backtrack_point_count", 0))
    evidence = assessment.get("prompt_evidence") or {}

    if RISK_ORDER.get(risk, 3) > RISK_ORDER[policy["max_prompt_risk_level"]]:
        reasons.append("risk_above_prompt_only_limit")
    if branches > policy["max_prompt_branches"]:
        reasons.append("branch_complexity_requires_engine")
    if gates > policy["max_prompt_gates"]:
        reasons.append("gate_enforcement_requires_engine")
    if backtracks > policy["max_prompt_backtrack_points"]:
        reasons.append("backtrack_complexity_requires_engine")
    if bool(assessment.get("mechanical_enforcement_required", False)):
        reasons.append("mechanical_enforcement_explicitly_required")
    if bool(assessment.get("regulated_or_high_consequence", False)):
        reasons.append("regulated_or_high_consequence_process")

    evidence_ready = (
        int(evidence.get("runs", 0)) >= policy["minimum_prompt_evidence_runs"]
        and float(evidence.get("composite_score", 0)) >= policy["minimum_prompt_composite_score"]
        and float(evidence.get("branch_score", 0)) >= policy["minimum_prompt_branch_score"]
        and float(evidence.get("backtrack_score", 0)) >= policy["minimum_prompt_backtrack_score"]
    )
    if not evidence_ready:
        reasons.append("prompt_only_evidence_not_sufficient")

    if reasons:
        recommended = "engine_runtime"
    elif bool(assessment.get("deliver_both_requested", False)):
        recommended = "both"
    else:
        recommended = "prompt_only"

    return {
        "schema_version": "ordo.arf.delivery_target_recommendation.v1",
        "status": "ready_for_analyst_decision",
        "recommended_target": recommended,
        "safe_default": "engine_runtime",
        "reasons": reasons or ["prompt_only_thresholds_satisfied"],
        "prompt_only_guarantees_lost": LOST_PROMPT_GUARANTEES,
        "analyst_must_confirm": True,
        "allowed_targets": sorted(ALLOWED_TARGETS),
        "assessment": assessment,
        "policy": policy,
    }


def record_delivery_target_decision(recommendation: dict[str, Any], selected_target: str, *, analyst_id: str = "not_recorded", rationale: str = "") -> dict[str, Any]:
    if selected_target not in ALLOWED_TARGETS:
        raise ValueError(f"Unsupported delivery target: {selected_target}")
    recommended = recommendation.get("recommended_target", "engine_runtime")
    override = selected_target != recommended
    if selected_target == "prompt_only" and recommendation.get("reasons") not in ([], ["prompt_only_thresholds_satisfied"]):
        decision_status = "blocked_prompt_only_override"
    else:
        decision_status = "confirmed"
    return {
        "schema_version": "ordo.arf.delivery_target_decision.v1",
        "status": decision_status,
        "selected_target": selected_target,
        "recommended_target": recommended,
        "analyst_override": override,
        "analyst_id": analyst_id,
        "rationale": rationale or ("accepted_recommendation" if not override else "override_reason_not_recorded"),
        "safe_default": "engine_runtime",
        "prompt_only_guarantees_lost_acknowledged": selected_target not in {"prompt_only", "both"} or decision_status == "confirmed",
        "package_outputs": {
            "engine_runtime": selected_target in {"engine_runtime", "both"},
            "prompt_only": selected_target in {"prompt_only", "both"},
        },
    }
