import editor_service as es


def _semantic_element():
    return {
        'output_contract': {
            'contract': 'NodeExecutionResult',
            'required': ['assistant_message','state_patch','route_key','needs_analyst','next_intent','rationale_short','action'],
        }
    }


def test_non_merge_row_missing_metadata_is_materialized_as_null():
    candidate = {
        'assistant_message': 'ok',
        'route_key': 'next',
        'state_updates': {
            'base_revision': 0,
            'operations': [
                {'op':'set','path':'business_meaning','value':{},'basis':'analyst_input','reason':'confirmed'},
                {'op':'append','path':'catalog.rows','value':{'id':'X'},'basis':'generated','reason':'generated'},
            ],
        },
    }
    out, adaptations = es._adapt_runtime_owned_node_envelope(
        candidate, semantic_element=_semantic_element(), semantic_traits={'requires_analyst': False}, phase='respond'
    )
    for operation in out['state_patch']['operations']:
        assert operation['row_key'] is None
        assert operation['row_match'] is None
    kinds = [x['kind'] for x in adaptations]
    assert kinds.count('derive_non_merge_row_metadata') == 2


def test_merge_row_identity_is_never_invented():
    candidate = {
        'assistant_message': 'ok', 'route_key':'next',
        'state_patch': {'base_revision':0,'operations':[{'op':'merge_row','path':'catalog.rows','value':{'id':'X'},'basis':'generated','reason':'generated'}]},
    }
    out, adaptations = es._adapt_runtime_owned_node_envelope(
        candidate, semantic_element=_semantic_element(), semantic_traits={'requires_analyst': False}, phase='respond'
    )
    op = out['state_patch']['operations'][0]
    assert 'row_key' not in op
    assert 'row_match' not in op
    assert not any(x.get('kind') == 'derive_non_merge_row_metadata' for x in adaptations)
