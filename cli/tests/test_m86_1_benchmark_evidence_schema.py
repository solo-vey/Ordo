from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "benchmarks"))

from validate_benchmark_evidence import load_schema, validate_evidence


class TestM861BenchmarkEvidenceSchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load_schema(ROOT / "benchmarks/schemas/benchmark_run_evidence.schema.json")
        cls.example = json.loads(
            (ROOT / "benchmarks/examples/benchmark_run_evidence.example.json").read_text(encoding="utf-8")
        )

    def test_canonical_example_passes(self):
        self.assertEqual(validate_evidence(self.example, self.schema), [])

    def test_missing_prompt_hash_fails(self):
        doc = copy.deepcopy(self.example)
        del doc["artifacts"]["prompt_sha256"]
        self.assertTrue(validate_evidence(doc, self.schema))

    def test_invalid_sha256_fails(self):
        doc = copy.deepcopy(self.example)
        doc["artifacts"]["input_sha256"] = "bad"
        self.assertTrue(validate_evidence(doc, self.schema))

    def test_missing_sampling_metadata_fails(self):
        doc = copy.deepcopy(self.example)
        del doc["invocation"]["temperature"]
        self.assertTrue(validate_evidence(doc, self.schema))

    def test_error_run_requires_error_object(self):
        doc = copy.deepcopy(self.example)
        doc["result"]["status"] = "error"
        doc["result"]["score"] = None
        doc["result"]["error"] = None
        self.assertTrue(any(i["path"] == "result.error" for i in validate_evidence(doc, self.schema)))

    def test_completed_run_requires_score(self):
        doc = copy.deepcopy(self.example)
        doc["result"]["status"] = "passed"
        doc["result"]["score"] = None
        self.assertTrue(any(i["path"] == "result.score" for i in validate_evidence(doc, self.schema)))

    def test_additional_top_level_property_fails(self):
        doc = copy.deepcopy(self.example)
        doc["unexpected"] = True
        self.assertTrue(validate_evidence(doc, self.schema))


if __name__ == "__main__":
    unittest.main()
