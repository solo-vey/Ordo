import json
import editor_service as es


def test_kf021_recovery_commits_catalog_row_corrections(monkeypatch):
    monkeypatch.setattr(es, '_live_credentials', lambda payload:{'provider':'custom','base_url':'http://local/v1','api_style':'chat_completions','model':'m','api_key':''})
    def fake_call(credentials, system_text, context):
        assert 'canonical dotted Ordo paths' in system_text
        assert context['affected_state'] == ['unit_test_catalog']
        obj={
            'assistant_message':'Виправлення застосовано.',
            'suggested_action':'retry_gate',
            'recommended_recovery_target':None,
            'state_patch':{'base_revision':999,'operations':[
                {'op':'merge_row','path':'unit_test_catalog.rows','value':{'expected_result':'Ризик-фактор визначено як відсутній','expected_state':'absent'},'basis':'analyst_input','reason':'null_behavior=absent','row_key':'tc_id','row_match':'UT_003'},
                {'op':'merge_row','path':'unit_test_catalog.rows','value':{'expected_result':'Попередній валідний стан ризик-фактора зберігається','expected_state':'unchanged'},'basis':'analyst_input','reason':'preserve_previous_state','row_key':'tc_id','row_match':'UT_009'},
            ]},
            'rationale_short':'typed correction'
        }
        return ({}, {}, json.dumps(obj, ensure_ascii=False), {'input_tokens':1,'output_tokens':1,'total_tokens':2,'cached_tokens':0,'reasoning_tokens':0})
    monkeypatch.setattr(es, '_provider_api_call', fake_call)
    state={'unit_test_catalog':{'rows':[
        {'tc_id':'UT_003','expected_result':'Стан визначено як відсутність даних','expected_state':'no_data','covers':['null_empty']},
        {'tc_id':'UT_009','expected_result':'Стан визначено як помилка','expected_state':'error','covers':['source_errors']},
    ]}}
    out=es._recovery_conversation({
        'evidence':{'gate_id':'G_PASSPORT_POST_MATERIALIZATION_PYTHON','affected_state':['unit_test_catalog']},
        'choices':[{'target':'N_GENERATE_UNIT_TESTS','label':'Unit tests'}],
        'state':state,
        'state_revision':20,
        'analyst_input':'Виправити UT_003 і UT_009 та повторити gate.'
    })
    assert out['state_patch_commit']['committed'] is True, out
    assert out['state_revision'] == 21, out
    assert out['suggested_action'] == 'retry_gate', out
    rows={x['tc_id']:x for x in out['state']['unit_test_catalog']['rows']}
    assert rows['UT_003']['expected_state']=='absent'
    assert rows['UT_009']['expected_state']=='unchanged'


def test_kf021_never_retries_unchanged_state_after_failed_patch(monkeypatch):
    monkeypatch.setattr(es, '_live_credentials', lambda payload:{'provider':'custom','base_url':'http://local/v1','api_style':'chat_completions','model':'m','api_key':''})
    def fake_call(credentials, system_text, context):
        obj={
            'assistant_message':'Нібито виправлено.',
            'suggested_action':'retry_gate',
            'recommended_recovery_target':None,
            'state_patch':{'base_revision':0,'operations':[
                {'op':'replace','path':'/unit_test_catalog/rows/2','value':{'tc_id':'UT_003','expected_state':'absent'},'basis':'analyst_input','reason':'bad slash path'}
            ]},
            'rationale_short':'bad patch'
        }
        return ({}, {}, json.dumps(obj, ensure_ascii=False), {'input_tokens':1,'output_tokens':1,'total_tokens':2,'cached_tokens':0,'reasoning_tokens':0})
    monkeypatch.setattr(es, '_provider_api_call', fake_call)
    state={'unit_test_catalog':{'rows':[{'tc_id':'UT_003','expected_state':'no_data'}]}}
    out=es._recovery_conversation({
        'evidence':{'gate_id':'G_X','affected_state':['unit_test_catalog']},
        'choices':[{'target':'N_GENERATE_UNIT_TESTS','label':'Unit tests'}],
        'state':state,'state_revision':20,'analyst_input':'fix and retry'})
    assert out['state_patch_commit']['committed'] is False, out
    assert out['suggested_action'] == 'stay', out
    assert out['state_revision'] == 20
    assert out['state'] == state
