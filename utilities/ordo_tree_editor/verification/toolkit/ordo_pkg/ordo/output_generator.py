from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import re
import hashlib

import yaml

from .loader import load_package
from .reporter import write_json
from .rendering_policy import load_template_catalogs, deterministic_entries, model_assisted_entries, make_model_assisted_handoff, validate_rendering_policy


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()




def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _sha256_json(data: Any) -> str:
    payload = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _sha256_bytes(payload)


def _load_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_name(value: str | None, default: str = "package") -> str:
    text = value or default
    text = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(text).strip())
    text = text.strip("._-") or default
    return text[:80]


def _load_latest_state(root: Path) -> tuple[dict[str, Any], str | None, str]:
    """Return (state, source_path, mode) from intake or run reports.

    Prefer guided-intake state because it represents the node-by-node flow.
    Fall back to run_report.json and finally to empty state.
    """
    intake_report = root / "reports" / "intake_report.json"
    if intake_report.exists():
        data = json.loads(intake_report.read_text(encoding="utf-8"))
        return data.get("state") or {}, str(intake_report.relative_to(root)), "intake"
    run_report = root / "reports" / "run_report.json"
    if run_report.exists():
        data = json.loads(run_report.read_text(encoding="utf-8"))
        state = ((data.get("state") or {}).get("final") or {})
        return state, str(run_report.relative_to(root)), "run"
    return {}, None, "source_only"


def _gate_statuses(root: Path) -> list[dict[str, Any]]:
    for candidate in [root / "reports" / "intake_report.json", root / "reports" / "run_report.json"]:
        if candidate.exists():
            data = json.loads(candidate.read_text(encoding="utf-8"))
            return data.get("gate_report") or []
    return []


def _outputs_status(root: Path) -> list[dict[str, Any]]:
    for candidate in [root / "reports" / "intake_report.json", root / "reports" / "run_report.json"]:
        if candidate.exists():
            data = json.loads(candidate.read_text(encoding="utf-8"))
            return data.get("outputs") or []
    return []


def _format_list(value: Any) -> str:
    if value in (None, "", []):
        return "- not specified"
    if isinstance(value, list):
        return "\n".join(f"- {item}" for item in value)
    return f"- {value}"


def _get_path(data: Any, dotted: str) -> Any:
    cur = data
    for part in dotted.split('.'):
        part = part.strip()
        if not part:
            continue
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return None
    return cur


def _apply_filter(value: Any, filter_name: str) -> str:
    filter_name = filter_name.strip()
    if filter_name == "bullets":
        return _format_list(value)
    if filter_name == "safe_name":
        return _safe_name(None if value is None else str(value))
    if filter_name == "bool_lower":
        return str(bool(value)).lower()
    if filter_name == "json":
        return json.dumps(value, ensure_ascii=False, indent=2)
    if value in (None, ""):
        return "not specified"
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value)


def _render_expr(expr: str, context: dict[str, Any]) -> str:
    parts = [p.strip() for p in expr.split('|')]
    key = parts[0]
    if key == "generated_at":
        value = context.get("generated_at")
    else:
        value = _get_path(context, key)
    if len(parts) == 1:
        if value is None:
            return "not specified"
        if isinstance(value, list):
            return ", ".join(str(v) for v in value)
        return str(value)
    rendered: Any = value
    for filter_name in parts[1:]:
        rendered = _apply_filter(rendered, filter_name)
    return str(rendered)


def _render_template(text: str, context: dict[str, Any]) -> str:
    return re.sub(r"\{\{\s*([^}]+?)\s*\}\}", lambda m: _render_expr(m.group(1), context), text)


