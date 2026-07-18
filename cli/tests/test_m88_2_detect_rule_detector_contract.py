from __future__ import annotations
import copy, json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [
    str(ROOT/"language"),
    str(ROOT/"language/runtime"),
    str(ROOT/"language/integration"),
    str(ROOT/"language/migration"),
]

from jsonschema import Draft202012Validator
from detector_contract import CanonicalDetector, DetectionContext
class TestM882(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema=json.loads((ROOT/"language/schemas/detect_rule.schema.json").read_text())
        cls.rules=json.loads((ROOT/"language/registries/detect_rule_registry.v1.json").read_text())["items"]
        cls.aps={x["id"]:x for x in json.loads((ROOT/"language/registries/antipattern_registry.v1.json").read_text())["items"]}
    def test_registry(self):
        self.assertGreaterEqual(len(self.rules), 1); self.assertEqual(len({x["id"] for x in self.rules}), len(self.rules))
    def test_schema_and_coverage(self):
        v=Draft202012Validator(self.schema)
        for x in self.rules: self.assertEqual(list(v.iter_errors(x)),[])
        self.assertEqual({x["antipattern_id"] for x in self.rules},set(self.aps))
    def test_detector(self):
        r=self.rules[0]; a=self.aps[r["antipattern_id"]]
        c=DetectionContext(signal_schema_version=r["input_contract"]["signal_schema_version"],context_type=r["input_contract"]["allowed_contexts"][0],source_id="T",signals={n:True for n in r["input_contract"]["required_signals"]})
        f=CanonicalDetector().evaluate(rule=r,antipattern=a,context=c)
        self.assertTrue(f.matched); self.assertEqual(f.finding_type,"ANTIPATTERN.FINDING")
    def test_deterministic(self): self.assertTrue(all(x["evaluation"]["deterministic"] for x in self.rules))

if __name__=="__main__": unittest.main()
