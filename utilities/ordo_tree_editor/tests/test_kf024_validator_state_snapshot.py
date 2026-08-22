import json
from pathlib import Path
import editor_service as es


def test_deterministic_validator_receives_runtime_state_snapshot(tmp_path, monkeypatch):
    monkeypatch.setattr(es, "_runtime_workspace", lambda: tmp_path)
    validator = '''#!/usr/bin/env python3
import argparse, json
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('artifact'); p.add_argument('--state'); p.add_argument('--report')
a=p.parse_args()
state=json.loads(Path(a.state).read_text())
payload={'status':'PASS' if state.get('sentinel')==42 else 'FAIL','checks':[]}
print(json.dumps(payload))
if a.report: Path(a.report).parent.mkdir(parents=True, exist_ok=True); Path(a.report).write_text(json.dumps(payload))
raise SystemExit(0 if payload['status']=='PASS' else 1)
'''
    es.PLAYBOOK_PACKAGE.clear()
    es.PLAYBOOK_PACKAGE.update({'source':{}, 'resources':{'validators/v.py':validator}})
    record={
        'id':'G_STATE_AWARE',
        'validator':'validators/v.py',
        'command':'python validators/v.py artifact.md --state runtime_state.json --report reports/v.json',
    }
    (tmp_path/'artifact.md').write_text('x')
    status, reason, extra = es._deterministic_gate_decision(record, {'sentinel':42})
    assert status == 'pass', reason
    assert json.loads((tmp_path/'runtime_state.json').read_text())['sentinel'] == 42
