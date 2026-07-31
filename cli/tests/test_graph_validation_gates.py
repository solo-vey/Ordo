from __future__ import annotations

from copy import deepcopy

from ordo.compiler import compile_source
from ordo.graph_validation import validate_process_graph
from ordo.linter import lint_source
from ordo.transition_provenance import validate_node_entry, validate_transition_provenance


def codes(report: dict) -> set[str]:
    return {issue["code"] for issue in report["issues"]}


def routed_gate_source(*, bidirectional: bool = False) -> dict:
    source = {
        "nodes": [
            {"id": "N_START", "on_answer": {"next": "G_READY"}},
            {"id": "N_DONE", "terminal": True},
        ],
        "gates": [
            {"id": "G_READY", "on_pass": "N_DONE", "on_fail": "STOP_FAILED"},
        ],
        "graph_contract": {
            "entry_node": "N_START",
            "external_terminal_targets": ["STOP_FAILED"],
            "allowed_cycle_regions": [],
        },
    }
    if bidirectional:
        source["graph_contract"]["bidirectional_transition_policy"] = "explicit_source_and_target"
        source["graph_contract"]["transition_provenance"] = {"enabled": True, "mode": "strict"}
        source["nodes"][0].update({"allowed_from": [], "entry_modes": ["root"]})
        source["gates"][0]["allowed_from"] = ["N_START"]
        source["nodes"][1]["allowed_from"] = ["G_READY"]
    return source


def test_top_level_gate_is_valid_transition_vertex():
    report = validate_process_graph(routed_gate_source())
    assert report["status"] == "passed", report
    assert report["summary"]["nodes"] == 2
    assert report["summary"]["gates"] == 1
    assert report["summary"]["graph_vertices"] == 3
    assert report["summary"]["reachable_active_vertices"] == 3


def test_missing_gate_target_is_blocking():
    source = routed_gate_source()
    source["gates"][0]["on_pass"] = "G_MISSING"
    report = validate_process_graph(source)
    assert "GRAPH_TARGET_MISSING" in codes(report)


def test_duplicate_node_and_gate_id_is_blocking():
    source = routed_gate_source()
    source["gates"][0]["id"] = "N_DONE"
    report = validate_process_graph(source)
    assert "GRAPH_ID_DUPLICATE" in codes(report)


def test_mixed_node_gate_cycle_is_checked_and_can_be_declared():
    source = routed_gate_source()
    source["nodes"].pop()
    source["gates"][0]["on_pass"] = "N_START"
    source["graph_contract"]["allowed_cycle_regions"] = [{"id": "RETRY", "nodes": ["N_START", "G_READY"]}]
    report = validate_process_graph(source)
    assert report["status"] == "passed", report
    assert report["summary"]["cycles_detected"] == 1


def test_gate_bidirectional_contract_and_provenance_pass():
    source = routed_gate_source(bidirectional=True)
    graph_report = validate_process_graph(source)
    provenance_report = validate_transition_provenance(source)
    assert graph_report["status"] == "passed", graph_report
    assert provenance_report["status"] == "passed", provenance_report
    assert validate_node_entry(source, target_node_id="G_READY", previous_node_id="N_START")["status"] == "passed"


def test_gate_bidirectional_contract_rejects_unaccepted_edge():
    source = routed_gate_source(bidirectional=True)
    source["gates"][0]["allowed_from"] = []
    report = validate_process_graph(source)
    assert "GRAPH_EDGE_ASYMMETRIC" in codes(report)


def test_gate_routes_survive_compile_and_lint():
    source = routed_gate_source(bidirectional=True)
    compiled = compile_source(deepcopy(source))
    gate = next(operation for operation in compiled["ops"] if operation["op"] == "GATE.DEF")
    assert gate["on_pass"] == "N_DONE"
    assert gate["on_fail"] == "STOP_FAILED"
    assert gate["allowed_from"] == ["N_START"]
    report = lint_source(source, {"test_cases": [{}]})
    assert report["graph_validation"]["status"] == "passed", report


def test_declarative_gate_catalogue_is_not_misclassified_as_process_vertex():
    source = {
        "nodes": [{"id": "N_START", "terminal": True}],
        "gates": [{"id": "G_CATALOGUE_ONLY", "on_fail": "block"}],
        "graph_contract": {"entry_node": "N_START"},
    }
    report = validate_process_graph(source)
    assert report["status"] == "passed", report
    assert report["summary"]["gates"] == 1
    assert report["summary"]["graph_vertices"] == 1
