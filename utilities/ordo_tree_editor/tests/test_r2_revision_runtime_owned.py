import editor_service as es

def test_model_base_revision_is_runtime_owned(monkeypatch):
    source={
      'nodes':[{'id':'N','action':'AI.X','update_state':{'x':'$generated.x'},'next':'T'},{'id':'T','terminal':True}],
      'gates':[], 'graph_contract':{'entry_node':'N'}
    }
    semantic={'elements':{
      'N':{'id':'N','kind':'model_node','semantic_source':{'action':'AI.X'},
           'state_contract':{'reads_hint':[],'declared_inputs_by_class':{'state':[]},'semantic_objects':[],'writes':['x'],'patch_template':[]},
           'routes':[{'key':'next','target':'T'}],
           'execution_traits':{'requires_analyst':False,'model_executed':True,'model_executed_phases':['enter']},
           'output_contract':{'contract':'NodeExecutionResult','state_patch':{'value_schema_by_path':{'x':{'type':['string','null']}},'operation_variants':[]},'json_schema':{'type':'object'}}},
      'T':{'id':'T','kind':'terminal','semantic_source':{'terminal':True},'state_contract':{'reads_hint':[],'declared_inputs_by_class':{'state':[]},'semantic_objects':[],'writes':[],'patch_template':[]},'routes':[],'execution_traits':{'requires_analyst':False,'model_executed':False,'runtime_executor':'terminal'}}
    }}
    old_pkg=dict(es.PLAYBOOK_PACKAGE); old_runtime=dict(es.LIVE_RUNTIME)
    try:
        es.PLAYBOOK_PACKAGE.update({'id':'r2','source':source,'semantic_plan':semantic,'semantic_plan_status':{'valid':True}})
        es.LIVE_RUNTIME.update({'provider':'custom','model':'m','base_url':'http://x','api_key':''})
        raw='''{"assistant_message":"ok","route_key":"next","needs_analyst":false,"next_intent":"done","rationale_short":"ok","action":null,"state_patch":{"base_revision":0,"operations":[{"op":"set","path":"x","value":"v","basis":"generated","reason":"test","row_key":null,"row_match":null}]}}'''
        monkeypatch.setattr(es,'_provider_api_call',lambda *a,**k: ({'model':'m'},{'id':'x'},raw,{'input_tokens':1,'output_tokens':1,'total_tokens':2,'cached_tokens':0,'reasoning_tokens':0}))
        r=es._call_openai_live({'package_id':'r2','source':source,'state':{},'state_revision':5,'history':[],'current_id':'N','phase':'enter'})
        assert r['state']['x']=='v'
        assert r['state_revision']==6
        assert r['debug']['alpha20']['state_patch']['base_revision']==5
        assert r['debug']['alpha20']['revision_before']==5
        assert r['debug']['alpha20']['revision_after']==6
    finally:
        es.PLAYBOOK_PACKAGE.clear(); es.PLAYBOOK_PACKAGE.update(old_pkg)
        es.LIVE_RUNTIME.clear(); es.LIVE_RUNTIME.update(old_runtime)
