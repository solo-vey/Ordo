from __future__ import annotations

"""Fail-closed maintenance lifecycle validation for versioned Ordo packages."""

from pathlib import Path
from typing import Any
import hashlib
import json
import tempfile
import zipfile

import yaml

from .canonical_source import validate_canonical_source


SCHEMA = "ordo.package_lifecycle.v1"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except Exception:
        return None


def _inside(root: Path, raw: Any) -> Path | None:
    if not isinstance(raw, str) or not raw:
        return None
    candidate = (root / raw).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def _issue(issues: list[dict[str, str]], code: str, message: str, location: str) -> None:
    issues.append({"severity": "error", "code": code, "message": message, "location": location})


def validate_package_lifecycle(package: str | Path, *, verify_baseline: bool = False) -> dict[str, Any]:
    """Validate maintenance artifacts without modifying package or runtime state."""
    root = Path(package).resolve()
    manifest_path = root / "ordo.yml"
    if not manifest_path.is_file():
        return {"schema_version": SCHEMA, "status": "blocked", "issues": [{"severity": "error", "code": "LIFECYCLE_MANIFEST_MISSING", "message": "missing ordo.yml", "location": "ordo.yml"}], "summary": {"errors": 1}}
    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        return {"schema_version": SCHEMA, "status": "blocked", "issues": [{"severity": "error", "code": "LIFECYCLE_MANIFEST_INVALID", "message": str(exc), "location": "ordo.yml"}], "summary": {"errors": 1}}
    contract = manifest.get("maintenance_lifecycle")
    if contract is None:
        return {"schema_version": SCHEMA, "status": "not_enabled", "issues": [], "summary": {"errors": 0}, "package": {"name": manifest.get("name"), "version": manifest.get("version")}}
    issues: list[dict[str, str]] = []
    if not isinstance(contract, dict):
        _issue(issues, "LIFECYCLE_CONTRACT_INVALID", "maintenance_lifecycle must be an object.", "ordo.yml.maintenance_lifecycle")
        contract = {}
    if contract.get("version") != "1.0":
        _issue(issues, "LIFECYCLE_VERSION_REQUIRED", "maintenance_lifecycle.version must be '1.0'.", "ordo.yml.maintenance_lifecycle.version")
    if contract.get("mode") != "strict":
        _issue(issues, "LIFECYCLE_STRICT_MODE_REQUIRED", "maintenance_lifecycle.mode must be strict for a release-bound package.", "ordo.yml.maintenance_lifecycle.mode")
    package_version = manifest.get("version")
    if not isinstance(package_version, str) or not package_version:
        _issue(issues, "LIFECYCLE_PACKAGE_VERSION_REQUIRED", "ordo.yml must declare a non-empty package version.", "ordo.yml.version")
    canonical = validate_canonical_source(root, expected_version=package_version if isinstance(package_version, str) else None)
    for error in canonical.get("errors", []) or []:
        _issue(issues, f"LIFECYCLE_{error.get('code')}", error.get("message", "canonical source validation failed"), "canonical_source")
    identity = canonical.get("source_identity") or {}
    source_digest = identity.get("sha256")
    required_assets = contract.get("required_assets") or []
    if not isinstance(required_assets, list) or not required_assets:
        _issue(issues, "LIFECYCLE_REQUIRED_ASSETS_REQUIRED", "required_assets must name README, regression, and maintenance assets.", "ordo.yml.maintenance_lifecycle.required_assets")
        required_assets = []
    for rel in required_assets:
        target = _inside(root, rel)
        if target is None or not target.is_file():
            _issue(issues, "LIFECYCLE_REQUIRED_ASSET_MISSING", f"required lifecycle asset is missing: {rel}", "ordo.yml.maintenance_lifecycle.required_assets")

    checkpoint = contract.get("checkpoint") or {}
    checkpoint_path = _inside(root, checkpoint.get("path") if isinstance(checkpoint, dict) else None)
    checkpoint_data = _read_json(checkpoint_path) if checkpoint_path and checkpoint_path.is_file() else None
    if checkpoint_data is None:
        _issue(issues, "LIFECYCLE_CHECKPOINT_MISSING", "immutable checkpoint metadata is required before a substantive source change.", "ordo.yml.maintenance_lifecycle.checkpoint.path")
    else:
        if checkpoint_data.get("immutable") is not True:
            _issue(issues, "LIFECYCLE_CHECKPOINT_NOT_IMMUTABLE", "checkpoint metadata must explicitly declare immutable: true.", str(checkpoint.get("path")))
        if checkpoint_data.get("package_version") != package_version:
            _issue(issues, "LIFECYCLE_CHECKPOINT_VERSION_MISMATCH", "checkpoint package version differs from ordo.yml.", str(checkpoint.get("path")))

    patch = contract.get("patch") or {}
    patch_path = _inside(root, patch.get("path") if isinstance(patch, dict) else None)
    if patch_path is None or not patch_path.is_file():
        _issue(issues, "LIFECYCLE_PATCH_SCRIPT_MISSING", "an assertion-based idempotent patch script is required.", "ordo.yml.maintenance_lifecycle.patch.path")
    else:
        script = patch_path.read_text(encoding="utf-8")
        if "LIFECYCLE_PATCH_IDEMPOTENT = True" not in script:
            _issue(issues, "LIFECYCLE_PATCH_NOT_IDEMPOTENT", "patch script must declare LIFECYCLE_PATCH_IDEMPOTENT = True.", str(patch.get("path")))
        if "BASELINE_SOURCE_SHA256" not in script:
            _issue(issues, "LIFECYCLE_PATCH_ASSERTION_MISSING", "patch script must contain a BASELINE_SOURCE_SHA256 assertion.", str(patch.get("path")))
        baseline = patch.get("baseline_source_sha256")
        if checkpoint_data is not None and checkpoint_data.get("source_sha256") != baseline:
            _issue(issues, "LIFECYCLE_CHECKPOINT_PATCH_MISMATCH", "checkpoint source SHA-256 must equal the patch baseline assertion.", "ordo.yml.maintenance_lifecycle.patch.baseline_source_sha256")
        if verify_baseline and baseline != source_digest:
            _issue(issues, "LIFECYCLE_PATCH_BASELINE_MISMATCH", "failed baseline assertion: current canonical source differs from the patch baseline; do not apply the patch.", "ordo.yml.maintenance_lifecycle.patch.baseline_source_sha256")
        if patch.get("idempotent") is not True:
            _issue(issues, "LIFECYCLE_PATCH_IDEMPOTENCE_UNDECLARED", "patch contract must declare idempotent: true.", "ordo.yml.maintenance_lifecycle.patch.idempotent")

    previous = contract.get("previous_release") or {}
    previous_path = _inside(root, previous.get("path") if isinstance(previous, dict) else None)
    previous_data = _read_json(previous_path) if previous_path and previous_path.is_file() else None
    if previous_data is None or previous_data.get("status") != "passed" or not ((previous_data.get("source_identity") or {}).get("sha256")):
        _issue(issues, "LIFECYCLE_PREVIOUS_RELEASE_INVALID", "previous_release must be validated evidence with source_identity.sha256.", "ordo.yml.maintenance_lifecycle.previous_release")
    elif previous_data.get("package_version") == package_version:
        _issue(issues, "LIFECYCLE_VERSION_NOT_ADVANCED", "previous validated release must have a different package version.", str(previous.get("path")))

    regression = contract.get("regression") or {}
    regression_path = _inside(root, regression.get("path") if isinstance(regression, dict) else None)
    regression_data = _read_json(regression_path) if regression_path and regression_path.is_file() else None
    if regression_data is None or regression_data.get("status") != "passed" or regression_data.get("schema_version") != "ordo.canonical_regression_report.v1":
        _issue(issues, "LIFECYCLE_REGRESSION_MISSING", "a passed canonical regression report is required.", "ordo.yml.maintenance_lifecycle.regression.path")
    elif regression_data.get("source_identity", {}).get("sha256") != source_digest:
        _issue(issues, "LIFECYCLE_REGRESSION_SOURCE_MISMATCH", "regression report does not bind to the current canonical source digest.", str(regression.get("path")))

    evidence = contract.get("release_evidence") or {}
    evidence_path = _inside(root, evidence.get("path") if isinstance(evidence, dict) else None)
    evidence_data = _read_json(evidence_path) if evidence_path and evidence_path.is_file() else None
    if evidence_data is None or evidence_data.get("status") != "passed" or not isinstance(evidence_data.get("source_identity"), dict):
        _issue(issues, "LIFECYCLE_RELEASE_EVIDENCE_MISSING", "passed release evidence is required.", "ordo.yml.maintenance_lifecycle.release_evidence.path")
    elif evidence_data.get("source_identity", {}).get("sha256") != source_digest:
        _issue(issues, "LIFECYCLE_EVIDENCE_SOURCE_MISMATCH", "release evidence does not bind to the current canonical source digest.", str(evidence.get("path")))

    exclusions = contract.get("runtime_excluded_paths") or []
    if not isinstance(exclusions, list) or not exclusions:
        _issue(issues, "LIFECYCLE_RUNTIME_EXCLUSIONS_REQUIRED", "runtime_excluded_paths must explicitly exclude build-only tooling.", "ordo.yml.maintenance_lifecycle.runtime_excluded_paths")
    for rel in exclusions if isinstance(exclusions, list) else []:
        if _inside(root, rel) is None:
            _issue(issues, "LIFECYCLE_RUNTIME_EXCLUSION_UNSAFE", "runtime exclusion must be a package-relative path.", "ordo.yml.maintenance_lifecycle.runtime_excluded_paths")
    return {"schema_version": SCHEMA, "status": "passed" if not issues else "blocked", "package": {"name": manifest.get("name"), "version": package_version}, "source_identity": identity, "issues": issues, "summary": {"errors": len(issues)}, "pass_evidence": {"source_identity": identity, "checkpoint": checkpoint.get("path") if isinstance(checkpoint, dict) else None} if not issues else None}


