from __future__ import annotations

from dataclasses import dataclass
from typing import Any


REQUIRED_AXES = (
    "active_question_clarity",
    "state_continuity",
    "backtrack_transparency",
    "scope_change_transparency",
    "handoff_readiness",
)


@dataclass(frozen=True)
class ReplayResult:
    status: str
    errors: tuple[str, ...]
    metrics: dict[str, float]


def evaluate_replay(case: dict[str, Any]) -> ReplayResult:
    errors: list[str] = []
    transcript = case.get("transcript") or []
    if not transcript:
        errors.append("TRANSCRIPT_MISSING")

    before = case.get("pre_state") or {}
    after = case.get("post_state") or {}
    expected = case.get("expected") or {}

    if after.get("active_node") != expected.get("active_node"):
        errors.append("ACTIVE_NODE_MISMATCH")
    if after.get("active_question") != expected.get("active_question"):
        errors.append("ACTIVE_QUESTION_MISMATCH")

    protected = set(expected.get("protected_fields", []))
    allowed = set(expected.get("allowed_mutations", []))
    all_keys = set(before) | set(after)
    changed = {k for k in all_keys if before.get(k) != after.get(k)}
    illegal = changed - allowed - {"active_node", "active_question", "status", "trace"}
    if illegal:
        errors.append("UNDECLARED_STATE_MUTATION:" + ",".join(sorted(illegal)))
    if any(k in changed for k in protected):
        errors.append("PROTECTED_STATE_CHANGED")

    experience = case.get("analyst_experience") or {}
    for axis in REQUIRED_AXES:
        value = experience.get(axis)
        if not isinstance(value, (int, float)) or not 0 <= value <= 1:
            errors.append(f"INVALID_EXPERIENCE_AXIS:{axis}")
    metrics = {axis: float(experience.get(axis, 0)) for axis in REQUIRED_AXES}
    metrics["mean"] = round(sum(metrics.values()) / len(REQUIRED_AXES), 4)

    if expected.get("requires_handoff") and not after.get("handoff_ready"):
        errors.append("HANDOFF_NOT_READY")
    if expected.get("must_preserve_prior_answers"):
        for key in expected.get("preserved_fields", []):
            if before.get(key) != after.get(key):
                errors.append(f"PRIOR_ANSWER_LOST:{key}")

    threshold = float(case.get("experience_threshold", 0.8))
    if metrics["mean"] < threshold:
        errors.append("ANALYST_EXPERIENCE_BELOW_THRESHOLD")

    return ReplayResult("passed" if not errors else "failed", tuple(errors), metrics)
