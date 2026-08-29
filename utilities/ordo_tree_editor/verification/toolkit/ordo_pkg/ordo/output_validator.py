from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import re
import hashlib

import yaml

from .loader import load_package
from .output_registry import resolve_template_set
from .reporter import write_json

PLACEHOLDER_RE = re.compile(r"\{\{\s*[^}]+?\s*\}\}")


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_output_manifest(root: Path) -> dict[str, Any]:
    path = root / "generated_outputs" / "output_manifest.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _load_generation_report(root: Path) -> dict[str, Any]:
    path = root / "reports" / "output_generation_report.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _output_allowed(root: Path) -> bool:
    for candidate in [root / "reports" / "intake_report.json", root / "reports" / "run_report.json"]:
        if candidate.exists():
            data = json.loads(candidate.read_text(encoding="utf-8"))
            outputs = data.get("outputs") or []
            if not outputs:
                return True
            return all(bool(item.get("allowed")) for item in outputs)
    return False


def _load_template_catalogs(root: Path, manifest: dict[str, Any]) -> list[tuple[dict[str, Any], Path, dict[str, Any]]]:
    loaded: list[tuple[dict[str, Any], Path, dict[str, Any]]] = []
    for item in manifest.get("output_template_sets") or []:
        set_id = item.get("id")
        version = str(item.get("version") or "").strip()
        source = item.get("source")
        if not set_id or not version:
            continue
        catalog, catalog_path, meta = resolve_template_set(root, set_id, version, preferred_source=source)
        loaded.append((catalog, catalog_path, meta))
    if loaded:
        return loaded
    for candidate in [root / "output_templates" / "output_templates.yaml", root / "templates" / "output_templates.yaml"]:
        if candidate.exists():
            loaded.append((yaml.safe_load(candidate.read_text(encoding="utf-8")) or {}, candidate, {"source": "package_local", "catalog": str(candidate)}))
    return loaded


def _expected_template_count(root: Path, manifest: dict[str, Any]) -> int:
    total = 0
    for catalog, _path, _meta in _load_template_catalogs(root, manifest):
        total += len(catalog.get("output_templates") or [])
    return total


