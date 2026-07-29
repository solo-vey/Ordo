from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from utilities.ordo_tree_editor.build_distribution import build
from utilities.ordo_tree_editor.editor_service import dump_value_yaml, dump_yaml, graph_view, parse_yaml, replace_node, replace_node_sections, tree_module_manifest_path, validate_source


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
    assert view["edges"] == [{"source": "N_START", "target": "N_DONE", "storage": "on_answer", "key": "nested next"}]


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
