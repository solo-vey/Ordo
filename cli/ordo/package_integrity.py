"""Coherence checks for one versioned Ordo package snapshot."""
from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import json
import zipfile

from .canonical_source import validate_canonical_source

SCHEMA = "ordo.package_integrity.v1"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except Exception:
        return None


def _validate_checksum_manifest(root: Path, path: Path, errors: list[dict[str, str]]) -> int:
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split("  ", 1)
        if len(parts) != 2:
            errors.append({"code": "PACKAGE_CHECKSUM_ENTRY_INVALID", "message": f"invalid checksum entry: {path.relative_to(root)}"})
            continue
        digest, rel = parts
        target = root / rel
        if not target.is_file() or _sha256(target) != digest:
            errors.append({"code": "PACKAGE_CHECKSUM_MISMATCH", "message": f"checksum mismatch or missing file: {rel}"})
        count += 1
    return count


def _validate_build_manifest(root: Path, package_version: str | None, errors: list[dict[str, str]]) -> tuple[int, int]:
    path = root / "reports" / "BUILD_MANIFEST.json"
    if not path.is_file():
        return 0, 0
    data = _read_json(path)
    if data is None:
        errors.append({"code": "PACKAGE_BUILD_MANIFEST_INVALID", "message": "reports/BUILD_MANIFEST.json is invalid"})
        return 0, 0
    if ((data.get("package") or {}).get("version")) != package_version:
        errors.append({"code": "PACKAGE_BUILD_VERSION_MISMATCH", "message": "build manifest version differs from ordo.yml"})
    files = data.get("files") or []
    for item in files:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            errors.append({"code": "PACKAGE_BUILD_FILE_INVALID", "message": "build manifest contains an invalid file entry"})
            continue
        target = root / item["path"]
        if not target.is_file() or item.get("sha256") != _sha256(target):
            errors.append({"code": "PACKAGE_BUILD_FILE_MISMATCH", "message": f"build manifest does not match: {item['path']}"})
    return 1, len(files)


def _validate_current_reports(root: Path, package_version: str | None, source_sha256: str | None, errors: list[dict[str, str]]) -> int:
    reports = root / "reports"
    if not reports.is_dir():
        return 0
    checked = 0
    for path in sorted(reports.glob("*.json")):
        data = _read_json(path)
        if data is None:
            continue
        identity = data.get("evidence_identity")
        if not isinstance(identity, dict):
            # Historical reports may remain present, but cannot be counted as
            # current package evidence.
            continue
        checked += 1
        if identity.get("evidence_scope") != "current_run":
            errors.append({"code": "PACKAGE_REPORT_SCOPE_INVALID", "message": f"report is not current-run evidence: {path.name}"})
        if identity.get("package_version") != package_version:
            errors.append({"code": "PACKAGE_REPORT_VERSION_MISMATCH", "message": f"report version differs from ordo.yml: {path.name}"})
        if ((identity.get("source_identity") or {}).get("sha256")) != source_sha256:
            errors.append({"code": "PACKAGE_REPORT_SOURCE_MISMATCH", "message": f"report source differs from canonical source: {path.name}"})
    return checked


def _component_inventory(root: Path) -> dict[str, list[dict[str, Any]]]:
    """Fingerprint the complete package snapshot by operational component."""
    inventory: dict[str, list[dict[str, Any]]] = {"manifest": [], "source": [], "validators": [], "templates": [], "reports": [], "other": []}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in {".git", "__pycache__", ".ordo-generated"} for part in path.relative_to(root).parts):
            continue
        rel = path.relative_to(root).as_posix()
        parts = path.relative_to(root).parts
        if rel == "ordo.yml":
            group = "manifest"
        elif parts[0] == "source":
            group = "source"
        elif parts[0] in {"cli_embedded", "validators"}:
            group = "validators"
        elif parts[0] in {"templates", "output_templates"} or "templates" in parts:
            group = "templates"
        elif parts[0] == "reports":
            group = "reports"
        else:
            group = "other"
        inventory[group].append({"path": rel, "sha256": _sha256(path), "size_bytes": path.stat().st_size})
    return inventory


def compare_reproducible_archives(first: str | Path, second: str | Path) -> dict[str, Any]:
    """Compare archive payloads by member path and SHA-256, ignoring ZIP metadata."""
    def inventory(path: Path) -> dict[str, str]:
        with zipfile.ZipFile(path) as archive:
            return {name: hashlib.sha256(archive.read(name)).hexdigest() for name in sorted(archive.namelist()) if not name.endswith("/")}
    left, right = inventory(Path(first)), inventory(Path(second))
    return {"schema_version": SCHEMA, "status": "passed" if left == right else "blocked", "first": str(first), "second": str(second), "first_inventory": left, "second_inventory": right}


def validate_package_integrity(package: str | Path, *, expected_version: str | None = None) -> dict[str, Any]:
    root = Path(package).resolve()
    errors: list[dict[str, str]] = []
    manifest_path = root / "ordo.yml"
    required = ["ordo.yml"]
    if not manifest_path.is_file():
        errors.append({"code": "PACKAGE_MANIFEST_MISSING", "message": "missing ordo.yml"})
        return _report(root, None, errors)
    try:
        import yaml
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        return _report(root, None, [{"code": "PACKAGE_MANIFEST_INVALID", "message": str(exc)}])
    version = manifest.get("version")
    if not isinstance(version, str) or not version:
        errors.append({"code": "PACKAGE_VERSION_MISSING", "message": "ordo.yml must declare version"})
    if expected_version is not None and version != expected_version:
        errors.append({"code": "PACKAGE_VERSION_MISMATCH", "message": "package version differs from expected version"})
    source = validate_canonical_source(root, expected_version=version)
    errors.extend(source.get("errors") or [])
    source_path = manifest.get("source", "source/program.ordo.yaml")
    if isinstance(source_path, str):
        required.append(source_path)
    for rel in required:
        if not (root / rel).is_file():
            errors.append({"code": "PACKAGE_REQUIRED_FILE_MISSING", "message": f"required package file is missing: {rel}"})
    checksums = root / "SHA256SUMS.txt"
    checksum_count = 0
    if checksums.is_file():
        checksum_count += _validate_checksum_manifest(root, checksums, errors)
    generated_checksums = root / "reports" / "SHA256SUMS.txt"
    if generated_checksums.is_file():
        checksum_count += _validate_checksum_manifest(root, generated_checksums, errors)
    source_sha256 = ((source.get("source_identity") or {}).get("sha256"))
    build_manifest_count, build_file_count = _validate_build_manifest(root, version, errors)
    current_reports = _validate_current_reports(root, version, source_sha256, errors)
    identity = {
        "name": manifest.get("name"),
        "version": version,
        "source": source.get("source_identity"),
        "checksum_entries": checksum_count,
        "build_manifest_count": build_manifest_count,
        "build_file_count": build_file_count,
        "current_evidence_reports": current_reports,
        "component_inventory": _component_inventory(root),
    }
    return _report(root, identity, errors)


def _report(root: Path, identity: dict[str, Any] | None, errors: list[dict[str, str]]) -> dict[str, Any]:
    return {"schema_version": SCHEMA, "status": "passed" if not errors else "blocked", "package": str(root), "package_identity": identity, "errors": errors, "pass_evidence": identity if not errors else None}