def validate_output(package_path: str | Path, *, require_generated: bool = True) -> dict[str, Any]:
    """Validate generated markdown artifacts against template manifest and gates.

    M12 intentionally validates rendered artifacts, not template source only.
    It checks existence, unresolved placeholders, empty files, markdown fences,
    and whether generation was allowed by runtime/intake output gates.
    """
    root, manifest, source, tests = load_package(package_path)
    reports_dir = root / manifest.get("reports", "reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    generated_dir = root / "generated_outputs"
    generation_report = _load_generation_report(root)
    output_manifest = _load_output_manifest(root)
    expected_count = _expected_template_count(root, manifest)
    generated_files = [root / p for p in generation_report.get("generated_files", [])]
    if not generated_files and generated_dir.exists():
        generated_files = sorted(p for p in generated_dir.rglob("*.md") if p.is_file())

    issues: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    if require_generated and expected_count > 0 and not generated_files:
        issues.append({
            "code": "OUTPUTS_NOT_GENERATED",
            "message": "Package declares output templates but no generated output files were found. Run `ordo generate-output <package>`.",
            "location": "generated_outputs/",
        })
    if expected_count and len(generated_files) < expected_count:
        issues.append({
            "code": "REQUIRED_OUTPUTS_MISSING",
            "message": f"Expected {expected_count} generated outputs from templates, found {len(generated_files)}.",
            "expected": expected_count,
            "found": len(generated_files),
        })
    if generation_report and generation_report.get("status") != "passed":
        issues.append({
            "code": "OUTPUT_GENERATION_NOT_PASSED",
            "message": "output_generation_report.json does not have status: passed.",
            "location": "reports/output_generation_report.json",
        })
    if generated_files and not output_manifest:
        issues.append({
            "code": "OUTPUT_MANIFEST_MISSING",
            "message": "Generated outputs exist but generated_outputs/output_manifest.json is missing.",
            "location": "generated_outputs/output_manifest.json",
        })
    if output_manifest:
        if output_manifest.get("schema") != "ordo.output_manifest.v0.1":
            issues.append({"code": "OUTPUT_MANIFEST_SCHEMA_INVALID", "message": "Output manifest schema is missing or unsupported.", "location": "generated_outputs/output_manifest.json"})
        artifacts = output_manifest.get("artifacts") or []
        if len(artifacts) != len(generated_files):
            issues.append({
                "code": "OUTPUT_MANIFEST_COUNT_MISMATCH",
                "message": "Output manifest artifact count does not match generated files count.",
                "manifest_artifacts": len(artifacts),
                "generated_files": len(generated_files),
            })
        for artifact in artifacts:
            rel = artifact.get("path")
            if not rel:
                issues.append({"code": "OUTPUT_MANIFEST_ARTIFACT_PATH_MISSING", "message": "Manifest artifact is missing path.", "location": "generated_outputs/output_manifest.json"})
                continue
            artifact_path = root / rel
            if not artifact_path.exists():
                issues.append({"code": "OUTPUT_MANIFEST_FILE_MISSING", "message": f"Manifest artifact file is missing: {rel}", "location": rel})
                continue
            actual_hash = _sha256_file(artifact_path)
            if artifact.get("hash") != actual_hash:
                issues.append({"code": "OUTPUT_MANIFEST_HASH_MISMATCH", "message": f"Manifest hash does not match file: {rel}", "location": rel, "expected": artifact.get("hash"), "actual": actual_hash})
            if artifact.get("bytes") != artifact_path.stat().st_size:
                issues.append({"code": "OUTPUT_MANIFEST_SIZE_MISMATCH", "message": f"Manifest byte size does not match file: {rel}", "location": rel})
            required_fields = ["id", "type", "format", "source_state", "handoff_status", "hash"]
            for field in required_fields:
                if field not in artifact:
                    issues.append({"code": "OUTPUT_MANIFEST_FIELD_MISSING", "message": f"Manifest artifact is missing required field `{field}`: {rel}", "location": f"generated_outputs/output_manifest.json:{rel}"})
            source_state = artifact.get("source_state") or {}
            if not source_state.get("hash"):
                issues.append({"code": "OUTPUT_MANIFEST_STATE_HASH_MISSING", "message": f"Manifest artifact is missing source state hash: {rel}", "location": rel})
    if generated_files and not _output_allowed(root):
        issues.append({
            "code": "OUTPUT_GENERATED_WITHOUT_ALLOWED_GATE",
            "message": "Generated outputs exist but latest run/intake output gate did not allow output.",
            "location": "reports/intake_report.json or reports/run_report.json",
        })

    package_name = str(manifest.get("name") or "")
    history_event_required_sections = {
        "01_HISTORY_EVENT_PASSPORT_": ["## Test strategy contract", "Test coverage level", "### Unit test coverage"],
        "02_JIRA_TASK_": ["## Test deliverables", "## Acceptance criteria", "Extended unit tests"],
        "04_IMPLEMENTATION_PROMPT_": ["## Required tests", "## Test documentation requirement"],
        "05_QA_PACKAGE_": ["## Empty/null/missing transitions", "## Unit test coverage"],
    } if package_name == "history_event.guided_intake" else {}

    file_reports: list[dict[str, Any]] = []
    for path in generated_files:
        rel = str(path.relative_to(root)).replace("\\", "/") if path.is_relative_to(root) else str(path)
        if not path.exists():
            issues.append({"code": "GENERATED_FILE_MISSING", "message": f"Generated file listed in report is missing: {rel}", "location": rel})
            continue
        text = path.read_text(encoding="utf-8")
        placeholders = PLACEHOLDER_RE.findall(text)
        fence_count = text.count("```")
        info = {
            "path": rel,
            "bytes": path.stat().st_size,
            "unresolved_placeholders": placeholders,
            "code_fence_count": fence_count,
        }
        file_reports.append(info)
        if path.stat().st_size == 0 or not text.strip():
            issues.append({"code": "GENERATED_FILE_EMPTY", "message": f"Generated output is empty: {rel}", "location": rel})
        if placeholders:
            issues.append({"code": "UNRESOLVED_OUTPUT_PLACEHOLDER", "message": f"Generated output contains unresolved placeholders: {rel}", "location": rel, "placeholders": placeholders})
        if fence_count % 2 != 0:
            issues.append({"code": "UNCLOSED_MARKDOWN_CODE_FENCE", "message": f"Generated output has an unclosed Markdown code fence: {rel}", "location": rel})
        if not text.lstrip().startswith("#"):
            warnings.append({"code": "OUTPUT_WITHOUT_TOP_HEADING", "message": f"Generated markdown output does not start with a heading: {rel}", "location": rel})
        for filename_prefix, required_sections in history_event_required_sections.items():
            if path.name.startswith(filename_prefix):
                for section in required_sections:
                    if section not in text:
                        issues.append({
                            "code": "VALIDATION_TEST_PROPAGATION_SECTION_MISSING",
                            "message": f"Generated History Event artifact is missing required test propagation section `{section}`: {rel}",
                            "location": rel,
                            "required_section": section,
                        })

    if history_event_required_sections and generated_files:
        generated_names = [path.name for path in generated_files]
        for filename_prefix in history_event_required_sections:
            if not any(name.startswith(filename_prefix) for name in generated_names):
                issues.append({
                    "code": "VALIDATION_TEST_PROPAGATION_ARTIFACT_MISSING",
                    "message": f"History Event generated outputs must include artifact with prefix `{filename_prefix}`.",
                    "location": "generated_outputs/",
                    "required_artifact_prefix": filename_prefix,
                })

    report = {
        "status": "failed" if issues else "passed",
        "package": {"name": manifest.get("name"), "version": manifest.get("version")},
        "summary": {
            "expected_outputs": expected_count,
            "generated_outputs": len(generated_files),
            "errors": len(issues),
            "warnings": len(warnings),
        },
        "generation_report": "reports/output_generation_report.json" if generation_report else None,
        "output_manifest": "generated_outputs/output_manifest.json" if output_manifest else None,
        "manifest_artifacts": len(output_manifest.get("artifacts") or []) if output_manifest else 0,
        "files": file_reports,
        "issues": issues,
        "warnings": warnings,
    }
    write_json(reports_dir / "output_validation_report.json", report)
    return report
