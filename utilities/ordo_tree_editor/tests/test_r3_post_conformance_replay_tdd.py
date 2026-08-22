import copy
import json
from pathlib import Path

import headless_runner as hr


def _summary(state_after, selected_route_key='approve'):
    return {
        'calls': [{
            'index': 1,
            'current_id': 'N_REVIEW',
            'phase': 'respond',
            'step_class': 'human_or_auto_answer',
            'runtime': {
                'state_before': {'decision': {'status': 'pending'}},
                'state_after': state_after,
                'revision_before': 0,
                'next_id': 'N_NEXT',
                'await_analyst': False,
                'run_status': 'running',
                'selected_route_key': selected_route_key,
            },
            'input': {'context': {'analyst_input': 'approve'}},
            'output': {},
        }]
    }


def _run(monkeypatch, tmp_path, expected_state, actual_state, actual_route='approve'):
    monkeypatch.setattr(hr, '_load_package', lambda _: {'id': 'pkg', 'source': {'nodes': []}})
    monkeypatch.setattr(hr.es, '_call_openai_live', lambda payload: {
        'state': copy.deepcopy(actual_state),
        'next_id': 'N_NEXT',
        'await_analyst': False,
        'run_status': 'running',
        # Actual live runtime contract exposes the selected route here.
        'route_key': actual_route,
        'debug': {'runtime': {'selected_route_key': actual_route}},
    })
    p = tmp_path / 'summary.json'
    p.write_text(json.dumps(_summary(expected_state)), encoding='utf-8')
    return hr.replay_evidence('dummy.zip', str(p))


def test_replay_ignores_runtime_clock_noise_but_keeps_semantic_state(monkeypatch, tmp_path):
    expected = {
        'decision': {'status': 'approved'},
        'analyst_reviewed_at': '2026-08-09T08:00:00Z',
        'runtime_timestamp': '2026-08-09T08:00:00Z',
    }
    actual = {
        'decision': {'status': 'approved'},
        'analyst_reviewed_at': '2026-08-09T08:00:03Z',
        'runtime_timestamp': '2026-08-09T08:00:03Z',
    }
    out = _run(monkeypatch, tmp_path, expected, actual)
    assert out['status'] == 'PASS'
    assert out['steps_failed'] == 0


def test_replay_still_fails_on_real_business_state_difference(monkeypatch, tmp_path):
    expected = {'decision': {'status': 'approved'}, 'runtime_timestamp': 't1'}
    actual = {'decision': {'status': 'rejected'}, 'runtime_timestamp': 't2'}
    out = _run(monkeypatch, tmp_path, expected, actual)
    assert out['status'] == 'FAIL'
    assert out['steps_failed'] == 1
    assert out['results'][0]['checks']['state_after'] is False


def test_replay_reads_route_key_from_actual_runtime_contract(monkeypatch, tmp_path):
    state = {'decision': {'status': 'approved'}}
    out = _run(monkeypatch, tmp_path, state, state, actual_route='approve')
    assert out['status'] == 'PASS'
    assert out['steps_failed'] == 0
    assert out['results'][0]['checks']['selected_route_key'] is True
