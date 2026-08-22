import io, json, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import editor_service as service
from alpha20_runtime import apply_state_patch_atomic
from ordo_yaml_semantics import declared_writes


def test_merge_deep_initializes_none_default():
    state = {"risk_factor_identity": None}
    patch = {"base_revision": 0, "operations": [{"op": "merge_deep", "path": "risk_factor_identity", "value": {"alias": "A_B"}, "basis": "generated"}]}
    new_state, status = apply_state_patch_atomic(state, patch, allowed_paths=["risk_factor_identity"], current_revision=0)
    assert status["committed"] is True
    assert new_state["risk_factor_identity"]["alias"] == "A_B"


def test_canonicalization_prevents_flat_nested_split():
    state = {"risk_factor_identity.name_ua": "old", "risk_factor_identity": {"alias": "OLD"}}
    patch = {"base_revision": 0, "operations": [{"op": "merge_deep", "path": "risk_factor_identity", "value": {"alias": "NEW"}, "basis": "generated"}]}
    new_state, status = apply_state_patch_atomic(state, patch, allowed_paths=["risk_factor_identity"], current_revision=0)
    assert status["committed"] is True
    assert "risk_factor_identity.name_ua" not in new_state
    assert new_state["risk_factor_identity"] == {"name_ua": "old", "alias": "NEW"}


def test_recursive_branch_writes_are_visible_to_editor_allowlist():
    record = {"on_answer": {"approve": {"update_state": {"analyst_approval": True}}, "branch": {"revise": {"update_state": {"review.notes": "$answer"}}}}}
    expected = set(declared_writes(record))
    assert expected == {"analyst_approval", "review.notes"}
    assert set(service._alpha20_write_allowlist(record)) == expected


def test_compiled_allowlist_is_not_widened_by_yaml():
    record = {"on_answer": {"update_state": {"forbidden_by_compiled": True}}}
    compiled_element = {"state_update_allowlist": ["allowed"]}
    compiled_phase = {"output_contract": {"state_update_allowlist": ["allowed"]}}
    assert service._alpha20_write_allowlist(record, compiled_element, compiled_phase) == ["allowed"]


def test_runtime_semantic_loader_accepts_v73_without_v6_plan(tmp_path):
    source = {"graph_contract": {"entry_node": "N1"}, "state": {"schema": {"x": None}}, "nodes": [{"id": "N1", "type": "automatic", "next": "DONE"}], "gates": []}
    source_text = __import__('yaml').safe_dump(source, sort_keys=False, allow_unicode=True)
    sha = __import__('hashlib').sha256(source_text.encode()).hexdigest()
    plan = {
        "format": "ordo.runtime_semantic_plan", "format_version": "1.4-alpha20", "source": {"sha256": sha},
        "validation": {"structural_status": "PASS", "semantic_status": "PASS", "compilation_issues": []},
        "elements": {"N1": {"id": "N1", "kind": "model_node", "semantic_source": source["nodes"][0], "state_contract": {"writes": []}, "routes": [], "resources": [], "execution_traits": {"model_executed": True}, "output_contract": {"contract": "NodeExecutionResult"}}},
        "resources": {}
    }
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, 'w') as z:
        z.writestr('source/program.ordo.yaml', source_text)
        z.writestr('compiled/runtime_semantic_plan.json', json.dumps(plan))
    parsed = service.parse_playbook_package('x.zip', bio.getvalue())
    assert parsed['semantic_plan_status']['valid'] is True
    assert service.PLAYBOOK_PACKAGE['semantic_plan']['format'] == 'ordo.runtime_semantic_plan'


def test_phase_aware_semantic_dispatch_detects_ai_in_respond_policy():
    from ordo_yaml_semantics import classify
    traits = classify({
        "question": "Source?", "answer_type": "text",
        "interpretation_policy": {"transform": "AI.EXTRACT_TRIGGER_SOURCE_BLOCK($answer)"},
        "on_answer": {"normalize": {"x": "AI.NORMALIZE($answer)"}},
    }, False)
    assert traits["kind"] == "interactive_node"
    assert traits["model_executed_phases"] == ["respond"]
    assert traits["runtime_executor"] == "human_interaction"


