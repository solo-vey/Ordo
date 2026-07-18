from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from .compiler import namespace_id
from .runner import evaluate_assertion_condition, initial_state


@dataclass
class TestIssue:
    severity: str
    code: str
    message: str
    location: str


def _add(issues: list[TestIssue], severity: str, code: str, message: str, location: str) -> None:
    issues.append(TestIssue(severity, code, message, location))


def _index_by_id(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item.get("id"): item for item in items if item.get("id")}


def _assertion_projection(assertion: dict[str, Any]) -> str:
    polarity = assertion.get("polarity")
    return "EXPECT.NOT" if polarity == "not" else "EXPECT.MUST"


def run_tests(source: dict[str, Any], tests: dict[str, Any] | None = None) -> dict[str, Any]:
    """Static Ordo test runner MVP.

    This does not execute an AI model. It validates that test cases reference existing
    Ordo units and that expected gate/assertion behavior is consistent with Source.
    """
    tests = tests or {}
    package = (source.get("ordo") or {}).get("package", "unnamed.package")
    test_cases = tests.get("test_cases", []) if isinstance(tests, dict) else []

    gates = _index_by_id(source.get("gates", []) or [])
    assertions = _index_by_id(source.get("assertions", []) or [])
    nodes = _index_by_id(source.get("nodes", []) or [])
    outputs = _index_by_id(source.get("outputs", []) or [])
    state = initial_state(source)
    gate_status = {gate_id: "structural_only" for gate_id in gates}
    assertion_evaluation = [
        evaluate_assertion_condition(assertion.get("condition", ""), source, state, gate_status)
        for assertion in assertions.values()
    ]
    assertions_behaviorally_evaluated = sum(1 for evaluated, _, _ in assertion_evaluation if evaluated)

    results: list[dict[str, Any]] = []
    all_issues: list[TestIssue] = []

    for tc_index, tc in enumerate(test_cases):
        tc_id = tc.get("id") or f"TEST_{tc_index}"
        expected = tc.get("expected", {}) or {}
        issues: list[TestIssue] = []
        base = f"test_cases[{tc_index}]"

        expected_node = expected.get("node")
        if expected_node and expected_node not in nodes:
            _add(issues, "error", "EXPECTED_NODE_NOT_FOUND", f"Expected node does not exist: {expected_node}", f"{base}.expected.node")

        for gate_index, expected_gate in enumerate(expected.get("gates", []) or []):
            gate_id = expected_gate.get("id")
            loc = f"{base}.expected.gates[{gate_index}]"
            if not gate_id:
                _add(issues, "error", "EXPECTED_GATE_ID_REQUIRED", "Expected gate id is required.", f"{loc}.id")
                continue
            gate = gates.get(gate_id)
            if not gate:
                _add(issues, "error", "EXPECTED_GATE_NOT_FOUND", f"Expected gate does not exist: {gate_id}", f"{loc}.id")
                continue
            if "method" in expected_gate and expected_gate.get("method") != gate.get("method"):
                _add(issues, "error", "EXPECTED_GATE_METHOD_MISMATCH", f"Expected method {expected_gate.get('method')} but source has {gate.get('method')}.", f"{loc}.method")
            if "trust_class" in expected_gate and expected_gate.get("trust_class") != gate.get("trust_class"):
                _add(issues, "error", "EXPECTED_GATE_TRUST_CLASS_MISMATCH", f"Expected trust_class {expected_gate.get('trust_class')} but source has {gate.get('trust_class')}.", f"{loc}.trust_class")
            if not expected_gate.get("status"):
                _add(issues, "warning", "EXPECTED_GATE_STATUS_MISSING", "Expected gate should specify status for behavior testing.", f"{loc}.status")

        for assertion_index, expected_assertion in enumerate(expected.get("assertions", []) or []):
            assertion_id = expected_assertion.get("id")
            loc = f"{base}.expected.assertions[{assertion_index}]"
            if not assertion_id:
                _add(issues, "error", "EXPECTED_ASSERTION_ID_REQUIRED", "Expected assertion id is required.", f"{loc}.id")
                continue
            assertion = assertions.get(assertion_id)
            if not assertion:
                _add(issues, "error", "EXPECTED_ASSERTION_NOT_FOUND", f"Expected assertion does not exist: {assertion_id}", f"{loc}.id")
                continue
            expected_projection = expected_assertion.get("projection")
            actual_projection = _assertion_projection(assertion)
            phases = assertion.get("phase") or []
            if expected_projection and expected_projection != actual_projection:
                _add(issues, "error", "EXPECTED_ASSERTION_PROJECTION_MISMATCH", f"Expected projection {expected_projection} but assertion projects to {actual_projection}.", f"{loc}.projection")
            if expected_projection and "test" not in phases:
                _add(issues, "error", "ASSERTION_TEST_PHASE_MISSING", f"Assertion {assertion_id} is expected in tests but lacks phase: test.", f"{loc}.projection")

        expected_output = expected.get("output", {}) or {}
        if expected_output:
            if "final_package_created" in expected_output and expected_output["final_package_created"] is True:
                # Ensure at least one output exists when a test expects final package creation.
                if not outputs:
                    _add(issues, "error", "EXPECTED_OUTPUT_BUT_NO_OUTPUT_DEF", "Test expects output creation but package has no outputs.", f"{base}.expected.output")

        expected_clarify = expected.get("clarify") or expected.get("clarify_request")
        if expected_clarify:
            node_id = expected_clarify.get("node")
            loc = f"{base}.expected.clarify"
            if node_id not in nodes:
                _add(issues, "error", "EXPECTED_CLARIFY_NODE_NOT_FOUND", f"Clarify node does not exist: {node_id}", f"{loc}.node")
            elif not nodes[node_id].get("on_unmatched_input"):
                _add(issues, "error", "EXPECTED_CLARIFY_NOT_CONFIGURED", f"Node {node_id} has no on_unmatched_input configuration.", loc)

        all_issues.extend(issues)
        errors = [asdict(i) for i in issues if i.severity == "error"]
        warnings = [asdict(i) for i in issues if i.severity == "warning"]
        results.append({
            "id": tc_id,
            "status": "passed" if not errors else "failed",
            "namespaced_id": namespace_id(package, tc_id),
            "summary": {"errors": len(errors), "warnings": len(warnings)},
            "issues": [asdict(i) for i in issues],
        })

    errors = [asdict(i) for i in all_issues if i.severity == "error"]
    warnings = [asdict(i) for i in all_issues if i.severity == "warning"]
    return {
        "status": "passed" if not errors else "failed",
        "mode": "static_behavior_validation",
        "note": "M2 test runner validates Ordo test expectations statically; it does not execute an AI model.",
        "summary": {
            "test_cases": len(test_cases),
            "passed": sum(1 for r in results if r["status"] == "passed"),
            "failed": sum(1 for r in results if r["status"] == "failed"),
            "errors": len(errors),
            "warnings": len(warnings),
            "assertions_total": len(assertions),
            "assertions_behaviorally_evaluated": assertions_behaviorally_evaluated,
            "assertions_structural_only": len(assertions) - assertions_behaviorally_evaluated,
        },
        "assertion_evaluation_note": "Static test runner checks references and reports how many assertions have deterministic behavioral evaluators.",
        "results": results,
    }
