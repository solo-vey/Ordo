from __future__ import annotations

import tempfile
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from integrated_compiler.compile_runtime_semantic_plan_v7 import compile_plan


def _compile(source: str) -> dict:
    with tempfile.TemporaryDirectory() as td:
        root=Path(td)
        p=root/'program.ordo.yaml'
        p.write_text(source, encoding='utf-8')
        return compile_plan(p, root)


def test_strict_dependency_mode_escalates_exact_but_not_guaranteed_gate_input():
    plan=_compile('''playbook:\n  id: strict-gate-guarantee\n  version: 0.1.0\ngraph_contract:\n  entry_node: N_VERIFY\n  dependency_strictness: strict\n  external_terminal_targets: [END_OK, END_FAIL]\nstate:\n  schema:\n    quality_bundle:\n      quality_report:\n        status: null\nnodes:\n  - id: N_VERIFY\n    type: automatic\n    action: AI.VERIFY\n    writes: [quality_bundle.quality_report.status]\n    next: G_QUALITY\ngates:\n  - id: G_QUALITY\n    method: mechanical\n    trust_class: deterministic\n    condition: state.quality_bundle.quality_report.status is one of PASS\n    allowed_from: [N_VERIFY]\n    on_pass: END_OK\n    on_fail: END_FAIL\n''')
    findings=(plan.get('state') or {}).get('gate_state_contract_analysis',{}).get('findings',[])
    row=next(x for x in findings if x.get('code')=='GATE_INPUT_PRODUCER_NOT_GUARANTEED')
    assert row['severity']=='error'


def _survivability_source(writer_write: str='evidence_bundle', writer_action: str='AI.UPDATE') -> str:
    return f'''playbook:\n  id: survivability-ancestor-overwrite\n  version: 0.1.0\ngraph_contract:\n  entry_node: N_PRODUCE\n  external_terminal_targets: [END_DONE]\nstate:\n  schema:\n    evidence_bundle:\n      technical_contract:\n        endpoint: null\n      analyst_gap: null\nnodes:\n  - id: N_PRODUCE\n    type: automatic\n    action: AI.EXTRACT\n    writes: [evidence_bundle.technical_contract]\n    next: N_CONSUME\n  - id: N_CONSUME\n    type: automatic\n    action: AI.COMPOSE\n    inputs: [evidence_bundle.technical_contract]\n    next: N_GAP\n  - id: N_GAP\n    type: automatic\n    action: {writer_action}\n    writes: [{writer_write}]\n    next: N_CONSUME\n'''


def test_revisit_survivability_flags_ancestor_set_replace_authorization():
    plan=_compile(_survivability_source())
    a=(plan.get('state') or {}).get('r3_required_path_survivability') or {}
    hits=[x for x in a.get('findings',[]) if x.get('code')=='REQUIRED_PATH_ANCESTOR_DESTRUCTIVE_OVERWRITE']
    assert hits, a
    hit=next(x for x in hits if x.get('element_id')=='N_GAP')
    assert 'evidence_bundle.technical_contract' in hit.get('affected_required_paths',[])
    assert {'set','replace','merge','merge_deep'} <= set(hit.get('destructive_ops') or [])


def test_revisit_survivability_does_not_flag_exact_descendant_writer_as_ancestor_overwrite():
    plan=_compile(_survivability_source(writer_write='evidence_bundle.analyst_gap'))
    a=(plan.get('state') or {}).get('r3_required_path_survivability') or {}
    assert not [x for x in a.get('findings',[]) if x.get('code')=='REQUIRED_PATH_ANCESTOR_DESTRUCTIVE_OVERWRITE' and x.get('element_id')=='N_GAP']

def test_schema_proven_ancestor_replacement_and_merges_are_not_false_positive():
    from integrated_compiler.compile_runtime_semantic_plan_v7 import _destructive_ops_for_required_path
    base_props={
        'op': {'enum':['set','replace','merge','merge_deep']},
        'path': {'const':'evidence_bundle'},
        'value': {
            'type':'object',
            'required':['technical_contract'],
            'additionalProperties':False,
            'properties':{
                'technical_contract':{
                    'type':'object',
                    'required':['endpoint'],
                    'additionalProperties':False,
                    'properties':{'endpoint':{'type':'string'}}
                }
            }
        }
    }
    variant={'type':'object','properties':base_props}
    assert _destructive_ops_for_required_path(variant,'evidence_bundle','evidence_bundle.technical_contract.endpoint') == set()
