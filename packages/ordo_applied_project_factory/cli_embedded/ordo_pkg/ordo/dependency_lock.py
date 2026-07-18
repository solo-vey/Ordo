from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .loader import load_package
from .output_registry import resolve_template_set
from .reporter import write_json

LOCKFILE_NAME = "ordo.lock.json"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_tree(root: Path) -> str:
    h = hashlib.sha256()
    if not root.exists():
        return ""
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = str(path.relative_to(root)).replace("\\", "/")
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(_sha256_file(path).encode("ascii"))
        h.update(b"\n")
    return h.hexdigest()


def _rel(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base)).replace("\\", "/")
    except ValueError:
        return str(path)


def _dependency(kind: str, dep_id: str, version: str, source: str, root_path: Path, catalog_path: Path | None, workspace_root: Path) -> dict[str, Any]:
    return {
        "kind": kind,
        "id": dep_id,
        "version": str(version),
        "source": source,
        "resolved_root": _rel(root_path, workspace_root),
        "catalog": _rel(catalog_path, workspace_root) if catalog_path else None,
        "hash": {
            "algorithm": "sha256-tree",
            "value": _sha256_tree(root_path),
        },
    }


def _find_workspace_root(package_root: Path) -> Path:
    # In the current repo layout packages live under <workspace>/packages/<pkg>.
    # Fall back to package parent when used standalone.
    candidate = package_root.parent.parent
    if (candidate / "output_templates").exists() or (candidate / "language").exists() or (candidate / "cli").exists():
        return candidate
    return package_root


def resolve_dependencies(package_path: str | Path) -> dict[str, Any]:
    """Resolve package dependencies into a deterministic lock structure.

    M10 locks template sets now and reserves stable sections for future
    libraries, profiles, and domain packs. This keeps the format forward
    compatible without pretending those dependency types are implemented yet.
    """
    package_root, manifest, source, tests = load_package(package_path)
    workspace_root = _find_workspace_root(package_root)
    dependencies: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    for item in manifest.get("output_template_sets") or []:
        dep_id = item.get("id")
        version = str(item.get("version") or "").strip()
        preferred_source = item.get("source")
        if not dep_id or not version:
            warnings.append({
                "code": "TEMPLATE_SET_LOCK_SKIPPED",
                "message": "output_template_sets entry must have id and version to be locked.",
                "entry": item,
            })
            continue
        catalog, catalog_path, meta = resolve_template_set(package_root, dep_id, version, preferred_source=preferred_source)
        dependencies.append(_dependency(
            kind="output_template_set",
            dep_id=dep_id,
            version=version,
            source=meta.get("source", preferred_source or "unknown"),
            root_path=Path(meta["root"]),
            catalog_path=Path(meta["catalog"]),
            workspace_root=workspace_root,
        ))

    # Reserved future dependency sections. If present in ordo.yml, they are locked
    # as manifest declarations without external resolution yet.
    for manifest_key, kind in [
        ("libraries", "library"),
        ("profiles", "profile"),
        ("domain_packs", "domain_pack"),
    ]:
        for item in manifest.get(manifest_key) or []:
            dep_id = item.get("id") or item.get(kind) or item.get("name")
            version = str(item.get("version") or "").strip()
            source_name = item.get("source", "manifest_declared")
            if not dep_id or not version:
                warnings.append({
                    "code": "DEPENDENCY_LOCK_INCOMPLETE",
                    "message": f"{manifest_key} entry must have id/name and version to be locked.",
                    "entry": item,
                })
                continue
            dependencies.append({
                "kind": kind,
                "id": dep_id,
                "version": version,
                "source": source_name,
                "resolved_root": None,
                "catalog": None,
                "hash": {"algorithm": "manifest-entry-sha256", "value": hashlib.sha256(json.dumps(item, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()},
                "resolution_status": "declared_only",
            })

    lock = {
        "lockfile_version": "1.0",
        "generated_by": "ordo-cli 0.6.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "package": {
            "name": manifest.get("name") or ((source.get("ordo") or {}).get("package")),
            "version": manifest.get("version"),
            "ordo_version": manifest.get("ordo_version") or ((source.get("ordo") or {}).get("version")),
            "root": _rel(package_root, workspace_root),
        },
        "dependencies": dependencies,
        "summary": {
            "dependencies_total": len(dependencies),
            "warnings": len(warnings),
            "kinds": sorted(set(d["kind"] for d in dependencies)),
        },
        "warnings": warnings,
    }
    return lock


def write_lock(package_path: str | Path, out: str | Path | None = None) -> dict[str, Any]:
    package_root, manifest, source, tests = load_package(package_path)
    lock = resolve_dependencies(package_root)
    lock_path = Path(out).resolve() if out else package_root / LOCKFILE_NAME
    write_json(lock_path, lock)
    reports_dir = package_root / manifest.get("reports", "reports")
    write_json(reports_dir / "lock_report.json", {
        "status": "passed" if not lock.get("warnings") else "passed_with_warnings",
        "lockfile": str(lock_path.relative_to(package_root)) if lock_path.is_relative_to(package_root) else str(lock_path),
        "summary": lock.get("summary"),
        "warnings": lock.get("warnings", []),
    })
    return lock


def validate_lock(package_path: str | Path) -> dict[str, Any]:
    package_root, manifest, source, tests = load_package(package_path)
    lock_path = package_root / LOCKFILE_NAME
    current = resolve_dependencies(package_root)
    if not lock_path.exists():
        report = {
            "status": "failed",
            "code": "LOCKFILE_MISSING",
            "message": f"{LOCKFILE_NAME} is required for release validation.",
            "expected_path": LOCKFILE_NAME,
        }
        write_json(package_root / manifest.get("reports", "reports") / "lock_validation_report.json", report)
        return report
    saved = json.loads(lock_path.read_text(encoding="utf-8"))
    # Compare only deterministic dependency identity/hash fields, not generated_at.
    saved_deps = saved.get("dependencies", [])
    current_deps = current.get("dependencies", [])
    status = "passed" if saved_deps == current_deps else "failed"
    report = {
        "status": status,
        "lockfile": LOCKFILE_NAME,
        "saved_dependencies_total": len(saved_deps),
        "current_dependencies_total": len(current_deps),
        "issues": [] if status == "passed" else [{
            "code": "LOCKFILE_OUT_OF_DATE",
            "message": "Resolved dependencies differ from ordo.lock.json. Run `ordo lock <package>`.",
        }],
    }
    write_json(package_root / manifest.get("reports", "reports") / "lock_validation_report.json", report)
    return report
