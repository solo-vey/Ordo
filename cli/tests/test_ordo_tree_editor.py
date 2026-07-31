from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from utilities.ordo_tree_editor.build_distribution import build
from utilities.ordo_tree_editor.editor_service import dump_value_yaml, dump_yaml, graph_view, parse_yaml, replace_node, replace_node_sections, replace_record_sections, tree_module_manifest_path, validate_source


def _source() -> dict:
    return {
        "ordo": {"version": "0.12", "package": "sample.editor", "control_level": "standard", "execution_mode": "chat_internal"},
        "graph_contract": {"entry_node": "N_START", "bidirectional_transition_policy": "explicit_source_and_target"},
        "nodes": [
            {"id": "N_START", "question": "Start?", "answer_type": "enum", "allow_unmatched_input": True, "on_answer": {"go": {"next": "N_DONE"}}, "allowed_from": []},
            {"id": "N_DONE", "question": "Done?", "answer_type": "confirmation", "allow_unmatched_input": True, "terminal": True, "allowed_from": ["N_START"]},
        ],
    }


def test_editor_yaml_round_trip_and_graph_projection():
    source = _source()
    parsed = parse_yaml(dump_yaml(source))
    view = graph_view(parsed)
    assert [node["id"] for node in view["nodes"]] == ["N_START", "N_DONE"]
    assert view["edges"] == [{"source": "N_START", "target": "N_DONE", "storage": "on_answer", "key": "go"}]


def test_editor_projects_arf_prototype_purpose_and_transitions():
    source = {
        "nodes": [
            {"id": "N_START", "purpose": "Collect the initial context.", "kind": "analyst_question", "transitions": {"continue": "N_DONE"}},
            {"id": "N_DONE", "purpose": "Finish the route.", "kind": "terminal", "transitions": {"blocked": "$stay"}},
        ]
    }
    view = graph_view(source)
    assert view["nodes"][0]["label"] == "Collect the initial context."
    assert view["nodes"][0]["answer_type"] == "analyst_question"
    assert view["edges"] == [{"source": "N_START", "target": "N_DONE", "storage": "transitions", "key": "continue"}]


def test_editor_projects_separate_executable_gates_and_external_terminals():
    source = {
        "graph_contract": {"entry_node": "N_INPUT", "external_terminal_targets": ["STOP_INPUTS_INCOMPLETE"]},
        "nodes": [{"id": "N_INPUT", "question": "Collect inputs.", "on_answer": {"continue": {"next": "G_INPUTS_PRESERVED"}}}],
        "gates": [{"id": "G_INPUTS_PRESERVED", "method": "mechanical", "condition": "Inputs are preserved.", "on_pass": "N_DONE", "on_fail": "STOP_INPUTS_INCOMPLETE"}],
        "outputs": [{"id": "OUT_FINAL"}],
    }
    view = graph_view(source)
    by_id = {item["id"]: item for item in view["nodes"]}
    assert by_id["G_INPUTS_PRESERVED"]["element_type"] == "gate"
    assert by_id["G_INPUTS_PRESERVED"]["collection"] == "gates"
    assert by_id["STOP_INPUTS_INCOMPLETE"]["element_type"] == "terminal"
    assert by_id["OUT_FINAL"]["element_type"] == "terminal"
    assert {tuple(edge[key] for key in ("source", "target", "storage", "key")) for edge in view["edges"]} == {
        ("N_INPUT", "G_INPUTS_PRESERVED", "on_answer", "continue"),
        ("G_INPUTS_PRESERVED", "N_DONE", "gate_route", "on_pass"),
        ("G_INPUTS_PRESERVED", "STOP_INPUTS_INCOMPLETE", "gate_route", "on_fail"),
    }


def test_editor_projects_top_level_and_on_answer_shorthand_next_routes():
    source = {
        "nodes": [
            {"id": "N_ANSWER", "on_answer": {"update_state": {"answer": "$answer"}, "next": "G_CHECK"}},
            {"id": "N_ACTION", "action": "AI.DERIVE", "next": "G_CHECK"},
        ],
        "gates": [{"id": "G_CHECK", "on_pass": "N_DONE", "on_fail": "STOP"}],
    }
    view = graph_view(source)
    assert {tuple(edge[key] for key in ("source", "target", "storage", "key")) for edge in view["edges"]} >= {
        ("N_ANSWER", "G_CHECK", "on_answer_next", "next"),
        ("N_ACTION", "G_CHECK", "next", "next"),
    }


