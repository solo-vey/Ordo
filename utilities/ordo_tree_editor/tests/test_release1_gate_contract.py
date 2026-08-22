from __future__ import annotations
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('editor_service_r1', ROOT/'editor_service.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def elem(ids):
    return {'output_contract':{'contract':'GateFailureOrPass','declared_check_ids':ids},'gate_contract':{'checks_inline':[{'id':x} for x in ids]}}

def result(ids,status='passed'):
    return {'status':status,'check_results':[{'check_id':x,'status':'pass','evidence':['ok'],'remediation':None,'not_run_reason':None} for x in ids]}

def test_full_per_check_pass():
    ids=['C1','C2','C3']; errors, accounting=mod._validate_gate_check_results(result(ids),elem(ids))
    assert errors==[]
    assert accounting['execution_status']=='evaluated'
    assert accounting['executed_check_ids']==ids

def test_missing_unknown_duplicate_fail():
    ids=['C1','C2']
    r=result(ids); r['check_results']=r['check_results'][:1]
    assert mod._validate_gate_check_results(r,elem(ids))[0]
    r=result(ids); r['check_results'][1]['check_id']='X'
    assert mod._validate_gate_check_results(r,elem(ids))[0]
    r=result(ids); r['check_results'][1]['check_id']='C1'
    assert mod._validate_gate_check_results(r,elem(ids))[0]

def test_pass_with_not_run_fails():
    ids=['C1','C2']; r=result(ids); r['check_results'][1]['status']='not_run'; r['check_results'][1]['not_run_reason']='context missing'
    errs,_=mod._validate_gate_check_results(r,elem(ids)); assert errs

def test_no_declared_checks_requires_explicit_empty():
    r={'status':'passed','check_results':[]}; errs,a=mod._validate_gate_check_results(r,elem([]))
    assert errs==[] and a['per_check_accounting']=='not_applicable'
    r['check_results']=[{'check_id':'X','status':'pass','evidence':[],'remediation':None,'not_run_reason':None}]
    assert mod._validate_gate_check_results(r,elem([]))[0]

def test_evidence_bounds():
    r=result(['C1']); r['check_results'][0]['evidence']=['a','b','c']
    assert mod._validate_gate_check_results(r,elem(['C1']))[0]
    r=result(['C1']); r['check_results'][0]['evidence']=['x'*321]
    assert mod._validate_gate_check_results(r,elem(['C1']))[0]
