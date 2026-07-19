from __future__ import annotations
import importlib.util, json, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; SCRIPT=ROOT/'tools/check_english_only_policy.py'; POLICY=ROOT/'policies/english_only_policy.yaml'
spec=importlib.util.spec_from_file_location('validator',SCRIPT); v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
class EnglishOnlyPolicyTests(unittest.TestCase):
 def test_current_repository_matches_migration_baseline(self):
  r=v.validate(ROOT,POLICY); self.assertEqual(r['status'],'passed'); self.assertEqual(r['new_violation_count'],0)
 def test_new_violation_blocks(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t); (root/'policies').mkdir(); (root/'docs').mkdir();
   (root/'policies/english_only_policy.yaml').write_text(POLICY.read_text());
   (root/'policies/english_only_migration_baseline.json').write_text(json.dumps({'baseline_revision':'x','violation_ids':[]}));
   (root/'docs/new.md').write_text('Український текст'); r=v.validate(root,root/'policies/english_only_policy.yaml'); self.assertEqual(r['status'],'blocked'); self.assertEqual(r['new_violation_count'],1)
 def test_removed_baseline_violation_is_allowed(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t); (root/'policies').mkdir();
   (root/'policies/english_only_policy.yaml').write_text(POLICY.read_text());
   (root/'policies/english_only_migration_baseline.json').write_text(json.dumps({'baseline_revision':'x','violation_ids':['missing-id']}));
   r=v.validate(root,root/'policies/english_only_policy.yaml'); self.assertEqual(r['status'],'passed'); self.assertEqual(r['baseline_removed_count'],1)
if __name__=='__main__': unittest.main()
