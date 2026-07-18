from __future__ import annotations
import copy, json, sys, unittest
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"language/migration"))
from migration_completeness_gate import evaluate_migration_completeness

class TestM894(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((ROOT/"language/schemas/migration_traceability_matrix.schema.json").read_text())
        cls.matrix = {
            "schema_version":"ordo.migration_traceability_matrix.v1",
            "matrix_id":"MIG-TRACE-LEGACY-001",
            "source_ref":"legacy.md",
            "rows":[
                {"clause_id":"C-0001","mandatory":True,"mapped_unit_ids":["U-0001"],"mapped_constructs":["AUTHORIZATION.GATE"],"coverage_status":"full","semantic_preservation":{"normativity_preserved":True,"mandatory_strength_preserved":True,"authorization_boundary_preserved":True,"decision_semantics_preserved":True,"evidence_requirement_preserved":True}},
                {"clause_id":"C-0002","mandatory":False,"mapped_unit_ids":["U-0002"],"mapped_constructs":["ACTION.NODE"],"coverage_status":"full","semantic_preservation":{"normativity_preserved":True,"mandatory_strength_preserved":True,"authorization_boundary_preserved":True,"decision_semantics_preserved":True,"evidence_requirement_preserved":True}}
            ]
        }
    def eval(self, m):
        return evaluate_migration_completeness(m, known_clause_ids={"C-0001","C-0002"}, known_unit_ids={"U-0001","U-0002"}, mandatory_clause_ids={"C-0001"})
    def test_schema(self): self.assertEqual(list(Draft202012Validator(self.schema).iter_errors(self.matrix)), [])
    def test_pass(self): self.assertEqual(self.eval(self.matrix)["status"], "passed")
    def test_missing_row_blocks(self):
        m=copy.deepcopy(self.matrix); m["rows"]=m["rows"][:1]
        self.assertEqual(self.eval(m)["status"], "blocked")
    def test_partial_mandatory_blocks(self):
        m=copy.deepcopy(self.matrix); m["rows"][0]["coverage_status"]="partial"
        self.assertEqual(self.eval(m)["status"], "blocked")
    def test_partial_optional_warns(self):
        m=copy.deepcopy(self.matrix); m["rows"][1]["coverage_status"]="partial"
        r=self.eval(m); self.assertEqual(r["status"], "passed"); self.assertEqual(r["summary"]["warning_count"],1)
    def test_authorization_loss_blocks(self):
        m=copy.deepcopy(self.matrix); m["rows"][0]["semantic_preservation"]["authorization_boundary_preserved"]=False
        self.assertIn("authorization_boundary_loss",{x["loss_type"] for x in self.eval(m)["findings"]})
    def test_full_without_construct_blocks(self):
        m=copy.deepcopy(self.matrix); m["rows"][1]["mapped_constructs"]=[]
        self.assertEqual(self.eval(m)["status"], "blocked")
    def test_mandatory_exclusion_blocks(self):
        m=copy.deepcopy(self.matrix); m["rows"][0]["coverage_status"]="excluded_with_reason"; m["rows"][0]["exclusion_reason"]="Documented exclusion reason."
        self.assertEqual(self.eval(m)["status"], "blocked")
    def test_unknown_unit_blocks(self):
        m=copy.deepcopy(self.matrix); m["rows"][1]["mapped_unit_ids"]=["U-9999"]
        self.assertEqual(self.eval(m)["status"], "blocked")

if __name__=="__main__": unittest.main()
