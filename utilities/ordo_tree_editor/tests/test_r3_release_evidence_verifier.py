from utilities.ordo_tree_editor.verify_release_evidence_v3 import verify


def base():
    return {
      'evidence_profile':'live','provenance':{'live_calls':2,'replayed_calls':0},
      'usage':{'calls':3},
      'accounting':{'provider_attempts':3,'token_baseline_attempts':3},
      'retry_quality':{'retry_histogram':{'1':1,'2':1},'acceptance_pass':True,'exhausted_retry_budget':0},
      'provider_capability_profile':{'status':'recorded','supports_json_schema':False},
      'run':{'status':'completed','outcome':{'reason':'terminal','nodeId':'END'},'llm_calls':2,
             'step_class_counts':{'live_model_call':2},
             'run_journal':{'artifact_freshness':[{'freshness_status':'fresh'}]}}
    }


def test_passes_canonical_evidence():
    out=verify(base(),{'missing_test_coverage':[]},'END')
    assert out['status']=='PASS', out


def test_fails_accounting_drift():
    x=base(); x['usage']['calls']=2
    out=verify(x,{'missing_test_coverage':[]},'END')
    assert out['status']=='FAIL'
    assert any(c['id']=='TOKEN_BASELINE_CALL_ACCOUNTING' and c['status']=='FAIL' for c in out['checks'])


def test_fails_without_probe():
    x=base(); x.pop('provider_capability_profile')
    out=verify(x,{'missing_test_coverage':[]},'END')
    assert out['status']=='FAIL'
