import json,re,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[2]
class TestRepair(unittest.TestCase):
 def test_required_files(self):
  req=['language/schemas/antipattern_def.schema.json','language/schemas/detect_rule.schema.json','language/runtime/antipattern_runtime.py','language/integration/antipattern_gate_adapter.py','language/schemas/process_instruction_migration_intake.schema.json','language/migration/migration_intake_contract.py','language/schemas/migration_clause_inventory.schema.json','language/migration/clause_inventory_model.py','language/schemas/migration_dependency_graph.schema.json','language/migration/dependency_reconstruction_model.py','language/migration/migration_completeness_gate.py','language/migration/end_to_end_migration.py']
  self.assertEqual([x for x in req if not (R/x).exists()],[])
 def test_backlog_unique(self):
  ids=re.findall(r'^### (BL-ORDO-\d+) —', (R/'backlog/CONSOLIDATED_BACKLOG.md').read_text(), re.M); self.assertEqual(len(ids),len(set(ids)))
 def test_pre_release_json(self):
  base=R/'reports/pre-release/legacy-root'
  json.loads((base/'PRE_RELEASE_HISTORY_EVENT_CLEAN_CHECK.json').read_text()); json.loads((base/'PRE_RELEASE_REPO_CHECK.json').read_text())
if __name__=='__main__': unittest.main()
