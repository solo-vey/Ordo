from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "benchmarks/ab"))

from contamination_controls import (
    scan_plain_prompt,
    validate_arm_equivalence,
    build_arm_payloads,
    shared_payload_sha256,
)
from validate_shared_dataset import validate_dataset


class TestM872SharedDatasetContamination(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = json.loads(
            (ROOT / "benchmarks/datasets/ordo_vs_plain_prompt_shared_tasks.v1.json").read_text(encoding="utf-8")
        )
        cls.schema = json.loads(
            (ROOT / "benchmarks/schemas/ab_shared_task_dataset.schema.json").read_text(encoding="utf-8")
        )

    def test_dataset_passes(self):
        self.assertEqual(validate_dataset(self.dataset, self.schema), [])

    def test_dataset_has_twenty_tasks(self):
        self.assertEqual(len(self.dataset["tasks"]), 20)

    def test_dataset_has_broad_categories(self):
        self.assertGreaterEqual(len({t["category"] for t in self.dataset["tasks"]}), 15)

    def test_dataset_has_enough_hard_tasks(self):
        self.assertGreaterEqual(sum(t["difficulty"] == "hard" for t in self.dataset["tasks"]), 8)

    def test_plain_prompt_without_ordo_tokens_passes(self):
        self.assertEqual(scan_plain_prompt("Assess the package and provide the next safe step."), [])

    def test_plain_prompt_with_ordo_tokens_fails(self):
        issues = scan_plain_prompt("Use Ordo state.snapshot and gate.report.")
        self.assertGreaterEqual(len(issues), 1)

    def test_arm_payloads_share_identical_frozen_content(self):
        task = self.dataset["tasks"][0]
        payloads = build_arm_payloads(task, "Plain instruction", "Ordo instruction")
        issues = validate_arm_equivalence(task, payloads["A"], payloads["B"])
        self.assertEqual(issues, [])

    def test_arm_a_shared_content_drift_is_detected(self):
        task = self.dataset["tasks"][0]
        payloads = build_arm_payloads(task, "Plain instruction", "Ordo instruction")
        payloads["A"]["required_output"] = ["different"]
        issues = validate_arm_equivalence(task, payloads["A"], payloads["B"])
        self.assertTrue(any(i["code"] == "ORDO-AB-CONTAM-002" for i in issues))

    def test_arm_b_shared_content_drift_is_detected(self):
        task = self.dataset["tasks"][0]
        payloads = build_arm_payloads(task, "Plain instruction", "Ordo instruction")
        payloads["B"]["acceptance_criteria"] = ["different"]
        issues = validate_arm_equivalence(task, payloads["A"], payloads["B"])
        self.assertTrue(any(i["code"] == "ORDO-AB-CONTAM-003" for i in issues))

    def test_shared_payload_hash_is_stable(self):
        task = self.dataset["tasks"][0]
        self.assertEqual(shared_payload_sha256(task), shared_payload_sha256(copy.deepcopy(task)))

    def test_duplicate_task_id_fails(self):
        doc = copy.deepcopy(self.dataset)
        doc["tasks"][1]["task_id"] = doc["tasks"][0]["task_id"]
        self.assertTrue(validate_dataset(doc, self.schema))

    def test_shared_ordo_like_term_can_be_allowlisted(self):
        prompt = "Candidate uses DECISION.LOG."
        self.assertEqual(
            scan_plain_prompt(prompt, allowed_shared_texts=["DECISION.LOG"]),
            [],
        )

    def test_extra_ordo_hint_remains_blocked_with_allowlist(self):
        prompt = "Candidate uses DECISION.LOG. Apply Ordo gates."
        issues = scan_plain_prompt(prompt, allowed_shared_texts=["DECISION.LOG"])
        self.assertGreaterEqual(len(issues), 1)


if __name__ == "__main__":
    unittest.main()
