from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from utilities.ordo_tree_editor import editor_service as es
from utilities.ordo_tree_editor import ordo_yaml_semantics as root_sem
from utilities.ordo_tree_editor.integrated_compiler import ordo_yaml_semantics as int_sem


def _traits_subset(value):
    return {k: value.get(k) for k in (
        "kind", "requires_analyst", "model_executed", "model_executed_phases",
        "runtime_executor", "renders_artifact", "deterministic",
    )}


def test_elc004_explicit_model_execution_is_not_reclassified_by_presentation_fields():
    node = {
        "id": "N_MODEL",
        "action": "AI.SUMMARIZE",
        "question": "Summary shown to analyst",
        "answer_type": "text",
        "node_context": {"knowledge_refs": ["reports/result.json"]},
        "next": "END",
    }
    traits = int_sem.classify(node, False)
    assert traits["runtime_executor"] == "semantic_model"
    assert traits["requires_analyst"] is False
    assert traits["model_executed"] is True


def test_elc004_true_human_question_remains_human_owned():
    node = {
        "id": "N_HUMAN",
        "question": "Provide the title.",
        "answer_type": "text",
        "on_answer": {"update_state": {"title": "$answer"}, "next": "END"},
    }
    traits = int_sem.classify(node, False)
    assert traits["runtime_executor"] == "human_interaction"
    assert traits["requires_analyst"] is True


def test_elc006_package_tool_classification_does_not_depend_on_prose_wording():
    base = {
        "id": "N_TOOL",
        "answer_type": "structured_record",
        "node_context": {"allowed_tools": ["tools/check.py"]},
        "on_answer": {"update_state": {"status": "$answer.status"}, "next": "END"},
    }
    neutral = dict(base, question="Process the supplied input and record the result.")
    explicit = dict(base, question="Run tools/check.py as deterministic helper; do not imitate result.")
    t_neutral = int_sem.classify(neutral, False)
    t_explicit = int_sem.classify(explicit, False)
    assert _traits_subset(t_neutral) == _traits_subset(t_explicit)
    assert t_neutral["runtime_executor"] == "package_tool"
    assert t_neutral["requires_analyst"] is False


def test_classifier_paths_have_behavior_parity_for_execution_traits():
    fixtures = [
        {
            "id": "N_HUMAN", "question": "Provide value?", "answer_type": "text",
            "on_answer": {"update_state": {"value": "$answer"}, "next": "END"},
        },
        {
            "id": "N_MODEL", "action": "AI.SUMMARIZE", "question": "Summary shown to analyst",
            "answer_type": "text", "node_context": {"knowledge_refs": ["r.json"]}, "next": "END",
        },
        {
            "id": "N_TOOL", "question": "Process the input.", "answer_type": "structured_record",
            "node_context": {"allowed_tools": ["tools/check.py"]},
            "on_answer": {"update_state": {"status": "$answer.status"}, "next": "END"},
        },
        {
            "id": "N_SYNTH",
            "question": "Provide the analyst a short summary",
            "answer_type": "structured_record",
            "node_context": {"knowledge_refs": ["reports/result.json"]},
            "on_answer": {"update_state": {"summary": "$answer.summary"}, "next": "END"},
        },
        {
            "id": "G_H", "method": "human", "trust_class": "human_decision",
            "on_pass": "END", "on_fail": "END",
        },
        {
            "id": "G_D", "method": "mechanical", "trust_class": "deterministic",
            "on_pass": "END", "on_fail": "END",
        },
    ]
    for fixture in fixtures:
        is_gate = fixture["id"].startswith("G_")
        assert _traits_subset(root_sem.classify(fixture, is_gate)) == _traits_subset(int_sem.classify(fixture, is_gate)), fixture["id"]


def test_elc005_structured_answer_selector_is_not_rejected_by_integrated_compile(tmp_path):
    raw = b'''playbook:\n  id: structured-human\n  version: 0.1.0\ngraph_contract:\n  entry_node: N_INPUT\n  external_terminal_targets: [END]\nstate:\n  schema:\n    name: string\nnodes:\n  - id: N_INPUT\n    question: "Provide structured input."\n    answer_type: structured\n    expected_fields: [name]\n    on_answer:\n      update_state:\n        name: $answer.name\n      next: END\ngates: []\n'''
    result = es.parse_playbook_package("structured.yaml", raw)
    assert result["semantic_plan_status"]["valid"] is True


def _provenance_source():
    return {
        "graph_contract": {
            "entry_node": "N_START",
            "external_terminal_targets": ["END"],
            "transition_provenance": {"enabled": True, "mode": "strict", "direct_edges_only": True, "invalid_entry_behavior": "block_and_recover"},
        },
        "state": {"schema": {"ok": None}},
        "nodes": [
            {"id": "N_START", "allowed_from": [], "entry_modes": ["root"], "on_answer": {"next": "G_CHECK"}, "question": "Continue?", "answer_type": "text"},
        ],
        "gates": [
            {"id": "G_CHECK", "allowed_from": ["N_START"], "method": "mechanical", "trust_class": "deterministic", "condition": "state.ok == true", "on_pass": "END", "on_fail": "END"},
        ],
    }


def test_elc007_live_runtime_blocks_disallowed_transition_provenance(monkeypatch):
    source = _provenance_source()
    package = {
        "id": "provpkg", "source": source,
        "semantic_plan": {"elements": {"G_CHECK": {"execution_traits": {"runtime_executor": "deterministic_gate", "requires_analyst": False, "model_executed": False}, "state_contract": {}}}},
    }
    es.PLAYBOOK_PACKAGES["provpkg"] = package
    monkeypatch.setattr(es, "_live_credentials", lambda payload: {"provider": "test", "model": "none", "base_url": "local"})
    out = es._call_openai_live({
        "package_id": "provpkg", "session_id": "s", "run_id": "r", "source": source,
        "current_id": "G_CHECK", "previous_node_id": "N_WRONG", "entry_mode": "transition",
        "phase": "enter", "state": {"ok": True}, "state_revision": 0, "history": [],
    })
    runtime = out["debug"]["runtime"]
    assert runtime["reason"] == "transition-provenance-blocked"
    assert runtime["state_after"] == {"ok": True}
    assert out["next_id"] is None
    assert runtime["transition_provenance"]["issues"][0]["code"] == "RUNTIME_PREDECESSOR_NOT_ALLOWED"


def test_elc007_explicit_entry_modes_are_enforced():
    source = _provenance_source()
    source["nodes"].append({"id":"N_RECOVER","allowed_from":[],"entry_modes":["recovery"],"question":"Repair?","answer_type":"text"})
    assert es._validate_live_transition_provenance(source, "N_START", None, "root")["status"] == "passed"
    assert es._validate_live_transition_provenance(source, "N_RECOVER", None, "recovery")["status"] == "passed"
    blocked = es._validate_live_transition_provenance(source, "N_RECOVER", None, "retry")
    assert blocked["status"] == "blocked"
    assert blocked["issues"][0]["code"] == "RUNTIME_ENTRY_PROVENANCE_MISSING"
