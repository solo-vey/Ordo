#!/usr/bin/env python3
import importlib.util, json, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('ordo_editor_service_replay', HERE.parent/'editor_service.py')
m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m)

creds={'provider':'custom','model':'recorded-model','base_url':'http://fixture.invalid/v1'}
m.LIVE_SESSIONS['regression']=creds.copy()
m.PLAYBOOK_PACKAGE.clear(); m.PLAYBOOK_PACKAGE.update({'id':'regression-package','compiled_plan_status':{'valid':False}})

f=json.loads((HERE/'fixtures'/'real_source_collection_decision.json').read_text())
producer=f['producer']
results=[]
for variant in ('gate_human_variant','gate_deterministic_variant'):
    gate=f[variant]
    source={'nodes':[producer,{'id':'MORE_INPUT_NODE'},{'id':'NEXT_NODE'}],'gates':[gate]}
    # recorded analyst response from real debug
    history=[{'role':'analyst','text':f['analyst_input'],'node_id':producer['id']}]
    gate_result=m._call_openai_live({
      'session_id':'regression','package_id':'regression-package','source':source,'current_id':gate['id'],
      'phase':'enter','state':{},'history':history,
    })
    results.append({'fixture':'source_collection_'+variant,'route_key':gate_result['route_key'],'next_id':gate_result['next_id'],'reason':gate_result['debug']['runtime']['reason'],'status':gate_result['run_status']})

# Missing input must halt unresolved, not silently follow on_fail.
unrelated={'id':'GENERIC_GATE','method':'deterministic','trust_class':'deterministic','required_inputs':['payload.checksum'],'condition':'checksum must match','on_pass':'NEXT_NODE','on_fail':'MORE_INPUT_NODE'}
source={'nodes':[{'id':'MORE_INPUT_NODE'},{'id':'NEXT_NODE'}],'gates':[unrelated]}
r=m._call_openai_live({'session_id':'regression','package_id':'regression-package','source':source,'current_id':'GENERIC_GATE','phase':'enter','state':{},'history':[]})
results.append({'fixture':'missing_input_unresolved','route_key':r['route_key'],'next_id':r['next_id'],'reason':r['debug']['runtime']['deterministic_gate']['reason'],'gate_result':r['debug']['runtime']['deterministic_gate']['result'],'status':r['run_status'],'completion_reason':r['completion_reason']})

# Previous debug proposal: replay recorded assistant proposal + bare analyst confirmation, no provider call.
f2=json.loads((HERE/'fixtures'/'real_attribute_confirmation.json').read_text())
record={'id':'ANY_PROPOSAL_NODE','answer_type':'table_confirmation_or_correction','on_answer':{'normalize':{'source_attribute_mapping.rows':'AI.NORMALIZE_CONFIRMED_RELEVANT_FIELD_ROWS($answer)'},'update_state':{'source_attribute_mapping.rows':'$normalized.source_attribute_mapping.rows'},'next':'VALIDATION_GATE'}}
gate2={'id':'VALIDATION_GATE','method':'self_verification','trust_class':'model_judgment','condition':'every row has module, data type, field path, field type, role, relevance rationale and source evidence','on_pass':'NEXT_NODE','on_fail':'ANY_PROPOSAL_NODE'}
source={'nodes':[record,{'id':'NEXT_NODE'}],'gates':[gate2]}
r=m._call_openai_live({'session_id':'regression','package_id':'regression-package','source':source,'current_id':record['id'],'phase':'respond','analyst_input':f2['analyst_input'],'state':f2['state'],'history':[{'role':'assistant','text':f2['assistant_proposal'],'node_id':record['id']}]})
rows=m._state_subtree(r['state'],'source_attribute_mapping.rows') or []
required=set(f2['expected_required_columns'])
results.append({'fixture':'attribute_confirmation','reason':r['debug']['runtime']['reason'],'row_count':len(rows),'full_schema':bool(rows) and all(required.issubset(row) for row in rows),'route_key':r['route_key'],'next_id':r['next_id']})

# New real 0.8.6 debug regression: model returned a valid canonical route and complete
# state updates but also incorrectly set await_analyst=true. Runtime must own
# orchestration and advance to canonical on_answer.next.
f3=json.loads((HERE/'fixtures'/'real_completed_respond_orchestration.json').read_text())
record3=f3['record']
target3={'id':f3['expected']['next_id'],'method':'self_verification','trust_class':'model_judgment','on_pass':'NEXT_NODE','on_fail':record3['id']}
source3={'nodes':[record3,{'id':'NEXT_NODE'}],'gates':[target3]}
recorded_result=f3['model_result']
def fake_provider_api_call(credentials, system_text, context):
    raw=json.dumps(recorded_result,ensure_ascii=False)
    usage={'input_tokens':0,'output_tokens':0,'total_tokens':0,'cached_tokens':0,'reasoning_tokens':0}
    return {'fixture':True}, {'fixture':True}, raw, usage
orig_provider=m._provider_api_call
m._provider_api_call=fake_provider_api_call
try:
    r=m._call_openai_live({'session_id':'regression','package_id':'regression-package','source':source3,'current_id':record3['id'],'phase':'respond','analyst_input':f3['analyst_input'],'state':{},'history':[]})
finally:
    m._provider_api_call=orig_provider
results.append({'fixture':'completed_respond_runtime_route_authority','route_key':r['route_key'],'next_id':r['next_id'],'await_analyst':r['await_analyst'],'override_reason':r['debug']['runtime'].get('orchestration_override_reason'),'state_update_keys':sorted(r['debug']['runtime']['state_updates'])})


