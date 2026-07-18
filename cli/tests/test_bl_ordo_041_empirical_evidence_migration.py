import hashlib, json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
EE=ROOT/"empirical_evidence"
class TestBLORDO041(unittest.TestCase):
 def test_validator_passes(self):
  p=subprocess.run([sys.executable,str(EE/"tools/validate_empirical_evidence.py"),str(EE)],capture_output=True,text=True)
  self.assertEqual(p.returncode,0,p.stdout+p.stderr)
 def test_source_manifest_matches_preserved_files(self):
  m=json.loads((EE/"manifests/SOURCE_MIGRATION_V1_3.json").read_text())
  base=EE/"raw_evidence/source_packages/ORDO_EMPIRICAL_EVIDENCE_BASE_v1_3"
  self.assertEqual(m["source_file_count"],92)
  for e in m["source_files"]:
   p=base/e["path"]; self.assertTrue(p.is_file()); self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),e["sha256"])
 def test_complete_pairing(self):
  idx=json.loads((EE/"manifests/EMPIRICAL_EVIDENCE_INDEX.json").read_text())
  self.assertEqual(len(idx["runs"]),10); self.assertEqual(len(idx["scorecards"]),10); self.assertEqual(len(idx["admissions"]),10)
 def test_no_csg_merge(self):
  idx=json.loads((EE/"manifests/EMPIRICAL_EVIDENCE_INDEX.json").read_text()); self.assertEqual(idx["existing_evaluation_relationship"],"independent_parallel")
if __name__=="__main__": unittest.main()
