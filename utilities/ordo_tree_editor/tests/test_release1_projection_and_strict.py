from __future__ import annotations
import pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import editor_service as es


def test_projection_defaults_are_projection_only():
    elem={
      'kind':'model_gate','semantic_source':{},'routes':[],
      'execution_traits':{},
      'state_contract':{
        'semantic_objects':['open_questions','business_meaning'],
        'reads_hint':[],
        'projection_defaults':{'enter':{'open_questions':[]}}
      },
      'output_contract':{}
    }
    state={'business_meaning':{'definition':'x'}}
    system,ctx,meta=es._assemble_runtime_semantic_call(elem,'G','enter',state,[], '')
    assert meta['context_complete'] is True
    assert meta['default_materialized']==['open_questions']
    assert ctx['runtime_state']['open_questions']==[]
    assert ctx['runtime_state']['__context_status__']['default_materialized']==['open_questions']
    assert 'open_questions' not in state


def test_missing_produced_state_is_typed():
    elem={'kind':'model_gate','semantic_source':{},'routes':[],'execution_traits':{},'state_contract':{'semantic_objects':['needed'],'reads_hint':[]},'output_contract':{}}
    _,ctx,meta=es._assemble_runtime_semantic_call(elem,'G','enter',{},[], '')
    assert meta['context_complete'] is False
    assert meta['missing_produced_state']==['needed']
    assert 'missing_preload' not in ctx['runtime_state']['__context_status__']


def test_runtime_strict_compatibility_profile():
    good={'type':'object','additionalProperties':False,'required':['x'],'properties':{'x':{'type':'string'}}}
    bad={'type':'object','additionalProperties':False,'required':[],'properties':{'x':{'type':'string'}}}
    custom={'provider':'custom','api_style':'chat_completions'}
    openai={'provider':'openai','api_style':'chat_completions'}
    assert es._runtime_strict_schema_compatible(good,custom)[0] is False
    assert es._runtime_strict_schema_compatible(good,openai)[0] is True
    assert es._runtime_strict_schema_compatible(bad,openai)[0] is False

def test_contract_unsatisfiable_is_typed_stop(monkeypatch):
    source={'nodes':[{'id':'N_OK','terminal':True}], 'gates':[{'id':'G','method':'model','trust_class':'model_judgment','condition':'x','on_pass':'N_OK','on_fail':'N_OK'}], 'graph_contract':{'entry_node':'G'}}
    semantic={'elements':{'G':{'id':'G','kind':'model_gate','semantic_source':{'condition':'x'},'state_contract':{'reads_hint':[],'semantic_objects':[],'writes':[],'patch_template':[]},'routes':[{'key':'on_pass','target':'N_OK'},{'key':'on_fail','target':'N_OK'}],'execution_traits':{'requires_analyst':False,'model_executed':True,'model_executed_phases':['enter']},'output_contract':{'contract':'GateFailureOrPass','declared_check_ids':['C1'],'json_schema':{'type':'object'}}}}}
    old_pkg=dict(es.PLAYBOOK_PACKAGE); old_runtime=dict(es.LIVE_RUNTIME)
    try:
        es.PLAYBOOK_PACKAGE.update({'id':'x','source':source,'semantic_plan':semantic,'semantic_plan_status':{'valid':True}})
        es.LIVE_RUNTIME.update({'provider':'custom','model':'m','base_url':'http://x','api_key':''})
        monkeypatch.setattr(es,'_provider_api_call',lambda *a,**k: ({},{},'{"foo":1}',{'input_tokens':1,'output_tokens':1,'total_tokens':2,'cached_tokens':0,'reasoning_tokens':0}))
        r=es._call_openai_live({'package_id':'x','source':source,'state':{},'history':[],'current_id':'G','phase':'enter'})
        assert r['run_status']=='halted'
        assert r['completion_reason']=='contract_unsatisfiable_by_model'
        assert r['failure_class']=='contract_unsatisfiable_by_model'
    finally:
        es.PLAYBOOK_PACKAGE.clear(); es.PLAYBOOK_PACKAGE.update(old_pkg)
        es.LIVE_RUNTIME.clear(); es.LIVE_RUNTIME.update(old_runtime)
