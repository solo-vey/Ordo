from __future__ import annotations

"""Canonical, source-bound regression contour for structural Ordo changes."""

from pathlib import Path
from typing import Any

from .canonical_source import validate_canonical_source
from .compiler import compile_source
from .coverage import build_coverage
from .graph_topology import graph_topology
from .graph_validation import validate_process_graph
from .linter import lint_source
from .loader import load_package
from .registry_checks import find_repo_root
from .reporter import write_json
from .tester import run_tests


SCHEMA = "ordo.canonical_regression_report.v1"


def _active(vertex: dict[str, Any]) -> bool:
    return not (str(vertex.get("lifecycle_status", "")).startswith("deprecated") or vertex.get("active_runtime_node") is False)


def _test_coverage(tests: dict[str, Any]) -> tuple[set[str], set[str]]:
    nodes: set[str] = set()
    gates: set[str] = set()
    for test in tests.get("test_cases", []) or []:
        if not isinstance(test, dict):
            continue
        expected = test.get("expected") or {}
        if not isinstance(expected, dict):
            continue
        if isinstance(expected.get("node"), str):
            nodes.add(expected["node"])
        for gate in expected.get("gates", []) or []:
            if isinstance(gate, str):
                gates.add(gate)
            elif isinstance(gate, dict) and isinstance(gate.get("id"), str):
                gates.add(gate["id"])
    return nodes, gates


def _negative_assertions(source: dict[str, Any], contract: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Check deleted graph ids plus explicitly forbidden vertices/artifacts."""
    topology = graph_topology(source)
    vertices = set(topology["nodes"]) | set(topology["gates"])
    artifacts = {str(item["id"]) for key in ("artifacts", "outputs") for item in source.get(key, []) or [] if isinstance(item, dict) and isinstance(item.get("id"), str)}
    checks: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    deleted = ((source.get("graph_contract") or {}).get("deleted_ids") or [])
    declarations = [{"kind": "vertex", "id": value, "origin": "graph_contract.deleted_ids"} for value in deleted if isinstance(value, str)]
    for item in contract.get("negative_assertions", []) or []:
        if isinstance(item, dict) and isinstance(item.get("kind"), str) and isinstance(item.get("id"), str):
            declarations.append({"kind": item["kind"], "id": item["id"], "origin": "regression_contract.negative_assertions"})
        else:
            issues.append({"severity": "error", "code": "REGRESSION_NEGATIVE_ASSERTION_INVALID", "message": "Negative assertion requires kind and id.", "location": "regression_contract.negative_assertions"})
    for item in declarations:
        known = vertices if item["kind"] == "vertex" else artifacts if item["kind"] == "artifact" else None
        absent = known is not None and item["id"] not in known
        checks.append({**item, "status": "passed" if absent else "failed"})
        if known is None:
            issues.append({"severity": "error", "code": "REGRESSION_NEGATIVE_ASSERTION_KIND_INVALID", "message": "Negative assertion kind must be vertex or artifact.", "location": item["origin"]})
        elif not absent:
            issues.append({"severity": "error", "code": "REGRESSION_REMOVED_CONSTRUCT_PRESENT", "message": f"Forbidden {item['kind']} {item['id']!r} is still present.", "location": item["origin"]})
    return checks, issues


def run_canonical_regression(source: dict[str, Any], tests: dict[str, Any], *, source_identity: dict[str, Any] | None = None, repo_root: str | None = None) -> dict[str, Any]:
    """Run the complete structural validation contour without mutating source."""
    contract = source.get("regression_contract") if isinstance(source.get("regression_contract"), dict) else {}
    issues: list[dict[str, Any]] = []
    topology = graph_topology(source)
    node_covered, gate_covered = _test_coverage(tests)
    active_nodes = {node_id for node_id, node in topology["nodes"].items() if _active(node)}
    active_gates = {gate_id for gate_id, gate in topology["gates"].items() if gate_id in topology["executable_gate_ids"] and _active(gate)}
    mode = contract.get("mode", "advisory")
    if contract and (contract.get("version") != "1.0" or mode not in {"strict", "advisory"}):
        issues.append({"severity": "error", "code": "REGRESSION_CONTRACT_INVALID", "message": "regression_contract requires version '1.0' and mode strict or advisory.", "location": "regression_contract"})
    required_coverage = contract.get("decision_rule_coverage") == "required"
    missing_nodes = sorted(active_nodes - node_covered)
    missing_gates = sorted(active_gates - gate_covered)
    if required_coverage:
        for vertex_id in missing_nodes:
            issues.append({"severity": "error", "code": "REGRESSION_DECISION_RULE_UNCOVERED", "message": f"Active decision node {vertex_id!r} has no regression test expectation.", "location": "tests.test_cases"})
        for vertex_id in missing_gates:
            issues.append({"severity": "error", "code": "REGRESSION_DECISION_RULE_UNCOVERED", "message": f"Active decision gate {vertex_id!r} has no regression test expectation.", "location": "tests.test_cases"})
    negative, negative_issues = _negative_assertions(source, contract)
    issues.extend(negative_issues)
    lint = lint_source(source, tests, repo_root=repo_root)
    graph = validate_process_graph(source)
    tests_report = run_tests(source, tests)
    coverage = build_coverage(source, tests)
    try:
        ir = compile_source(source)
        compilation = {"status": "passed", "ops_count": len(ir.get("ops", []))}
    except Exception as exc:  # pragma: no cover - defensive boundary
        compilation = {"status": "failed", "error": str(exc)}
    contours = {
        "canonical_source": {"status": "passed" if source_identity else "not_bound", "source_identity": source_identity},
        "lint": {"status": lint["status"], "summary": lint.get("summary", {})},
        "graph": {"status": graph["status"], "summary": graph.get("summary", {})},
        "compile": compilation,
        "test": {"status": tests_report["status"], "summary": tests_report.get("summary", {})},
        "coverage": {"status": coverage["status"], "summary": coverage.get("summary", {})},
    }
    for name, result in contours.items():
        if result["status"] not in {"passed", "not_bound"}:
            issues.append({"severity": "error", "code": "REGRESSION_CONTOUR_FAILED", "message": f"Required {name} validation contour did not pass.", "location": name})
    errors = [item for item in issues if item["severity"] == "error"]
    return {
        "schema_version": SCHEMA,
        "status": "passed" if not errors else "failed",
        "source_identity": source_identity,
        "contours": contours,
        "discovered_graph": {"active_nodes": sorted(active_nodes), "active_gates": sorted(active_gates), "dynamic_routes": [item.id for item in topology["dynamic_route_declarations"]]},
        "decision_rule_coverage": {"required": required_coverage, "covered_nodes": sorted(node_covered), "covered_gates": sorted(gate_covered), "uncovered_nodes": missing_nodes, "uncovered_gates": missing_gates},
        "negative_assertions": negative,
        "issues": issues,
        "summary": {"errors": len(errors), "active_vertices": len(active_nodes) + len(active_gates), "negative_assertions": len(negative)},
    }


def run_package_canonical_regression(package: str | Path, *, out: str | Path | None = None) -> dict[str, Any]:
    root, _manifest, source, tests = load_package(package)
    identity = validate_canonical_source(root)
    report = run_canonical_regression(source, tests, source_identity=identity.get("source_identity"), repo_root=str(find_repo_root(root)) if find_repo_root(root) else None)
    target = Path(out).resolve() if out else root / "reports" / "canonical_regression_report.json"
    write_json(target, report)
    return report
