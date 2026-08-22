import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import editor_service as es

def test_debug_summary_builds_reproduction():
    debug={
      'run':{'path':['N_A','G_B'],'history':[{'role':'analyst','node_id':'N_A','text':'answer'}], 'outcome':{'status':'halted','reason':'x','nodeId':'G_B'}},
      'calls':[{'index':1,'current_id':'N_A','element_kind':'node','phase':'enter','runtime':{'llm_call_skipped':False,'state_before':{},'state_after':{'x':1},'selected_route_key':None,'next_id':None},'output':{'parsed_result':{'assistant_message':'q'}}}]
    }
    r=es.build_debug_reproduction_view(debug)
    assert r['kind']=='debug_reproduction'
    assert r['suggested_checkpoint']=='G_B'
    assert r['answers_by_node']['N_A']==['answer']
    assert r['recorded_calls'][0]['parsed_result']['assistant_message']=='q'

def test_parse_debug_json_as_reproduction():
    debug={'run':{'path':['N_A'],'history':[],'outcome':{'nodeId':'N_A'}},'calls':[{'current_id':'N_A','phase':'enter','runtime':{},'output':{'parsed_result':{}}}]}
    r=es.parse_replay_package('debug-run-summary.json', json.dumps(debug).encode())
    assert r['schema_version']=='ordo.debug_reproduction.v1'
    assert r['total_recorded_calls']==1

def test_parse_replay_adds_provenance_sha_and_recorded_against():
    debug={
      'provider':'custom','base_url':'http://ml03/v1','model':'gemma',
      'run':{'path':['N_A'],'history':[],'outcome':{'nodeId':'N_A'},'run_id':'run-123'},
      'calls':[{'current_id':'N_A','phase':'enter','runtime':{},'output':{'parsed_result':{}}}]
    }
    raw=json.dumps(debug,sort_keys=True).encode()
    r=es.parse_replay_package('debug-run-summary.json', raw)
    assert len(r['source_sha256'])==64
    assert r['source_filename']=='debug-run-summary.json'
    assert r['recorded_against']=={'provider':'custom','base_url':'http://ml03/v1','model':'gemma'}