def test_semantic_instruction_strips_gate_routes_and_history_is_not_opt_in(monkeypatch):
    element = {
        "kind": "model_gate",
        "semantic_source": {"title": "Gate", "condition": "check", "on_pass": "OK", "on_fail": "BAD"},
        "execution_traits": {"model_executed": True, "model_executed_phases": ["enter"], "requires_analyst": False},
        "state_contract": {"semantic_objects": [], "reads_hint": [], "patch_template": []},
        "routes": [{"key": "on_pass", "target": "OK"}, {"key": "on_fail", "target": "BAD"}],
        "resources": [], "output_contract": {"contract": "GateFailureOrPass"},
    }
    history = [{"role": "user", "content": "previous answer"}, {"role": "assistant", "content": "previous response"}]
    system, context, meta = service._assemble_runtime_semantic_call(element, "G", "enter", {}, history, "")
    assert "on_pass" not in context["semantic_task"]
    assert "on_fail" not in context["semantic_task"]
    assert context["recent_history"]


def test_semantic_legacy_state_updates_are_converted_not_dropped(monkeypatch):
    source = {
        "graph_contract": {"entry_node": "N1", "external_terminal_targets": ["DONE"]},
        "state": {"schema": {"x": None}},
        "nodes": [{"id": "N1", "question": "x?", "answer_type": "text", "interpretation_policy": {"transform": "AI.NORMALIZE($answer)"}, "update_state": {"x": "$answer.x"}, "next": "DONE"}],
        "gates": [],
    }
    sem = {
        "id": "N1", "kind": "model_node", "semantic_source": source["nodes"][0],
        "execution_traits": {"model_executed": True, "model_executed_phases": ["respond"], "runtime_executor": "human_interaction", "requires_analyst": True},
        "state_contract": {"writes": ["x"], "semantic_objects": [], "reads_hint": [], "patch_template": []},
        "routes": [{"key": "next", "target": "DONE", "kind": "canonical"}], "resources": [],
        "output_contract": {"contract": "NodeExecutionResult", "required": ["assistant_message", "state_patch", "needs_analyst", "next_intent"]},
    }
    service.PLAYBOOK_PACKAGE.update({"id": "pkg", "source": source, "semantic_plan": {"elements": {"N1": sem}, "resources": {}}, "semantic_plan_status": {"valid": True}, "resources": {}})
    monkeypatch.setattr(service, "_live_credentials", lambda payload: {"provider": "custom", "base_url": "http://x", "api_style": "chat_completions", "model": "stub", "api_key": None})
    raw = json.dumps({"assistant_message": "ok", "state_updates": {"x": "kept"}, "route_key": "next", "needs_analyst": False, "next_intent": "continue_default_path"})
    monkeypatch.setattr(service, "_provider_api_call", lambda credentials, system, context: ({}, {}, raw, {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2, "cached_tokens": 0, "reasoning_tokens": 0}))
    result = service._call_openai_live({"package_id": "pkg", "source": source, "current_id": "N1", "phase": "respond", "analyst_input": "value", "state": {}, "history": []})
    assert result["state"]["x"] == "kept"
    assert result["debug"]["alpha20"]["state_patch"]["operations"]


def test_artifact_presenter_runtime_executor_does_not_fall_back_to_model(monkeypatch):
    source = {
        "graph_contract": {"entry_node": "N1", "external_terminal_targets": ["DONE"]},
        "state": {"schema": {}},
        "nodes": [{"id": "N1", "action": "ARTIFACT.PRESENT_FOR_REVIEW", "artifact": {"path": "generated_outputs/X.md"}, "next": "DONE"}],
        "gates": [],
    }
    sem = {
        "id": "N1", "kind": "deterministic_operation", "semantic_source": source["nodes"][0],
        "execution_traits": {"model_executed": False, "model_executed_phases": [], "runtime_executor": "artifact_presenter", "requires_analyst": False},
        "state_contract": {"writes": [], "semantic_objects": [], "reads_hint": [], "patch_template": []},
        "routes": [{"key": "next", "target": "DONE", "kind": "canonical"}], "resources": [],
        "output_contract": {"contract": "NodeExecutionResult"},
    }
    service.PLAYBOOK_PACKAGE.update({"id": "pkg2", "source": source, "semantic_plan": {"elements": {"N1": sem}, "resources": {}}, "semantic_plan_status": {"valid": True}, "resources": {}})
    monkeypatch.setattr(service, "_live_credentials", lambda payload: {"provider": "custom", "base_url": "http://x", "api_style": "chat_completions", "model": "stub", "api_key": None})
    monkeypatch.setattr(service, "_provider_api_call", lambda *a, **k: (_ for _ in ()).throw(AssertionError("model must not be called")))
    result = service._call_openai_live({"package_id": "pkg2", "source": source, "current_id": "N1", "phase": "enter", "state": {}, "history": []})
    assert result["next_id"] == "DONE"
    assert result["debug"]["runtime"]["runtime_executor"] == "artifact_presenter"