def test_editor_projects_canonical_navigation_contract_and_list_transitions():
    source = {
        "nodes": [
            {
                "id": "N_REQUEST",
                "title": "Request current state",
                "navigation_contract": {"allowed_from": [], "allowed_to": ["G_READY", "N_DONE"]},
                "transitions": [
                    {"id": "T_TO_GATE", "when": "state supplied", "to": "G_READY"},
                    {"id": "T_TO_DONE", "when": "already ready", "to": "N_DONE"},
                ],
            },
            {"id": "N_DONE", "title": "Done", "navigation_contract": {"allowed_from": ["N_REQUEST"]}},
        ],
        "gates": [{"id": "G_READY", "condition": "Ready", "pass_to": "N_DONE", "fail_to": "STOP_NOT_READY"}],
        "terminals": [{"id": "STOP_NOT_READY", "title": "Not ready"}],
    }
    view = graph_view(source)
    assert {tuple(edge[key] for key in ("source", "target", "storage", "key")) for edge in view["edges"]} == {
        ("N_REQUEST", "G_READY", "transitions_list", "T_TO_GATE"),
        ("N_REQUEST", "N_DONE", "transitions_list", "T_TO_DONE"),
        ("G_READY", "N_DONE", "gate_route", "pass_to"),
        ("G_READY", "STOP_NOT_READY", "gate_route", "fail_to"),
    }
    by_id = {item["id"]: item for item in view["nodes"]}
    assert by_id["STOP_NOT_READY"]["element_type"] == "terminal"


def test_editor_projects_allowed_to_when_transition_list_is_absent_without_duplicate_edges():
    source = {"nodes": [{"id": "N_START", "navigation_contract": {"allowed_to": ["N_DONE"]}}, {"id": "N_DONE"}]}
    view = graph_view(source)
    assert view["edges"] == [{"source": "N_START", "target": "N_DONE", "storage": "navigation_allowed_to", "key": "N_DONE"}]


def test_editor_replaces_separate_gate_sections_and_preserves_node_routes():
    source = {
        "nodes": [{"id": "N_INPUT", "on_answer": {"continue": {"next": "G_OLD"}}}],
        "gates": [{"id": "G_OLD", "on_pass": "N_DONE", "on_fail": "STOP"}],
    }
    updated = replace_record_sections(source, "gates", "G_OLD", {"id": "G_NEW", "on_pass": "N_DONE", "on_fail": "STOP"})
    assert updated["gates"][0]["id"] == "G_NEW"
    assert updated["nodes"][0]["on_answer"]["continue"]["next"] == "G_NEW"


def test_editor_renames_canonical_targets_and_navigation_contracts():
    source = {
        "graph_contract": {"entry_node": "N_START"},
        "nodes": [
            {"id": "N_START", "navigation_contract": {"allowed_to": ["G_OLD"]}, "transitions": [{"id": "T", "to": "G_OLD"}]},
            {"id": "N_DONE", "navigation_contract": {"allowed_from": ["G_OLD"]}},
        ],
        "gates": [{"id": "G_OLD", "pass_to": "N_DONE", "fail_to": "STOP"}],
    }
    updated = replace_record_sections(source, "gates", "G_OLD", {"id": "G_NEW", "pass_to": "N_DONE", "fail_to": "STOP"})
    assert updated["nodes"][0]["navigation_contract"]["allowed_to"] == ["G_NEW"]
    assert updated["nodes"][0]["transitions"][0]["to"] == "G_NEW"
    assert updated["nodes"][1]["navigation_contract"]["allowed_from"] == ["G_NEW"]


def test_editor_replaces_full_node_record_without_dropping_unknown_fields():
    source = _source()
    replacement = {
        "id": "N_RENAMED",
        "kind": "blocking_gate",
        "purpose": "Keep this complete ARF-style node record.",
        "inputs": ["context"],
        "outputs": ["decision"],
        "transitions": {"pass": "N_DONE"},
        "custom_contract": {"preserved": True},
    }
    updated = replace_node(source, "N_START", replacement)
    assert updated["nodes"][0] == replacement
    assert updated["nodes"][1]["allowed_from"] == ["N_RENAMED"]
    assert updated["graph_contract"]["entry_node"] == "N_RENAMED"


def test_editor_replaces_structured_node_sections():
    source = _source()
    updated = replace_node_sections(source, "N_START", {
        "id": "N_START",
        "kind": "question",
        "purpose": "Collect the decision context.",
        "inputs": "- context",
        "transitions": "continue: N_DONE",
    })
    assert updated["nodes"][0]["purpose"] == "Collect the decision context."
    assert updated["nodes"][0]["inputs"] == ["context"]
    assert updated["nodes"][0]["transitions"] == {"continue": "N_DONE"}


def test_editor_scalar_section_values_do_not_show_yaml_document_markers():
    assert dump_value_yaml("N_START") == "N_START"


def test_editor_returns_canonical_graph_finding_for_invalid_transition():
    source = _source()
    source["nodes"][0]["on_answer"]["go"]["next"] = "N_UNKNOWN"
    report = validate_source(source)
    assert report["status"] == "failed"
    assert any(issue["code"] == "GRAPH_TARGET_MISSING" for issue in report["issues"])


def test_editor_discovers_the_repository_tree_module_library():
    assert tree_module_manifest_path().is_file()


def test_editor_distribution_is_reproducible_and_contains_launchable_sources():
    with TemporaryDirectory() as temporary_directory:
        root = Path(temporary_directory)
        first = root / "first.zip"
        second = root / "second.zip"
        build(first)
        build(second)
        assert first.read_bytes() == second.read_bytes()
