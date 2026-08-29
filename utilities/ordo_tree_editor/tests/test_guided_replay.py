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

def test_parse_legacy_debug_json_is_rejected():
    debug={'run':{'path':['N_A'],'history':[],'outcome':{'nodeId':'N_A'}},'calls':[{'current_id':'N_A','phase':'enter','runtime':{},'output':{'parsed_result':{}}}]}
    try:
        es.parse_replay_package('debug-run-summary.json', json.dumps(debug).encode())
    except ValueError as error:
        assert 'canonical debug handoff ZIP' in str(error)
    else:
        raise AssertionError('legacy replay JSON must be rejected')
