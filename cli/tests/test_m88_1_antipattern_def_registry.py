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
class TestM881(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema=json.loads((ROOT/"language/schemas/antipattern_def.schema.json").read_text())
        cls.items=json.loads((ROOT/"language/registries/antipattern_registry.v1.json").read_text())["items"]
    def test_registry(self):
        self.assertEqual(len(self.items),7); self.assertEqual(len({x["id"] for x in self.items}),7)
    def test_schema(self):
        v=Draft202012Validator(self.schema)
        for x in self.items: self.assertEqual(list(v.iter_errors(x)),[])
    def test_critical_blocks(self):
        for x in self.items:
            if x["severity"]=="critical": self.assertEqual(x["enforcement"],"blocking")
    def test_support_fields(self):
        for x in self.items:
            self.assertTrue(x["recovery"]["resume_from"]); self.assertTrue(x["remediation"]["actions"]); self.assertTrue(x["evidence"]["reference_ids"])

if __name__=="__main__": unittest.main()
