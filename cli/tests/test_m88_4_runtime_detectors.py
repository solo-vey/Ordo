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

from antipattern_runtime import AntipatternRuntime
class TestM884(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime=AntipatternRuntime.from_language_root(ROOT/"language")
        cls.cases=json.loads((ROOT/"language/runtime/fixtures/initial_antipattern_runtime_cases.v1.json").read_text())["cases"]
    def test_all_cases(self):
        self.assertEqual(len(self.cases),6)
        for c in self.cases:
            f=self.runtime.evaluate_one(antipattern_id=c["antipattern_id"],state=c["state"],context_type=c["context_type"],source_id=c["case_id"])
            self.assertTrue(f[0]["matched"])
    def test_safe_case(self):
        f=self.runtime.evaluate_one(antipattern_id="PROMPT_AS_IMPLEMENTATION",state={"artifacts":{"implementation_prompt":"x","source_code":["a"],"tests":["t"]}},context_type="process_trace",source_id="SAFE")
        self.assertFalse(f[0]["matched"])
    def test_gate_report_contract(self):
        r=self.runtime.evaluate_all(state={},context_type="conversation",source_id="META")
        self.assertEqual(r["report_type"],"GATE.REPORT")
        self.assertIn(r["decision"],{"allow","allow_with_advisory","block"})

if __name__=="__main__": unittest.main()
