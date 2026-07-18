from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "benchmarks/ab"))

from validate_ab_protocol import validate_protocol


class TestM871ABProtocolRubric(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = json.loads((ROOT / "benchmarks/ab/ordo_vs_plain_prompt_protocol.v1.json").read_text())
        cls.rubric = json.loads((ROOT / "benchmarks/ab/ordo_vs_plain_prompt_scoring_rubric.v1.json").read_text())

    def test_protocol_and_rubric_pass(self):
        self.assertEqual(validate_protocol(self.protocol, self.rubric), [])

    def test_weights_sum_to_100(self):
        self.assertEqual(sum(d["weight"] for d in self.rubric["dimensions"]), 100)

    def test_plain_prompt_arm_forbids_ordo_leakage(self):
        forbidden = self.protocol["design"]["arms"]["A"]["forbidden_content"]
        self.assertTrue(any("Ordo" in item for item in forbidden))

    def test_shared_controls_are_frozen(self):
        shared = self.protocol["design"]["shared_controls"]
        self.assertTrue(all(shared[k] for k in ["same_model", "same_input", "same_acceptance_criteria", "same_sampling_parameters", "same_retry_policy"]))

    def test_blinding_is_required(self):
        self.assertTrue(self.protocol["design"]["blinding"]["scorer_blind_to_arm"])

    def test_counterbalancing_is_required(self):
        self.assertTrue(self.protocol["design"]["counterbalancing"]["enabled"])

    def test_invalid_weight_sum_fails(self):
        rubric = copy.deepcopy(self.rubric)
        rubric["dimensions"][0]["weight"] += 1
        self.assertTrue(validate_protocol(self.protocol, rubric))

    def test_unblinded_protocol_fails(self):
        protocol = copy.deepcopy(self.protocol)
        protocol["design"]["blinding"]["scorer_blind_to_arm"] = False
        self.assertTrue(validate_protocol(protocol, self.rubric))

    def test_low_pair_threshold_fails(self):
        protocol = copy.deepcopy(self.protocol)
        protocol["analysis_plan"]["closure_thresholds"]["minimum_complete_pairs"] = 5
        self.assertTrue(validate_protocol(protocol, self.rubric))


if __name__ == "__main__":
    unittest.main()
