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

from migration_intake_contract import validate_decomposition
class TestM891(unittest.TestCase):
    def test_intake_requires_preservation_contract(self):
        s=json.loads((ROOT/"language/schemas/process_instruction_migration_intake.schema.json").read_text())
        self.assertIn("preservation_contract", s["required"])
        self.assertIn("validation_policy", s["required"])
    def test_mapping_pass(self):
        self.assertEqual(validate_decomposition([{"clause_id":"C1","mandatory":True}],[{"unit_type":"gate","source_clause_refs":["C1"]}])["status"],"passed")
    def test_unmapped_blocks(self):
        self.assertEqual(validate_decomposition([{"clause_id":"C1","mandatory":True}],[])["status"],"blocked")
    def test_protocol_steps(self):
        p=json.loads((ROOT/"language/migration/decomposition_protocol.v1.json").read_text())
        self.assertEqual(len(p["steps"]),8)

if __name__=="__main__": unittest.main()