def _make_template_outputs(root: Path, manifest: dict[str, Any], source: dict[str, Any], state: dict[str, Any], out_dir: Path) -> tuple[list[Path], dict[str, Any] | None, list[dict[str, Any]]]:
    catalogs = load_template_catalogs(root, manifest)
    if not catalogs:
        return [], None, []
    generated: list[Path] = []
    artifact_manifest_entries: list[dict[str, Any]] = []
    gate_statuses = _gate_statuses(root)
    outputs_status = _outputs_status(root)
    gate_by_id = {g.get("id"): g for g in gate_statuses if g.get("id")}
    output_by_id = {o.get("id"): o for o in outputs_status if o.get("id")}
    context = {
        "state": state,
        "manifest": manifest,
        "source": source,
        "package": {
            "name": manifest.get("name") or ((source.get("ordo") or {}).get("package")) or root.name,
            "version": manifest.get("version"),
            "ordo_version": manifest.get("ordo_version") or ((source.get("ordo") or {}).get("version")),
        },
        "generated_at": _utc_now(),
        "gate_summary": {
            "total": len(gate_statuses),
            "passed": len([g for g in gate_statuses if g.get("status") == "passed"]),
            "pending": len([g for g in gate_statuses if str(g.get("status", "")).startswith("pending")]),
            "blocked": len([g for g in gate_statuses if g.get("status") == "blocked"]),
        },
    }
    state_hash = _sha256_json(state)
    template_sets_report: list[dict[str, Any]] = []
    for catalog, catalog_path, meta in catalogs:
        templates = deterministic_entries(catalog)
        set_generated: list[str] = []
        for item in templates:
            template_ref = item.get("template")
            output_path_expr = item.get("path")
            if not template_ref or not output_path_expr:
                continue
            template_path = (catalog_path.parent / template_ref).resolve()
            if not template_path.exists():
                continue
            target_rel = _render_template(output_path_expr, context)
            target = (out_dir / target_rel).resolve()
            target.parent.mkdir(parents=True, exist_ok=True)
            rendered = _render_template(template_path.read_text(encoding="utf-8"), context)
            target.write_text(rendered, encoding="utf-8")
            generated.append(target)
            rel_path = str(target.relative_to(root)) if target.is_relative_to(root) else str(target)
            set_generated.append(rel_path)
            allowed_after = item.get("allowed_after") or []
            output_evidence = [output_by_id.get(output_id) for output_id in allowed_after if output_by_id.get(output_id)]
            required_gate_ids: list[str] = []
            for out_status in output_evidence:
                required_gate_ids.extend(out_status.get("required_gates") or [])
            gate_evidence = [gate_by_id[g] for g in required_gate_ids if g in gate_by_id]
            allowed = True if not output_evidence else all(bool(o.get("allowed")) for o in output_evidence)
            artifact_manifest_entries.append({
                "id": item.get("id") or Path(target_rel).stem,
                "type": item.get("type") or "document",
                "format": item.get("format") or target.suffix.lstrip(".") or "markdown",
                "path": rel_path.replace("\\", "/"),
                "template": {
                    "set_id": meta.get("id"),
                    "set_version": meta.get("version"),
                    "set_source": meta.get("source"),
                    "catalog": str(catalog_path.relative_to(root)) if catalog_path.is_relative_to(root) else str(catalog_path),
                    "template_ref": template_ref,
                    "template_hash": _sha256_file(template_path),
                    "render_mode": item.get("render_mode", "deterministic"),
                    "renderer": item.get("renderer", "ordo.simple"),
                    "requires_model_rendering": bool(item.get("requires_model_rendering", False)),
                },
                "source_state": {
                    "source": None,  # filled by caller
                    "mode": None,    # filled by caller
                    "hash": state_hash,
                },
                "allowed_after": allowed_after,
                "gate_evidence": gate_evidence,
                "output_gate_evidence": output_evidence,
                "handoff_status": "ready_for_handoff" if allowed else "blocked_or_review_only",
                "hash": _sha256_file(target),
                "bytes": target.stat().st_size,
            })
        model_handoffs: list[str] = []
        model_handoff_dir = root / "runtime" / "model_assisted_render_handoff"
        for item in model_assisted_entries(catalog):
            template_ref = item.get("template")
            output_path_expr = item.get("path")
            if not template_ref or not output_path_expr:
                continue
            template_path = (catalog_path.parent / template_ref).resolve()
            if not template_path.exists():
                continue
            expected_output_path = _render_template(output_path_expr, context)
            template_text = template_path.read_text(encoding="utf-8")
            model_handoff_dir.mkdir(parents=True, exist_ok=True)
            handoff = make_model_assisted_handoff(
                root=root,
                catalog_path=catalog_path,
                meta=meta,
                entry=item,
                template_text=template_text,
                confirmed_state=state,
                expected_output_path=expected_output_path,
                context_hash=state_hash,
            )
            handoff_path = model_handoff_dir / f"{_safe_name(item.get('id'), 'model_assisted_template')}.json"
            write_json(handoff_path, handoff)
            model_handoffs.append(str(handoff_path.relative_to(root)).replace("\\", "/"))
        template_sets_report.append({
            "id": meta.get("id"),
            "version": meta.get("version"),
            "source": meta.get("source"),
            "catalog": str(catalog_path.relative_to(root)) if catalog_path.is_relative_to(root) else str(catalog_path),
            "deterministic_templates_total": len(templates),
            "deterministic_templates_generated": len(set_generated),
            "model_assisted_templates_total": len(model_assisted_entries(catalog)),
            "model_assisted_handoffs_created": len(model_handoffs),
            "templates_total": len(templates) + len(model_assisted_entries(catalog)),
            "templates_generated": len(set_generated),
            "generated_files": set_generated,
            "model_assisted_handoff_packets": model_handoffs,
        })
    template_report = {
        "template_sets_total": len(catalogs),
        "templates_total": sum(item["templates_total"] for item in template_sets_report),
        "deterministic_templates_total": sum(item.get("deterministic_templates_total", 0) for item in template_sets_report),
        "model_assisted_templates_total": sum(item.get("model_assisted_templates_total", 0) for item in template_sets_report),
        "model_assisted_handoffs_created": sum(item.get("model_assisted_handoffs_created", 0) for item in template_sets_report),
        "templates_generated": len(generated),
        "mode": "two_tier_template_based",
        "template_sets": template_sets_report,
    }
    return generated, template_report, artifact_manifest_entries

