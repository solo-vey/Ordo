"""Identity and freshness contract for validation evidence."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import uuid

from .canonical_source import validate_canonical_source

SCHEMA = "ordo.validation_evidence_identity.v1"


def _normalise_layers(layers: list[Any] | None, status: str | None = None) -> list[dict[str, str]]:
    default_status = "passed" if status in {"passed", "generated", "go", "completed"} else (status or "unknown")
    result: list[dict[str, str]] = []
    for layer in layers or []:
        if isinstance(layer, str):
            result.append({"layer": layer, "status": default_status})
        elif isinstance(layer, dict) and isinstance(layer.get("layer"), str):
            result.append({"layer": layer["layer"], "status": str(layer.get("status") or default_status)})
    return result


def inferred_layers(report: dict[str, Any], report_name: str | None = None) -> list[dict[str, str]]:
    name = (report_name or "").lower()
    if "lint" in name:
        layers = ["parse", "schema", "graph", "policy"]
    elif "compile" in name:
        layers = ["parse", "schema", "graph", "compilation"]
    elif "test" in name or "coverage" in name:
        layers = ["regression"]
    elif "artifact" in name or "output" in name:
        layers = ["artifact"]
    elif "release" in name or "package" in name:
        layers = ["parse", "schema", "graph", "lineage", "regression", "artifact"]
    else:
        layers = ["validation"]
    return _normalise_layers(layers, str(report.get("status") or "unknown"))


def build_evidence_identity(package: str | Path, *, layers: list[Any] | None = None, run_id: str | None = None, report_status: str | None = None) -> dict[str, Any]:
    root = Path(package).resolve()
    source = validate_canonical_source(root)
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "schema_version": SCHEMA,
        "run_id": run_id or f"run-{uuid.uuid4().hex}",
        "run_timestamp": now,
        "package_path": str(root),
        "package_version": source.get("package_version"),
        "source_identity": source.get("source_identity"),
        "validator_layers": _normalise_layers(layers, report_status),
        "evidence_scope": "current_run",
        "historical_evidence": [],
    }


def validate_evidence_report(report: dict[str, Any], package: str | Path, *, required_layers: list[str] | None = None) -> dict[str, Any]:
    expected = build_evidence_identity(package, layers=required_layers or [])
    errors: list[dict[str, str]] = []
    actual = report.get("evidence_identity") or {}
    if actual.get("schema_version") != SCHEMA:
        errors.append({"code": "EVIDENCE_IDENTITY_MISSING", "message": "report lacks validation evidence identity"})
    if actual.get("package_version") != expected.get("package_version"):
        errors.append({"code": "EVIDENCE_VERSION_MISMATCH", "message": "report package version differs from current package"})
    expected_source = expected.get("source_identity") or {}
    actual_source = actual.get("source_identity") or {}
    for field in ("verified_source_path", "size_bytes", "mtime_ns", "sha256"):
        if actual_source.get(field) != expected_source.get(field):
            errors.append({"code": "EVIDENCE_SOURCE_MISMATCH", "message": f"report source identity differs for {field}"})
    required = set(required_layers or [])
    actual_layers = {item.get("layer") for item in actual.get("validator_layers") or [] if isinstance(item, dict)}
    missing = sorted(required - actual_layers)
    if missing:
        errors.append({"code": "EVIDENCE_LAYER_MISSING", "message": f"report is missing validator layers: {', '.join(missing)}"})
    return {"schema_version": SCHEMA, "status": "passed" if not errors else "blocked", "errors": errors, "report_identity": actual, "current_identity": expected}


def attach_evidence_identity(report: dict[str, Any], package: str | Path, *, layers: list[Any] | None = None, run_id: str | None = None, report_name: str | None = None) -> dict[str, Any]:
    enriched = dict(report)
    effective_layers = layers if layers is not None else inferred_layers(enriched, report_name)
    enriched["evidence_identity"] = build_evidence_identity(package, layers=effective_layers, run_id=run_id, report_status=str(enriched.get("status") or "unknown"))
    return enriched
