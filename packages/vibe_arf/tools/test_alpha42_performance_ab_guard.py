#!/usr/bin/env python3
import json, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
tool=ROOT/'tools/validate_performance_ab.py'
assert tool.exists(), 'A/B validator missing'
def run(before,after):
 with tempfile.TemporaryDirectory() as td:
  b=Path(td)/'b.json'; a=Path(td)/'a.json'; o=Path(td)/'o.json'
  b.write_text(json.dumps(before)); a.write_text(json.dumps(after))
  cp=subprocess.run([sys.executable,str(tool),'--before',str(b),'--after',str(a),'--output',str(o)],capture_output=True,text=True)
  return cp.returncode,json.loads(o.read_text())
base={'candidate_sha256':'a'*64,'scenario_id':'S1','runtime_version':'rt','evaluator_version':'ev','simulator_policy_version':'sim','score_regime_id':'r1','artifact_sha256':'b'*64,'active_gap_set_sha256':'c'*64,'process_score':950,'result_score':980,'wall_time_ms':10000}
good=dict(base,wall_time_ms=7000)
rc,r=run(base,good); assert rc==0 and r['status']=='PASS' and r['improvement_ratio']>1.4
bad=dict(good,artifact_sha256='d'*64)
rc,r=run(base,bad); assert rc!=0 and r['status']=='FAIL' and 'ARTIFACT_CHANGED' in r['findings']
bad2=dict(good,score_regime_id='r2')
rc,r=run(base,bad2); assert rc!=0 and 'SCORE_REGIME_CHANGED' in r['findings']
print('ALPHA42 PERFORMANCE A/B GUARD: PASS')
