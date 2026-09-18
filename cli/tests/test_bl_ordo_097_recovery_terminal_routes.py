from __future__ import annotations

from pathlib import Path

import yaml

from ordo.graph_validation import validate_process_graph
from ordo.intake import guided_intake


def _source() -> dict:
    return {
        "ordo": {"version": "0.12", "package": "demo.recovery", "control_level": "standard", "execution_mode": "full_runtime"},
        "nodes": [
            {"id": "N_INPUT", "question": "Confirm input.", "allowed_answers": ["ok"], "on_answer": {"ok": {"next": "N_DONE"}}, "on_unmatched_input": {"max_attempts": 1, "on_exhausted": {"action": "clarify"}}, "failure_routes": [{"kind": "input", "classification": "recoverable", "next": "N_RECOVERY"}], "allowed_from": []},
            {"id": "N_RECOVERY", "question": "Correct input.", "allowed_answers": ["done"], "on_answer": {"done": {"next": "N_DONE"}}, "allowed_from": ["N_INPUT"]},
            {"id": "N_DONE", "terminal": True, "allowed_from": ["N_INPUT", "N_RECOVERY"]},
            {"id": "STOP_INPUT_INVALID", "terminal": True, "allowed_from": []},
        ],
        "graph_contract": {"entry_node": "N_INPUT", "bidirectional_transition_policy": "explicit_source_and_target"},
    }


def _codes(report: dict) -> set[str]:
    return {item["code"] for item in report["issues"]}


def _package(tmp_path: Path, source: dict) -> Path:
    root = tmp_path / "package"
    (root / "source").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "ordo.yml").write_text("name: demo.recovery\nversion: '1.0.0'\nsource: source/program.ordo.yaml\ntests: tests/test_cases.yaml\n", encoding="utf-8")
    (root / "source/program.ordo.yaml").write_text(yaml.safe_dump(source, sort_keys=False), encoding="utf-8")
    (root / "tests/test_cases.yaml").write_text("test_cases: []\n", encoding="utf-8")
    return root


def test_recoverable_failure_route_preserves_flow_and_reaches_explicit_terminal(tmp_path: Path) -> None:
    source = _source()
    assert "GRAPH_STOP_UNCONNECTED" in _codes(validate_process_graph(source))
    source["nodes"].pop()
    assert validate_process_graph(source)["status"] == "passed"
    package = _package(tmp_path, source)
    answers = package / "answers.yaml"
    answers.write_text("N_INPUT:\n  attempts: [bad, bad]\nN_RECOVERY: done\n", encoding="utf-8")
    report = guided_intake(package, answers_path=answers, non_interactive=True)
    assert report["status"] == "passed", report
    routed = [event for event in report["events"] if event["type"] == "recoverable_failure_routed"]
    assert routed and routed[0]["next"] == "N_RECOVERY"
    assert report["state"]["last_closed_node"] == "N_RECOVERY"


def test_terminal_failure_routes_must_be_explicit_and_recovery_cannot_stop() -> None:
    source = _source()
    source["nodes"].pop()
    source["nodes"][0]["failure_routes"] = [{"kind": "validation", "classification": "terminal", "next": "N_RECOVERY"}]
    assert "GRAPH_TERMINAL_ROUTE_NOT_EXPLICIT" in _codes(validate_process_graph(source))
    source["nodes"][0]["failure_routes"] = [{"kind": "validation", "classification": "recoverable", "next": "N_DONE"}]
    assert "GRAPH_RECOVERY_ROUTE_NOT_RECOVERABLE" in _codes(validate_process_graph(source))


def test_orphan_or_nonterminal_stop_is_rejected_after_route_changes() -> None:
    source = _source()
    source["nodes"][-1]["terminal"] = False
    codes = _codes(validate_process_graph(source))
    assert {"GRAPH_STOP_NOT_TERMINAL", "GRAPH_STOP_UNCONNECTED", "GRAPH_STOP_UNREACHABLE"} <= codes
