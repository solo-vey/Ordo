from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / 'integration'
LANGUAGE = ROOT.parents[1] / 'language'
if str(INTEGRATION) not in sys.path:
    sys.path.insert(0, str(INTEGRATION))

from antipattern_hook_runtime import execute_hook


def load_schema(name: str):
    return json.loads((LANGUAGE / 'schemas' / name).read_text(encoding='utf-8'))


class ContractAdapter:
    def __init__(self, decision: str):
        self.decision = decision

    def evaluate_gate(self, **kwargs):
        matched = self.decision != 'allow'
        finding = {
            'schema_version': 'ordo.antipattern_finding.v1',
            'finding_type': 'ANTIPATTERN.FINDING',
            'finding_id': 'FIND-CONTRACT-001',
            'rule_id': 'RULE-CONTRACT',
            'antipattern_id': 'MANDATORY_BRANCH_SHORT_CIRCUIT',
            'matched': matched,
            'severity': 'critical' if self.decision == 'block' else 'warning',
            'enforcement': 'blocking' if self.decision == 'block' else 'advisory',
            'decision': self.decision,
            'message': 'Contract validation finding.',
            'evidence': [{'signal':'branch_complete','predicate':'equals','observed_value':False,'expected_value':True}],
            'recovery': {},
            'remediation': {},
            'source': {'context_type':'runtime_state','source_id':'N_TEST'},
            'timestamps': {'detected_at':'2026-07-13T00:00:00+00:00'},
            'resolution': {'status':'open'}
        }
        matched_findings = 1 if matched else 0
        return {
            'schema_version':'ordo.antipattern_gate_report.v1',
            'report_type':'GATE.REPORT',
            'decision':self.decision,
            'summary':{
                'total_findings':1,
                'matched_findings':matched_findings,
                'blocking_findings':1 if self.decision == 'block' else 0,
                'advisory_findings':1 if self.decision == 'allow_with_advisory' else 0,
                'inconclusive_findings':0,
                'highest_severity':finding['severity'] if matched else None,
            },
            'blocking_finding_ids':['FIND-CONTRACT-001'] if self.decision == 'block' else [],
            'advisory_finding_ids':['FIND-CONTRACT-001'] if self.decision == 'allow_with_advisory' else [],
            'findings':[finding],
            'gate_id':'TEST_GATE',
            'context_type':'runtime_state',
            'source_id':'N_TEST',
            'enabled_antipatterns':['MANDATORY_BRANCH_SHORT_CIRCUIT'],
            'inconclusive_escalated_to_block':False,
        }


def hook():
    return {
        'hook_id':'APH-CONTRACT-TEST',
        'phase':'after_state_update_before_transition',
        'context_type':'runtime_state',
        'source_id':'N_TEST',
        'input':{'state_projection':['signal'],'source_hash_ref':None},
        'output':{
            'report_state_field':'antipattern_gate_report',
            'findings_state_field':'antipattern_findings',
            'gate_status_state_field':'antipattern_gate_status',
            'evidence_refs_state_field':'antipattern_evidence_refs',
        },
        'routing':{
            'on_block':{'repair_target':'N_REPAIR'},
            'on_allow':{'action':'continue_transition'},
            'on_advisory':{'action':'continue_transition_with_evidence'},
        },
        'enabled_antipattern_overrides':['MANDATORY_BRANCH_SHORT_CIRCUIT'],
    }


class StateEvidenceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fc = FormatChecker()
        cls.report_validator = Draft202012Validator(load_schema('antipattern_gate_report.schema.json'), format_checker=fc)
        cls.finding_validator = Draft202012Validator(load_schema('antipattern_finding.schema.json'), format_checker=fc)
        cls.evidence_validator = Draft202012Validator(load_schema('antipattern_evidence_ref.schema.json'), format_checker=fc)

    def execute(self, decision='block'):
        state = {'signal':True,'antipattern_findings':[],'antipattern_evidence_refs':[]}
        execute_hook(package_root=ROOT, hook=hook(), state=state, normal_next_target='N_NEXT', adapter=ContractAdapter(decision))
        return state

    def test_persisted_report_finding_and_evidence_validate(self):
        state = self.execute('block')
        self.report_validator.validate(state['antipattern_gate_report'])
        self.finding_validator.validate(state['antipattern_findings'][0])
        self.evidence_validator.validate(state['antipattern_evidence_refs'][0])

    def test_report_digest_matches_persisted_report(self):
        state = self.execute('allow_with_advisory')
        encoded = json.dumps(state['antipattern_gate_report'], sort_keys=True, ensure_ascii=False, default=str)
        expected = hashlib.sha256(encoded.encode('utf-8')).hexdigest()
        self.assertEqual(state['antipattern_evidence_refs'][0]['report_digest'], expected)

    def test_duplicate_execution_deduplicates_findings_and_evidence(self):
        state = {'signal':True,'antipattern_findings':[],'antipattern_evidence_refs':[]}
        for _ in range(2):
            execute_hook(package_root=ROOT, hook=hook(), state=state, normal_next_target='N_NEXT', adapter=ContractAdapter('block'))
        self.assertEqual(len(state['antipattern_findings']), 1)
        self.assertEqual(len(state['antipattern_evidence_refs']), 1)

    def test_block_state_invariants(self):
        state = self.execute('block')
        self.assertEqual(state['antipattern_gate_status'], 'block')
        self.assertTrue(state['antipattern_repair_required'])
        self.assertEqual(state['antipattern_repair_target'], 'N_REPAIR')
        self.assertEqual(state['antipattern_blocked_transition_target'], 'N_NEXT')

    def test_non_block_clears_repair_state(self):
        state = {'signal':True,'antipattern_findings':[],'antipattern_evidence_refs':[], 'antipattern_repair_required':True, 'antipattern_repair_target':'OLD', 'antipattern_blocked_transition_target':'OLD_NEXT'}
        execute_hook(package_root=ROOT, hook=hook(), state=state, normal_next_target='N_NEXT', adapter=ContractAdapter('allow'))
        self.assertFalse(state['antipattern_repair_required'])
        self.assertIsNone(state['antipattern_repair_target'])
        self.assertIsNone(state['antipattern_blocked_transition_target'])


if __name__ == '__main__':
    unittest.main()
