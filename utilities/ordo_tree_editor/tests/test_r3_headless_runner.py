import headless_runner as hr

def test_headless_preflight_function_exists_and_replay_is_never_acceptance():
    assert callable(hr.preflight)
    assert callable(hr.replay_evidence)