def _make_generic_outputs(root: Path, manifest: dict[str, Any], source: dict[str, Any], state: dict[str, Any], out_dir: Path, *, state_source: str | None, state_mode: str) -> tuple[list[Path], list[dict[str, Any]]]:
    generated: list[Path] = []
    name = manifest.get("name") or (source.get("ordo") or {}).get("package") or root.name
    summary = out_dir / "01_PACKAGE_OUTPUT_SUMMARY.md"
    summary.write_text(f"""# Ordo Package Output Summary — {name}

> Generated by `ordo generate-output`.

## Package

```yaml
name: {manifest.get('name')}
version: {manifest.get('version')}
ordo_version: {manifest.get('ordo_version')}
```

## State

```json
{json.dumps(state, ensure_ascii=False, indent=2)}
```

## Handoff note

This output was generated from package state. It should be treated as a derived artifact. The Ordo Source YAML remains the source of truth.
""", encoding="utf-8")
    generated.append(summary)
    entry = {
        "id": "PACKAGE_OUTPUT_SUMMARY",
        "type": "document",
        "format": "markdown",
        "path": str(summary.relative_to(root)).replace("\\", "/"),
        "template": None,
        "source_state": {"source": state_source, "mode": state_mode, "hash": _sha256_json(state)},
        "allowed_after": [],
        "gate_evidence": _gate_statuses(root),
        "output_gate_evidence": _outputs_status(root),
        "handoff_status": "ready_for_handoff" if all(bool(o.get("allowed")) for o in _outputs_status(root)) else "blocked_or_review_only",
        "hash": _sha256_file(summary),
        "bytes": summary.stat().st_size,
    }
    return generated, [entry]


