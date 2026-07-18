from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / 'integration'
if str(INTEGRATION) not in sys.path:
    sys.path.insert(0, str(INTEGRATION))

from antipattern_hook_runtime import execute_hook, execute_node_hooks


class FakeAdapter:
    def __init__(self, decision: str):
        self.decision = decision

    def evaluate_gate(self, **kwargs):
        finding = {
            'finding_id': 'FIND-TEST',
            'matched': self.decision != 'allow',
            'enforcement': 'blocking' if self.decision == 'block' else 'advisory',
            'severity': 'critical' if self.decision == 'block' else 'warning',
        }
        return {
            'decision': self.decision,
            'gate_id': 'TEST_GATE',
            'findings': [finding],
            'blocking_finding_ids': ['FIND-TEST'] if self.decision == 'block' else [],
            'advisory_finding_ids': ['FIND-TEST'] if self.decision == 'allow_with_advisory' else [],
        }


def hook(phase='after_state_update_before_transition'):
    return {
        'hook_id': 'APH-TEST-HOOK',
        'phase': phase,
        'context_type': 'runtime_state',
        'source_id': 'N_TEST',
        'input': {'state_projection': ['signal'], 'source_hash_ref': None},
        'output': {
            'report_state_field': 'antipattern_gate_report',
            'findings_state_field': 'antipattern_findings',
            'gate_status_state_field': 'antipattern_gate_status',
            'evidence_refs_state_field': 'antipattern_evidence_refs',
        },
        'routing': {
            'on_block': {'repair_target': 'N_REPAIR'},
            'on_allow': {'action': 'continue_transition'},
            'on_advisory': {'action': 'continue_transition_with_evidence'},
        },
        'enabled_antipattern_overrides': ['MANDATORY_BRANCH_SHORT_CIRCUIT'],
    }


class RuntimeBehaviorTests(unittest.TestCase):
    def test_block_routes_to_repair_and_persists_evidence(self):
        state = {'signal': True, 'antipattern_findings': [], 'antipattern_evidence_refs': []}
        result = execute_hook(package_root=ROOT, hook=hook(), state=state, normal_next_target='N_NEXT', adapter=FakeAdapter('block'))
        self.assertTrue(result.blocked)
        self.assertEqual(result.next_target, 'N_REPAIR')
        self.assertTrue(state['antipattern_repair_required'])
        self.assertEqual(state['antipattern_blocked_transition_target'], 'N_NEXT')
        self.assertEqual(state['antipattern_gate_status'], 'block')
        self.assertEqual(len(state['antipattern_evidence_refs']), 1)

    def test_advisory_continues_and_persists_finding(self):
        state = {'signal': True, 'antipattern_findings': [], 'antipattern_evidence_refs': []}
        result = execute_hook(package_root=ROOT, hook=hook(), state=state, normal_next_target='N_NEXT', adapter=FakeAdapter('allow_with_advisory'))
        self.assertFalse(result.blocked)
        self.assertTrue(result.advisory)
        self.assertEqual(result.next_target, 'N_NEXT')
        self.assertEqual(len(state['antipattern_findings']), 1)

    def test_allow_continues(self):
        state = {'signal': True, 'antipattern_findings': [], 'antipattern_evidence_refs': []}
        result = execute_hook(package_root=ROOT, hook=hook(), state=state, normal_next_target='N_NEXT', adapter=FakeAdapter('allow'))
        self.assertEqual(result.next_target, 'N_NEXT')
        self.assertFalse(result.blocked)

    def test_runtime_error_fails_closed(self):
        class BrokenAdapter:
            def evaluate_gate(self, **kwargs):
                raise ValueError('broken')
        state = {'signal': True, 'antipattern_findings': [], 'antipattern_evidence_refs': []}
        result = execute_hook(package_root=ROOT, hook=hook(), state=state, normal_next_target='N_NEXT', adapter=BrokenAdapter())
        self.assertTrue(result.blocked)
        self.assertIn('runtime_error', result.report)

    def test_multiple_hooks_stop_after_block(self):
        node = {'antipattern_hooks': [hook(), {**hook(), 'hook_id': 'APH-TEST-HOOK-2'}]}
        state = {'signal': True, 'antipattern_findings': [], 'antipattern_evidence_refs': []}
        result = execute_node_hooks(package_root=ROOT, node=node, phase='after_state_update_before_transition', state=state, normal_next_target='N_NEXT', adapter=FakeAdapter('block'))
        self.assertEqual(result['executed_hook_ids'], ['APH-TEST-HOOK'])
        self.assertEqual(result['next_target'], 'N_REPAIR')


if __name__ == '__main__':
    unittest.main()
