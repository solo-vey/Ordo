from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
import hashlib
import json

import yaml


def _walk(value: Any, path: str = "root"):
    if isinstance(value, dict):
        yield path, value
        for key, child in value.items():
            yield from _walk(child, f"{path}.{key}")
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            yield from _walk(child, f"{path}[{idx}]")


def reconcile_prompt_registry(package_root: str | Path) -> dict[str, Any]:
    root = Path(package_root)
    source_path = root / "source" / "program.ordo.yaml"
    manifest_path = root / "PROMPT_MANIFEST.json"
    source = yaml.safe_load(source_path.read_text(encoding="utf-8")) or {}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    registry_entries = source.get("prompt_registry", {}).get("prompts", []) or []
    registry = {entry["prompt_id"]: entry for entry in registry_entries}
    manifest_entries = {entry["prompt_id"]: entry for entry in manifest.get("prompts", [])}

    attachments: dict[str, list[dict[str, str]]] = defaultdict(list)
    for path, item in _walk(source):
        for ref in item.get("prompt_refs", []) or []:
            if isinstance(ref, dict) and ref.get("prompt_id"):
                attachments[str(ref["prompt_id"])].append({"channel": "prompt_ref", "path": path})

    startup = source.get("startup_package_profile", {}) or {}
    for idx, mode in enumerate(startup.get("startup_modes", []) or []):
        if isinstance(mode, dict) and mode.get("prompt_id"):
            attachments[str(mode["prompt_id"])].append({
                "channel": "startup_mode",
                "path": f"startup_package_profile.startup_modes[{idx}]",
            })

    ids = [entry.get("prompt_id") for entry in registry_entries]
    duplicate_ids = sorted([prompt_id for prompt_id, count in Counter(ids).items() if count > 1])
    missing_manifest = sorted(set(registry) - set(manifest_entries))
    extra_manifest = sorted(set(manifest_entries) - set(registry))
    missing_files: list[str] = []
    checksum_mismatches: list[str] = []
    deprecated_targets: list[str] = []
    active: list[str] = []
    conditional_dormant: list[str] = []
    orphaned: list[str] = []

    for prompt_id, entry in registry.items():
        path = root / str(entry.get("path", ""))
        if not path.is_file():
            missing_files.append(prompt_id)
        m = manifest_entries.get(prompt_id)
        if m and path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != m.get("sha256") or path.stat().st_size != m.get("bytes"):
                checksum_mismatches.append(prompt_id)
        if str(entry.get("lifecycle", "stable")) == "deprecated" and attachments.get(prompt_id):
            deprecated_targets.append(prompt_id)
        if attachments.get(prompt_id):
            active.append(prompt_id)
        elif str(entry.get("required", "")).lower() == "conditional":
            conditional_dormant.append(prompt_id)
        else:
            orphaned.append(prompt_id)

    errors = duplicate_ids + missing_manifest + extra_manifest + missing_files + checksum_mismatches + deprecated_targets + orphaned
    return {
        "schema_version": "ordo.prompt_registry_reconciliation.v1",
        "package": source.get("program", {}).get("id") or source.get("id") or root.name,
        "registry_entries": len(registry_entries),
        "manifest_entries": len(manifest_entries),
        "attachment_count": sum(len(v) for v in attachments.values()),
        "active_prompt_ids": sorted(active),
        "conditional_dormant_prompt_ids": sorted(conditional_dormant),
        "orphaned_prompt_ids": sorted(orphaned),
        "duplicate_prompt_ids": duplicate_ids,
        "missing_manifest_entries": missing_manifest,
        "extra_manifest_entries": extra_manifest,
        "missing_prompt_files": sorted(missing_files),
        "checksum_mismatches": sorted(checksum_mismatches),
        "deprecated_prompt_refs": sorted(deprecated_targets),
        "attachments": {key: value for key, value in sorted(attachments.items())},
        "status": "passed" if not errors else "failed",
    }
