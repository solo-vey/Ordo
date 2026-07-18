from __future__ import annotations
import json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [
    str(ROOT/"language"),
    str(ROOT/"language/runtime"),
    str(ROOT/"language/integration"),
]
from antipattern_finding_model import aggregate_findings, materialize_finding
from detector_contract import CanonicalDetector, DetectionContext

class TestM883(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules=json.loads((ROOT/"language/registries/detect_rule_registry.v1.json").read_text())["items"]
        cls.aps={x["id"]:x for x in json.loads((ROOT/"language/registries/antipattern_registry.v1.json").read_text())["items"]}

    def materialized(self):
        r=self.rules[0]; a=self.aps[r["antipattern_id"]]
        c=DetectionContext(
            signal_schema_version=r["input_contract"]["signal_schema_version"],
            context_type=r["input_contract"]["allowed_contexts"][0],
            source_id="M88-3",
            signals={n:True for n in r["input_contract"]["required_signals"]},
        )
        raw=CanonicalDetector().evaluate(rule=r,antipattern=a,context=c)
        return materialize_finding(raw,context=c,detected_at="2026-07-12T12:00:00+00:00")

    def test_materialized_blocking_decision(self):
        f=self.materialized()
        self.assertEqual(f["decision"],"block")
        self.assertEqual(f["finding_type"],"ANTIPATTERN.FINDING")

    def test_blocking_aggregate(self):
        f=self.materialized()
        r=aggregate_findings([f])
        self.assertEqual(r["decision"],"block")
        self.assertEqual(r["summary"]["blocking_findings"],1)

    def test_advisory_aggregate(self):
        f=self.materialized()
        f["severity"]="warning"; f["enforcement"]="advisory"; f["decision"]="allow_with_advisory"
        r=aggregate_findings([f])
        self.assertEqual(r["decision"],"allow_with_advisory")

    def test_policy(self):
        p=json.loads((ROOT/"language/registries/antipattern_policy.v1.json").read_text())
        self.assertTrue(p["critical_must_block"])

if __name__=="__main__":
    unittest.main()
