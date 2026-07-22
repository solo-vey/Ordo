from pathlib import Path
import yaml

from cli.ordo.compiler import lower_flow_reuse

ROOT = Path(__file__).resolve().parents[2]
PROGRAM = ROOT / 'packages/ordo_applied_project_factory/source/program.ordo.yaml'
MODULE = ROOT / 'packages/ordo_applied_project_factory/source/modules/35_optional_flow_reuse.ordo.module.yaml'


def load(path):
    return yaml.safe_load(path.read_text(encoding='utf-8'))


def node_ids(program):
    return {n['id'] for n in program.get('nodes', [])}


def test_two_real_apf_reuse_regions_are_authored():
    block = load(MODULE)['flow_reuse']
    assert len(block['joins']) == 2
    assert len(block['shared_tails']) == 2
    assert len(block['references']) == 2


def test_all_real_tail_nodes_exist_in_apf_graph():
    program = load(PROGRAM)
    ids = node_ids(program)
    block = program['flow_reuse']
    for tail in block['shared_tails']:
        assert tail['entry'] in ids
        assert set(tail['nodes']) <= ids
    for join in block['joins']:
        assert join['target']['node'] in ids
        assert all(endpoint['node'] in ids for endpoint in join['incoming'])


def test_lowering_preserves_declared_join_targets_and_provenance():
    program = load(PROGRAM)
    ops = lower_flow_reuse(program, 'ordo.apf')
    join_defs = {op['source_local_id']: op for op in ops if op['op'] == 'FLOW.JOIN.DEF'}
    assert join_defs['JOIN.OUTPUT.TEMPLATE.READY']['target'] == 'apf.graph.N_TERMINAL_PATH_READY_CHECK'
    assert join_defs['JOIN.VALIDATION.RESULT']['target'] == 'apf.graph.N_SHARED_TAIL_VALIDATION_RESULT_REVIEW'
    assert all(op['provenance_policy'] == 'preserve_all_inputs' for op in join_defs.values())


def test_optional_layer_does_not_replace_or_delete_explicit_nodes():
    program = load(PROGRAM)
    ids = node_ids(program)
    expected = {
        'N_OUTPUT_TEMPLATE_REVIEW_LOOP',
        'N_OUTPUT_TEMPLATE_CREATION_LOOP',
        'N_TERMINAL_PATH_READY_CHECK',
        'N_SHARED_TAIL_MINIMAL_VALIDATION',
        'N_SHARED_TAIL_FULL_VALIDATION_DECISION',
        'N_SHARED_TAIL_VALIDATION_RESULT_REVIEW',
        'N_SHARED_TAIL_FINAL_HANDOFF',
    }
    assert expected <= ids


def test_shared_tail_reference_resolution_is_semantically_stable():
    program = load(PROGRAM)
    ops = lower_flow_reuse(program, 'ordo.apf')
    refs = {op['source_local_id']: op for op in ops if op['op'] == 'SHARED.TAIL.REFERENCE.RESOLVED'}
    assert refs['REF.OUTPUT.TEMPLATE.READINESS']['resolved_entry'] == 'apf.output_template.N_TERMINAL_PATH_READY_CHECK'
    assert refs['REF.VALIDATION.HANDOFF']['resolved_entry'] == 'apf.validation_handoff.N_SHARED_TAIL_VALIDATION_RESULT_REVIEW'
    assert all(op['preserve_provenance'] is True for op in refs.values())
