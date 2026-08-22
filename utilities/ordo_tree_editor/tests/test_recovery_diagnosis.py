import json, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT))
import editor_service as es


def run_case(raw_obj, expected_status, expected_target):
    oldcred, oldcall = es._live_credentials, es._provider_api_call
    try:
        es._live_credentials=lambda payload:{'provider':'custom','base_url':'http://local/v1','api_style':'chat_completions','model':'m','api_key':''}
        es._provider_api_call=lambda credentials, system_text, context: ({}, {}, json.dumps(raw_obj), {'input_tokens':1,'output_tokens':1,'total_tokens':2,'cached_tokens':0,'reasoning_tokens':0})
        out=es._recovery_diagnosis({'evidence':{'gate_id':'G_X','explanation':'PM evidence unavailable'},'choices':[{'target':'N_A','label':'A'}]})
        d=out['diagnosis']
        assert d['diagnosis_status']==expected_status, d
        assert d['recommended_recovery_target']==expected_target, d
    finally:
        es._live_credentials, es._provider_api_call = oldcred, oldcall

run_case({
 'diagnosis_status':'insufficient_evidence','summary':'Cannot identify a failed PM check','failed_checks':[],
 'missing_evidence':['PM-001..PM-010 results'],'likely_affected_state':[],
 'recommended_recovery_target':'N_NOT_ALLOWED','recommendation_confidence':'high','analyst_explanation':'Evidence is missing.'
}, 'insufficient_evidence', None)
run_case({
 'diagnosis_status':'identified','summary':'Known issue','failed_checks':['PM-003'],'missing_evidence':[],
 'likely_affected_state':['trigger_logic'],'recommended_recovery_target':'N_A','recommendation_confidence':'high','analyst_explanation':'Fix A.'
}, 'identified', 'N_A')
print('RECOVERY DIAGNOSIS REGRESSION: PASS')
