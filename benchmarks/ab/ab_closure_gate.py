from __future__ import annotations

from typing import Any


def evaluate_ab_closure(
    summary: dict[str, Any],
    *,
    external_real_model_evidence: bool,
    blind_scoring_complete: bool,
    minimum_pairs: int = 60,
    minimum_models: int = 2,
    quality_noninferiority_margin: float = -0.10,
) -> dict[str, Any]:
    issues = []

    if summary.get("complete_pairs", 0) < minimum_pairs:
        issues.append({
            "code": "ORDO-AB-CLOSE-001",
            "message": f"requires at least {minimum_pairs} complete pairs",
        })

    if summary.get("distinct_models", 0) < minimum_models:
        issues.append({
            "code": "ORDO-AB-CLOSE-002",
            "message": f"requires at least {minimum_models} distinct models",
        })

    if not external_real_model_evidence:
        issues.append({
            "code": "ORDO-AB-CLOSE-003",
            "message": "real external model evidence is required",
        })

    if not blind_scoring_complete:
        issues.append({
            "code": "ORDO-AB-CLOSE-004",
            "message": "blind scoring must be complete",
        })

    quality = summary.get("quality") or {}
    ci = quality.get("paired_bootstrap_95_ci") or {}
    if ci.get("lower") is not None and ci["lower"] < quality_noninferiority_margin:
        issues.append({
            "code": "ORDO-AB-CLOSE-005",
            "message": (
                "quality non-inferiority is not demonstrated: "
                f"lower CI {ci['lower']:.6f} is below margin "
                f"{quality_noninferiority_margin:.6f}"
            ),
        })

    state_counts = (summary.get("state_protection_failure") or {}).get("counts") or {}
    if state_counts.get("B_only", 0) > state_counts.get("A_only", 0):
        issues.append({
            "code": "ORDO-AB-CLOSE-006",
            "message": "Ordo arm has more state-protection-only failures",
        })

    fabrication_counts = (summary.get("fabrication_failure") or {}).get("counts") or {}
    if fabrication_counts.get("B_only", 0) > fabrication_counts.get("A_only", 0):
        issues.append({
            "code": "ORDO-AB-CLOSE-007",
            "message": "Ordo arm has more fabrication-only failures",
        })

    return {
        "schema_version": "ordo.ab_closure_gate.v1",
        "status": "passed" if not issues else "blocked",
        "issues": issues,
        "requirements": {
            "minimum_pairs": minimum_pairs,
            "minimum_models": minimum_models,
            "external_real_model_evidence": True,
            "blind_scoring_complete": True,
            "quality_noninferiority_margin": quality_noninferiority_margin,
        },
    }
