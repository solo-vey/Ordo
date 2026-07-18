from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import json

from .build_identity import current_tree_sha256, validate_report_binding


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_checksum_manifest(root: Path, manifest_path: Path) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    if not manifest_path.exists():
        return [{
            "severity": "error",
            "code": "ORDO-RECON-001",
            "message": "checksum manifest is missing",
            "location": str(manifest_path),
        }]
    for lineno, raw in enumerate(manifest_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        try:
            expected, rel = line.split(None, 1)
        except ValueError:
            issues.append({
                "severity": "error",
                "code": "ORDO-RECON-002",
                "message": "invalid checksum manifest line",
                "location": f"{manifest_path}:{lineno}",
            })
            continue
        rel = rel.lstrip("* ")
        target = root / rel
        if not target.exists():
            issues.append({
                "severity": "error",
                "code": "ORDO-RECON-003",
                "message": f"checksummed file is missing: {rel}",
                "location": str(target),
            })
            continue
        actual = _sha256(target)
        if actual != expected:
            issues.append({
                "severity": "error",
                "code": "ORDO-RECON-004",
                "message": f"checksum mismatch: {rel}",
                "location": str(target),
            })
    return issues


def verify_build_manifest(root: Path, manifest_path: Path) -> list[dict[str, Any]]:
    if not manifest_path.exists():
        return [{
            "severity": "error",
            "code": "ORDO-RECON-005",
            "message": "build manifest is missing",
            "location": str(manifest_path),
        }]
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [{
            "severity": "error",
            "code": "ORDO-RECON-006",
            "message": f"build manifest is invalid JSON: {exc}",
            "location": str(manifest_path),
        }]
    issues: list[dict[str, Any]] = []
    entries = payload.get("files") or payload.get("artifacts") or []
    for item in entries:
        rel = item.get("path")
        expected = item.get("sha256")
        if not rel or not expected:
            issues.append({
                "severity": "error",
                "code": "ORDO-RECON-007",
                "message": "build manifest entry lacks path or sha256",
                "location": str(manifest_path),
            })
            continue
        target = root / rel
        if not target.exists():
            issues.append({
                "severity": "error",
                "code": "ORDO-RECON-008",
                "message": f"manifest artifact is missing: {rel}",
                "location": str(target),
            })
            continue
        if _sha256(target) != expected:
            issues.append({
                "severity": "error",
                "code": "ORDO-RECON-009",
                "message": f"manifest artifact hash mismatch: {rel}",
                "location": str(target),
            })
    return issues


def pre_zip_reconciliation(
    root: str | Path,
    identity: dict[str, Any],
    validation_reports: list[str | Path],
    *,
    checksum_manifest: str | Path | None = None,
    build_manifest: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(root).resolve()
    issues: list[dict[str, Any]] = []

    actual_tree = current_tree_sha256(root)
    if actual_tree != identity.get("current_tree_sha256"):
        issues.append({
            "severity": "error",
            "code": "ORDO-RECON-010",
            "message": "current tree changed after build identity creation",
            "location": str(root),
        })

    for report_path in validation_reports:
        path = Path(report_path)
        if not path.exists():
            issues.append({
                "severity": "error",
                "code": "ORDO-RECON-011",
                "message": "required validation report is missing",
                "location": str(path),
            })
            continue
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            issues.append({
                "severity": "error",
                "code": "ORDO-RECON-012",
                "message": f"validation report is invalid JSON: {exc}",
                "location": str(path),
            })
            continue
        for item in validate_report_binding(report, identity):
            item.setdefault("location", str(path))
            issues.append(item)
        if report.get("status") != "passed":
            issues.append({
                "severity": "error",
                "code": "ORDO-RECON-013",
                "message": "validation report is not passed",
                "location": str(path),
            })

    if checksum_manifest is not None:
        issues.extend(verify_checksum_manifest(root, Path(checksum_manifest)))
    if build_manifest is not None:
        issues.extend(verify_build_manifest(root, Path(build_manifest)))

    return {
        "schema_version": "ordo.pre_zip_reconciliation.v1",
        "status": "passed" if not issues else "failed",
        "build_session_id": identity.get("build_session_id"),
        "current_tree_sha256": actual_tree,
        "issues": issues,
    }
