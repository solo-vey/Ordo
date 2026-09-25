from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SERVICE=(ROOT/'editor_service.py').read_text(encoding='utf-8')

def test_async_package_preparation_routes_and_disconnect_guard():
    assert 'def _start_playbook_preparation' in SERVICE
    assert 'def _playbook_preparation_worker' in SERVICE
    assert 'def _playbook_preparation_status' in SERVICE
    assert '"/api/playbook-package-start"' in SERVICE
    assert '"/api/playbook-package-status"' in SERVICE
    assert 'except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):' in SERVICE

def test_async_preparation_exposes_granular_stage_progress():
    assert '_PLAYBOOK_PREPARATION_STAGE_ORDER' in SERVICE
    for stage in [
        'inspect_input','validate_package','locate_source','index_resources',
        'resolve_runtime_authority','extract_compile_workspace','compile_runtime_plan',
        'validate_runtime_plan','verify_package_integrity','build_editor_views','finalize_package',
    ]:
        assert f'"{stage}"' in SERVICE
    assert 'elapsed_seconds' in SERVICE
    assert 'idle_seconds' in SERVICE
    assert 'Integrated compiler running' in SERVICE
    assert 'Runtime-plan validator running' in SERVICE
