from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import yaml

from ordo.graph_validation import validate_process_graph
from ordo.linter import lint_source

ROOT = Path(__file__).resolve().parents[2]
APF = ROOT / "packages/ordo_applied_project_factory/source/program.ordo.yaml"


def load_apf():
    return yaml.safe_load(APF.read_text(encoding="utf-8"))


def codes(report):
    return {issue["code"] for issue in report["issues"]}


def test_real_apf_graph_passes():
    report = validate_process_graph(load_apf())
    assert report["status"] == "passed"
    assert report["summary"]["reachable_active_nodes"] == 98
    assert report["summary"]["cycles_detected"] == 7


def test_missing_transition_target_fails():
    source = load_apf()
    source["nodes"][0]["on_answer"]["domain_model_plus_tree"]["next"] = "N_DOES_NOT_EXIST"
    report = validate_process_graph(source)
    assert "GRAPH_TARGET_MISSING" in codes(report)


def test_active_unreachable_node_fails():
    source = load_apf()
    source["nodes"].append({"id": "N_ORPHAN", "terminal": True, "on_unmatched_input": {"action": "CLARIFY.REQUEST"}})
    report = validate_process_graph(source)
    assert "GRAPH_NODE_UNREACHABLE" in codes(report)


def test_dead_end_node_fails():
    source = load_apf()
    node = next(n for n in source["nodes"] if n["id"] == "N_APPLIED_PROJECT_GOAL")
    node.pop("on_answer")
    report = validate_process_graph(source)
    assert "GRAPH_DEAD_END_NODE" in codes(report)


def test_undeclared_cycle_fails():
    source = load_apf()
    source["graph_contract"]["allowed_cycle_regions"] = []
    report = validate_process_graph(source)
    assert "GRAPH_CYCLE_UNDECLARED" in codes(report)


def test_linter_integrates_graph_gate():
    source = load_apf()
    source["nodes"][0]["on_answer"]["domain_model_plus_tree"]["next"] = "N_DOES_NOT_EXIST"
    report = lint_source(source, {"test_cases": [{}]})
    assert report["status"] == "failed"
    assert "GRAPH_TARGET_MISSING" in codes(report)
    assert report["graph_validation"]["status"] == "failed"


def test_asymmetric_forward_edge_fails():
    source = load_apf()
    target = next(n for n in source["nodes"] if n["id"] == "N_APPLIED_PROJECT_GOAL")
    target["allowed_from"] = [item for item in target["allowed_from"] if item != "N_FACTORY_MODE_SELECTION"]
    report = validate_process_graph(source)
    assert "GRAPH_EDGE_ASYMMETRIC" in codes(report)


def test_asymmetric_incoming_declaration_fails():
    source = load_apf()
    target = next(n for n in source["nodes"] if n["id"] == "N_APPLIED_PROJECT_GOAL")
    target["allowed_from"].append("N_APPLIED_PROCESS_TYPE")
    report = validate_process_graph(source)
    assert "GRAPH_EDGE_ASYMMETRIC" in codes(report)


def test_unknown_incoming_source_fails():
    source = load_apf()
    source["nodes"][1]["allowed_from"].append("N_DOES_NOT_EXIST")
    report = validate_process_graph(source)
    assert "GRAPH_SOURCE_MISSING" in codes(report)


def test_duplicate_incoming_source_fails():
    source = load_apf()
    source["nodes"][1]["allowed_from"].append(source["nodes"][1]["allowed_from"][0])
    report = validate_process_graph(source)
    assert "GRAPH_INCOMING_DUPLICATE" in codes(report)


def test_terminal_outgoing_edge_fails():
    source = {
        "nodes": [
            {"id": "A", "on_answer": {"ok": {"next": "T"}}, "allowed_from": []},
            {"id": "T", "terminal": True, "on_answer": {"retry": {"next": "A"}}, "allowed_from": ["A"]},
        ],
        "graph_contract": {"entry_node": "A"},
    }
    report = validate_process_graph(source)
    assert "GRAPH_TERMINAL_OUTGOING" in codes(report)


def test_declared_dynamic_terminal_source_satisfies_terminal_path():
    source = {
        "nodes": [
            {"id": "A", "on_answer": {"loop": {"next": "A"}}},
        ],
        "graph_contract": {
            "entry_node": "A",
            "allowed_cycle_regions": [{"id": "LOOP", "nodes": ["A"]}],
            "dynamic_terminal_sources": ["A"],
        },
    }
    report = validate_process_graph(source)
    assert report["status"] == "passed"


def test_unknown_dynamic_terminal_source_fails():
    source = {"nodes": [{"id": "A", "terminal": True}], "graph_contract": {"entry_node": "A", "dynamic_terminal_sources": ["MISSING"]}}
    report = validate_process_graph(source)
    assert "GRAPH_DYNAMIC_TERMINAL_SOURCE_MISSING" in codes(report)


def test_duplicate_transition_in_one_list_scope_fails():
    source = {
        "nodes": [
            {"id": "A", "on_answer": {"ok": [{"next": "B"}, {"next": "B"}]}, "allowed_from": []},
            {"id": "B", "terminal": True, "allowed_from": ["A"]},
        ],
        "graph_contract": {"entry_node": "A"},
    }
    report = validate_process_graph(source)
    assert "GRAPH_TRANSITION_DUPLICATE" in codes(report)


def test_active_non_entry_without_incoming_edge_fails():
    source = load_apf()
    source["nodes"].append({
        "id": "N_ACTIVE_WITHOUT_INCOMING",
        "on_answer": {"ok": {"next": "END_HANDOFF_ACCEPTED"}},
        "allowed_from": [],
    })
    report = validate_process_graph(source)
    assert "GRAPH_NODE_NO_INCOMING" in codes(report)
