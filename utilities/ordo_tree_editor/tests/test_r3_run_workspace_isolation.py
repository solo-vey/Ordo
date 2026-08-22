from utilities.ordo_tree_editor import editor_service as es

def test_r3_runtime_workspace_isolated_by_package_session_run(tmp_path, monkeypatch):
    monkeypatch.setattr(es.tempfile, 'gettempdir', lambda: str(tmp_path))
    a=es._runtime_workspace(package_id='pkg',session_id='session-a',run_id='run-1')
    b=es._runtime_workspace(package_id='pkg',session_id='session-b',run_id='run-1')
    c=es._runtime_workspace(package_id='pkg',session_id='session-a',run_id='run-2')
    d=es._runtime_workspace(package_id='pkg2',session_id='session-a',run_id='run-1')
    assert len({a,b,c,d}) == 4
    assert a.parts[-3:] == ('pkg','session-a','run-1')

def test_r3_active_run_context_selects_request_workspace(tmp_path, monkeypatch):
    monkeypatch.setattr(es.tempfile, 'gettempdir', lambda: str(tmp_path))
    token=es._ACTIVE_RUN_CONTEXT.set({'package_id':'pkg','session_id':'s','run_id':'r'})
    try:
        assert es._runtime_workspace().parts[-3:] == ('pkg','s','r')
    finally:
        es._ACTIVE_RUN_CONTEXT.reset(token)
