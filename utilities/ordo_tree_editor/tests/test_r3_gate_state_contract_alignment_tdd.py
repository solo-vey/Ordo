from __future__ import annotations

import io
import zipfile

from utilities.ordo_tree_editor import editor_service as es


def _zip(source: str) -> bytes:
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('program.ordo.yaml', source)
    return b.getvalue()


def _base_source(producer_writes: str, gate_path: str) -> str:
    return f'''playbook:\n  id: gate-state-contract-tdd\n  version: 0.1.0\ngraph_contract:\n  entry_node: N_VERIFY\n  external_terminal_targets: [END_DONE, END_FAIL]\nstate:\n  schema:\n    quality_bundle:\n      quality_report:\n        status: null\n      quality_status: null\nnodes:\n  - id: N_VERIFY\n    type: automatic\n    action: AI.VERIFY\n    writes: [{producer_writes}]\n    next: G_QUALITY\ngates:\n  - id: G_QUALITY\n    method: mechanical\n    trust_class: deterministic\n    condition: state.{gate_path} is one of PASS\n    allowed_from: [N_VERIFY]\n    on_pass: END_DONE\n    on_fail: END_FAIL\n'''


def _analysis(parsed: dict) -> dict:
    package=es.PLAYBOOK_PACKAGES[parsed['id']]
    return ((package['semantic_plan'].get('state') or {}).get('gate_state_contract_analysis') or {})


def test_gate_condition_state_reference_is_first_class_consumer_dependency():
    parsed=es.parse_playbook_package('mismatch.zip', _zip(_base_source('quality_bundle.quality_report.status','quality_bundle.quality_status')))
    a=_analysis(parsed)
    row=next(x for x in a['gate_inputs'] if x['gate_id']=='G_QUALITY' and x['path']=='quality_bundle.quality_status')
    assert row['status']=='unproduced'
    assert row['exact_upstream_producers']==[]
    assert any(x.get('code')=='GATE_INPUT_HAS_NO_UPSTREAM_PRODUCER' for x in a['findings'])


def test_gate_input_exact_upstream_write_is_aligned_but_model_write_is_not_guaranteed():
    parsed=es.parse_playbook_package('aligned.zip', _zip(_base_source('quality_bundle.quality_report.status','quality_bundle.quality_report.status')))
    a=_analysis(parsed)
    row=next(x for x in a['gate_inputs'] if x['gate_id']=='G_QUALITY')
    assert row['status']=='declared_not_guaranteed'
    assert row['exact_upstream_producers']==['N_VERIFY']
    assert any(x.get('code')=='GATE_INPUT_PRODUCER_NOT_GUARANTEED' for x in a['findings'])


def test_ancestor_object_write_does_not_prove_leaf_gate_input_shape():
    parsed=es.parse_playbook_package('ancestor.zip', _zip(_base_source('quality_bundle','quality_bundle.quality_status')))
    a=_analysis(parsed)
    row=next(x for x in a['gate_inputs'] if x['gate_id']=='G_QUALITY')
    assert row['status']=='ancestor_write_only'
    assert row['ancestor_upstream_producers']==['N_VERIFY']
    assert any(x.get('code')=='GATE_INPUT_ONLY_ANCESTOR_WRITE' for x in a['findings'])


def test_runtime_does_not_invent_alias_for_missing_gate_input():
    result, reason, extra = es._evaluate_mechanical_condition(
        'state.quality_bundle.quality_status is one of PASS',
        {'quality_bundle': {'quality_report': {'status': 'PASS'}}},
    )
    assert result == 'unresolved'
    assert 'quality_bundle.quality_status' in extra['missing_required_inputs']
