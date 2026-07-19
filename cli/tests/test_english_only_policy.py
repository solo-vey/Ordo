from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; SCRIPT=ROOT/"tools/check_english_only_policy.py"; FIX=ROOT/"cli/tests/fixtures/english_only_policy"
class T(unittest.TestCase):
    def runv(self,repo):
        with tempfile.TemporaryDirectory() as d:
            rp=Path(d)/"r.json"; p=subprocess.run([sys.executable,str(SCRIPT),str(repo),"--out",str(rp),"--json"],cwd=ROOT,capture_output=True,text=True)
            return p,json.loads(rp.read_text())
    def test_pass(self):
        p,r=self.runv(FIX/"pass_repo"); self.assertEqual(p.returncode,0,p.stdout+p.stderr); self.assertEqual(r["status"],"passed")
    def test_fail_closed(self):
        p,r=self.runv(FIX/"fail_repo"); self.assertEqual(p.returncode,1); self.assertEqual(r["violation_count"],1)
    def test_repo(self):
        p,r=self.runv(ROOT); self.assertEqual(p.returncode,0,p.stdout+p.stderr); self.assertEqual(r["status"],"passed")
    def test_no_separate_workflow(self):
        names={p.name for p in (ROOT/".github/workflows").glob("*.yml")}; self.assertNotIn("english-only-policy.yml",names)
if __name__=="__main__": unittest.main()
