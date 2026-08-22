from pathlib import Path
import json, zipfile
import pytest

from utilities.ordo_tree_editor import editor_service as es


def _tool_package(tmp_path: Path, *, machine_route='next'):
    root = tmp_path / 'pkg'
    (root / 'tools').mkdir(parents=True)
    route_line = '' if machine_route is None else f', "route_key": {json.dumps(machine_route)}'
    (root / 'tools' / 'materialize.py').write_text(
        'import argparse,json\n'
        'from pathlib import Path\n'
        'p=argparse.ArgumentParser(); p.add_argument("--output"); a=p.parse_args()\n'
        'Path(a.output).parent.mkdir(parents=True,exist_ok=True); Path(a.output).write_text("ok")\n'
        f'print(json.dumps({{"status":"VALID","artifact_state":"READY"{route_line}}}))\n',
        encoding='utf-8',
    )
    source = {
        'graph_contract': {'entry_node': 'N_ART'},
        'state': {'schema': {'artifact_state': None}},
        'nodes': [{
            'id': 'N_ART',
            # This legacy-looking action must NOT override the semantic executor.
            'action': 'DOCUMENT.GENERATE',
            'question': 'Run `python tools/materialize.py --output generated/out.md` as deterministic helper.',
            'answer_type': 'structured_record',
            'node_context': {
                'allowed_tools': ['tools/materialize.py'],
                'output_contract': {'state_diff': 'required', 'next_node': 'explicit'},
            },
            'on_answer': {
                'update_state': {'artifact_state': '$answer.artifact_state'},
                'next': 'G_VALID',
            },
        }],
        'gates': [{
            'id': 'G_VALID', 'method': 'mechanical', 'trust_class': 'deterministic',
            'condition': 'state.artifact_state == READY', 'on_pass': 'OUT_DONE', 'on_fail': 'OUT_FAIL',
        }],
    }
    (root / 'program.ordo.yaml').write_text('nodes: []\n', encoding='utf-8')
    zpath = tmp_path / 'pkg.zip'
    with zipfile.ZipFile(zpath, 'w') as z:
        for p in root.rglob('*'):
            if p.is_file():
                z.write(p, p.relative_to(root).as_posix())
    semantic = {
        'elements': {
            'N_ART': {
                'id': 'N_ART', 'kind': 'deterministic_operation',
                'execution_traits': {'runtime_executor': 'package_tool', 'model_executed': False, 'model_executed_phases': [], 'requires_analyst': False},
                'state_contract': {},
                'routes': [{'key': 'next', 'target': 'G_VALID'}],
            }
        }
    }
    package = {'id': 'routepkg', 'raw_zip': zpath.read_bytes(), 'source': source, 'semantic_plan': semantic}
    return package, source


def test_red_semantic_package_tool_authority_beats_legacy_document_generate(tmp_path, monkeypatch):
    package, source = _tool_package(tmp_path, machine_route='next')
    es.PLAYBOOK_PACKAGES['routepkg'] = package
    monkeypatch.setattr(es, '_live_credentials', lambda payload: {'provider': 'test', 'model': 'none', 'base_url': 'local', 'api_style': 'test'})
    out = es._call_openai_live({
        'package_id': 'routepkg', 'session_id': tmp_path.name, 'run_id': tmp_path.name,
        'source': source, 'current_id': 'N_ART', 'phase': 'enter', 'state': {}, 'state_revision': 0, 'history': [],
    })
    assert out['debug']['runtime']['runtime_executor'] == 'package_tool'
    assert out['route_key'] == 'next'
    assert out['next_id'] == 'G_VALID'
    assert out['state']['artifact_state'] == 'READY'


def _direct_tool_result(tmp_path: Path, machine_route, routes):
    package, source = _tool_package(tmp_path, machine_route=machine_route)
    token_p = es._ACTIVE_PLAYBOOK_PACKAGE.set(package)
    token_r = es._ACTIVE_RUN_CONTEXT.set({'package_id': 'routepkg', 'session_id': tmp_path.name, 'run_id': tmp_path.name})
    try:
        record = source['nodes'][0]
        # Direct tests vary the runtime route surface independently of source parsing.
        return es._execute_package_tool(
            {'provider': 'test', 'model': 'none', 'base_url': 'local', 'api_style': 'test'},
            record, 'N_ART', 'node', 'enter', {}, routes, 0,
        )
    finally:
        es._ACTIVE_RUN_CONTEXT.reset(token_r)
        es._ACTIVE_PLAYBOOK_PACKAGE.reset(token_p)


def test_red_unknown_tool_route_is_not_silently_replaced_by_next(tmp_path):
    out = _direct_tool_result(tmp_path, 'not_declared', [{'key': 'next', 'target': 'G_VALID'}])
    assert out['run_status'] == 'halted'
    assert out['completion_reason'] == 'deterministic_route_closure_failed'
    diag = out['debug']['runtime']['deterministic_execution_route_closure']
    assert diag['status'] == 'FAIL'
    assert diag['reason'] == 'unknown_route_key'


def test_red_multiple_declarative_routes_without_tool_route_fail_closed(tmp_path):
    package, source = _tool_package(tmp_path, machine_route=None)
    # Remove on_answer.next so there is no explicit default route from the node.
    source['nodes'][0]['on_answer'].pop('next', None)
    token_p = es._ACTIVE_PLAYBOOK_PACKAGE.set(package)
    token_r = es._ACTIVE_RUN_CONTEXT.set({'package_id': 'routepkg', 'session_id': tmp_path.name, 'run_id': tmp_path.name})
    try:
        out = es._execute_package_tool(
            {'provider': 'test', 'model': 'none', 'base_url': 'local', 'api_style': 'test'},
            source['nodes'][0], 'N_ART', 'node', 'enter', {},
            [{'key': 'accept', 'target': 'G_VALID'}, {'key': 'reject', 'target': 'G_OTHER'}], 0,
        )
    finally:
        es._ACTIVE_RUN_CONTEXT.reset(token_r); es._ACTIVE_PLAYBOOK_PACKAGE.reset(token_p)
    assert out['run_status'] == 'halted'
    assert out['completion_reason'] == 'deterministic_route_closure_failed'
    assert out['debug']['runtime']['deterministic_execution_route_closure']['reason'] == 'route_not_selected'


def test_single_declarative_next_remains_valid_when_tool_omits_route(tmp_path):
    out = _direct_tool_result(tmp_path, None, [{'key': 'next', 'target': 'G_VALID'}])
    assert out['run_status'] == 'running'
    assert out['route_key'] == 'next'
    assert out['next_id'] == 'G_VALID'


def test_red_selected_route_target_must_resolve_in_active_graph(tmp_path):
    out = _direct_tool_result(tmp_path, 'next', [{'key': 'next', 'target': 'G_MISSING'}])
    assert out['run_status'] == 'halted'
    assert out['completion_reason'] == 'deterministic_route_closure_failed'
    assert out['debug']['runtime']['deterministic_execution_route_closure']['reason'] == 'unresolved_target'
