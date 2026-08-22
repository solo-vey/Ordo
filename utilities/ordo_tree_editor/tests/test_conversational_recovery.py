import json, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT))
import editor_service as es

oldcred, oldcall = es._live_credentials, es._provider_api_call
try:
    es._live_credentials=lambda payload:{'provider':'custom','base_url':'http://local/v1','api_style':'chat_completions','model':'m','api_key':''}
    def fake_call(credentials, system_text, context):
        obj={
            'assistant_message':'Бракує уточнення у functional_test_catalog. Можете надати його тут або перейти до вузла тестів.',
            'suggested_action':'stay',
            'recommended_recovery_target':None,
            'state_patch':{'base_revision':0,'operations':[{
                'op':'append','path':'functional_test_catalog.rows','value':{'tc_id':'FT-X'},
                'basis':'analyst_input','reason':'Analyst supplied corrected recovery data'
            }]},
            'rationale_short':'Recovery conversation stays on the same node.'
        }
        return ({}, {}, json.dumps(obj, ensure_ascii=False), {'input_tokens':1,'output_tokens':1,'total_tokens':2,'cached_tokens':0,'reasoning_tokens':0})
    es._provider_api_call=fake_call
    out=es._recovery_conversation({
        'evidence':{'gate_id':'G_X','affected_state':['functional_test_catalog']},
        'choices':[{'target':'N_GENERATE_FUNCTIONAL_TESTS','label':'Tests'}],
        'state':{'functional_test_catalog':{'rows':[]},'risk_factor_identity':{'alias':'X'}},
        'analyst_input':'додай цей тест'
    })
    assert out['state_patch_commit']['committed'] is True, out
    assert out['state']['functional_test_catalog']['rows']==[{'tc_id':'FT-X'}], out
    assert out['state']['risk_factor_identity']['alias']=='X', out

    def bad_call(credentials, system_text, context):
        obj={'assistant_message':'x','suggested_action':'stay','recommended_recovery_target':None,
             'state_patch':{'base_revision':0,'operations':[{'op':'set','path':'risk_factor_identity.alias','value':'BAD','basis':'recovery','reason':'bad'}]},'rationale_short':''}
        return ({}, {}, json.dumps(obj), {'input_tokens':1,'output_tokens':1,'total_tokens':2,'cached_tokens':0,'reasoning_tokens':0})
    es._provider_api_call=bad_call
    out=es._recovery_conversation({'evidence':{'gate_id':'G_X','affected_state':['functional_test_catalog']},'choices':[],'state':{'functional_test_catalog':{'rows':[]},'risk_factor_identity':{'alias':'X'}},'analyst_input':'x'})
    assert out['state_patch_commit']['committed'] is False, out
    assert out['state']['risk_factor_identity']['alias']=='X', out
finally:
    es._live_credentials, es._provider_api_call = oldcred, oldcall
print('CONVERSATIONAL RECOVERY REGRESSION: PASS')
