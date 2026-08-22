#!/usr/bin/env python3
from pathlib import Path
import importlib.util,json,yaml
R=Path(__file__).resolve().parents[1]; checks=[]
def ck(n,v): checks.append((n,bool(v)))
pol=json.loads((R/'source/generated-playbook-semantic-execution-policy.json').read_text())
ck('MODEL_MODE_REFERENCE',pol['model_mode_reference']['cli_is_semantic_authority'] is False)
ck('MERGE_BY_DIFF_POLICY',pol['state_update']['mode']=='MERGE_BY_DIFF' and pol['state_update']['unrelated_keys_must_survive'])
ck('REENTRY_POLICY',pol['reentry']['current_node_is_authoritative'] and not pol['reentry']['historical_visitation_is_completion_evidence'])
ck('ON_FAIL_RECOVERY',pol['gate_recovery']['on_fail_is_real_route'])
ck('NO_RUNTIME_DATA_POLLUTION',pol['data_layer_runtime_workaround_barrier']['forbid_runner_bug_compensation_in_business_data_layer'])
ck('EXHAUSTIVE_DISCOVERY',pol['analyst_authority_discovery']['exhaustive_before_ask'])
ck('STABLE_DECISION_ID',pol['stable_decision_identity']['decision_id_required'] and not pol['stable_decision_identity']['reask_resolved_without_new_conflict'])
ck('FULL_REPAIR_LOOP',pol['repair_loop_regression']['minimum_trace']==['VALIDATE_FAIL','FOLLOW_ON_FAIL','LOCAL_REPAIR','REMATERIALIZE_OR_RECOMPUTE','REVALIDATE_PASS'])
# deterministic helper behavior
spec=importlib.util.spec_from_file_location('x',R/'tools/execute_deterministic_state_transform.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
r=m.trans('merge_state_diff',{'state':{'a':1,'nested':{'x':1,'keep':2},'untouched':9},'state_diff':{'nested':{'x':3},'b':4}})['state']
ck('MERGE_PRESERVES_UNRELATED',r=={'a':1,'nested':{'x':3,'keep':2},'untouched':9,'b':4})
dec=[{'decision_id':'D2','information_group':'G1','authority_owner':'human','consequential':True,'status':'UNRESOLVED','priority':2},{'decision_id':'D1','information_group':'G1','authority_owner':'human','consequential':True,'status':'UNRESOLVED','priority':1},{'decision_id':'D3','information_group':'G2','authority_owner':'human','consequential':True,'status':'RESOLVED'}]
b=m.trans('discover_authority_decisions',{'candidate_decisions':dec})
ck('DISCOVERY_BATCHES_ALL_VISIBLE_SAME_GROUP',b['decision_count']==2 and b['authority_batches'][0]['decision_ids']==['D1','D2'])
a=m.trans('apply_authority_decision_diff',{'decisions':dec[:2],'responses':[{'decision_id':'D1','status':'RESOLVED','answer':'A'}]})
ck('PARTIAL_ANSWER_PRESERVED',set(a['unresolved_decision_ids'])=={'D2'} and any(x['decision_id']=='D1' and x['status']=='RESOLVED' for x in a['decisions']))
# authoring template/regression wiring
reg=json.loads((R/'source/generated-playbook-regression-policy.json').read_text()); ck('REGRESSION_FAMILIES_WIRED',set(pol['required_regression_families'])<=set(x.upper() for x in [y.upper() for y in pol['required_regression_families']]) and 'source/generated-playbook-semantic-execution-policy.json' in reg['authoring_defaults'])
kit=json.loads((R/'authoring_templates/reusable/TEMPLATE_KIT_REGISTRY.json').read_text()); ck('REUSABLE_TEMPLATE_WIRED','semantic_execution_invariants' in kit['templates'])
# Data Layer owns contract
cat=yaml.safe_load((R/'authoring/information_object_catalog.yaml').read_text()); ck('DATA_LAYER_CONTRACT',any(x.get('id')=='I_GENERATED_PLAYBOOK_SEMANTIC_EXECUTION_CONTRACT' for x in cat.get('objects',[])))
# no concrete passport/jira specifics introduced
text=(R/'source/generated-playbook-semantic-execution-policy.json').read_text().lower(); ck('FRAMEWORK_GENERIC',all(x not in text for x in ['jira','passport','liga-9889','authority_decision_batch']))
failed=[n for n,v in checks if not v]
for n,v in checks: print(('PASS' if v else 'FAIL'),n)
print(f'ALPHA44_GENERATED_PLAYBOOK_SEMANTIC_EXECUTION: {len(checks)-len(failed)}/{len(checks)} PASS')
raise SystemExit(1 if failed else 0)
