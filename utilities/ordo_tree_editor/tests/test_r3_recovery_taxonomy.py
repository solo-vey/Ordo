from utilities.ordo_tree_editor.alpha20_runtime import normalize_gate_failure

def test_context_failure_maps_to_v2_context_scope():
    out=normalize_gate_failure('G',missing_information=[{'path':'x'}],suggested_recovery_scope='context')
    assert out['recovery_scope_v2']=='context'
    assert out['failure_class_v2']=='CONTEXT_ERROR'

def test_local_validation_maps_to_state_scope():
    out=normalize_gate_failure('G',invalid_state=['x'],suggested_recovery_scope='single_node')
    assert out['recovery_scope_v2']=='state'
    assert out['failure_class_v2']=='STATE_VALIDATION_ERROR'
