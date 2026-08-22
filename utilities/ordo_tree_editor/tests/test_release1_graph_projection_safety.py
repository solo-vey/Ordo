import editor_service as es


def _ids(graph):
    return {n['id'] for n in graph['nodes']}


def test_reserved_block_is_not_synthetic_node():
    source = {
        'nodes': [{'id': 'N_START', 'next': 'G_CHECK'}],
        'gates': [{'id': 'G_CHECK', 'on_pass': 'N_DONE', 'on_fail': 'block'}],
        'terminals': [{'id': 'N_DONE'}],
        'graph_contract': {'entry_node': 'N_START'},
    }
    graph = es.graph_view(source)
    assert 'block' not in _ids(graph)
    assert not any(e['target'] == 'block' for e in graph['edges'])
    assert graph['projection_diagnostics']['suppressed_reserved_routes'] == [
        {'source': 'G_CHECK', 'key': 'on_fail', 'value': 'block'}
    ]


def test_reserved_word_can_be_real_declared_entity():
    source = {
        'nodes': [{'id': 'N_START', 'next': 'G_CHECK'}, {'id': 'block', 'terminal': True}],
        'gates': [{'id': 'G_CHECK', 'on_pass': 'block', 'on_fail': 'block'}],
        'graph_contract': {'entry_node': 'N_START'},
    }
    graph = es.graph_view(source)
    assert 'block' in _ids(graph)
    assert sum(1 for e in graph['edges'] if e['target'] == 'block') == 2


def test_navigation_allowed_to_is_not_control_flow_edge():
    source = {
        'nodes': [
            {'id': 'N_START', 'next': 'N_NEXT', 'navigation_contract': {'allowed_to': ['N_OTHER']}},
            {'id': 'N_NEXT', 'terminal': True},
            {'id': 'N_OTHER', 'terminal': True},
        ],
        'graph_contract': {'entry_node': 'N_START'},
    }
    graph = es.graph_view(source)
    assert not any(e['source'] == 'N_START' and e['target'] == 'N_OTHER' for e in graph['edges'])
    assert {'source': 'N_START', 'target': 'N_OTHER'} in graph['projection_diagnostics']['navigation_permissions_not_rendered_as_control_flow']


def test_all_projected_edges_are_release1_control_flow():
    source = {
        'nodes': [{'id': 'N_START', 'next': 'G_CHECK'}],
        'gates': [{'id': 'G_CHECK', 'on_pass': 'N_DONE', 'on_fail': 'N_START'}],
        'terminals': [{'id': 'N_DONE'}],
        'graph_contract': {'entry_node': 'N_START'},
    }
    graph = es.graph_view(source)
    assert graph['edges']
    assert all(e.get('edge_type') == 'control_flow' for e in graph['edges'])


def test_unreachable_terminal_is_reported_not_invented_into_flow():
    source = {
        'nodes': [{'id': 'N_START', 'next': 'N_DONE'}],
        'terminals': [{'id': 'N_DONE'}, {'id': 'N_UNUSED'}],
        'graph_contract': {'entry_node': 'N_START'},
    }
    graph = es.graph_view(source)
    assert graph['projection_diagnostics']['unreachable_terminals'] == ['N_UNUSED']
    assert not any(e['target'] == 'N_UNUSED' for e in graph['edges'])
