from __future__ import annotations
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import editor_service as es


def test_direct_human_binding_increment_is_runtime_owned():
    record={
        'on_answer': {
            'retry': {
                'update_state': {'counter': '$increment'},
                'next': 'N_NEXT',
            }
        }
    }
    new_state, updates = es._apply_direct_answer_updates(record, {'counter': 2}, 'retry')
    assert updates['counter'] == 3
    assert new_state['counter'] == 3


def test_structured_human_increment_overrides_model_counter_value_and_patch():
    record={'on_answer': {'update_state': {'notes': '$answer.notes', 'counter': '$increment'}}}
    updates={'notes':'fixed', 'counter': 999}
    patch={
        'base_revision': 4,
        'operations': [
            {'op':'set','path':'notes','value':'fixed','basis':'model'},
            {'op':'set','path':'counter','value':999,'basis':'model'},
        ]
    }
    merged, normalized_patch, forced = es._apply_declared_human_runtime_expressions(
        record, {'counter': 2}, 'respond', updates, patch
    )
    assert forced == {'counter': 3}
    assert merged['counter'] == 3
    counter_ops=[op for op in normalized_patch['operations'] if op.get('path')=='counter']
    assert len(counter_ops)==1
    assert counter_ops[0]['value']==3
    assert counter_ops[0]['basis']=='runtime_declared_increment'