def test_structured_interactive_proposal_requires_model_respond():
    from ordo_yaml_semantics import classify
    traits = classify({
        "question": "Confirm proposal", "answer_type": "structured",
        "proposal_generation": {"purpose": "draft"},
        "on_answer": {"update_state": {"identity.alias": "$answer.alias"}},
    }, False)
    assert traits["model_executed_phases"] == ["enter", "respond"]


def test_named_answer_normalize_requires_model_respond_without_ai_opcode():
    from ordo_yaml_semantics import classify
    traits = classify({
        "question": "Schedules?", "answer_type": "text",
        "on_answer": {"normalize": {"policy.rows": [{"periodicity": "$answer.default_schedule"}]}}
    }, False)
    assert traits["model_executed_phases"] == ["respond"]


def test_terminal_executor_completes_without_model(monkeypatch):
    source = {"graph_contract": {"entry_node": "T"}, "state": {"schema": {}}, "nodes": [{"id": "T", "terminal": True}], "gates": []}
    sem = {"id": "T", "kind": "terminal", "semantic_source": source["nodes"][0],
           "execution_traits": {"model_executed": False, "model_executed_phases": [], "runtime_executor": "terminal", "requires_analyst": False},
           "state_contract": {"writes": [], "semantic_objects": [], "reads_hint": [], "patch_template": []},
           "routes": [], "resources": [], "output_contract": {"contract": "NodeExecutionResult"}}
    service.PLAYBOOK_PACKAGE.update({"id": "pkg-terminal", "source": source, "semantic_plan": {"elements": {"T": sem}, "resources": {}}, "semantic_plan_status": {"valid": True}, "resources": {}})
    monkeypatch.setattr(service, "_live_credentials", lambda payload: {"provider": "custom", "base_url": "http://x", "api_style": "chat_completions", "model": "stub", "api_key": None})
    monkeypatch.setattr(service, "_provider_api_call", lambda *a, **k: (_ for _ in ()).throw(AssertionError("model must not be called")))
    result = service._call_openai_live({"package_id": "pkg-terminal", "source": source, "current_id": "T", "phase": "enter", "state": {}, "history": []})
    assert result["run_status"] == "completed"
    assert result["terminal"] is True


def test_artifact_presenter_uses_expected_path(monkeypatch):
    source = {"graph_contract": {"entry_node": "N1", "external_terminal_targets": ["DONE"]}, "state": {"schema": {}},
              "nodes": [{"id": "N1", "action": "ARTIFACT.PRESENT_FOR_REVIEW", "artifact": {"expected_path": "generated_outputs/Expected.md"}, "next": "DONE"}], "gates": []}
    sem = {"id": "N1", "kind": "deterministic_operation", "semantic_source": source["nodes"][0],
           "execution_traits": {"model_executed": False, "model_executed_phases": [], "runtime_executor": "artifact_presenter", "requires_analyst": False},
           "state_contract": {"writes": [], "semantic_objects": [], "reads_hint": [], "patch_template": []},
           "routes": [{"key": "next", "target": "DONE", "kind": "canonical"}], "resources": [], "output_contract": {"contract": "NodeExecutionResult"}}
    service.PLAYBOOK_PACKAGE.update({"id": "pkg-expected", "source": source, "semantic_plan": {"elements": {"N1": sem}, "resources": {}}, "semantic_plan_status": {"valid": True}, "resources": {}})
    monkeypatch.setattr(service, "_live_credentials", lambda payload: {"provider": "custom", "base_url": "http://x", "api_style": "chat_completions", "model": "stub", "api_key": None})
    result = service._call_openai_live({"package_id": "pkg-expected", "source": source, "current_id": "N1", "phase": "enter", "state": {}, "history": []})
    assert "generated_outputs/Expected.md" in result["assistant_message"]
