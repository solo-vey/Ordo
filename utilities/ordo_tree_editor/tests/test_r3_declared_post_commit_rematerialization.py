import json
from utilities.ordo_tree_editor import editor_service as es


def test_model_node_declared_rematerialization_uses_post_commit_state(monkeypatch):
    pkg={
        'id':'pkg-r3-remat',
        'source':{
            'nodes':[{
                'id':'N_APPROVE',
                'action':'AI.UPDATE',
                'update_state':{'doc.status':'approved'},
                'rematerialization':{'template':'t.md','bindings':'b.yaml','output':'generated/out.md'},
                'next':'END',
            }],
            'gates':[],
            'terminals':[{'id':'END'}],
        },
        'resources':{
            't.md':'Status: {{ status }}\n',
            'b.yaml':'bindings:\n  status: state.doc.status\n',
        },
    }
    pkg_token=es._ACTIVE_PLAYBOOK_PACKAGE.set(pkg)
    run_token=es._ACTIVE_RUN_CONTEXT.set({'package_id':'pkg-r3-remat','session_id':'s','run_id':'r'})
    try:
        monkeypatch.setattr(es,'_live_credentials',lambda payload:{
            'provider':'custom','base_url':'x','api_style':'chat_completions','model':'m','api_key':'k','structured_output_mode':'json_object'
        })
        monkeypatch.setattr(es,'_provider_api_call',lambda *args,**kwargs:(
            {'messages':[]},{},json.dumps({
                'assistant_message':'ok','route_key':'next','state_updates':{'doc':{'status':'approved'}},
                'rationale_short':'','await_analyst':False,
            }),{'input_tokens':1,'output_tokens':1,'total_tokens':2}
        ))
        result=es._call_openai_live_impl({
            'source':pkg['source'],'state':{'doc':{'status':'draft'}},'state_revision':1,
            'current_id':'N_APPROVE','phase':'enter','session_id':'s','run_id':'r',
        })
        artifact=result['debug']['runtime']['artifact']
        assert result['state_revision']==2
        assert artifact['materialized_from_revision']==2
        assert artifact['producer_node']=='N_APPROVE'
        assert artifact['rematerialized_post_commit'] is True
        assert (es._runtime_workspace()/'generated/out.md').read_text(encoding='utf-8')=='Status: approved\n'
    finally:
        es._ACTIVE_RUN_CONTEXT.reset(run_token)
        es._ACTIVE_PLAYBOOK_PACKAGE.reset(pkg_token)
