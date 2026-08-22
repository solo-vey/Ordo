import json
from types import SimpleNamespace
import editor_service as es


def test_deterministic_validator_exposes_recovery_metadata(monkeypatch, tmp_path):
    monkeypatch.setattr(es, '_runtime_workspace', lambda: tmp_path)
    monkeypatch.setattr(es, '_package_resource_text', lambda ref: (ref, '# fake validator'))
    payload={
        'status':'FAIL',
        'checks':[{'id':'POST-R2-CROSS-STATE','status':'FAIL','message':'UT mismatch'}],
        'affected_state':['unit_test_catalog'],
        'recommended_recovery_target':'N_GENERATE_UNIT_TESTS',
    }
    def fake_run(argv, cwd, text, capture_output, timeout):
        report=tmp_path/'reports'/'post.json'; report.parent.mkdir(parents=True,exist_ok=True)
        report.write_text(json.dumps(payload),encoding='utf-8')
        return SimpleNamespace(returncode=1, stdout=json.dumps(payload), stderr='')
    monkeypatch.setattr(es.subprocess, 'run', fake_run)
    record={
        'id':'G_PASSPORT_POST_MATERIALIZATION_PYTHON',
        'validator':'validators/validate_risk_factor_passport.py',
        'command':'python validators/validate_risk_factor_passport.py generated_outputs/RISK_FACTOR_PASSPORT.md --report reports/post.json',
    }
    result, reason, extra=es._deterministic_gate_decision(record,{})
    assert result=='fail'
    assert extra['affected_state']==['unit_test_catalog']
    assert extra['recommended_recovery_target']=='N_GENERATE_UNIT_TESTS'
    assert extra['validator_failed_checks'][0]['check_id']=='POST-R2-CROSS-STATE'
