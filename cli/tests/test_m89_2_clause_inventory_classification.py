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

from clause_inventory_model import validate_inventory
class TestM892(unittest.TestCase):
    def test_clear_passes(self):
        i={"clauses":[{"clause_id":"C-0001","semantic_classes":["gate"],"classification_confidence":.9,"mandatory":True,"ambiguity":{"status":"clear","ambiguity_ids":[]}}]}
        self.assertEqual(validate_inventory(i,[])["status"],"passed")
    def test_low_confidence_blocks(self):
        i={"clauses":[{"clause_id":"C-0001","semantic_classes":["action"],"classification_confidence":.4,"mandatory":False,"ambiguity":{"status":"clear","ambiguity_ids":[]}}]}
        self.assertIn("MIG-CONF-001",{x["code"] for x in validate_inventory(i,[])["issues"]})
    def test_critical_ambiguity_blocks(self):
        i={"clauses":[{"clause_id":"C-0001","semantic_classes":["authorization"],"classification_confidence":.5,"mandatory":True,"ambiguity":{"status":"ambiguous","ambiguity_ids":["AMB-X-001"]}}]}
        a=[{"ambiguity_id":"AMB-X-001","clause_refs":["C-0001"],"impact":"critical","resolution_policy":"capture_and_escalate","status":"open"}]
        self.assertIn("MIG-AMB-BLOCK-001",{x["code"] for x in validate_inventory(i,a)["issues"]})
    def test_protocol(self):
        p=json.loads((ROOT/"language/migration/semantic_classification_protocol.v1.json").read_text())
        self.assertTrue(p["silent_ambiguity_resolution_forbidden"])
        self.assertEqual(p["low_confidence_threshold"], 0.6)

if __name__=="__main__": unittest.main()
