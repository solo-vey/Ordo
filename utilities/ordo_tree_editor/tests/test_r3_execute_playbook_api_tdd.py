from __future__ import annotations
import json
from pathlib import Path
import sys
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parents[1]))
from utilities.ordo_tree_editor import editor_service as svc
from utilities.ordo_tree_editor.api_reference import build_spec

REQUIRED={
 ('post','/api/execute-run-start'),
 ('post','/api/execute-run-step'),
 ('post','/api/execute-run-advance'),
 ('post','/api/execute-run-input'),
 ('post','/api/execute-run-stop'),
 ('get','/api/execute-run-status'),
 ('get','/api/execute-run-debug'),
}

def test_execute_api_is_documented_and_guide_exists():
    spec=build_spec()
    routes={(m,p) for p,item in spec['paths'].items() for m in item if m in {'get','post'}}
    assert REQUIRED <= routes
    guide=ROOT/'web'/'api-docs'/'execute-playbook.html'
    text=guide.read_text(encoding='utf-8')
    for _,path in REQUIRED:
        assert path in text
    assert 'Auto Answers' in text and 'debug' in text.lower()


def test_replay_registration_produces_reusable_auto_answers_id(monkeypatch):
    replay={"steps":[{"id":"N_HUMAN","interactions":[{"analyst_response":"yes"}]}]}
    monkeypatch.setattr(svc,'parse_replay_package',lambda filename,raw: replay)
    result=svc._register_replay_package('answers.zip',b'abc')
    assert result['replay_id']
    stored=svc.REPLAY_PACKAGES[result['replay_id']]
    assert stored['answers_by_node']=={'N_HUMAN':['yes']}


def test_managed_run_uses_same_live_step_and_captures_state_transcript_debug(monkeypatch):
    package_id='pkg-test'
    svc.PLAYBOOK_PACKAGES[package_id]={
      'id':package_id,
      'source':{'graph_contract':{'entry_node':'N_START'},'nodes':[{'id':'N_START'},{'id':'N_HUMAN'},{'id':'N_DONE','terminal':True}]},
    }
    calls=[]
    def fake_step(payload):
        calls.append((payload['current_id'],payload.get('phase'),payload.get('analyst_input','')))
        if payload['current_id']=='N_START':
            return {'state':{'x':1},'state_revision':1,'assistant_message':'started','await_analyst':False,'next_id':'N_HUMAN','route_key':'next','run_status':'running','completion_reason':None,'debug':{'runtime':{'marker':'a'}},'llm_call_skipped':True}
        if payload['current_id']=='N_HUMAN' and payload.get('phase')=='enter':
            return {'state':payload['state'],'state_revision':1,'assistant_message':'question','await_analyst':True,'next_id':None,'route_key':None,'run_status':'running','completion_reason':None,'debug':{'runtime':{'marker':'b'}},'llm_call_skipped':True}
        if payload['current_id']=='N_HUMAN' and payload.get('phase')=='respond':
            return {'state':{'x':1,'answer':'yes'},'state_revision':2,'assistant_message':'accepted','await_analyst':False,'next_id':'N_DONE','route_key':'next','run_status':'running','completion_reason':None,'debug':{'runtime':{'marker':'c'}},'llm_call_skipped':True}
        raise AssertionError(payload)
    monkeypatch.setattr(svc,'_execute_live_step_with_revision',fake_step)
    replay_id='replay-test'
    svc.REPLAY_PACKAGES[replay_id]={'replay_id':replay_id,'answers_by_node':{'N_HUMAN':['yes']},'filename':'a.zip','replay':{}}
    run=svc._managed_execute_run_start({'package_id':package_id,'session_id':'s','auto_answers_replay_id':replay_id})
    out=svc._managed_execute_run_advance(run['run_id'],max_steps=10)
    assert out['outcome']['status']=='completed'
    assert out['state']=={'x':1,'answer':'yes'}
    assert calls==[('N_START','enter',''),('N_HUMAN','enter',''),('N_HUMAN','respond','yes')]
    debug=svc._managed_execute_run_debug(run['run_id'])
    assert len(debug['debug_trace'])==3
    assert any(x.get('role')=='analyst' and x.get('text')=='yes' for x in debug['transcript'])


def test_managed_run_error_snapshot_is_fail_closed(monkeypatch):
    package_id='pkg-error'
    svc.PLAYBOOK_PACKAGES[package_id]={'id':package_id,'source':{'graph_contract':{'entry_node':'N_START'},'nodes':[{'id':'N_START'}]}}
    monkeypatch.setattr(svc,'_execute_live_step_with_revision',lambda payload: (_ for _ in ()).throw(RuntimeError('boom')))
    run=svc._managed_execute_run_start({'package_id':package_id,'session_id':'s'})
    result=svc._managed_execute_run_step(run['run_id'])
    assert result['outcome']['status']=='error'
    dbg=svc._managed_execute_run_debug(run['run_id'])
    assert dbg['error']['message']=='boom'
    assert dbg['state']=={}
    assert dbg['current_id']=='N_START'
    assert 'traceback' in dbg['error']
