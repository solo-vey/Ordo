import editor_service as es

def test_gate_branch_update_resolution_constants_and_gate_refs():
    record={
      'on_pass_update_state':{'ctx.status':'sufficient','ctx.findings':'$gate.failed_checks'},
      'on_fail_update_state':{'ctx.status':'needs_clarification'},
    }
    result={'failed_checks':[{'check_id':'X'}]}
    out=es._runtime_owned_gate_branch_updates(record,{'key':'on_pass'},result)
    assert out=={'ctx.status':'sufficient','ctx.findings':[{'check_id':'X'}]}
    out2=es._runtime_owned_gate_branch_updates(record,{'key':'on_fail'},result)
    assert out2=={'ctx.status':'needs_clarification'}
