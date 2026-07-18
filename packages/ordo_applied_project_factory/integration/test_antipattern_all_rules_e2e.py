from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / "integration"
if str(INTEGRATION) not in sys.path:
    sys.path.insert(0, str(INTEGRATION))

from antipattern_runtime_binding import build_adapter
from antipattern_hook_runtime import execute_hook

CASES_PATH = INTEGRATION / "fixtures_antipattern_e2e.apf.v1.json"
SOURCE_PATH = ROOT / "source/program.ordo.yaml"
CANONICAL_RULES = {
    "PROMPT_AS_IMPLEMENTATION",
    "PACKAGE_VALIDATION_WITHOUT_COMPLETENESS_VALIDATION",
    "MANDATORY_BRANCH_SHORT_CIRCUIT",
    "FINAL_LABEL_OVERCLAIM",
    "SCOPE_CONFIRMATION_AS_IMPLEMENTATION_AUTHORIZATION",
    "COMPLEXITY_ROUTING_AND_EXECUTION_IN_ONE_NODE",
}


def load_cases():
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))["cases"]


def flatten_paths(value, prefix=""):
    paths = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            if isinstance(child, dict):
                paths.extend(flatten_paths(child, path))
            else:
                paths.append(path)
    return paths


def make_hook(case):
    return {
        "schema_version": "ordo.antipattern_wiring_hook.v1",
        "hook_id": "APH-E2E-" + case["rule_id"].replace("_", "-")[:80],
        "phase": "after_state_update_before_transition",
        "adapter": {
            "module": "language.integration.antipattern_gate_adapter",
            "class": "AntipatternGateAdapter",
            "method": "evaluate_gate",
            "activation_profile": "language/integration/antipattern_activation_profile.apf.v1.json",
        },
        "context_type": case["context_type"],
        "source_id": "N_E2E_" + case["rule_id"],
        "input": {
            "state_projection": flatten_paths(case["state"]),
            "source_hash_ref": None,
            "required_signals_policy": "explicit_projection_must_cover_blocking_rules",
        },
        "output": {
            "report_state_field": "antipattern_gate_report",
            "findings_state_field": "antipattern_findings",
            "gate_status_state_field": "antipattern_gate_status",
            "evidence_refs_state_field": "antipattern_evidence_refs",
        },
        "decision_policy": {
            "block": "stop_transition_and_route_to_repair",
            "allow_with_advisory": "continue_and_persist_findings",
            "allow": "continue_and_persist_report",
            "inconclusive": "block_when_required_signals_missing_for_blocking_rule",
        },
        "routing": {
            "on_block": {"action": "route_to_repair", "repair_target": "N_E2E_REPAIR"},
            "on_allow": {"action": "continue_transition"},
            "on_advisory": {"action": "continue_transition_with_evidence"},
        },
        "enabled_antipattern_overrides": [case["rule_id"]],
    }


class AllRulesAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapter = build_adapter(ROOT)
        cls.cases = load_cases()

    def test_fixture_has_positive_and_negative_for_every_rule(self):
        coverage = {rule: set() for rule in CANONICAL_RULES}
        for case in self.cases:
            coverage[case["rule_id"]].add(case["expected_decision"])
        for rule, decisions in coverage.items():
            self.assertEqual(decisions, {"allow", "block"}, rule)

    def test_real_adapter_positive_negative_cases(self):
        for case in self.cases:
            with self.subTest(case=case["case_id"]):
                report = self.adapter.evaluate_gate(
                    state=copy.deepcopy(case["state"]),
                    context_type=case["context_type"],
                    source_id=case["case_id"],
                    detected_at="2026-07-13T00:00:00+00:00",
                    enabled_antipattern_overrides=[case["rule_id"]],
                )
                self.assertEqual(report["decision"], case["expected_decision"])
                matched = [f for f in report["findings"] if f.get("matched")]
                if case["expected_decision"] == "block":
                    self.assertTrue(matched)
                    self.assertTrue(report["blocking_finding_ids"])
                else:
                    self.assertFalse(matched)

    def test_detector_results_are_deterministic(self):
        for case in self.cases:
            kwargs = dict(
                state=copy.deepcopy(case["state"]),
                context_type=case["context_type"],
                source_id=case["case_id"],
                detected_at="2026-07-13T00:00:00+00:00",
                enabled_antipattern_overrides=[case["rule_id"]],
            )
            first = self.adapter.evaluate_gate(**kwargs)
            second = self.adapter.evaluate_gate(**kwargs)
            self.assertEqual(first, second, case["case_id"])


class AllRulesEndToEndRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapter = build_adapter(ROOT)
        cls.cases = load_cases()

    def test_every_positive_case_blocks_and_routes_to_repair(self):
        for case in [c for c in self.cases if c["expected_decision"] == "block"]:
            with self.subTest(case=case["case_id"]):
                state = copy.deepcopy(case["state"])
                state.update({"antipattern_findings": [], "antipattern_evidence_refs": []})
                result = execute_hook(
                    package_root=ROOT,
                    hook=make_hook(case),
                    state=state,
                    normal_next_target="N_E2E_NEXT",
                    adapter=self.adapter,
                )
                self.assertTrue(result.blocked)
                self.assertEqual(result.next_target, "N_E2E_REPAIR")
                self.assertEqual(state["antipattern_blocked_transition_target"], "N_E2E_NEXT")
                self.assertTrue(state["antipattern_repair_required"])
                self.assertEqual(state["antipattern_gate_status"], "block")
                self.assertTrue(state["antipattern_findings"])
                self.assertEqual(len(state["antipattern_evidence_refs"]), 1)

    def test_every_negative_case_continues_and_persists_evidence(self):
        for case in [c for c in self.cases if c["expected_decision"] == "allow"]:
            with self.subTest(case=case["case_id"]):
                state = copy.deepcopy(case["state"])
                state.update({"antipattern_findings": [], "antipattern_evidence_refs": []})
                result = execute_hook(
                    package_root=ROOT,
                    hook=make_hook(case),
                    state=state,
                    normal_next_target="N_E2E_NEXT",
                    adapter=self.adapter,
                )
                self.assertFalse(result.blocked)
                self.assertEqual(result.next_target, "N_E2E_NEXT")
                self.assertFalse(state["antipattern_repair_required"])
                self.assertEqual(state["antipattern_gate_status"], "allow")
                self.assertEqual(len(state["antipattern_evidence_refs"]), 1)


class CriticalHookRegressionTests(unittest.TestCase):
    def test_all_critical_hooks_reference_only_canonical_rules(self):
        source = yaml.safe_load(SOURCE_PATH.read_text(encoding="utf-8"))
        hooks = [h for node in source["nodes"] for h in (node.get("antipattern_hooks") or [])]
        self.assertEqual(len(hooks), 13)
        observed = set()
        for hook in hooks:
            rules = set(hook.get("enabled_antipattern_overrides") or [])
            self.assertTrue(rules)
            self.assertTrue(rules <= CANONICAL_RULES)
            observed |= rules
        self.assertEqual(observed, CANONICAL_RULES)


    def test_actual_critical_hooks_block_representative_positive_case_for_each_rule(self):
        source = yaml.safe_load(SOURCE_PATH.read_text(encoding="utf-8"))
        hooks = [h for node in source["nodes"] for h in (node.get("antipattern_hooks") or [])]
        adapter = build_adapter(ROOT)
        cases_by_rule = {c["rule_id"]: c for c in load_cases() if c["expected_decision"] == "block"}
        for rule in sorted(CANONICAL_RULES):
            actual_hook = next(h for h in hooks if rule in (h.get("enabled_antipattern_overrides") or []))
            case = cases_by_rule[rule]
            single_rule_hook = copy.deepcopy(actual_hook)
            single_rule_hook["enabled_antipattern_overrides"] = [rule]
            state = copy.deepcopy(case["state"])
            state.update({"antipattern_findings": [], "antipattern_evidence_refs": []})
            result = execute_hook(
                package_root=ROOT,
                hook=single_rule_hook,
                state=state,
                normal_next_target="N_ACTUAL_NEXT",
                adapter=adapter,
            )
            self.assertTrue(result.blocked, rule)
            self.assertEqual(result.next_target, actual_hook["routing"]["on_block"]["repair_target"], rule)
            self.assertTrue(state["antipattern_evidence_refs"], rule)

    def test_hook_ids_are_unique_and_repair_targets_exist(self):
        source = yaml.safe_load(SOURCE_PATH.read_text(encoding="utf-8"))
        node_ids = {node["id"] for node in source["nodes"]}
        hooks = [h for node in source["nodes"] for h in (node.get("antipattern_hooks") or [])]
        hook_ids = [h["hook_id"] for h in hooks]
        self.assertEqual(len(hook_ids), len(set(hook_ids)))
        for hook in hooks:
            self.assertIn(hook["routing"]["on_block"]["repair_target"], node_ids)


if __name__ == "__main__":
    unittest.main()
