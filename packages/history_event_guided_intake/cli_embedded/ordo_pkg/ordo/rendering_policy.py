from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import re
import json
import hashlib

import yaml

from .output_registry import resolve_template_set

DETERMINISTIC_RENDER_MODE = "deterministic"
MODEL_ASSISTED_RENDER_MODE = "model_assisted"
ALLOWED_RENDER_MODES = {DETERMINISTIC_RENDER_MODE, MODEL_ASSISTED_RENDER_MODE}
ALLOWED_DETERMINISTIC_RENDERERS = {"ordo.simple"}
ALLOWED_MODEL_ASSISTED_RENDERERS = {"ai.markdown", "ai.yaml", "ai.json"}
UNSUPPORTED_SIMPLE_PATTERNS: list[tuple[str, str]] = [
    (r"{%\s*for\b", "for blocks are not supported by ordo.simple"),
    (r"{%\s*if\b", "if blocks are not supported by ordo.simple"),
    (r"{%", "Jinja-style block syntax is not supported by ordo.simple"),
    (r"\{#", "Jinja-style comments are not supported by ordo.simple"),
    (r"\bloop\.index\b", "loop.index is not supported by ordo.simple"),
    (r"\.items\s*\(\s*\)", ".items() iteration is not supported by ordo.simple"),
    (r"\|\s*default\s*\(", "complex default(...) filters are not supported by ordo.simple"),
]

@dataclass
class RenderingIssue:
    severity: str
    code: str
    message: str
    location: str
    template_id: str | None = None


def _issue(issues: list[RenderingIssue], severity: str, code: str, message: str, location: str, template_id: str | None = None) -> None:
    issues.append(RenderingIssue(severity, code, message, location, template_id))


def _load_local_template_catalog(root: Path) -> tuple[dict[str, Any] | None, Path | None, dict[str, Any] | None]:
    for candidate in [root / "output_templates" / "output_templates.yaml", root / "templates" / "output_templates.yaml"]:
        if candidate.exists():
            return yaml.safe_load(candidate.read_text(encoding="utf-8")) or {}, candidate, {"source": "package_local", "catalog": str(candidate)}
    return None, None, None


def load_template_catalogs(root: Path, manifest: dict[str, Any]) -> list[tuple[dict[str, Any], Path, dict[str, Any]]]:
    loaded: list[tuple[dict[str, Any], Path, dict[str, Any]]] = []
    for item in manifest.get("output_template_sets") or []:
        set_id = item.get("id")
        version = str(item.get("version") or "").strip()
        preferred_source = item.get("source")
        if not set_id or not version:
            continue
        catalog, catalog_path, meta = resolve_template_set(root, set_id, version, preferred_source=preferred_source)
        loaded.append((catalog, catalog_path, meta))
    if loaded:
        return loaded
    local, local_path, meta = _load_local_template_catalog(root)
    if local and local_path and meta:
        loaded.append((local, local_path, meta))
    return loaded


def normalize_template_entry(item: dict[str, Any], *, section: str) -> dict[str, Any]:
    entry = dict(item)
    if section == "model_assisted_output_templates":
        entry.setdefault("render_mode", MODEL_ASSISTED_RENDER_MODE)
        entry.setdefault("requires_model_rendering", True)
    else:
        entry.setdefault("render_mode", DETERMINISTIC_RENDER_MODE)
        entry.setdefault("requires_model_rendering", entry.get("render_mode") == MODEL_ASSISTED_RENDER_MODE)
    if entry.get("render_mode") == DETERMINISTIC_RENDER_MODE:
        entry.setdefault("renderer", "ordo.simple")
        entry.setdefault("requires_model_rendering", False)
    elif entry.get("render_mode") == MODEL_ASSISTED_RENDER_MODE:
        entry.setdefault("renderer", "ai.markdown")
        entry.setdefault("requires_model_rendering", True)
        entry.setdefault("validation", "strict_confirmed_state_only")
        entry.setdefault("tbd_policy", "preserve_tbd_until_confirmed")
    return entry


