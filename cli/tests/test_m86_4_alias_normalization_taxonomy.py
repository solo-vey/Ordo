from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "benchmarks"))

from csg_normalization import AliasRegistry, MismatchTaxonomy, compare_opcode


class TestM864AliasNormalizationTaxonomy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = AliasRegistry.from_file(ROOT / "benchmarks/taxonomy/csg_aliases.v1.json")
        cls.taxonomy = MismatchTaxonomy.from_file(ROOT / "benchmarks/taxonomy/mismatch_taxonomy.v1.json")

    def test_canonical_opcode_stays_canonical(self):
        value, alias = self.registry.normalize("DECISION.LOG")
        self.assertEqual(value, "DECISION.LOG")
        self.assertFalse(alias)

    def test_underscore_alias_normalizes(self):
        value, alias = self.registry.normalize("DECISION_RECORD")
        self.assertEqual(value, "DECISION.LOG")
        self.assertTrue(alias)

    def test_case_and_separator_normalization(self):
        value, alias = self.registry.normalize(" state-snapshot ")
        self.assertEqual(value, "STATE.SNAPSHOT")
        self.assertTrue(alias)

    def test_unknown_opcode_is_not_rewritten(self):
        value, alias = self.registry.normalize("MEMORY.COMMIT")
        self.assertEqual(value, "MEMORY.COMMIT")
        self.assertFalse(alias)

    def test_alias_equivalence_classified_as_alias_gap(self):
        result = compare_opcode("DECISION.LOG", "DECISION_RECORD", self.registry)
        self.assertTrue(result["semantic_match"])
        self.assertEqual(result["mismatch_class"], "alias_gap")

    def test_real_opcode_mismatch_is_not_hidden_by_aliases(self):
        result = compare_opcode("TRACE.LOG", "MEMORY.COMMIT", self.registry)
        self.assertFalse(result["semantic_match"])
        self.assertEqual(result["mismatch_class"], "fabricated_opcode")

    def test_known_taxonomy_class(self):
        item = self.taxonomy.classify("gate_semantics_reversal")
        self.assertEqual(item["severity"], "critical")

    def test_unknown_taxonomy_class_uses_fallback(self):
        item = self.taxonomy.classify("new_future_class")
        self.assertEqual(item["id"], "unknown_mismatch")

    def test_registry_has_no_collisions(self):
        payload = {
            "aliases": [
                {"canonical": "A.B", "variants": ["same"]},
                {"canonical": "C.D", "variants": ["same"]},
            ]
        }
        with self.assertRaises(ValueError):
            AliasRegistry(payload)


if __name__ == "__main__":
    unittest.main()
