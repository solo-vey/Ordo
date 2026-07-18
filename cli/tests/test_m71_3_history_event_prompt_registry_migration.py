from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT / "packages" / "history_event_guided_intake"
PROGRAM = PKG / "source" / "program.ordo.yaml"
MANIFEST = PKG / "PROMPT_MANIFEST.json"
ALLOWED_PHASES = {
    "before_question",
    "during_clarification",
    "after_answer",
    "before_confirmation",
    "on_open_gap",
    "on_gate_fail",
    "before_artifact_generation",
}
ID_RE = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+\.v[1-9][0-9]*$")


def _program() -> dict:
    return yaml.safe_load(PROGRAM.read_text())


def _prompt_refs(value):
    if isinstance(value, dict):
        for ref in value.get("prompt_refs", []):
            yield ref
        for nested in value.values():
            yield from _prompt_refs(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _prompt_refs(nested)


def test_registry_uses_stable_semantic_versioned_ids() -> None:
    entries = _program()["prompt_registry"]["prompts"]
    ids = [entry["prompt_id"] for entry in entries]
    assert len(ids) == len(set(ids)) == 13
    for entry in entries:
        prompt_id = entry["prompt_id"]
        assert ID_RE.fullmatch(prompt_id)
        assert entry["prompt_family"] == prompt_id.rsplit(".v", 1)[0]
        assert entry["version"] == int(prompt_id.rsplit(".v", 1)[1])
        assert entry["supersedes"] is None
        assert Path(entry["path"]).name == f"{prompt_id}.md"
        assert not Path(entry["path"]).parts[1:2] in [("nodes",), ("artifacts",), ("repair",), ("runtime",)]


def test_all_prompt_refs_resolve_and_use_controlled_phases() -> None:
    program = _program()
    ids = {entry["prompt_id"] for entry in program["prompt_registry"]["prompts"]}
    refs = list(_prompt_refs(program))
    assert refs
    assert {ref["prompt_id"] for ref in refs} <= ids
    assert {ref["use"] for ref in refs} <= ALLOWED_PHASES


def test_manifest_covers_registry_and_checksums_match() -> None:
    program = _program()
    manifest = json.loads(MANIFEST.read_text())
    registry = {entry["prompt_id"]: entry for entry in program["prompt_registry"]["prompts"]}
    manifest_entries = {entry["prompt_id"]: entry for entry in manifest["prompts"]}
    assert manifest["milestone"] == "M71.3"
    assert manifest["identity_model"] == "stable_semantic_prompt_ids_v1"
    assert registry.keys() == manifest_entries.keys()
    for prompt_id, entry in manifest_entries.items():
        path = PKG / entry["path"]
        assert path.is_file()
        assert entry["prompt_family"] == registry[prompt_id]["prompt_family"]
        assert entry["version"] == registry[prompt_id]["version"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]
        assert path.stat().st_size == entry["bytes"]


def test_legacy_ids_exist_only_as_compatibility_metadata() -> None:
    manifest = json.loads(MANIFEST.read_text())
    legacy = {entry["legacy_prompt_id"] for entry in manifest["legacy_id_mappings"]}
    assert len(legacy) == 13
    program_text = PROGRAM.read_text()
    for legacy_id in legacy:
        assert f"prompt_id: {legacy_id}" not in program_text


def test_migration_map_is_complete() -> None:
    csv_text = (PKG / "PROMPT_ID_MIGRATION_MAP.csv").read_text()
    md_text = (PKG / "PROMPT_ID_MIGRATION_MAP.md").read_text()
    manifest = json.loads(MANIFEST.read_text())
    for item in manifest["legacy_id_mappings"]:
        assert item["legacy_prompt_id"] in csv_text and item["prompt_id"] in csv_text
        assert item["legacy_prompt_id"] in md_text and item["prompt_id"] in md_text
