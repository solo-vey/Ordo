#!/usr/bin/env python3
import argparse,json,re,sys
from pathlib import Path
REQ=['candidate_sha256','revision_id','scenario_id','runtime_version','evaluator_version','simulator_policy_version','wall_time_ms','compile_ms','inspect_ms','runtime_execution_ms','model_simulation_ms','artifact_materialization_ms','evaluation_ms','graph_steps','model_node_calls','analyst_interactions','gap_loop_iterations','normalize_passes','contract_audit_passes','auto_resolve_passes','candidate_compile_count','runtime_restart_count','artifact_sha256','score_regime_id','valid_evaluation']
HEX=re.compile(r'^[0-9a-f]{64}$')
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('evidence'); ns=ap.parse_args(); d=json.loads(Path(ns.evidence).read_text())
 errs=[]
 for k in REQ:
  if k not in d: errs.append(f'missing {k}')
 for k in ('candidate_sha256','artifact_sha256'):
  if k in d and not HEX.match(str(d[k])): errs.append(f'invalid {k}')
 for k in ('wall_time_ms','compile_ms','inspect_ms','runtime_execution_ms','model_simulation_ms','artifact_materialization_ms','evaluation_ms','graph_steps','model_node_calls','analyst_interactions','gap_loop_iterations','normalize_passes','contract_audit_passes','auto_resolve_passes','candidate_compile_count','runtime_restart_count'):
  if k in d and (not isinstance(d[k],(int,float)) or d[k]<0): errs.append(f'invalid {k}')
 if errs:
  print('FAIL'); [print(x) for x in errs]; return 1
 print('OPTIMIZATION TIMING EVIDENCE: PASS'); return 0
if __name__=='__main__': raise SystemExit(main())
