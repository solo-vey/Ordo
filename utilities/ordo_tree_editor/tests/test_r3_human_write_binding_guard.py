from __future__ import annotations
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import editor_service as es


def _yaml(bound: bool) -> bytes:
    binding = '''\n      update_state:\n        baseline_reference: $answer.baseline_reference\n        evidence_status: $answer.evidence_status\n''' if bound else ''
    return f'''playbook:\n  id: generic-human-binding-guard\n  version: 0.1.0\ngraph_contract:\n  entry_node: N_INTAKE\n  external_terminal_targets: [END_DONE]\nstate:\n  schema:\n    baseline_reference:\n    evidence_status:\nnodes:\n  - id: N_INTAKE\n    type: human_decision\n    question: "Provide evidence."\n    answer_type: structured\n    expected_fields: [baseline_reference, evidence_status]\n    writes: [baseline_reference, evidence_status]\n    on_answer:{binding}\n      next: END_DONE\n'''.encode('utf-8')


def test_human_declared_writes_without_answer_binding_loads_for_inspection_only():
    result=es.parse_playbook_package('bad-human.yaml', _yaml(False))
    assert result['load_status']=='degraded'
    assert result['capabilities']['execute'] is False
    assert result['capabilities']['show_tree'] is True
    assert any('HUMAN_WRITE_WITHOUT_BINDING' in str(item.get('message') or '') for item in result['load_diagnostics'])


def test_human_declared_writes_with_update_state_are_allowed():
    result=es.parse_playbook_package('good-human.yaml', _yaml(True))
    assert result['semantic_plan_status']['valid'] is True
    assert result['preparation_report']['validation']['status']=='PASS'