def _write_output_manifest(root: Path, manifest: dict[str, Any], source: dict[str, Any], artifacts: list[dict[str, Any]], *, state_source: str | None, state_mode: str, generation_mode: str) -> dict[str, Any]:
    """Write a formal M13 manifest for generated output artifacts."""
    output_manifest = {
        "schema": "ordo.output_manifest.v0.1",
        "generated_at": _utc_now(),
        "package": {
            "name": manifest.get("name") or ((source.get("ordo") or {}).get("package")) or root.name,
            "version": manifest.get("version"),
            "ordo_version": manifest.get("ordo_version") or ((source.get("ordo") or {}).get("version")),
        },
        "state_source": state_source,
        "state_mode": state_mode,
        "generation_mode": generation_mode,
        "artifacts_total": len(artifacts),
        "artifacts": artifacts,
        "summary": {
            "ready_for_handoff": len([a for a in artifacts if a.get("handoff_status") == "ready_for_handoff"]),
            "blocked_or_review_only": len([a for a in artifacts if a.get("handoff_status") != "ready_for_handoff"]),
        },
    }
    manifest_path = root / "generated_outputs" / "output_manifest.json"
    write_json(manifest_path, output_manifest)
    return output_manifest

def generate_output(package_path: str | Path, out: str | Path | None = None, require_allowed: bool = True) -> dict[str, Any]:
    root, manifest, source, tests = load_package(package_path)
    output_status = _outputs_status(root)
    blocked_outputs = [o for o in output_status if not o.get("allowed")]
    if require_allowed and output_status and blocked_outputs:
        report = {
            "status": "blocked",
            "generated_at": _utc_now(),
            "reason": "one or more outputs are not allowed by required gates",
            "blocked_outputs": blocked_outputs,
            "generated_files": [],
        }
        write_json(root / "reports" / "output_generation_report.json", report)
        return report

    state, state_source, mode = _load_latest_state(root)
    out_dir = Path(out).resolve() if out else root / "generated_outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    rendering_policy_report = validate_rendering_policy(root, manifest)
    if rendering_policy_report.get("status") == "failed":
        report = {
            "status": "failed",
            "generated_at": _utc_now(),
            "reason": "rendering policy validation failed",
            "rendering_policy_report": rendering_policy_report,
            "generated_files": [],
        }
        write_json(root / "reports" / "output_generation_report.json", report)
        return report

    files, template_report, artifact_manifest_entries = _make_template_outputs(root, manifest, source, state, out_dir)
    generation_mode = (template_report or {}).get("mode") if template_report else "generic_fallback"
    if not files:
        files, artifact_manifest_entries = _make_generic_outputs(root, manifest, source, state, out_dir, state_source=state_source, state_mode=mode)
    else:
        for entry in artifact_manifest_entries:
            entry.setdefault("source_state", {})["source"] = state_source
            entry.setdefault("source_state", {})["mode"] = mode
    output_manifest = _write_output_manifest(root, manifest, source, artifact_manifest_entries, state_source=state_source, state_mode=mode, generation_mode=generation_mode)

    gate_statuses = _gate_statuses(root)
    summary = {
        "status": "passed",
        "generated_at": _utc_now(),
        "package": manifest.get("name") or ((source.get("ordo") or {}).get("package")) or root.name,
        "state_source": state_source,
        "state_mode": mode,
        "generation_mode": generation_mode,
        "template_report": template_report,
        "rendering_policy_report": rendering_policy_report,
        "output_dir": str(out_dir),
        "generated_files": [str(p.relative_to(root)) if p.is_relative_to(root) else str(p) for p in files],
        "output_manifest": "generated_outputs/output_manifest.json",
        "output_manifest_hash": _sha256_file(root / "generated_outputs" / "output_manifest.json"),
        "artifacts_total": output_manifest.get("artifacts_total"),
        "gate_summary": {
            "total": len(gate_statuses),
            "passed": len([g for g in gate_statuses if g.get("status") == "passed"]),
            "pending": len([g for g in gate_statuses if str(g.get("status", "")).startswith("pending")]),
            "blocked": len([g for g in gate_statuses if g.get("status") == "blocked"]),
        },
    }
    write_json(root / "reports" / "output_generation_report.json", summary)
    return summary
