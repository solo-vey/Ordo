from __future__ import annotations

from copy import deepcopy

from ordo.canonical_regression import run_canonical_regression
from ordo.compiler import compile_source


def source() -> dict:
    return {
        "ordo": {"version": "0.12", "package": "example.regression", "control_level": "standard", "execution_mode": "full_runtime"},
        "state": {"schema": {"approved": False}},
        "graph_contract": {"entry_node": "N_DECIDE", "external_terminal_targets": ["END_DONE"], "deleted_ids": ["N_REMOVED"]},
        "nodes": [{"id": "N_DECIDE", "on_unmatched_input": {"action": "CLARIFY.REQUEST"}, "transitions": {"next": "G_READY"}}],
        "gates": [{"id": "G_READY", "method": "mechanical", "trust_class": "deterministic", "condition": "state.approved is true", "on_pass": "END_DONE"}],
        "regression_contract": {"version": "1.0", "mode": "strict", "decision_rule_coverage": "required", "negative_assertions": [{"kind": "artifact", "id": "A_REMOVED"}]},
    }


def cases() -> dict:
    return {"test_cases": [{"id": "TC_DECIDE", "expected": {"node": "N_DECIDE", "gates": [{"id": "G_READY", "status": "passed"}]}}]}


def test_dynamic_discovery_runs_complete_contour_and_binds_source_identity() -> None:
    identity = {"verified_source_path": "source/program.ordo.yaml", "size_bytes": 123, "mtime_ns": 456, "sha256": "a" * 64}
    report = run_canonical_regression(source(), cases(), source_identity=identity)
    assert report["status"] == "passed", report
    assert set(report["contours"]) == {"canonical_source", "lint", "graph", "compile", "test", "coverage"}
    assert report["source_identity"] == identity
    assert report["discovered_graph"]["active_gates"] == ["G_READY"]
    assert report["negative_assertions"][0]["status"] == "passed"
    contract = next(op for op in compile_source(deepcopy(source()))["ops"] if op["op"] == "REGRESSION.CONTRACT.DEF")
    assert contract["decision_rule_coverage"] == "required"


def test_new_vertices_and_removed_constructs_fail_closed() -> None:
    value = source()
    value["nodes"].append({"id": "N_NEW", "on_unmatched_input": {"action": "CLARIFY.REQUEST"}})
    report = run_canonical_regression(value, cases())
    assert report["status"] == "failed"
    assert "N_NEW" in report["decision_rule_coverage"]["uncovered_nodes"]

    value = source()
    value["artifacts"] = [{"id": "A_REMOVED"}]
    report = run_canonical_regression(value, cases())
    assert any(item["code"] == "REGRESSION_REMOVED_CONSTRUCT_PRESENT" for item in report["issues"])
