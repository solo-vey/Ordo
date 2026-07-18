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

from antipattern_gate_adapter import AntipatternGateAdapter
from bl_ordo_020_closure_gate import evaluate_closure
class TestM885(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a=AntipatternGateAdapter.from_language_root(ROOT/"language")
        cls.aps=json.loads((ROOT/"language/registries/antipattern_registry.v1.json").read_text())
        cls.rules=json.loads((ROOT/"language/registries/detect_rule_registry.v1.json").read_text())
        cls.profile=json.loads((ROOT/"language/integration/antipattern_activation_profile.apf.v1.json").read_text())
    def test_fixtures(self):
        for c in json.loads((ROOT/"language/runtime/fixtures/antipattern_integration_cases.v1.json").read_text())["cases"]:
            r=self.a.evaluate_gate(state=c["state"],context_type=c["context_type"],source_id=c["case_id"])
            self.assertEqual(r["decision"],c["expected_decision"])
    def test_enforcement(self):
        r=self.a.evaluate_gate(state={"conversation":{"scope_confirmed":True},"repository":{"mutation_started":True},"authorization":{"repository_mutation":False},"node":{"execution_started":False}},context_type="conversation",source_id="B")
        with self.assertRaises(RuntimeError): self.a.enforce_gate(r)
    def test_closure(self):
        g=evaluate_closure(antipattern_registry=self.aps,rule_registry=self.rules,activation_profile=self.profile,regression_passed=True,integration_passed=True)
        self.assertEqual(g["status"],"passed")

if __name__=="__main__": unittest.main()
