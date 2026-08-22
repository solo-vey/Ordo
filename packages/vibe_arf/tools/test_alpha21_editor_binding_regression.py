#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import importlib.util,json,hashlib
R=Path(__file__).resolve().parents[1]
results=[]; failures=[]
def check(name,fn):
    try: fn(); results.append({'id':name,'status':'PASS'})
    except Exception as e: failures.append({'id':name,'error':f'{type(e).__name__}: {e}'}); results.append({'id':name,'status':'FAIL','error':f'{type(e).__name__}: {e}'})
def load_tool(filename,modname):
    p=R/'tools'/filename; spec=importlib.util.spec_from_file_location(modname,p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def exact_binding():
    d=json.loads((R/'source/editor-runtime-compatibility-contract.json').read_text())
    b=d.get('editor_binding') or {}
    assert b.get('mode')=='exact_editor_dev_adapter_binding',b
    assert b.get('latest_editor_version')=='alpha.20.0.188-dev R3',b
    assert b.get('binding_status')=='VERIFIED_RELEASE_HARDENING_EDITOR_0188',b
    assert b.get('editor_source_zip_sha256')=='572150b0acebf46770ca0246e974169f56b9187016055d90c579cbe69d642ca2',b

def package_tool_classification():
    m=load_tool('verify_generated_playbook_contract.py','gp21_owner')
    node={'id':'N_TOOL','question':'Execute deterministic helper and return structured evidence.','answer_type':'structured_record','node_context':{'allowed_tools':['tools/check.py']},'purpose':'Deterministic package tool. Execute exactly: python tools/check.py --input runtime/input.json','on_answer':{'update_state':{'evidence':'$answer.evidence'},'next':'G_DONE'}}
    assert m._owner(node)=='deterministic',m._owner(node)

def binding_evidence():
    d=json.loads((R/'source/editor-binding-evidence.json').read_text())
    assert d.get('status')=='PASS',d
    ed=d.get('editor') or {}
    assert ed.get('release')=='alpha.20.0.188-dev R3'
    assert ed.get('source_kind')=='release_hardening_editor_from_user_supplied_0187'
    req=((d.get('probes') or {}).get('required_state_writes_targeted_regression') or {})
    assert req.get('status')=='PASS' and req.get('tests_passed')==10 and req.get('tests_failed')==0,req
    pre=((d.get('probes') or {}).get('native_headless_preflight') or {})
    assert pre.get('status')=='PASS',pre
    sim=((d.get('probes') or {}).get('terminal_simulation_kit_016') or {})
    assert sim.get('status')=='PASS' and sim.get('steps')==199 and sim.get('errors')==0,sim

def free_text_fix():
    d=json.loads((R/'source/editor-runtime-compatibility-contract.json').read_text())
    rule=next(x for x in d.get('rules',[]) if x.get('id')=='FREE_TEXT_ROUTE_SURFACE_REGRESSION')
    assert rule.get('classification')=='EDITOR_REGRESSION',rule

def headless_replay():
    d=json.loads((R/'source/editor-binding-evidence.json').read_text())
    sim=((d.get('probes') or {}).get('terminal_simulation_kit_016') or {})
    assert sim.get('status')=='PASS',sim
    assert sim.get('steps')==199 and sim.get('errors')==0,sim
    assert sim.get('final_node')=='END_PLAYBOOK_PACKAGE_ACCEPTED',sim

def immutable_evidence():
    d=json.loads((R/'PORTABLE_PACKAGE_MANIFEST.json').read_text())
    rows={x.get('path'):x for x in d.get('immutable_files',[])}
    for rel in ['source/editor-binding-evidence.json','tools/test_alpha21_editor_binding_regression.py']:
        assert rel in rows,rel
        p=R/rel; b=p.read_bytes(); row=rows[rel]
        assert row.get('sha256')==hashlib.sha256(b).hexdigest() and row.get('bytes')==len(b),rel

for name,fn in [('R25_EXACT_EDITOR_BINDING',exact_binding),('R26_EDITOR_PACKAGE_TOOL_CLASSIFICATION',package_tool_classification),('R27_EDITOR_BINDING_EVIDENCE',binding_evidence),('R28_FREE_TEXT_EDITOR_FIX_CLASSIFIED',free_text_fix),('R29_HEADLESS_RECORDED_LIVE_REPLAY',headless_replay),('R30_EDITOR_BINDING_EVIDENCE_IMMUTABLE',immutable_evidence)]: check(name,fn)
status='PASS' if not failures else 'FAIL'
print(json.dumps({'status':status,'tests_total':len(results),'passed':sum(x['status']=='PASS' for x in results),'failed':sum(x['status']=='FAIL' for x in results),'results':results},ensure_ascii=False,indent=2))
raise SystemExit(0 if status=='PASS' else 1)
