from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any
import json

from .loader import load_package
from .dependency_lock import write_lock, validate_lock
from .reporter import write_json


def _rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path)


def _load_lock(root: Path) -> dict[str, Any]:
    lock_path = root / "ordo.lock.json"
    if not lock_path.exists():
        return write_lock(root)
    return json.loads(lock_path.read_text(encoding="utf-8"))


def check_conflicts(package_path: str | Path) -> dict[str, Any]:
    """Detect unresolved dependency/layer conflicts.

    M11 is intentionally conservative. It supports explicit conflicts declared in
    `ordo.yml` and basic duplicate dependency/hash conflicts in the lockfile. It
    does not infer semantic conflicts between arbitrary templates or domain rules.
    """
    root, manifest, source, tests = load_package(package_path)
    reports_dir = root / manifest.get("reports", "reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    lock_validation = validate_lock(root)
    if lock_validation.get("status") != "passed":
        lock = write_lock(root)
    else:
        lock = _load_lock(root)
    dependencies = lock.get("dependencies") or []
    issues: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    by_key: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for dep in dependencies:
        by_key[(dep.get("kind"), dep.get("id"))].append(dep)
    for (kind, dep_id), items in by_key.items():
        hashes = {((item.get("hash") or {}).get("value")) for item in items}
        versions = {str(item.get("version")) for item in items}
        if len(items) > 1 and (len(hashes) > 1 or len(versions) > 1):
            issues.append({
                "code": "DEPENDENCY_RESOLUTION_CONFLICT",
                "message": f"Dependency {kind}:{dep_id} resolves to multiple versions or hashes.",
                "kind": kind,
                "id": dep_id,
                "versions": sorted(versions),
                "hashes": sorted(h for h in hashes if h),
            })

    # Declared conflicts are explicit by design; every one must have human-approved override.
    declared_conflicts = manifest.get("dependency_conflicts") or manifest.get("layer_conflicts") or []
    overrides = manifest.get("overrides") or []
    override_targets = {item.get("target"): item for item in overrides if item.get("target")}
    for conflict in declared_conflicts:
        target = conflict.get("target") or conflict.get("id") or conflict.get("unit")
        if not target:
            issues.append({
                "code": "CONFLICT_TARGET_REQUIRED",
                "message": "Declared conflict must define target/id/unit.",
                "conflict": conflict,
            })
            continue
        override = override_targets.get(target)
        if not override:
            issues.append({
                "code": "UNRESOLVED_LAYER_CONFLICT",
                "message": f"Conflict for {target} has no explicit override.",
                "target": target,
            })
            continue
        if not override.get("reason"):
            issues.append({
                "code": "OVERRIDE_REASON_REQUIRED",
                "message": f"Override for {target} must define reason.",
                "target": target,
            })
        if override.get("approved_by") != "human":
            issues.append({
                "code": "OVERRIDE_HUMAN_APPROVAL_REQUIRED",
                "message": f"Override for {target} must be approved_by: human.",
                "target": target,
            })

    # Template ID collisions across multiple sets are warnings unless declared as conflict.
    template_ids: dict[str, list[str]] = defaultdict(list)
    for dep in dependencies:
        if dep.get("kind") != "output_template_set":
            continue
        catalog = dep.get("catalog")
        if not catalog:
            continue
        workspace_root = root.parent.parent if root.parent.name == "packages" else root
        catalog_path = workspace_root / catalog
        if not catalog_path.exists():
            continue
        import yaml
        data = yaml.safe_load(catalog_path.read_text(encoding="utf-8")) or {}
        for item in data.get("output_templates") or []:
            tid = item.get("id")
            if tid:
                template_ids[tid].append(f"{dep.get('id')}@{dep.get('version')}")
    for tid, owners in template_ids.items():
        if len(set(owners)) > 1:
            warnings.append({
                "code": "OUTPUT_TEMPLATE_ID_COLLISION",
                "message": f"Output template id {tid} appears in multiple template sets.",
                "template_id": tid,
                "owners": sorted(set(owners)),
            })

    report = {
        "status": "failed" if issues else "passed",
        "package": {"name": manifest.get("name"), "version": manifest.get("version")},
        "summary": {"errors": len(issues), "warnings": len(warnings), "dependencies_checked": len(dependencies)},
        "issues": issues,
        "warnings": warnings,
    }
    write_json(reports_dir / "dependency_conflict_report.json", report)
    return report