# Real 0.8.6 attribute correction: analyst confirms/corrects the proposal, while the
# recorded model emits a compact row schema. Runtime must enrich it back to the
# reviewed proposal schema before proceeding to validation.
f4=json.loads((HERE/'fixtures'/'real_attribute_correction_schema_loss.json').read_text())
record4={'id':'GENERIC_TABLE_REVIEW','answer_type':'table_confirmation_or_correction','on_answer':{'normalize':{'source_attribute_mapping.rows':'AI.NORMALIZE_CONFIRMED_RELEVANT_FIELD_ROWS($answer)'},'update_state':{'source_attribute_mapping.rows':'$normalized.source_attribute_mapping.rows'},'next':'VALIDATION_GATE_2'}}
gate4={'id':'VALIDATION_GATE_2','method':'self_verification','trust_class':'model_judgment','condition':'every row preserves the reviewed table schema','on_pass':'NEXT_NODE','on_fail':record4['id']}
source4={'nodes':[record4,{'id':'NEXT_NODE'}],'gates':[gate4]}
recorded_result4={'assistant_message':'accepted','route_key':'next','state_updates':f4['model_updates'],'rationale_short':'recorded compact update','await_analyst':False}
def fake_provider_api_call4(credentials, system_text, context):
    raw=json.dumps(recorded_result4,ensure_ascii=False)
    usage={'input_tokens':0,'output_tokens':0,'total_tokens':0,'cached_tokens':0,'reasoning_tokens':0}
    return {'fixture':True}, {'fixture':True}, raw, usage
orig_provider=m._provider_api_call
m._provider_api_call=fake_provider_api_call4
try:
    r=m._call_openai_live({'session_id':'regression','package_id':'regression-package','source':source4,'current_id':record4['id'],'phase':'respond','analyst_input':f4['analyst_input'],'state':f4['state'],'history':[{'role':'assistant','text':f4['assistant_proposal'],'node_id':record4['id']}]})
finally:
    m._provider_api_call=orig_provider
rows4=m._state_subtree(r['state'],'source_attribute_mapping.rows') or []
required4=set(f4['expected_columns'])
results.append({'fixture':'attribute_correction_schema_preservation','row_count':len(rows4),'full_schema':bool(rows4) and all(required4.issubset(row) and all(row.get(k) not in (None,'') for k in required4) for row in rows4),'route_key':r['route_key'],'next_id':r['next_id'],'reconciliation':r['debug']['runtime'].get('structured_proposal_reconciliation')})


# Current 0.8.7 client-value retry regression: after validation returns to the same
# proposal node, the editor must show the already-owned output mapping rather than
# regenerate a fresh generic draft. An affirmative response commits exactly that table.
f5=json.loads((HERE/'fixtures'/'real_client_value_retry_continuity.json').read_text())
record5=f5['record']
gate5={'id':'GENERIC_VALIDATION_GATE','method':'self_verification','trust_class':'model_judgment','condition':'mapping must use confirmed source fields','on_pass':'NEXT_NODE','on_fail':record5['id']}
source5={'nodes':[record5,{'id':'NEXT_NODE'}],'gates':[gate5]}
history5=[
    {'role':'assistant','text':'Earlier proposal','node_id':record5['id']},
    {'role':'analyst','text':'Коригую mapping','node_id':record5['id']},
    {'role':'assistant','text':'Mapping saved','node_id':record5['id']},
]
r_enter=m._call_openai_live({'session_id':'regression','package_id':'regression-package','source':source5,'current_id':record5['id'],'phase':'enter','state':f5['state'],'history':history5})
enter_text=r_enter['assistant_message']
history5.append({'role':'assistant','text':enter_text,'node_id':record5['id']})
r_respond=m._call_openai_live({'session_id':'regression','package_id':'regression-package','source':source5,'current_id':record5['id'],'phase':'respond','analyst_input':'погоджую','state':f5['state'],'history':history5})
committed=m._state_subtree(r_respond['state'],'output_payload_mapping.rows') or []
results.append({'fixture':'client_mapping_retry_continuity','enter_reason':r_enter['debug']['runtime']['reason'],'enter_preserved_target':('values.companyTypeUA' in enter_text),'enter_regenerated_target':('`status`' in enter_text or '| status |' in enter_text),'respond_reason':r_respond['debug']['runtime']['reason'],'next_id':r_respond['next_id'],'same_rows':committed==f5['state']['output_payload_mapping']['rows']})

ok=(results[0]['next_id']=='NEXT_NODE' and results[1]['next_id']=='NEXT_NODE' and results[2]['gate_result']=='unresolved' and results[2]['next_id'] is None and results[3]['full_schema'] and results[3]['next_id']=='VALIDATION_GATE' and results[4]['next_id']==f3['expected']['next_id'] and results[4]['await_analyst'] is False and results[4]['override_reason']=='allowed-route-overrides-model-await' and results[5]['full_schema'] and results[5]['next_id']=='VALIDATION_GATE_2' and results[5]['reconciliation'] and results[5]['reconciliation'].get('mode')=='schema-preserving-reconciliation' and results[6]['enter_reason']=='retry-existing-structured-output' and results[6]['enter_preserved_target'] and not results[6]['enter_regenerated_target'] and results[6]['respond_reason']=='generic-proposal-preserving-confirmation' and results[6]['same_rows'] and results[6]['next_id']=='GENERIC_VALIDATION_GATE')
print(json.dumps({'status':'PASS' if ok else 'FAIL','results':results},ensure_ascii=False,indent=2))
raise SystemExit(0 if ok else 1)
