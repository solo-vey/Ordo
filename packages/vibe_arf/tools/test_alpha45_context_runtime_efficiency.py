#!/usr/bin/env python3
from pathlib import Path
import json, sys, yaml
R=Path(__file__).resolve().parents[1]
checks={}
def ck(k,v): checks[k]=bool(v)

def j(rel):
    p=R/rel
    return json.loads(p.read_text(encoding='utf-8')) if p.is_file() else {}
def y(rel):
    p=R/rel
    return yaml.safe_load(p.read_text(encoding='utf-8')) if p.is_file() else {}

policy=j('source/context-runtime-efficiency-policy.json')
tmpl=y('authoring_templates/reusable/CONTEXT_RUNTIME_EFFICIENCY.template.yaml') or {}
prog=y('source/program.ordo.yaml') or {}
module=y('source/modules/40_policies.ordo.module.yaml') or {}
objs=(y('authoring/information_object_catalog.yaml') or {}).get('objects',[])
groups=(y('authoring/information_group_catalog.yaml') or {}).get('groups',[])
flows=(y('authoring/information_flow_graph.yaml') or {}).get('edges',[])
proj=(y('authoring/ordo_projection.yaml') or {}).get('information_bindings',[])
inherit=j('source/generated-playbook-execution-inheritance-policy.json')
perf=j('source/performance-token-optimization-subprocess-policy.json')
contract=j('DISTRIBUTION_PACKAGE_CONTRACT.json')

ck('policy_exists', bool(policy))
ck('policy_id', policy.get('policy_id')=='CONTEXT_RUNTIME_EFFICIENCY')
ck('policy_cross_domain', policy.get('scope')=='cross_domain')
metrics=set(policy.get('metrics',[]))
for m in ['static_source_bytes','startup_loaded_bytes','node_prompt_loaded_bytes','node_knowledge_loaded_bytes','model_visible_tool_output_bytes','package_bytes','platform_overhead_tokens']:
    ck('metric_'+m, m in metrics)
rules=policy.get('runtime_read_rules',{})
for k in ['no_recursive_package_preload','no_full_source_preload','active_element_targeted_read','lazy_prompt_loading','lazy_knowledge_loading','authoring_editor_runtime_isolation']:
    ck('rule_'+k, rules.get(k) is True)
ck('targeted_read_budget', policy.get('targeted_read_budget',{}).get('default_max_bytes')==8192 and policy.get('targeted_read_budget',{}).get('default_max_lines')==80)
ck('token_estimate_labeled', policy.get('token_estimation',{}).get('fallback')=='utf8_bytes_div_4' and policy.get('token_estimation',{}).get('must_label_estimate') is True)
ck('platform_separation', policy.get('context_accounting',{}).get('separate_platform_overhead') is True)
ck('compact_refs', policy.get('optimization_patterns',{}).get('compact_evidence_by_reference') is True)
ck('delta_outputs', policy.get('optimization_patterns',{}).get('delta_outputs_for_repeat_passes') is True)
ck('dependency_fingerprint', policy.get('optimization_patterns',{}).get('material_dependency_fingerprint_before_rerun') is True)
ck('equivalence_gate', policy.get('acceptance',{}).get('semantic_quality_equivalence_required') is True)

ck('template_exists', bool(tmpl))
ck('template_scope', tmpl.get('scope')=='cross_domain')
seq=tmpl.get('sequence',[])
ck('template_context_audit', 'CONTEXT_RUNTIME_AUDIT' in seq)
ck('template_context_gate', 'CONTEXT_EVIDENCE_GATE' in seq)

laws={x.get('id'):x for x in prog.get('playbook_laws',{}).get('laws',[]) if isinstance(x,dict)}
mlaws={x.get('id'):x for x in module.get('playbook_laws',{}).get('laws',[]) if isinstance(x,dict)}
ck('law_program', 'E88_CONTEXT_RUNTIME_EFFICIENCY' in laws)
ck('law_module', 'E88_CONTEXT_RUNTIME_EFFICIENCY' in mlaws)
ck('law_markdown', 'E88_CONTEXT_RUNTIME_EFFICIENCY' in (R/'PLAYBOOK_LAWS.md').read_text(encoding='utf-8'))

