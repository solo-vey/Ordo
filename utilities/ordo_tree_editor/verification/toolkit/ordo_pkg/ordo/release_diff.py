from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json

from .loader import load_package
from .reporter import write_json


def _read_json(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Provenance file not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def _artifact_map(items: list[dict[str, Any]] | None) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in items or []:
        path = item.get("path")
        if path:
            out[str(path)] = item
    return out


def _compare_artifact_sets(base_items: list[dict[str, Any]] | None, head_items: list[dict[str, Any]] | None) -> dict[str, Any]:
    base = _artifact_map(base_items)
    head = _artifact_map(head_items)
    base_keys = set(base)
    head_keys = set(head)
    added = sorted(head_keys - base_keys)
    removed = sorted(base_keys - head_keys)
    changed = []
    unchanged = []
    for key in sorted(base_keys & head_keys):
        b = base[key]
        h = head[key]
        if b.get("sha256") != h.get("sha256") or b.get("bytes") != h.get("bytes"):
            changed.append({
                "path": key,
                "base_sha256": b.get("sha256"),
                "head_sha256": h.get("sha256"),
                "base_bytes": b.get("bytes"),
                "head_bytes": h.get("bytes"),
            })
        else:
            unchanged.append(key)
    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged_count": len(unchanged),
        "summary": {
            "added": len(added),
            "removed": len(removed),
            "changed": len(changed),
            "unchanged": len(unchanged),
        },
    }


def _get(d: dict[str, Any], *path: str) -> Any:
    cur: Any = d
    for p in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(p)
    return cur


def _compare_scalar(base: dict[str, Any], head: dict[str, Any], path: tuple[str, ...]) -> dict[str, Any] | None:
    b = _get(base, *path)
    h = _get(head, *path)
    if b != h:
        return {"field": ".".join(path), "base": b, "head": h}
    return None


def diff_release_provenance(package_path: str | Path, *, base: str | Path, head: str | Path | None = None, out: str | Path | None = None) -> dict[str, Any]:
    """Compare two release provenance manifests and write a release diff report.

    The command is intentionally provenance-based: it does not infer meaning from
    arbitrary files. It compares the controlled evidence chain recorded by M14.
    """
    root, manifest, source, tests = load_package(package_path)
    reports_dir = root / manifest.get("reports", "reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    base_path = Path(base)
    head_path = Path(head) if head else reports_dir / "release_provenance.json"
    base_data = _read_json(base_path)
    head_data = _read_json(head_path)

    scalar_changes = []
    for field in [
        ("toolchain", "ordo_cli_version"),
        ("toolchain", "ordo_language_version"),
        ("package", "name"),
        ("package", "version"),
        ("package", "control_level"),
        ("package", "execution_mode"),
        ("release", "status"),
        ("release", "handoff_status"),
        ("release", "archive", "sha256"),
    ]:
        change = _compare_scalar(base_data, head_data, field)
        if change:
            scalar_changes.append(change)

    sections = {
        "source_files": _compare_artifact_sets(_get(base_data, "inputs", "source_files"), _get(head_data, "inputs", "source_files")),
        "lock_files": _compare_artifact_sets(_get(base_data, "inputs", "lock_files"), _get(head_data, "inputs", "lock_files")),
        "compiled_ir": _compare_artifact_sets(_get(base_data, "derived_artifacts", "compiled_ir"), _get(head_data, "derived_artifacts", "compiled_ir")),
        "runtime_trace_and_state": _compare_artifact_sets(_get(base_data, "derived_artifacts", "runtime_trace_and_state"), _get(head_data, "derived_artifacts", "runtime_trace_and_state")),
        "generated_outputs": _compare_artifact_sets(_get(base_data, "derived_artifacts", "generated_outputs"), _get(head_data, "derived_artifacts", "generated_outputs")),
        "reports": _compare_artifact_sets(_get(base_data, "reports"), _get(head_data, "reports")),
    }

    changed_sections = []
    for name, section in sections.items():
        s = section.get("summary", {})
        if s.get("added") or s.get("removed") or s.get("changed"):
            changed_sections.append(name)

    archive_base = _get(base_data, "release", "archive", "sha256")
    archive_head = _get(head_data, "release", "archive", "sha256")
    reproducible = archive_base == archive_head and not scalar_changes and not changed_sections

    report = {
        "schema": "ordo.release_diff.v0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "identical" if reproducible else "changed",
        "package": {
            "root": str(root),
            "name": manifest.get("name"),
            "version": manifest.get("version"),
        },
        "base": {"path": str(base_path), "package": _get(base_data, "package", "name"), "version": _get(base_data, "package", "version")},
        "head": {"path": str(head_path), "package": _get(head_data, "package", "name"), "version": _get(head_data, "package", "version")},
        "reproducibility": {
            "archive_hash_equal": archive_base == archive_head,
            "fully_reproducible_against_base": reproducible,
            "base_archive_sha256": archive_base,
            "head_archive_sha256": archive_head,
        },
        "scalar_changes": scalar_changes,
        "sections": sections,
        "summary": {
            "scalar_changes": len(scalar_changes),
            "changed_sections": changed_sections,
            "changed_sections_count": len(changed_sections),
            "source_changed": "source_files" in changed_sections,
            "lock_changed": "lock_files" in changed_sections,
            "ir_changed": "compiled_ir" in changed_sections,
            "runtime_changed": "runtime_trace_and_state" in changed_sections,
            "outputs_changed": "generated_outputs" in changed_sections,
            "reports_changed": "reports" in changed_sections,
        },
    }
    out_path = Path(out) if out else reports_dir / "release_diff_report.json"
    write_json(out_path, report)
    return report
