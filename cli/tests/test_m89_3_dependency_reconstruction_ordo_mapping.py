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

from dependency_reconstruction_model import validate_dependency_graph
class TestM893(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g={"nodes":[{"node_id":"U-0001","unit_type":"authorization","source_clause_refs":["C-0001"],"mandatory":True},{"node_id":"U-0002","unit_type":"action","source_clause_refs":["C-0002"],"mandatory":True}],"edges":[{"edge_id":"E-0001","from":"U-0001","to":"U-0002","relation":"authorizes","source_clause_refs":["C-0001","C-0002"]}]}
        cls.m={"entries":[{"unit_id":"U-0001","mapping_mode":"direct"},{"unit_id":"U-0002","mapping_mode":"direct"}]}
    def test_pass(self): self.assertEqual(validate_dependency_graph(self.g,self.m,{"C-0001","C-0002"})["status"],"passed")
    def test_cycle_blocks(self):
        g=copy.deepcopy(self.g); g["edges"].append({"edge_id":"E-0002","from":"U-0002","to":"U-0001","relation":"requires","source_clause_refs":["C-0002"]})
        self.assertIn("MIG-GRAPH-CYCLE-001",{x["code"] for x in validate_dependency_graph(g,self.m,{"C-0001","C-0002"})["issues"]})
    def test_unresolved_blocks(self):
        m=copy.deepcopy(self.m); m["entries"][1]["mapping_mode"]="unresolved"
        self.assertIn("MIG-MAP-MANDATORY-001",{x["code"] for x in validate_dependency_graph(self.g,m,{"C-0001","C-0002"})["issues"]})
    def test_recovery_cycle_allowed(self):
        g=copy.deepcopy(self.g); g["edges"].append({"edge_id":"E-0002","from":"U-0002","to":"U-0001","relation":"recovers_to","source_clause_refs":["C-0002"]})
        self.assertNotIn("MIG-GRAPH-CYCLE-001",{x["code"] for x in validate_dependency_graph(g,self.m,{"C-0001","C-0002"})["issues"]})

if __name__=="__main__": unittest.main()
