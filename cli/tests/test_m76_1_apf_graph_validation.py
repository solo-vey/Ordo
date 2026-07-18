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
    assert report["summary"]["reachable_active_nodes"] == 79
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