obj_ids={x.get('id') for x in objs if isinstance(x,dict)}
ck('data_object', 'I_CONTEXT_RUNTIME_EFFICIENCY_CONTRACT' in obj_ids)
g={x.get('id'):x for x in groups if isinstance(x,dict)}
ck('group_membership', 'I_CONTEXT_RUNTIME_EFFICIENCY_CONTRACT' in g.get('G_CHANGE_REPAIR',{}).get('members',[]))
flow_tuples={(x.get('from'),x.get('to'),x.get('type')) for x in flows if isinstance(x,dict)}
ck('flow_into_context', ('I_OPTIMIZATION_RUNTIME_EFFICIENCY_CONTRACT','I_CONTEXT_RUNTIME_EFFICIENCY_CONTRACT','depends_on') in flow_tuples)
ck('flow_into_perf', ('I_CONTEXT_RUNTIME_EFFICIENCY_CONTRACT','I_PERFORMANCE_TOKEN_OPTIMIZATION_SUBPROCESS_CONTRACT','depends_on') in flow_tuples)
ck('projection_binding', any(x.get('information_id')=='I_CONTEXT_RUNTIME_EFFICIENCY_CONTRACT' and 'N_PO_CONTEXT_RUNTIME_AUDIT' in x.get('node_ids',[]) for x in proj if isinstance(x,dict)))

nodes={x.get('id'):x for x in prog.get('nodes',[]) if isinstance(x,dict)}
gates={x.get('id'):x for x in prog.get('gates',[]) if isinstance(x,dict)}
ck('context_node', 'N_PO_CONTEXT_RUNTIME_AUDIT' in nodes)
ck('context_gate', 'G_PO_CONTEXT_EVIDENCE_VALID' in gates)
ck('quality_routes_context', gates.get('G_PO_QUALITY_BASELINE_STABLE',{}).get('on_pass')=='N_PO_CONTEXT_RUNTIME_AUDIT')
ck('context_routes_gate', nodes.get('N_PO_CONTEXT_RUNTIME_AUDIT',{}).get('on_answer',{}).get('next')=='G_PO_CONTEXT_EVIDENCE_VALID')
ck('gate_routes_telemetry', gates.get('G_PO_CONTEXT_EVIDENCE_VALID',{}).get('on_pass')=='N_PO_TELEMETRY_COLLECT')
ck('context_state', all(k in prog.get('state',{}).get('schema',{}) for k in ['context_runtime_efficiency_evidence','context_runtime_asset_classification','context_runtime_startup_read_audit']))
ck('context_tool', (R/'tools/audit_context_runtime_efficiency.py').is_file())
ck('context_validator', (R/'tools/validate_context_runtime_efficiency.py').is_file())

ck('inherit_template', inherit.get('reusable_subprocesses',{}).get('PERFORMANCE_TOKEN_OPTIMIZATION_LOOP',{}).get('context_efficiency_template')=='authoring_templates/reusable/CONTEXT_RUNTIME_EFFICIENCY.template.yaml')
ck('perf_context_metrics', all(x in perf.get('metrics',[]) for x in ['startup_loaded_bytes','node_prompt_loaded_bytes','node_knowledge_loaded_bytes','model_visible_tool_output_bytes']))
ck('perf_context_policy_ref', 'source/context-runtime-efficiency-policy.json' in perf.get('knowledge_refs',[]))

model_start=((R/'START_HERE_MODEL_MODE.md').read_text(encoding='utf-8')+'\n'+(R/'START_PROMPT_MODEL_MODE.md').read_text(encoding='utf-8')).lower()
for phrase in ['do not recursively read','do not preload','active node','authoring/','design/']:
    ck('model_start_'+phrase.replace('/','').replace(' ','_'), phrase in model_start)

mr=contract.get('profiles',{}).get('MODEL_RUN',{})
ck('model_consumer_classification', mr.get('asset_selection')=='consumer_aware_transitive_dependency_closure')
ck('model_context_policy', mr.get('context_efficiency_policy')=='source/context-runtime-efficiency-policy.json')

failed=[k for k,v in checks.items() if not v]
print(json.dumps({'status':'PASS' if not failed else 'FAIL','passed':sum(checks.values()),'total':len(checks),'failed':failed},indent=2,ensure_ascii=False))
raise SystemExit(0 if not failed else 1)
