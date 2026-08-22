#!/usr/bin/env python3
import json, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def req(cond,msg):
    if not cond: raise AssertionError(msg)

policy_path=ROOT/'source/optimization-runtime-efficiency-policy.json'
schema_path=ROOT/'source/optimization-timing-evidence.schema.json'
detector=ROOT/'tools/detect_time_degradation.py'
req(policy_path.exists(),'runtime efficiency policy missing')
req(schema_path.exists(),'timing evidence schema missing')
req(detector.exists(),'time degradation detector missing')
policy=json.loads(policy_path.read_text())
req(policy['tracks']['quality']['namespace'] != policy['tracks']['performance']['namespace'],'quality/performance namespaces must differ')
req(policy['one_pass_model_execution']['preferred'] is True,'one-pass callback must be preferred')
req(policy['restart_from_zero']['allowed_when_callback_available'] is False,'restart-from-zero must be forbidden when callback exists')
req(policy['compile_cache']['key_fields'] == ['candidate_sha256','runtime_version','compiler_or_kit_version','compile_config_hash'],'cache key must be semantic')
req(policy['time_degradation']['threshold_multiplier']['configurable'] is True,'threshold must be configurable')
req(abs(policy['time_degradation']['threshold_multiplier']['default']-1.35)<1e-9,'default diagnostic threshold should be 1.35')
req(policy['gap_loop_fusion']['status']=='CONTROLLED_EXPERIMENT_ONLY','gap-loop fusion must remain experiment-only')
req(policy['gap_loop_fusion']['must_preserve']['score_regime'] is True,'fusion must preserve score regime')
req(policy['parallelism']['independent_scenarios'] is True,'independent scenarios should be parallelizable')
req(policy['stop_rules']['invalid_revision_counts_toward_stagnation'] is False,'invalid revision must not count toward stagnation')
req(policy['stop_rules']['valid_non_improving_limit']==3,'stagnation limit must be 3')

schema=json.loads(schema_path.read_text())
required=set(schema['required'])
for k in ['candidate_sha256','revision_id','scenario_id','wall_time_ms','compile_ms','runtime_execution_ms','model_simulation_ms','artifact_materialization_ms','evaluation_ms','graph_steps','model_node_calls','gap_loop_iterations','candidate_compile_count','runtime_restart_count','artifact_sha256','score_regime_id','valid_evaluation']:
    req(k in required,f'missing timing field {k}')

sample={
 'candidate_sha256':'a'*64,'revision_id':'r6','scenario_id':'CERTIFICATE_INVALID','runtime_version':'rt1','evaluator_version':'ev1','simulator_policy_version':'sim1',
 'wall_time_ms':14500,'compile_ms':1000,'inspect_ms':400,'runtime_execution_ms':10000,'model_simulation_ms':1500,'artifact_materialization_ms':500,'evaluation_ms':1100,
 'graph_steps':150,'model_node_calls':4,'analyst_interactions':3,'gap_loop_iterations':8,'normalize_passes':8,'contract_audit_passes':8,'auto_resolve_passes':8,'candidate_compile_count':2,'runtime_restart_count':1,
 'artifact_sha256':'b'*64,'score_regime_id':'reg1','process_score':950,'result_score':980,'overall_score':970,'valid_evaluation':True,
 'semantic_complexity_delta':0.03,'recent_valid_wall_times_ms':[10000,10200,9800,10100]
}
with tempfile.TemporaryDirectory() as td:
    inp=Path(td)/'timing.json'; out=Path(td)/'report.json'
    inp.write_text(json.dumps(sample))
    cp=subprocess.run([sys.executable,str(detector),'--input',str(inp),'--output',str(out)],capture_output=True,text=True)
    req(cp.returncode==0,cp.stderr or cp.stdout)
    report=json.loads(out.read_text())
    req(report['status']=='PERFORMANCE_DEGRADATION','detector should trigger')
    req('RUNTIME_RESTART' in report['signals'],'restart signal missing')
    req('DUPLICATE_COMPILE' in report['signals'],'compile signal missing')
    req(report['score_effect']==0,'performance diagnostic must not alter quality score')

ap=json.loads((ROOT/'source/autonomous-playbook-improvement-policy.json').read_text())
for k in ['timing_evidence','performance_diagnostics','latest_candidate','best_candidate','best_score','valid_stagnation_count','optimization_status']:
    req(k in ap['evidence']['required'],f'autonomous evidence missing {k}')
print('ALPHA42 TIME DEGRADATION OPTIMIZATION: PASS')
