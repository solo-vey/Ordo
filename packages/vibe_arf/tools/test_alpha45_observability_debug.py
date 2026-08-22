#!/usr/bin/env python3
from pathlib import Path
import json, yaml, subprocess, sys, tempfile
R=Path(__file__).resolve().parents[1]
checks={}
def ck(k,v): checks[k]=bool(v)
def j(rel):
 p=R/rel; return json.loads(p.read_text()) if p.is_file() else {}
def y(rel):
 p=R/rel; return yaml.safe_load(p.read_text()) if p.is_file() else {}
policy=j('source/observability-debug-policy.json')
prog=y('source/program.ordo.yaml') or {}; module=y('source/modules/40_policies.ordo.module.yaml') or {}
inherit=j('source/generated-playbook-execution-inheritance-policy.json'); perf=j('source/performance-token-optimization-subprocess-policy.json')
objs=(y('authoring/information_object_catalog.yaml') or {}).get('objects',[])
groups=(y('authoring/information_group_catalog.yaml') or {}).get('groups',[])
flows=(y('authoring/information_flow_graph.yaml') or {}).get('edges',[])
proj=(y('authoring/ordo_projection.yaml') or {}).get('information_bindings',[])
ck('policy_exists',bool(policy)); ck('policy_id',policy.get('policy_id')=='OBSERVABILITY_DEBUG'); ck('scope',policy.get('scope')=='cross_domain')
for f in ['node_id','execution_count','duration_ms','input_bytes','output_bytes','input_tokens','output_tokens','token_count_source','dependency_fingerprint','route','result_sha256']:
 ck('node_metric_'+f, f in policy.get('per_node_telemetry',{}).get('fields',[]))
rec=policy.get('execution_receipts',{})
ck('receipts_append_only',rec.get('append_only') is True); ck('receipts_hash_chain',rec.get('hash_chain') is True)
for f in ['run_id','sequence','from_node','to_node','route','input_projection_sha256','state_update_sha256','previous_receipt_sha256','receipt_sha256','timestamp','status']:
 ck('receipt_'+f,f in rec.get('required_fields',[]))
ctx=policy.get('context_accounting',{})
for f in ['filesystem_scanned_bytes','tool_output_visible_bytes','model_loaded_content_bytes','platform_overhead_tokens','playbook_controlled_tokens']:
 ck('context_'+f,f in ctx.get('separate_metrics',[]))
ck('platform_separate',ctx.get('platform_overhead_separate') is True)
ck('startup_read_audit',policy.get('startup_read_audit',{}).get('enabled') is True)
ck('startup_no_new_reads',policy.get('startup_read_audit',{}).get('audit_must_not_trigger_new_reads') is True)
ck('pass_diag_zero_score',policy.get('pass_count_diagnostic',{}).get('score_effect')==0)
ck('hotspot_ranking',set(policy.get('hotspot_ranking',{}).get('dimensions',[])) >= {'total_time','total_input','total_output','execution_count','context_overread','filesystem_scan'})
ck('visible_timing_ref',policy.get('visible_timing_policy')=='source/visible-debug-timing-policy.json')
for name in ['DEBUG_RUN_INDEX.json','EXECUTION_RECEIPTS.jsonl','PER_NODE_TELEMETRY.jsonl','TIMING_SUMMARY.json','TOKEN_USAGE_SUMMARY.json','FILE_ACCESS_SUMMARY.json','SELF_REPAIR_LOG.jsonl','VALIDATION_SUMMARY.json']:
 ck('bundle_'+name,name in policy.get('standard_debug_bundle',{}).get('required_or_explicitly_unavailable',[]))
for rel in ['tools/append_execution_receipt.py','tools/collect_observability_debug.py','tools/validate_observability_debug.py']:
 ck('tool_'+Path(rel).name,(R/rel).is_file())
