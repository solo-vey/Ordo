from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("alpha20_runtime", ROOT / "alpha20_runtime.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def patch(ops, rev=0):
    return {"base_revision": rev, "operations": ops}


def test_state_patch_atomic_success():
    state = {"trigger_logic": {"case_policy": "case_sensitive"}, "rows": []}
    p = patch([
        {"op": "set", "path": "trigger_logic.trim_policy", "value": "no_trim", "basis": "analyst_input"},
        {"op": "append", "path": "rows", "value": {"id": 1}, "basis": "generated"},
    ])
    new_state, result = mod.apply_state_patch_atomic(state, p, allowed_paths=["trigger_logic", "rows"], current_revision=0)
    assert result["committed"] is True
    assert new_state["trigger_logic"]["trim_policy"] == "no_trim"
    assert new_state["rows"] == [{"id": 1}]
    assert state["rows"] == []


def test_state_patch_is_atomic_on_failure():
    state = {"x": 1, "rows": {}}
    p = patch([
        {"op": "set", "path": "x", "value": 2},
        {"op": "append", "path": "rows", "value": 3},
    ])
    new_state, result = mod.apply_state_patch_atomic(state, p, allowed_paths=["x", "rows"], current_revision=0)
    assert result["committed"] is False
    assert new_state == state


def test_write_allowlist_is_fail_closed_when_missing():
    p = patch([{"op": "set", "path": "secret.value", "value": 1}])
    result = mod.validate_state_patch(p)
    assert result["valid"] is False
    assert any("outside write allowlist" in e for e in result["errors"])


def test_write_allowlist_rejects_outside_path():
    p = patch([{"op": "set", "path": "secret.value", "value": 1}])
    result = mod.validate_state_patch(p, allowed_paths=["trigger_logic"])
    assert result["valid"] is False
    assert any("outside write allowlist" in e for e in result["errors"])


def test_base_revision_is_required_and_checked():
    missing = mod.validate_state_patch({"operations": []}, allowed_paths=["x"], current_revision=0)
    assert missing["valid"] is False
    assert "base_revision is required" in " ".join(missing["errors"])
    stale = mod.validate_state_patch(patch([], rev=2), allowed_paths=["x"], current_revision=3)
    assert stale["valid"] is False
    assert "base_revision mismatch" in " ".join(stale["errors"])


def test_merge_deep_preserves_siblings():
    state = {"trigger_logic": {"source": {"field": "status", "type": "string"}, "case_policy": "sensitive"}}
    p = patch([{"op": "merge_deep", "path": "trigger_logic", "value": {"source": {"field": "statusCode"}}, "basis": "recovery"}])
    new_state, result = mod.apply_state_patch_atomic(state, p, allowed_paths=["trigger_logic"], current_revision=0)
    assert result["committed"] is True
    assert new_state["trigger_logic"]["source"] == {"field": "statusCode", "type": "string"}
    assert new_state["trigger_logic"]["case_policy"] == "sensitive"


def test_merge_row_updates_only_matching_row_and_preserves_columns():
    state = {"catalog": {"rows": [
        {"tc_id": "TC-1", "scenario": "old", "short_input": "x", "expected_result": "yes"},
        {"tc_id": "TC-2", "scenario": "keep", "short_input": "y", "expected_result": "no"},
    ]}}
    p = patch([{"op": "merge_row", "path": "catalog.rows", "row_key": "tc_id", "row_match": "TC-1", "value": {"scenario": "new"}, "basis": "recovery"}])
    new_state, result = mod.apply_state_patch_atomic(state, p, allowed_paths=["catalog.rows"], current_revision=0)
    assert result["committed"] is True
    assert new_state["catalog"]["rows"][0] == {"tc_id": "TC-1", "scenario": "new", "short_input": "x", "expected_result": "yes"}
    assert new_state["catalog"]["rows"][1]["scenario"] == "keep"


def test_gate_failure_is_structured():
    failure = mod.normalize_gate_failure(
        "G_TEST",
        failed_checks=[{"check_id": "PM-005", "summary": "schema mismatch"}],
        missing_coverage=["schedule"],
        affected_state=["functional_test_catalog"],
    )
    assert failure["status"] == "failed"
    assert failure["failed_checks"][0]["check_id"] == "PM-005"
    assert failure["missing_coverage"] == ["schedule"]
    for key in ("invalid_state", "missing_information", "evidence"):
        assert key in failure


def test_legacy_updates_preserve_unknown_provenance_and_merge_semantics():
    p = mod.legacy_updates_to_state_patch({"a": {"b": 3}, "x.y": 4}, base_revision=0)
    assert p["base_revision"] == 0
    assert p["operations"][0] == {"op": "merge_deep", "path": "a", "value": {"b": 3}, "basis": "legacy_unknown"}
    assert p["operations"][1] == {"op": "set", "path": "x.y", "value": 4, "basis": "legacy_unknown"}


def test_collection_value_schema_enforced():
    schema = {"catalog.rows": {"type":"array", "items":{"type":"object", "required":["id","name"], "properties":{"id":{"type":"string"},"name":{"type":"string"}}, "additionalProperties":False}}}
    good = patch([{"op":"set","path":"catalog.rows","value":[{"id":"A","name":"Alpha"}]}])
    bad = patch([{"op":"set","path":"catalog.rows","value":[{"id":"A"}]}])
    assert mod.validate_state_patch(good, allowed_paths=["catalog.rows"], current_revision=0, value_schemas=schema)["valid"]
    result = mod.validate_state_patch(bad, allowed_paths=["catalog.rows"], current_revision=0, value_schemas=schema)
    assert not result["valid"] and any("name is required" in e for e in result["errors"])

def test_collection_value_schema_atomic_rejection():
    schema = {"catalog.rows": {"type":"array", "items":{"type":"object", "required":["id"], "properties":{"id":{"type":"string"}}, "additionalProperties":False}}}
    state={"catalog":{"rows":[{"id":"OLD"}]}}
    bad=patch([{"op":"set","path":"catalog.rows","value":[{"wrong":"X"}]}])
    new_state, status = mod.apply_state_patch_atomic(state,bad,allowed_paths=["catalog.rows"],current_revision=0,value_schemas=schema)
    assert not status["committed"] and new_state == state
