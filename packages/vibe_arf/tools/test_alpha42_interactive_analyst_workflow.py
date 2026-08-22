#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys, tempfile
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]

def req(cond,msg):
    if not cond: raise AssertionError(msg)

policy_path=ROOT/'source/interactive-analyst-workflow-policy.json'
req(policy_path.exists(),'interactive analyst workflow policy missing')
policy=json.loads(policy_path.read_text())
req(policy['conversation_model']=='continuous_fact_stream','conversation must be fact stream')
req(policy['field_resolution']['statuses']==['KNOWN','UNASKED','UNKNOWN_CONFIRMED','INAPPLICABLE'],'resolution status contract mismatch')
req(policy['field_resolution']['value_does_not_imply_status'] is True,'value text/null must not imply resolution status')
req(policy['incremental_intake']['capture_all_relevant_facts'] is True,'off-shape facts must be captured')
req(policy['incremental_intake']['recompute_after_each_meaningful_message'] is True,'gaps must recompute after merge')
req(policy['corrections']['silent_overwrite_forbidden'] is True,'silent overwrite must be forbidden')
req(policy['questioning']['derive_before_ask'] is True,'derive-before-ask required')
req(policy['questioning']['reask_unknown_confirmed_without_new_evidence'] is False,'confirmed unknown must not be re-asked')
req(policy['materialization']['substantive_unasked_is_hard_block'] is True,'UNASKED substantive field must block materialization')
req(policy['progress']['enter_before_long_operation'] is True,'progress ENTER must precede long work')
for test_id in ['FULL_INPUT','INCREMENTAL_INPUT','OFF_SHAPE_ANSWER','EXPLICIT_UNKNOWN','UNASKED_SUBSTANTIVE','CORRECTION','REORDER','CHUNKING_INVARIANCE','INPUT_ORDER_INVARIANCE']:
    req(test_id in policy['required_regression_families'],f'missing regression family {test_id}')

# Canonical Data Layer contracts.
oc=yaml.safe_load((ROOT/'authoring/information_object_catalog.yaml').read_text()) or {}
objs={x['id']:x for x in oc.get('objects') or [] if isinstance(x,dict) and x.get('id')}
for oid in ['I_INTERACTIVE_ANALYST_WORKFLOW_CONTRACT','I_FIELD_RESOLUTION_STATUS_CONTRACT','I_INTERACTIVE_COMPLETENESS_CONTRACT','I_ANALYST_INTERACTION_ROBUSTNESS_CONTRACT']:
    req(oid in objs,f'missing Data Layer object {oid}')
gc=yaml.safe_load((ROOT/'authoring/information_group_catalog.yaml').read_text()) or {}
groups={x['id']:x for x in gc.get('groups') or [] if isinstance(x,dict) and x.get('id')}
req('I_INTERACTIVE_ANALYST_WORKFLOW_CONTRACT' in groups['G_INFORMATION_MODEL']['members'],'interactive workflow contract must be in G_INFORMATION_MODEL')
req('I_FIELD_RESOLUTION_STATUS_CONTRACT' in groups['G_INFORMATION_MODEL']['members'],'field status contract must be in G_INFORMATION_MODEL')
req('I_INTERACTIVE_COMPLETENESS_CONTRACT' in groups['G_PROCESS_DESIGN']['members'],'completeness contract must be in G_PROCESS_DESIGN')
req('I_ANALYST_INTERACTION_ROBUSTNESS_CONTRACT' in groups['G_VERIFICATION']['members'],'robustness contract must be in G_VERIFICATION')
ip=yaml.safe_load((ROOT/'authoring/interaction_projection.yaml').read_text()) or {}
ipol=ip.get('policy') or {}
req(ipol.get('continuous_fact_stream') is True,'interaction projection must declare continuous fact stream')
req(ipol.get('capture_off_shape_facts') is True,'interaction projection must capture off-shape facts')
req(ipol.get('recompute_after_merge') is True,'interaction projection must recompute after merge')

# Deterministic merge and completeness behavior.
transform=ROOT/'tools/execute_deterministic_state_transform.py'
def run_op(op,payload):
    with tempfile.TemporaryDirectory() as td:
        inp=Path(td)/'in.json'; out=Path(td)/'out.json'
        inp.write_text(json.dumps(payload),encoding='utf-8')
        cp=subprocess.run([sys.executable,str(transform),'--operation',op,'--input',str(inp),'--output',str(out)],capture_output=True,text=True)
        req(cp.returncode==0,cp.stderr or cp.stdout)
        return json.loads(out.read_text())['result']

