from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT / "packages" / "history_event_guided_intake"
PHASES = {
    "before_question", "during_clarification", "after_answer",
    "before_confirmation", "on_open_gap", "on_gate_fail",
    "before_artifact_generation",
}


def _program() -> dict:
    return yaml.safe_load((PKG / "source/program.ordo.yaml").read_text(encoding="utf-8"))


def _manifest() -> dict:
    return json.loads((PKG / "PROMPT_MANIFEST.json").read_text(encoding="utf-8"))


def _objects_with_refs(value):
    if isinstance(value, dict):
        if "prompt_refs" in value:
            yield value
        for child in value.values():
            yield from _objects_with_refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from _objects_with_refs(child)


def test_all_runtime_prompt_refs_resolve_phase_and_checksum() -> None:
    manifest = {p["prompt_id"]: p for p in _manifest()["prompts"]}
    refs = []
    for obj in _objects_with_refs(_program()):
        refs.extend(obj["prompt_refs"])
    assert refs
    for ref in refs:
        assert ref["use"] in PHASES
        entry = manifest[ref["prompt_id"]]
        path = PKG / entry["path"]
        assert path.is_file()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]


def test_same_phase_order_is_source_list_order() -> None:
    program = _program()
    node = next(n for n in program["nodes"] if n["id"] == "N_VALUE_SEMANTICS")
    assert [(r["prompt_id"], r["use"]) for r in node["prompt_refs"]] == [
        ("hp.normalization.value_comparison.v1", "before_question"),
        ("hp.normalization.value_comparison.v1", "during_clarification"),
    ]


def test_trace_schema_forbids_prompt_text_and_navigation_fields() -> None:
    schema = json.loads((PKG / "source/contracts/runtime/prompt_application_trace.schema.json").read_text())
    item = schema["properties"]["prompt_refs_applied"]["items"]
    assert item["additionalProperties"] is False
    assert "prompt_text" not in item["properties"]
    assert "prompt_body" not in item["properties"]
    assert "next_node" not in item["properties"]


def test_trace_example_matches_manifest_and_source_order() -> None:
    example = json.loads((PKG / "source/contracts/runtime/prompt_application_trace.example.json").read_text())
    manifest = {p["prompt_id"]: p for p in _manifest()["prompts"]}
    assert example["runtime_step_id"] == "N_VALUE_SEMANTICS"
    assert [x["ordinal"] for x in example["prompt_refs_applied"]] == [1, 2]
    for evidence in example["prompt_refs_applied"]:
        assert evidence["sha256"] == manifest[evidence["prompt_id"]]["sha256"]
        assert evidence["use"] in PHASES


def test_runtime_instruction_preserves_ir_authority_and_hidden_prompt_text() -> None:
    text = (PKG / "START_HERE_RUNTIME_MODE.md").read_text(encoding="utf-8")
    assert "CLI/JSON IR selects the current executable step" in text
    assert "without exposing prompt text" in text
    assert "record prompt application evidence" in text
    assert "prompt_id" in text and "sha256" in text and "ordinal" in text


def test_prompt_files_do_not_claim_explicit_navigation_authority() -> None:
    forbidden = [
        r"\bset next_node\b", r"\bchange next_node\b", r"\bskip required node\b",
        r"\bbypass gate\b", r"\bmark approved\b", r"\bwrite state directly\b",
    ]
    for path in (PKG / "prompts").glob("*.md"):
        text = path.read_text(encoding="utf-8").lower()
        for pattern in forbidden:
            assert not re.search(pattern, text), f"{path.name}: {pattern}"