# graph/data layer/laws
laws={x.get('id'):x for x in prog.get('playbook_laws',{}).get('laws',[]) if isinstance(x,dict)}; mlaws={x.get('id'):x for x in module.get('playbook_laws',{}).get('laws',[]) if isinstance(x,dict)}
ck('law_program','E93_OBSERVABILITY_DEBUG' in laws); ck('law_module','E93_OBSERVABILITY_DEBUG' in mlaws); ck('law_markdown','E93_OBSERVABILITY_DEBUG' in (R/'PLAYBOOK_LAWS.md').read_text())
objids={x.get('id') for x in objs if isinstance(x,dict)}; ck('info_object','I_OBSERVABILITY_DEBUG_CONTRACT' in objids)
g={x.get('id'):x for x in groups if isinstance(x,dict)}; ck('group_member','I_OBSERVABILITY_DEBUG_CONTRACT' in g.get('G_CHANGE_REPAIR',{}).get('members',[]))
ft={(x.get('from'),x.get('to'),x.get('type')) for x in flows if isinstance(x,dict)}
ck('flow_context_obs',('I_CONTEXT_RUNTIME_EFFICIENCY_CONTRACT','I_OBSERVABILITY_DEBUG_CONTRACT','depends_on') in ft)
ck('flow_obs_perf',('I_OBSERVABILITY_DEBUG_CONTRACT','I_PERFORMANCE_TOKEN_OPTIMIZATION_SUBPROCESS_CONTRACT','depends_on') in ft)
ck('projection',any(x.get('information_id')=='I_OBSERVABILITY_DEBUG_CONTRACT' and 'N_PO_TELEMETRY_COLLECT' in x.get('node_ids',[]) for x in proj if isinstance(x,dict)))
nodes={x.get('id'):x for x in prog.get('nodes',[]) if isinstance(x,dict)}
tel=nodes.get('N_PO_TELEMETRY_COLLECT',{})
ck('telemetry_policy_ref','source/observability-debug-policy.json' in tel.get('node_context',{}).get('knowledge_refs',[]))
ck('telemetry_collect_tool','tools/collect_observability_debug.py' in tel.get('node_context',{}).get('allowed_tools',[]))
ck('telemetry_validate_tool','tools/validate_observability_debug.py' in tel.get('node_context',{}).get('allowed_tools',[]))
# inheritance / perf
lawids={x.get('id') for x in inherit.get('laws',[]) if isinstance(x,dict)}
for rid in ['EXECUTION_RECEIPTS_REQUIRED','PER_NODE_OBSERVABILITY_REQUIRED','CONTEXT_ACCOUNTING_SEPARATION','STANDARD_DEBUG_BUNDLE','PASS_COUNT_DEGRADATION_DIAGNOSTIC']:
 ck('inherit_'+rid,rid in lawids)
ck('inherit_policy','source/observability-debug-policy.json' in inherit.get('required_generated_artifacts',[]))
ck('perf_policy_ref','source/observability-debug-policy.json' in perf.get('knowledge_refs',[]))
ck('debug_builder_index_contract','DEBUG_RUN_INDEX.json' in (R/'tools/build_debug_handoff_package.py').read_text())
# behavioral receipt hash chain
try:
 with tempfile.TemporaryDirectory() as td:
  cmd=[sys.executable,str(R/'tools/append_execution_receipt.py'),td,'--run-id','r1','--from-node','A','--to-node','B','--route','pass','--input-sha','1'*64,'--update-sha','2'*64,'--status','PASS']
  p1=subprocess.run(cmd,capture_output=True,text=True); p2=subprocess.run(cmd[:-6]+['--from-node','B','--to-node','C','--route','next','--input-sha','3'*64,'--update-sha','4'*64,'--status','PASS'],capture_output=True,text=True)
  lp=Path(td)/'runtime/evidence/EXECUTION_RECEIPTS.jsonl'; rows=[json.loads(x) for x in lp.read_text().splitlines()] if lp.exists() else []
  ck('behavior_receipt_append',p1.returncode==0 and p2.returncode==0 and len(rows)==2)
  ck('behavior_receipt_chain',len(rows)==2 and rows[1].get('previous_receipt_sha256')==rows[0].get('receipt_sha256'))
  ck('behavior_receipt_sequence',len(rows)==2 and [x.get('sequence') for x in rows]==[1,2])
except Exception:
 for k in ['behavior_receipt_append','behavior_receipt_chain','behavior_receipt_sequence']: ck(k,False)
# profile registration
pe=j('verification/PROFILE_EXTENSIONS.json'); ck('profile_registration',any(x.get('id')=='alpha45_observability_debug' for x in pe.get('checks',[]) if isinstance(x,dict)))
failed=[k for k,v in checks.items() if not v]
print(json.dumps({'status':'PASS' if not failed else 'FAIL','passed':sum(checks.values()),'total':len(checks),'failed':failed},indent=2))
raise SystemExit(1 if failed else 0)
