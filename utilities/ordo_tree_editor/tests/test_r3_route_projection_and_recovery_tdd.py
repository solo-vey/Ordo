from __future__ import annotations
import json
from integrated_compiler.compile_runtime_semantic_plan_v7 import extract_routes
import editor_service as es


def test_tool_args_do_not_become_runtime_routes():
    element = {
        "id": "N_MAT",
        "action": "PACKAGE.MATERIALIZE",
        "args": ["--step", "N_MAT"],
        "next": "G_VALIDATE",
        "template": "x.md",
        "bindings": "x.yaml",
        "output": "out.md",
    }
    routes = extract_routes(element, {"N_MAT", "G_VALIDATE"}, is_gate=False)
    assert routes == [{"key": "next", "target": "G_VALIDATE", "kind": "canonical", "source_path": "next"}]


def test_semantic_recovery_next_alias_is_preserved_as_next_id():
    raw = json.dumps({
        "status": "resolved",
        "assistant_message": "",
        "reason": "route recovery",
        "state_patch": {"base_revision": 7, "operations": []},
        "next": "G_VALIDATE",
    })
    candidate = es._semantic_recovery_candidate_from_raw(raw, current_revision=7, allowed_paths=set())
    assert candidate["next_id"] == "G_VALIDATE"
    assert "next" not in candidate
    assert any(x.get("kind") == "next_to_next_id" for x in candidate.get("_ordo_normalization", []))
