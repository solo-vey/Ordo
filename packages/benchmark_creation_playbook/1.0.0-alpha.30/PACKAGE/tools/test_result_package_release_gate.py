#!/usr/bin/env python3
from pathlib import Path
import json, subprocess, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
TOOL=ROOT/'tools/validate_result_package_release.py'
POLICY=ROOT/'RESULT_PACKAGE_RELEASE_GATE_POLICY.yaml'
cases={
 'base_valid':(0,'PASS_RELEASE'),
 'validator_fail':(1,'BLOCKED_REGENERATE'),
 'foreign_literal':(1,'BLOCKED_REGENERATE'),
 'stale_approval':(1,'BLOCKED_REGENERATE'),
 'not_ready':(1,'NO_GO'),
 'incomplete_manual_qa':(1,'BLOCKED_REGENERATE'),
}
results=[]
with tempfile.TemporaryDirectory() as td:
  for name,(rc_expected,disp_expected) in cases.items():
    report=Path(td)/f'{name}.json'
    p=subprocess.run([sys.executable,str(TOOL),'--package-dir',str(ROOT/'fixtures/result_package_release_gate'/name),'--policy',str(POLICY),'--report',str(report)],capture_output=True,text=True)
    data=json.loads(report.read_text())
    ok=p.returncode==rc_expected and data['release_disposition']==disp_expected
    results.append({'case':name,'passed':ok,'returncode':p.returncode,'disposition':data['release_disposition'],'expected':disp_expected})
out={'schema_version':'ordo.benchmark.result_package_release_gate.acceptance.v1','passed':all(x['passed'] for x in results),'passed_count':sum(x['passed'] for x in results),'total':len(results),'cases':results}
path=ROOT/'reports/RESULT_PACKAGE_RELEASE_GATE_ACCEPTANCE_TESTS.json'; path.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
raise SystemExit(0 if out['passed'] else 1)