base={'canonical_fields':{
    'source.endpoint':{'value':None,'resolution_status':'UNASKED','field_class':'SUBSTANTIVE_REQUIRED'},
    'errors.404':{'value':None,'resolution_status':'UNASKED','field_class':'SUBSTANTIVE_REQUIRED'},
    'refresh':{'value':None,'resolution_status':'UNASKED','field_class':'SUBSTANTIVE_DECISIONAL'},
    'jurisdiction':{'value':None,'resolution_status':'UNASKED','field_class':'SUBSTANTIVE_REQUIRED'},
}}
merged=run_op('merge_incremental_analyst_facts',{**base,'incoming_facts':[
    {'field_id':'source.endpoint','value':'/v1/company','resolution_status':'KNOWN','provenance_type':'analyst','statement_id':'s1'},
    {'field_id':'errors.404','value':'NO_DATA','resolution_status':'KNOWN','provenance_type':'analyst','statement_id':'s1'},
    {'field_id':'refresh','value':None,'resolution_status':'UNKNOWN_CONFIRMED','provenance_type':'analyst','statement_id':'s1'},
]})
req(merged['canonical_fields']['errors.404']['value']=='NO_DATA','additional off-question fact lost')
req(merged['canonical_fields']['refresh']['resolution_status']=='UNKNOWN_CONFIRMED','explicit unknown not preserved structurally')
req(merged['facts_merged']==3,'all relevant facts must be merged')

# Ambiguous contradiction becomes conflict; explicit correction supersedes.
conf=run_op('merge_incremental_analyst_facts',{'canonical_fields':{'jurisdiction':{'value':'UA','resolution_status':'KNOWN','field_class':'SUBSTANTIVE_REQUIRED','provenance_type':'analyst'}},'incoming_facts':[{'field_id':'jurisdiction','value':'EU','resolution_status':'KNOWN','provenance_type':'analyst'}]})
req(conf['conflicts'] and conf['canonical_fields']['jurisdiction']['value']=='UA','ambiguous contradiction must not silently overwrite')
corr=run_op('merge_incremental_analyst_facts',{'canonical_fields':{'jurisdiction':{'value':'UA','resolution_status':'KNOWN','field_class':'SUBSTANTIVE_REQUIRED','provenance_type':'analyst'}},'incoming_facts':[{'field_id':'jurisdiction','value':'EU','resolution_status':'KNOWN','provenance_type':'correction','explicit_correction':True,'statement_id':'s2'}]})
req(corr['canonical_fields']['jurisdiction']['value']=='EU','explicit correction must supersede')
req(corr['canonical_fields']['jurisdiction'].get('supersedes'),'correction provenance missing')

scan=run_op('interactive_completeness_scan',{'canonical_fields':merged['canonical_fields']})
req(scan['status']=='BLOCK','remaining UNASKED substantive field must block compose')
req('refresh' not in scan['unasked_substantive_fields'],'UNKNOWN_CONFIRMED must not be treated as unasked')
ready_fields=merged['canonical_fields']; ready_fields['source.endpoint']['resolution_status']='KNOWN'; ready_fields['errors.404']['resolution_status']='KNOWN';
# refresh is explicit unknown; close the deliberately unasked jurisdiction too.
ready_fields['jurisdiction']={'value':'UA','resolution_status':'KNOWN','field_class':'SUBSTANTIVE_REQUIRED','provenance_type':'analyst'}
scan2=run_op('interactive_completeness_scan',{'canonical_fields':ready_fields})
req(scan2['status']=='READY_TO_COMPOSE','KNOWN/UNKNOWN_CONFIRMED substantive fields should be composable')

# Text token UNKNOWN is data, not lifecycle state.
kw=run_op('merge_incremental_analyst_facts',{'canonical_fields':{},'incoming_facts':[{'field_id':'unknown_raw_status_rule','value':'unknown raw status -> explicit uncertain runtime state','resolution_status':'KNOWN','field_class':'SUBSTANTIVE_REQUIRED','provenance_type':'analyst'}]})
req(kw['canonical_fields']['unknown_raw_status_rule']['resolution_status']=='KNOWN','keyword UNKNOWN must not change structural status')

# Chunking/order invariance for non-conflicting facts.
facts=[{'field_id':'a','value':1,'resolution_status':'KNOWN','field_class':'SUBSTANTIVE_REQUIRED','provenance_type':'analyst'},{'field_id':'b','value':2,'resolution_status':'KNOWN','field_class':'SUBSTANTIVE_REQUIRED','provenance_type':'analyst'}]
one=run_op('merge_incremental_analyst_facts',{'canonical_fields':{},'incoming_facts':facts})['canonical_fields']
part1=run_op('merge_incremental_analyst_facts',{'canonical_fields':{},'incoming_facts':[facts[1]]})['canonical_fields']
part2=run_op('merge_incremental_analyst_facts',{'canonical_fields':part1,'incoming_facts':[facts[0]]})['canonical_fields']
req(one==part2,'chunking/input order should not change canonical state for the same non-conflicting truth set')

# Laws must make the semantics canonical.
prog=yaml.safe_load((ROOT/'source/program.ordo.yaml').read_text()) or {}
laws={x.get('id'):x.get('text','') for x in ((prog.get('playbook_laws') or {}).get('laws') or []) if isinstance(x,dict)}
for lid in ['E66_INCREMENTAL_ANALYST_FACT_STREAM','E67_STRUCTURAL_FIELD_RESOLUTION_STATUS','E68_INTERACTIVE_COMPLETENESS_AND_CANONICAL_SYNC','E69_ANALYST_INTERACTION_ROBUSTNESS']:
    req(lid in laws,f'missing canonical law {lid}')

print('ALPHA42 INTERACTIVE ANALYST WORKFLOW: PASS')
