from __future__ import annotations

from typing import Any
import math
import random
import statistics


def paired_differences(pairs: list[dict[str, Any]]) -> list[float]:
    return [
        float(item["scoring"]["B_total"]) - float(item["scoring"]["A_total"])
        for item in pairs
        if item.get("complete", True)
    ]


def paired_bootstrap_ci(
    values: list[float],
    *,
    confidence: float = 0.95,
    iterations: int = 5000,
    seed: int = 42,
) -> dict[str, float | None]:
    if not values:
        return {"lower": None, "upper": None, "mean": None}

    rng = random.Random(seed)
    means = []
    n = len(values)
    for _ in range(iterations):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        means.append(statistics.fmean(sample))
    means.sort()

    alpha = 1 - confidence
    lower_idx = max(0, int((alpha / 2) * iterations))
    upper_idx = min(iterations - 1, int((1 - alpha / 2) * iterations) - 1)
    return {
        "lower": means[lower_idx],
        "upper": means[upper_idx],
        "mean": statistics.fmean(values),
    }


def standardized_paired_effect(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    sd = statistics.stdev(values)
    if sd == 0:
        if statistics.fmean(values) == 0:
            return 0.0
        return math.inf if statistics.fmean(values) > 0 else -math.inf
    return statistics.fmean(values) / sd


def sign_test_two_sided(values: list[float]) -> dict[str, float | int | None]:
    nonzero = [v for v in values if v != 0]
    n = len(nonzero)
    if n == 0:
        return {"n": 0, "positive": 0, "negative": 0, "p_value": 1.0}
    positive = sum(v > 0 for v in nonzero)
    negative = n - positive
    k = min(positive, negative)

    # Exact two-sided binomial sign test under p=0.5.
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    p_value = min(1.0, 2 * tail)
    return {
        "n": n,
        "positive": positive,
        "negative": negative,
        "p_value": p_value,
    }


def mcnemar_counts(
    pairs: list[dict[str, Any]],
    metric: str,
) -> dict[str, int]:
    # metric must be boolean, where True means failure occurred.
    a_only = 0
    b_only = 0
    both = 0
    neither = 0
    for pair in pairs:
        a = bool(pair["binary_metrics"]["A"].get(metric, False))
        b = bool(pair["binary_metrics"]["B"].get(metric, False))
        if a and not b:
            a_only += 1
        elif b and not a:
            b_only += 1
        elif a and b:
            both += 1
        else:
            neither += 1
    return {
        "A_only": a_only,
        "B_only": b_only,
        "both": both,
        "neither": neither,
    }


def exact_mcnemar_p_value(counts: dict[str, int]) -> float:
    b = counts["A_only"]
    c = counts["B_only"]
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def summarize_ab_results(pairs: list[dict[str, Any]]) -> dict[str, Any]:
    complete = [p for p in pairs if p.get("complete", True)]
    diffs = paired_differences(complete)
    models = {p["model_id"] for p in complete}
    tasks = {p["task_id"] for p in complete}

    fabrication_counts = mcnemar_counts(complete, "fabrication_failure")
    state_counts = mcnemar_counts(complete, "state_protection_failure")

    return {
        "schema_version": "ordo.ab_statistical_summary.v1",
        "complete_pairs": len(complete),
        "distinct_models": len(models),
        "distinct_tasks": len(tasks),
        "quality": {
            "A_mean": statistics.fmean([p["scoring"]["A_total"] for p in complete]) if complete else None,
            "B_mean": statistics.fmean([p["scoring"]["B_total"] for p in complete]) if complete else None,
            "mean_paired_difference_B_minus_A": statistics.fmean(diffs) if diffs else None,
            "paired_bootstrap_95_ci": paired_bootstrap_ci(diffs),
            "standardized_paired_effect": standardized_paired_effect(diffs),
            "sign_test": sign_test_two_sided(diffs),
        },
        "fabrication_failure": {
            "counts": fabrication_counts,
            "mcnemar_p_value": exact_mcnemar_p_value(fabrication_counts),
        },
        "state_protection_failure": {
            "counts": state_counts,
            "mcnemar_p_value": exact_mcnemar_p_value(state_counts),
        },
    }