def validate_unpacked_release(archive: str | Path) -> dict[str, Any]:
    """Independently unpack a ZIP and apply the same lifecycle validator."""
    archive_path = Path(archive).resolve()
    if not archive_path.is_file() or not zipfile.is_zipfile(archive_path):
        return {"schema_version": SCHEMA, "status": "blocked", "issues": [{"severity": "error", "code": "LIFECYCLE_ARCHIVE_INVALID", "message": "archive is missing or not a ZIP file", "location": str(archive_path)}], "summary": {"errors": 1}}
    with tempfile.TemporaryDirectory(prefix="ordo-lifecycle-unpack-") as temporary:
        destination = Path(temporary)
        with zipfile.ZipFile(archive_path) as bundle:
            names = bundle.namelist()
            if any(Path(name).is_absolute() or ".." in Path(name).parts for name in names):
                return {"schema_version": SCHEMA, "status": "blocked", "issues": [{"severity": "error", "code": "LIFECYCLE_ARCHIVE_UNSAFE", "message": "archive has unsafe member path", "location": str(archive_path)}], "summary": {"errors": 1}}
            bundle.extractall(destination)
        roots = [path.parent for path in destination.rglob("ordo.yml")]
        if len(roots) != 1:
            return {"schema_version": SCHEMA, "status": "blocked", "issues": [{"severity": "error", "code": "LIFECYCLE_UNPACKED_PACKAGE_AMBIGUOUS", "message": "archive must contain exactly one package manifest", "location": str(archive_path)}], "summary": {"errors": 1}}
        report = validate_package_lifecycle(roots[0])
        report["unpacked_archive"] = {"path": str(archive_path), "sha256": _sha256(archive_path)}
        return report
