#!/usr/bin/env python3
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
results=[]; failures=[]
def check(i,fn):
    try:
        fn(); results.append({'id':i,'status':'PASS'})
    except Exception as e:
        failures.append((i,str(e))); results.append({'id':i,'status':'FAIL','error':str(e)})

def contract_has_only_adapter_authority():
    d=json.loads((R/'source/editor-runtime-compatibility-contract.json').read_text())
    forbidden={'MODEL_WRITE_ENFORCEMENT','HUMAN_RESPONSE_DIRECTNESS','RUN_EVIDENCE_GATE','FREE_TEXT_RETRY_PROGRESS','GRAPH_CLOSURE'}
    ids={x['id'] for x in d['rules']}
    assert not (ids & forbidden), sorted(ids & forbidden)
    assert all('VIBE_BLOCKING' not in str(x.get('classification','')) for x in d['rules'])

def structured_answers_not_prohibited():
    txt=(R/'source/editor-runtime-compatibility-contract.json').read_text().lower()
    assert 'structured $answer.<field> semantic selectors are prohibited' not in txt
    assert 'structured answer selectors are prohibited' not in txt

def retry_workaround_not_in_editor_contract():
    txt=(R/'source/editor-runtime-compatibility-contract.json').read_text().lower()
    assert 'free_text_retry_progress' not in txt
    auto=json.loads((R/'source/auto-answers-authoring-profile.json').read_text())
    assert 'RETRY_SCENARIO_PROGRESS' in {x['id'] for x in auto['rules']}

def fixed_editor_is_external_verified_binding():
    d=json.loads((R/'source/editor-binding-evidence.json').read_text())
    ed=d['editor']
    assert ed['release']=='alpha.20.0.188-dev R3'
    assert ed.get('source_kind')=='release_hardening_editor_from_user_supplied_0187'
    assert 'local_delta_chain' not in ed
    assert d['probes']['terminal_simulation_kit_016']['steps']==199
    assert d['probes']['terminal_simulation_kit_016']['errors']==0
    assert d['probes']['required_state_writes_targeted_regression']['tests_passed']==10
    assert d['probes']['required_state_writes_targeted_regression']['tests_failed']==0

def contract_provenance_no_local_patch_claim():
    d=json.loads((R/'source/editor-runtime-compatibility-contract.json').read_text())
    s=json.dumps(d,ensure_ascii=False).lower()
    assert 'user-supplied 0.151-dev plus' not in s
    assert d['editor_binding']['binding_status']=='VERIFIED_RELEASE_HARDENING_EDITOR_0188'

def semantic_authority_still_language():
    d=json.loads((R/'source/editor-runtime-compatibility-contract.json').read_text())
    assert d['semantic_authority'] is False
    assert d['semantic_source_of_truth']=='canonical_support/language'
    p=json.loads((R/'source/runtime-adapter-compatibility-policy.json').read_text())
    assert p['semantic_source_of_truth']=='canonical_ordo_language'

for i,f in [
 ('R39_EDITOR_CONTRACT_ONLY_ADAPTER_AUTHORITY',contract_has_only_adapter_authority),
 ('R40_STRUCTURED_ANSWERS_NOT_PROHIBITED_BY_EDITOR_BINDING',structured_answers_not_prohibited),
 ('R41_RETRY_WORKAROUND_OWNED_BY_AUTO_ANSWERS',retry_workaround_not_in_editor_contract),
 ('R42_USER_SUPPLIED_0153_BINDING_EVIDENCE',fixed_editor_is_external_verified_binding),
 ('R43_NO_LOCAL_PATCH_PROVENANCE_IN_BINDING',contract_provenance_no_local_patch_claim),
 ('R44_LANGUAGE_REMAINS_SEMANTIC_AUTHORITY',semantic_authority_still_language),
]: check(i,f)
print(json.dumps({'status':'FAIL' if failures else 'PASS','tests_total':len(results),'passed':sum(x['status']=='PASS' for x in results),'failed':len(failures),'results':results},ensure_ascii=False,indent=2))
raise SystemExit(1 if failures else 0)