def iter_template_entries(catalog: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    entries: list[tuple[str, dict[str, Any]]] = []
    for item in catalog.get("output_templates") or []:
        entries.append(("output_templates", normalize_template_entry(item or {}, section="output_templates")))
    for item in catalog.get("model_assisted_output_templates") or []:
        entries.append(("model_assisted_output_templates", normalize_template_entry(item or {}, section="model_assisted_output_templates")))
    return entries


def deterministic_entries(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    return [entry for _section, entry in iter_template_entries(catalog) if entry.get("render_mode") == DETERMINISTIC_RENDER_MODE]


def model_assisted_entries(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    return [entry for _section, entry in iter_template_entries(catalog) if entry.get("render_mode") == MODEL_ASSISTED_RENDER_MODE]


def unsupported_simple_syntax(text: str) -> list[dict[str, str]]:
    found: list[dict[str, str]] = []
    for pattern, reason in UNSUPPORTED_SIMPLE_PATTERNS:
        match = re.search(pattern, text)
        if match:
            found.append({"pattern": pattern, "reason": reason, "match": match.group(0)})
    return found


def validate_rendering_policy(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    issues: list[RenderingIssue] = []
    catalogs = load_template_catalogs(root, manifest)
    deterministic_count = 0
    model_assisted_count = 0
    for catalog, catalog_path, meta in catalogs:
        for section, entry in iter_template_entries(catalog):
            template_id = entry.get("id") or "<missing-id>"
            loc = f"{catalog_path}:{section}.{template_id}"
            render_mode = entry.get("render_mode")
            renderer = entry.get("renderer")
            if not entry.get("id"):
                _issue(issues, "error", "ORDO-RENDER-SCHEMA-001", "Template id is required.", loc, template_id)
            if render_mode not in ALLOWED_RENDER_MODES:
                _issue(issues, "error", "ORDO-RENDER-SCHEMA-002", "Template render_mode must be deterministic or model_assisted.", loc, template_id)
                continue
            template_ref = entry.get("template")
            if not template_ref:
                _issue(issues, "error", "ORDO-RENDER-SCHEMA-003", "Template path is required.", loc, template_id)
                continue
            template_path = (catalog_path.parent / template_ref).resolve()
            if not template_path.exists():
                _issue(issues, "error", "ORDO-RENDER-SCHEMA-004", "Template file does not exist.", loc, template_id)
                continue
            text = template_path.read_text(encoding="utf-8")
            if render_mode == DETERMINISTIC_RENDER_MODE:
                deterministic_count += 1
                if renderer not in ALLOWED_DETERMINISTIC_RENDERERS:
                    _issue(issues, "error", "ORDO-RENDER-SCHEMA-005", "Deterministic template must use renderer: ordo.simple.", loc, template_id)
                if entry.get("requires_model_rendering") is True:
                    _issue(issues, "error", "ORDO-RENDER-SCHEMA-006", "Deterministic template must not require model rendering.", loc, template_id)
                for found in unsupported_simple_syntax(text):
                    _issue(issues, "error", "ORDO-RENDER-001", f"Deterministic template contains unsupported syntax: {found['reason']}.", loc, template_id)
            if render_mode == MODEL_ASSISTED_RENDER_MODE:
                model_assisted_count += 1
                if renderer == "ordo.simple" or renderer not in ALLOWED_MODEL_ASSISTED_RENDERERS:
                    _issue(issues, "error", "ORDO-RENDER-002", "Model-assisted template must not be rendered by ordo.simple and must use ai.markdown/ai.yaml/ai.json.", loc, template_id)
                if entry.get("requires_model_rendering") is not True:
                    _issue(issues, "error", "ORDO-RENDER-SCHEMA-007", "Model-assisted template must set requires_model_rendering: true.", loc, template_id)
                if entry.get("validation") != "strict_confirmed_state_only":
                    _issue(issues, "warning", "ORDO-RENDER-W01", "Model-assisted template should use validation: strict_confirmed_state_only.", loc, template_id)
                if entry.get("tbd_policy") != "preserve_tbd_until_confirmed":
                    _issue(issues, "warning", "ORDO-RENDER-W02", "Model-assisted template should preserve TBD markers until confirmation.", loc, template_id)
    errors = [asdict(i) for i in issues if i.severity == "error"]
    warnings = [asdict(i) for i in issues if i.severity == "warning"]
    return {
        "status": "passed" if not errors else "failed",
        "mode": "two_tier_rendering_policy",
        "summary": {
            "catalogs": len(catalogs),
            "deterministic_templates": deterministic_count,
            "model_assisted_templates": model_assisted_count,
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "issues": [asdict(i) for i in issues],
    }


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def make_model_assisted_handoff(
    *,
    root: Path,
    catalog_path: Path,
    meta: dict[str, Any],
    entry: dict[str, Any],
    template_text: str,
    confirmed_state: dict[str, Any],
    expected_output_path: str,
    context_hash: str,
) -> dict[str, Any]:
    return {
        "schema": "ordo.model_assisted_render_handoff.v0.1",
        "artifact_id": entry.get("id"),
        "render_mode": MODEL_ASSISTED_RENDER_MODE,
        "renderer": entry.get("renderer"),
        "requires_model_rendering": True,
        "validation": entry.get("validation", "strict_confirmed_state_only"),
        "tbd_policy": entry.get("tbd_policy", "preserve_tbd_until_confirmed"),
        "expected_output_path": expected_output_path,
        "template": {
            "catalog": str(catalog_path.relative_to(root)) if catalog_path.is_relative_to(root) else str(catalog_path),
            "template_ref": entry.get("template"),
            "template_hash": sha256_text(template_text),
            "content": template_text,
        },
        "confirmed_state": confirmed_state,
        "confirmed_state_hash": context_hash,
        "explicit_tbd_defaults": entry.get("explicit_tbd_defaults") or ["⚠️ TBD"],
        "forbidden_unconfirmed_terms": entry.get("forbidden_unconfirmed_terms") or [],
        "forbidden_inference_rules": entry.get("forbidden_inference_rules") or [
            "Do not infer missing values.",
            "Do not mark candidate/proposed values as confirmed.",
            "Do not remove TBD markers unless the field is confirmed in confirmed_state.",
            "Do not add provider classes, file names, IDs, dates, or implementation facts not present in confirmed_state or template text.",
        ],
        "post_validation_required": [
            "unresolved_placeholders_absent",
            "yaml_json_parse_if_applicable",
            "confirmed_state_consistency",
            "cross_artifact_consistency",
            "tbd_markers_preserved_unless_confirmed",
        ],
        "catalog_meta": meta,
    }
