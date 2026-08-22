from utilities.ordo_tree_editor import editor_service as es


def gate(**extra):
    g={"coverage_requirements":["a","b","c"],"coverage_catalogs":["catalog.rows"]}
    g.update(extra); return g


def test_empty_self_declaration_does_not_credit_coverage():
    state={"catalog":{"rows":[{"tc_id":"X-1","covers":["a","b"]}]}}
    out=es._evaluate_test_coverage_gate(gate(),state)
    assert out[0]=='fail'
    assert out[2]['invalid_coverage_rows']
    assert out[2]['acceptance_eligible'] is False


def test_row_cannot_claim_more_than_policy_limit():
    state={"catalog":{"rows":[{"tc_id":"X-1","scenario":"s","short_input":"i","expected_result":"r","covers":["a","b","c"]}]}}
    out=es._evaluate_test_coverage_gate(gate(coverage_max_ids_per_row=2),state)
    assert out[0]=='fail'
    assert out[2]['overcredited_rows'][0]['max_allowed']==2


def test_registry_can_crosscheck_expected_state_generically():
    g=gate(coverage_registry={"a":{"required":True,"expected_states":["absent"]},"b":{"required":False},"c":{"required":False}})
    state={"catalog":{"rows":[{"tc_id":"X-1","scenario":"s","short_input":"i","expected_result":"r","expected_state":"present","covers":["a"]}]}}
    out=es._evaluate_test_coverage_gate(g,state)
    assert out[0]=='fail'
    assert out[2]['expected_state_conflicts'][0]['coverage_id']=='a'
