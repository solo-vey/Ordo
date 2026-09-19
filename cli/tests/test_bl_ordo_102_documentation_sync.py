from __future__ import annotations

from ordo.documentation_sync import render_pseudo_chat, validate_documentation_graph


def source() -> dict:
    return {
        "ordo": {"version": "0.12", "package": "demo.documentation", "control_level": "standard", "execution_mode": "full_runtime"},
        "graph_contract": {"entry_node": "N_START"},
        "nodes": [
            {"id": "N_START", "question": "Provide the title.", "on_answer": {"next": "G_READY"}},
            {"id": "N_DONE", "terminal": True},
            {"id": "N_UNUSED", "question": "This route is not reachable.", "terminal": True},
        ],
        "gates": [{"id": "G_READY", "condition": "state.title != ''", "on_pass": "N_DONE", "on_fail": "N_START"}],
    }


def test_generated_pseudo_chat_passes_against_its_executable_graph(tmp_path) -> None:
    document = tmp_path / "PSEUDO_CHAT.md"
    document.write_text(render_pseudo_chat(source()), encoding="utf-8")

    report = validate_documentation_graph(source(), document)

    assert report["status"] == "passed", report
    assert report["summary"] == {"reachable_vertices": 3, "reachable_transitions": 3, "errors": 0}


def test_stale_node_and_transition_are_rejected(tmp_path) -> None:
    document = tmp_path / "PSEUDO_CHAT.md"
    document.write_text(
        render_pseudo_chat(source())
        + "\n<!-- ordo-node: N_REMOVED -->\n"
        + "<!-- ordo-transition: N_START -> N_REMOVED -->\n",
        encoding="utf-8",
    )

    report = validate_documentation_graph(source(), document)

    assert report["status"] == "failed"
    assert {issue["code"] for issue in report["issues"]} >= {"DOC_GRAPH_NODE_REMOVED", "DOC_GRAPH_TRANSITION_STALE"}


def test_unreachable_documented_node_is_rejected(tmp_path) -> None:
    document = tmp_path / "PSEUDO_CHAT.md"
    document.write_text(render_pseudo_chat(source()) + "\n<!-- ordo-node: N_UNUSED -->\n", encoding="utf-8")

    report = validate_documentation_graph(source(), document)

    assert report["status"] == "failed"
    assert "DOC_GRAPH_NODE_UNREACHABLE" in {issue["code"] for issue in report["issues"]}
