from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / "integration"
if str(INTEGRATION) not in sys.path:
    sys.path.insert(0, str(INTEGRATION))

from antipattern_runtime_binding import build_adapter, load_antipattern_binding


class FundamentalTaxonomyBindingTests(unittest.TestCase):
    def test_all_runtime_rules_map_to_active_fundamentals(self):
        binding, _ = load_antipattern_binding(ROOT)
        mapping = binding["resolved_taxonomy_map"]
        self.assertEqual(len(mapping), 6)
        self.assertEqual(len(set(mapping.values())), 6)

    def test_owner_approval_gate_is_enabled(self):
        binding, _ = load_antipattern_binding(ROOT)
        self.assertTrue(binding["taxonomy_binding"]["new_fundamental_requires_owner_approval"])

    def test_gate_report_exposes_fundamental_mapping(self):
        adapter = build_adapter(ROOT)
        report = adapter.evaluate_gate(
            state={"artifacts": {"implementation_prompt": "implement this", "source_code": None, "repository_patch": None, "tests": None, "implementation_artifacts": None}, "claims": {"implementation_complete": True}},
            context_type="process_trace",
            source_id="taxonomy-binding-test",
            detected_at="2026-07-13T00:00:00+00:00",
            enabled_antipattern_overrides=["PROMPT_AS_IMPLEMENTATION"],
        )
        self.assertEqual(
            report["detector_to_fundamental_mapping"],
            {"PROMPT_AS_IMPLEMENTATION": "EVIDENCE_REALITY_MISMATCH"},
        )
        self.assertEqual(report["enabled_fundamental_antipatterns"], ["EVIDENCE_REALITY_MISMATCH"])


if __name__ == "__main__":
    unittest.main()
