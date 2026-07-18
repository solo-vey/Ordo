from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "benchmarks"))

from validate_csg_dataset import validate_dataset


class TestM863AdversarialCSGDataset(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = json.loads(
            (ROOT / "benchmarks/datasets/csg_adversarial_v2.json").read_text(encoding="utf-8")
        )
        cls.schema = json.loads(
            (ROOT / "benchmarks/schemas/csg_adversarial_dataset.schema.json").read_text(encoding="utf-8")
        )

    def test_dataset_passes(self):
        self.assertEqual(validate_dataset(self.dataset, self.schema), [])

    def test_has_twenty_cases(self):
        self.assertEqual(len(self.dataset["cases"]), 20)

    def test_has_broad_taxonomy(self):
        categories = {case["category"] for case in self.dataset["cases"]}
        self.assertGreaterEqual(len(categories), 18)

    def test_unique_ids(self):
        ids = [case["case_id"] for case in self.dataset["cases"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_duplicate_id_fails(self):
        doc = copy.deepcopy(self.dataset)
        doc["cases"][1]["case_id"] = doc["cases"][0]["case_id"]
        self.assertTrue(validate_dataset(doc, self.schema))

    def test_wrong_case_count_fails(self):
        doc = copy.deepcopy(self.dataset)
        doc["case_count"] = 999
        self.assertTrue(validate_dataset(doc, self.schema))

    def test_positive_and_negative_controls_present(self):
        positive = [c for c in self.dataset["cases"] if c["expected"]["semantic_match"]]
        negative = [c for c in self.dataset["cases"] if not c["expected"]["semantic_match"]]
        self.assertGreaterEqual(len(positive), 2)
        self.assertGreaterEqual(len(negative), 10)


if __name__ == "__main__":
    unittest.main()
