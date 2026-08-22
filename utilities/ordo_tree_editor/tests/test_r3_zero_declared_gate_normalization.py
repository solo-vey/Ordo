from utilities.ordo_tree_editor import editor_service as es

def test_gate_validator_still_rejects_raw_undeclared_results():
    sem={'output_contract':{'contract':'GateFailureOrPass','declared_check_ids':[]}}
    errors,_=es._validate_gate_check_results({'check_results':[{'check_id':'X'}]},sem)
    assert errors

# Source-level regression for the bounded provider adaptation in the live semantic loop.
def test_live_loop_has_runtime_owned_zero_check_normalization():
    import inspect
    src=inspect.getsource(es._call_openai_live_impl)
    assert 'drop_undeclared_gate_check_results' in src
    assert 'zero_declared_checks' in src
