from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "benchmarks/ab"))

from statistical_analysis import (
    paired_differences,
    paired_bootstrap_ci,
    standardized_paired_effect,
    sign_test_two_sided,
    mcnemar_counts,
    exact_mcnemar_p_value,
    summarize_ab_results,
)
from ab_closure_gate import evaluate_ab_closure


def make_pairs(n=60, models=("m1", "m2"), advantage=10):
    pairs = []
    for i in range(n):
        pairs.append({
            "pair_id": f"P{i}",
            "task_id": f"T{i % 20}",
            "model_id": models[i % len(models)],
            "complete": True,
            "scoring": {
                "A_total": 60 + (i % 5),
                "B_total": 60 + (i % 5) + advantage,
            },
            "binary_metrics": {
                "A": {
                    "fabrication_failure": i % 10 == 0,
                    "state_protection_failure": i % 12 == 0,
                },
                "B": {
                    "fabrication_failure": False,
                    "state_protection_failure": False,
                },
            },
        })
    return pairs


class TestM875StatisticalAnalysisClosure(unittest.TestCase):
    def test_paired_differences(self):
        pairs = make_pairs(3, advantage=7)
        self.assertEqual(paired_differences(pairs), [7.0, 7.0, 7.0])

    def test_bootstrap_ci_for_constant_difference(self):
        ci = paired_bootstrap_ci([5.0] * 20, iterations=500)
        self.assertEqual(ci["lower"], 5.0)
        self.assertEqual(ci["upper"], 5.0)

    def test_standardized_effect_positive(self):
        value = standardized_paired_effect([1, 2, 3, 4])
        self.assertGreater(value, 0)

    def test_sign_test_detects_positive_direction(self):
        result = sign_test_two_sided([1] * 10)
        self.assertEqual(result["positive"], 10)
        self.assertLess(result["p_value"], 0.01)

    def test_mcnemar_counts(self):
        counts = mcnemar_counts(make_pairs(20), "fabrication_failure")
        self.assertGreater(counts["A_only"], 0)
        self.assertEqual(counts["B_only"], 0)

    def test_mcnemar_zero_discordance(self):
        self.assertEqual(exact_mcnemar_p_value({"A_only": 0, "B_only": 0}), 1.0)

    def test_summary_contains_required_metrics(self):
        summary = summarize_ab_results(make_pairs())
        self.assertEqual(summary["complete_pairs"], 60)
        self.assertEqual(summary["distinct_models"], 2)
        self.assertIn("paired_bootstrap_95_ci", summary["quality"])

    def test_green_closure_passes(self):
        summary = summarize_ab_results(make_pairs())
        gate = evaluate_ab_closure(
            summary,
            external_real_model_evidence=True,
            blind_scoring_complete=True,
        )
        self.assertEqual(gate["status"], "passed")

    def test_fixture_only_closure_is_blocked(self):
        summary = summarize_ab_results(make_pairs())
        gate = evaluate_ab_closure(
            summary,
            external_real_model_evidence=False,
            blind_scoring_complete=True,
        )
        self.assertIn("ORDO-AB-CLOSE-003", {i["code"] for i in gate["issues"]})

    def test_insufficient_pairs_blocked(self):
        summary = summarize_ab_results(make_pairs(20))
        gate = evaluate_ab_closure(
            summary,
            external_real_model_evidence=True,
            blind_scoring_complete=True,
        )
        self.assertIn("ORDO-AB-CLOSE-001", {i["code"] for i in gate["issues"]})

    def test_unblinded_scoring_blocked(self):
        summary = summarize_ab_results(make_pairs())
        gate = evaluate_ab_closure(
            summary,
            external_real_model_evidence=True,
            blind_scoring_complete=False,
        )
        self.assertIn("ORDO-AB-CLOSE-004", {i["code"] for i in gate["issues"]})

    def test_negative_quality_ci_blocks(self):
        summary = summarize_ab_results(make_pairs(60, advantage=-10))
        gate = evaluate_ab_closure(
            summary,
            external_real_model_evidence=True,
            blind_scoring_complete=True,
        )
        self.assertIn("ORDO-AB-CLOSE-005", {i["code"] for i in gate["issues"]})

    def test_small_negative_ci_within_practical_margin_passes(self):
        summary = summarize_ab_results(make_pairs())
        summary["quality"]["paired_bootstrap_95_ci"]["lower"] = -0.08333333333333333
        gate = evaluate_ab_closure(
            summary,
            external_real_model_evidence=True,
            blind_scoring_complete=True,
            quality_noninferiority_margin=-0.10,
        )
        self.assertEqual(gate["status"], "passed")

    def test_same_ci_fails_under_strict_zero_margin(self):
        summary = summarize_ab_results(make_pairs())
        summary["quality"]["paired_bootstrap_95_ci"]["lower"] = -0.08333333333333333
        gate = evaluate_ab_closure(
            summary,
            external_real_model_evidence=True,
            blind_scoring_complete=True,
            quality_noninferiority_margin=0.0,
        )
        self.assertIn("ORDO-AB-CLOSE-005", {i["code"] for i in gate["issues"]})


if __name__ == "__main__":
    unittest.main()
