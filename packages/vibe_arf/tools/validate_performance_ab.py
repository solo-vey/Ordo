#!/usr/bin/env python3
import argparse,json,math
from pathlib import Path

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--before',required=True); ap.add_argument('--after',required=True); ap.add_argument('--output',required=True); ns=ap.parse_args()
 b=json.loads(Path(ns.before).read_text()); a=json.loads(Path(ns.after).read_text())
 findings=[]
 equal_fields=[('scenario_id','SCENARIO_CHANGED'),('runtime_version','RUNTIME_CHANGED'),('evaluator_version','EVALUATOR_CHANGED'),('simulator_policy_version','SIMULATOR_POLICY_CHANGED'),('score_regime_id','SCORE_REGIME_CHANGED'),('artifact_sha256','ARTIFACT_CHANGED'),('active_gap_set_sha256','ACTIVE_GAPS_CHANGED')]
 for f,code in equal_fields:
  if b.get(f)!=a.get(f): findings.append(code)
 for f,code in [('process_score','PROCESS_SCORE_CHANGED'),('result_score','RESULT_SCORE_CHANGED')]:
  if b.get(f)!=a.get(f): findings.append(code)
 bw=float(b.get('wall_time_ms',0) or 0); aw=float(a.get('wall_time_ms',0) or 0)
 if bw<=0 or aw<=0: findings.append('INVALID_WALL_TIME')
 ratio=(bw/aw) if bw>0 and aw>0 else None
 if ratio is not None and ratio<=1.0: findings.append('NO_PERFORMANCE_IMPROVEMENT')
 out={'status':'PASS' if not findings else 'FAIL','findings':findings,'improvement_ratio':ratio,'before_wall_time_ms':bw,'after_wall_time_ms':aw,'quality_score_effect':0,'equivalence_required':True}
 Path(ns.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(out['status']); return 0 if not findings else 1
if __name__=='__main__': raise SystemExit(main())
