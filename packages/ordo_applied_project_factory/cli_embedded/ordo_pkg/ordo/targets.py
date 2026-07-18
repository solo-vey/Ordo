from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable
import json

from .reporter import write_json
from .runtime_evidence import attach_report_digest, file_sha256
from .session_trace import initialize_session_trace, TRACE_FORMAT, TRACE_PATH
from .runtime import resolve_runtime_paths

TARGETS_SCHEMA_VERSION = "ordo.targets.v1"
ORDO_CODE_VIEW_FORMAT = "ordo-code-view.v1"
PROTOCOL_LINE = "[protocol] raw compiled/* read is a violation; this output is the only valid source"


def normalize_runtime_view(value: str | None) -> str:
    raw = str(value or "ordo-code").strip().lower().replace("_", "-")
    if raw in {"ordo-code-view", "ordocode", "code", "ai-code"}:
        return "ordo-code"
    if raw in {"json-ir", "json_only", "json-only"}:
        return "json"
    if raw in {"json,ordo-code", "ordo-code,json", "all"}:
        return "json,ordo-code"
    if raw in {"json", "ordo-code"}:
        return raw
    return "ordo-code"


def runtime_view_includes_ordo_code(value: str | None) -> bool:
    return normalize_runtime_view(value) in {"ordo-code", "json,ordo-code"}


def runtime_view_behavior(value: str | None) -> dict[str, Any]:
    normalized = normalize_runtime_view(value)
    if normalized == "json":
        return {
            "runtime_view": "json",
            "ai_facing_mode": "json_report",
            "default_next_step_format": "json",
            "question_protocol": "AI shows question/allowed answers from next-step JSON report plus report digest; ordo-code target is not packaged.",
            "allowed_cli_formats": ["json"],
        }
    if normalized == "json,ordo-code":
        return {
            "runtime_view": "json,ordo-code",
            "ai_facing_mode": "mixed_json_and_ordo_code",
            "default_next_step_format": "ordo-code",
            "question_protocol": "AI shows CLI-rendered current_contract fragment plus question and report digest; JSON report remains available for machine checking.",
            "allowed_cli_formats": ["json", "ordo-code"],
        }
    return {
        "runtime_view": "ordo-code",
        "ai_facing_mode": "ordo_code_contract",
        "default_next_step_format": "ordo-code",
        "question_protocol": "AI shows CLI-rendered current_contract fragment plus question and report digest.",
        "allowed_cli_formats": ["ordo-code"],
    }



def _extract_canary(ir: dict[str, Any]) -> str:
    security = ir.get("security") if isinstance(ir, dict) else None
    if isinstance(security, dict) and security.get("canary_secret"):
        return str(security.get("canary_secret"))
    for op in (ir.get("ops", []) if isinstance(ir, dict) else []):
        if isinstance(op, dict) and op.get("canary") and op.get("question"):
            return str(op.get("question"))
    return ""

def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path)


def _sha256_prefixed(path: Path) -> str:
    return "sha256:" + file_sha256(path)


def _local_id(op: dict[str, Any]) -> str:
    return str(op.get("source_local_id") or str(op.get("id", "")).split(".")[-1])


def _strip_namespace(value: Any) -> str:
    if value is None:
        return ""
    return str(value).split(".")[-1]


def _triple(text: Any) -> str:
    body = "" if text is None else str(text)
    body = body.replace('"""', '\"\"\"')
    return '"""\n' + body + '\n    """'


def _allowed_answers(op: dict[str, Any]) -> list[str]:
    allowed = op.get("allowed_answers")
    if isinstance(allowed, list):
        return [str(x) for x in allowed]
    on_answer = op.get("on_answer")
    if isinstance(on_answer, dict) and "update_state" not in on_answer:
        return [str(k) for k in on_answer.keys()]
    return []


def _transition_lines(op: dict[str, Any], indent: str = "    ") -> list[str]:
    on_answer = op.get("on_answer")
    lines: list[str] = []
    if isinstance(on_answer, dict):
        if "next" in on_answer:
            lines.append(f"{indent}answer -> {_strip_namespace(on_answer.get('next')) or 'END'}")
            return lines
        for answer, branch in on_answer.items():
            target = ""
            if isinstance(branch, dict):
                target = _strip_namespace(branch.get("next"))
            lines.append(f"{indent}{answer} -> {target or 'END'}")
    if not lines:
        lines.append(f"{indent}answer -> END")
    return lines


def _node_kind(op: dict[str, Any]) -> str:
    if _allowed_answers(op):
        return "branch"
    return "question"


def _render_node(op: dict[str, Any]) -> str:
    node_id = _local_id(op)
    allowed = _allowed_answers(op)
    kind = _node_kind(op)
    lines: list[str] = []
    lines.append(f"  node {node_id} {{")
    lines.append(f"    kind: {kind}")
    lines.append(f"    answer_type: {op.get('answer_type') or 'free_text'}")
    lines.append("")
    lines.append("    ask: " + _triple(op.get("question")))
    lines.append("")
    if allowed:
        lines.append("    allowed {")
        lines.extend(_transition_lines(op, indent="      "))
        lines.append("    }")
        lines.append("")
        lines.append("    reject unless answer in [" + ", ".join(allowed) + "]")
    else:
        lines.append("    transition {")
        lines.extend(_transition_lines(op, indent="      "))
        lines.append("    }")
        lines.append("")
        lines.append("    accept: free_text")
    if op.get("on_unmatched_input"):
        lines.append("    on_unmatched_input: clarify")
    lines.append("")
    lines.append("    evidence required:")
    lines.append("      next_step_report")
    lines.append("      intake_submit_report")
    lines.append("      runtime_evidence")
    lines.append("  }")
    return "\n".join(lines)


def _render_gate(op: dict[str, Any]) -> str:
    gate_id = _local_id(op)
    condition = op.get("condition")
    if isinstance(condition, dict):
        condition_text = json.dumps(condition, ensure_ascii=False, sort_keys=True)
    else:
        condition_text = str(condition or "")
    return "\n".join([
        f"  gate {gate_id} {{",
        f"    method: {op.get('method') or 'unknown'}",
        f"    trust_class: {op.get('trust_class') or 'unknown'}",
        f"    condition: {condition_text}",
        "    verify through: check-gate / validate-state / verify-session",
        "  }",
    ])


def render_ordo_code_view_from_ir(ir: dict[str, Any], *, ir_hash: str = "", node_id: str | None = None) -> str:
    package = str(ir.get("package") or "unnamed.package")
    lines: list[str] = []
    lines.append(f"program {package} {{")
    lines.append(f"  view_format: {ORDO_CODE_VIEW_FORMAT}")
    if ir_hash:
        lines.append(f"  derived_from_ir_hash: {ir_hash}")
    lines.append("  source_of_truth: compiled/program.ir.json")
    lines.append("  ai_direct_read: false")
    lines.append("")
    matched = False
    for op in ir.get("ops", []) or []:
        if not isinstance(op, dict):
            continue
        if op.get("canary") or op.get("source_local_id") == "N99_CANARY_DO_NOT_EMIT":
            continue
        if op.get("op") == "NODE.DEF":
            local = _local_id(op)
            if node_id and local != node_id:
                continue
            matched = True
            lines.append(_render_node(op))
            lines.append("")
        elif op.get("op") == "GATE.DEF" and not node_id:
            lines.append(_render_gate(op))
            lines.append("")
    if node_id and not matched:
        lines.append(f"  missing_node {node_id} {{")
        lines.append("    status: not_found")
        lines.append("  }")
        lines.append("")
    lines.append("}")
    return "\n".join(lines) + "\n"


def emit_compiled_targets(
    root: str | Path,
    *,
    ir_path: str | Path | None = None,
    source_path: str | Path | None = None,
    runtime_view: str = "ordo-code",
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    compiled_dir = root_path / "compiled"
    compiled_dir.mkdir(parents=True, exist_ok=True)
    ir_file = Path(ir_path).resolve() if ir_path else compiled_dir / "program.ir.json"
    ir = json.loads(ir_file.read_text(encoding="utf-8"))
    canonical_ir_hash = _sha256_prefixed(ir_file)

    targets: dict[str, Any] = {
        "json-ir": {
            "path": _rel(root_path, ir_file),
            "role": "canonical_runtime_ir",
            "source_of_truth": True,
            "ai_direct_read": False,
            "sha256": canonical_ir_hash,
        }
    }

    normalized_runtime_view = normalize_runtime_view(runtime_view)
    view_file = compiled_dir / "program.ordo.view"
    if runtime_view_includes_ordo_code(normalized_runtime_view):
        view_file.write_text(render_ordo_code_view_from_ir(ir, ir_hash=canonical_ir_hash), encoding="utf-8")
        targets["ordo-code-view"] = {
            "path": _rel(root_path, view_file),
            "role": "ai_facing_runtime_contract",
            "format": ORDO_CODE_VIEW_FORMAT,
            "source_of_truth": False,
            "ai_direct_read": False,
            "served_by_cli": True,
            "derived_from_ir_hash": canonical_ir_hash,
            "sha256": _sha256_prefixed(view_file),
        }
    elif view_file.exists():
        # Prevent a stale M60.1/M60.2 ordo-code projection from leaking into
        # an explicitly JSON-only runtime package.
        view_file.unlink()

    trace_info = initialize_session_trace(root_path, ir_hash=canonical_ir_hash, package_name=str(ir.get("package") or root_path.name))
    targets["session-trace"] = {
        "path": TRACE_PATH,
        "role": "append_only_execution_proof",
        "format": TRACE_FORMAT,
        "source_of_truth": False,
        "mutable": True,
        "written_by": "cli",
        "verified_by": "verify-session",
        "derived_from_ir_hash": canonical_ir_hash,
        "initial_sha256": trace_info.get("sha256", ""),
    }

    source_hash = ""
    if source_path:
        sp = Path(source_path).resolve()
        if sp.exists():
            source_hash = _sha256_prefixed(sp)

    manifest = {
        "schema_version": TARGETS_SCHEMA_VERSION,
        "source_hash": source_hash,
        "canonical_ir_hash": canonical_ir_hash,
        "canonical_target": "json-ir",
        "runtime_view": normalized_runtime_view,
        "runtime_view_behavior": runtime_view_behavior(normalized_runtime_view),
        "targets": targets,
    }
    write_json(compiled_dir / "targets.manifest.json", manifest)
    return manifest


def _load_ir_for_runtime(package_path: str | Path) -> tuple[Path, Path, dict[str, Any]]:
    resolved = resolve_runtime_paths(package_path)
    if resolved.get("status") != "resolved":
        raise RuntimeError(json.dumps(resolved.get("issues", []), ensure_ascii=False))
    root: Path = resolved["root"]
    ir_file: Path = resolved["compiled_path"]
    return root, ir_file, json.loads(ir_file.read_text(encoding="utf-8"))


def render_runtime_view(
    package_path: str | Path,
    *,
    format: str = "ordo-code",
    node_id: str | None = None,
    out: str | Path | None = None,
) -> dict[str, Any]:
    if format not in {"ordo-code", "ordo-code-view"}:
        report = {"status": "failed", "issues": [{"severity": "error", "code": "ORDO-TARGET-010", "message": f"unsupported runtime view format: {format}"}]}
        return report
    root, ir_file, ir = _load_ir_for_runtime(package_path)
    # In a packaged runtime profile, only expose ordo-code when that projection
    # was deliberately packaged for this runtime_view mode. Source/dev packages
    # may still render the view for authoring-time inspection.
    runtime_manifest = root / "ordo.runtime.json"
    targets_manifest = root / "compiled" / "targets.manifest.json"
    if runtime_manifest.exists():
        try:
            tm = json.loads(targets_manifest.read_text(encoding="utf-8"))
        except Exception:
            tm = {}
        if "ordo-code-view" not in ((tm.get("targets") or {}) if isinstance(tm, dict) else {}):
            report = {
                "status": "blocked",
                "issues": [{"severity": "error", "code": "ORDO-TARGET-015", "message": "ordo-code runtime view is not packaged for this runtime_view mode", "location": "compiled/targets.manifest.json"}],
                "human_output_policy": "Use next-step JSON report in runtime_view=json mode, or rebuild the runtime package with --runtime-view ordo-code.",
            }
            target = Path(out).resolve() if out else root / "reports" / "runtime_view_report.json"
            write_json(target, attach_report_digest(report))
            return report
    ir_hash = _sha256_prefixed(ir_file)
    view = render_ordo_code_view_from_ir(ir, ir_hash=ir_hash, node_id=node_id)
    report = {
        "status": "generated",
        "mode": "m60_1_ai_facing_runtime_view",
        "format": "ordo-code",
        "node_id": node_id or "",
        "runtime_source": _rel(root, ir_file),
        "derived_from_ir_hash": ir_hash,
        "protocol": PROTOCOL_LINE,
        "view": view,
        "human_output_policy": "AI may show this CLI-rendered contract fragment; direct compiled/* reading remains prohibited.",
    }
    report = attach_report_digest(report)
    target = Path(out).resolve() if out else root / "reports" / "runtime_view_report.json"
    write_json(target, report)
    return report


def verify_targets(package_path: str | Path, *, out: str | Path | None = None) -> dict[str, Any]:
    resolved = resolve_runtime_paths(package_path)
    if resolved.get("status") != "resolved":
        root_obj = resolved.get("root")
        root = Path(root_obj) if root_obj else Path(package_path).resolve()
        report = {"status": "failed", "mode": "m60_1_target_verification", "issues": resolved.get("issues", [])}
        target = Path(out).resolve() if out else root / "reports" / "target_verification_report.json"
        write_json(target, attach_report_digest(report))
        return report
    root: Path = resolved["root"]
    compiled_path: Path = resolved["compiled_path"]
    manifest_path = root / "compiled" / "targets.manifest.json"
    issues: list[dict[str, Any]] = []
    target_results: dict[str, Any] = {}
    if not manifest_path.exists():
        issues.append({"severity": "error", "code": "ORDO-TARGET-001", "message": "targets.manifest.json missing", "location": "compiled/targets.manifest.json"})
        manifest: dict[str, Any] = {}
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as exc:
            manifest = {}
            issues.append({"severity": "error", "code": "ORDO-TARGET-002", "message": f"targets.manifest.json invalid: {exc}", "location": "compiled/targets.manifest.json"})
    actual_ir_hash = _sha256_prefixed(compiled_path) if compiled_path.exists() else ""
    if manifest and manifest.get("canonical_ir_hash") != actual_ir_hash:
        issues.append({"severity": "error", "code": "ORDO-TARGET-003", "message": "canonical_ir_hash mismatch", "location": "compiled/targets.manifest.json"})
    targets = manifest.get("targets") if isinstance(manifest.get("targets"), dict) else {}
    if "json-ir" not in targets:
        issues.append({"severity": "error", "code": "ORDO-TARGET-004", "message": "json-ir target missing", "location": "compiled/targets.manifest.json"})
    for name, spec in targets.items():
        if not isinstance(spec, dict):
            issues.append({"severity": "error", "code": "ORDO-TARGET-005", "message": f"target spec is not a mapping: {name}", "location": "compiled/targets.manifest.json"})
            continue
        path = root / str(spec.get("path", ""))
        result = {"path": spec.get("path"), "status": "ok"}
        if not path.exists():
            result["status"] = "missing"
            issues.append({"severity": "error", "code": "ORDO-TARGET-006", "message": f"target file missing: {name}", "location": str(spec.get("path", ""))})
        else:
            actual = _sha256_prefixed(path)
            result["actual_sha256"] = actual
            if spec.get("mutable"):
                result["status"] = "ok_mutable"
                result["initial_sha256"] = spec.get("initial_sha256", "")
                if name == "session-trace":
                    try:
                        from .session_trace import parse_session_trace
                        parsed_trace = parse_session_trace(root)
                        if parsed_trace.get("format") and parsed_trace.get("format") != spec.get("format"):
                            result["status"] = "format_mismatch"
                            issues.append({"severity": "error", "code": "ORDO-TARGET-012", "message": "session-trace format mismatch", "location": str(spec.get("path", ""))})
                        if parsed_trace.get("ir_hash") and parsed_trace.get("ir_hash") != actual_ir_hash:
                            result["status"] = "ir_hash_mismatch"
                            issues.append({"severity": "error", "code": "ORDO-TARGET-013", "message": "session-trace ir_hash mismatch", "location": str(spec.get("path", ""))})
                    except Exception as exc:
                        result["status"] = "parse_error"
                        issues.append({"severity": "error", "code": "ORDO-TARGET-014", "message": f"session-trace cannot be parsed: {exc}", "location": str(spec.get("path", ""))})
            else:
                if spec.get("sha256") != actual:
                    result["status"] = "hash_mismatch"
                    issues.append({"severity": "error", "code": "ORDO-TARGET-007", "message": f"target hash mismatch: {name}", "location": str(spec.get("path", ""))})
            if name != "json-ir" and spec.get("derived_from_ir_hash") != actual_ir_hash:
                result["status"] = "ir_hash_mismatch"
                issues.append({"severity": "error", "code": "ORDO-TARGET-008", "message": f"target derived_from_ir_hash mismatch: {name}", "location": str(spec.get("path", ""))})
        target_results[name] = result

    # Keep M59.3 canary invisible in all AI-facing target projections.
    try:
        ir = json.loads(compiled_path.read_text(encoding="utf-8")) if compiled_path.exists() else {}
        canary = _extract_canary(ir)
        for name, spec in targets.items():
            if name == "json-ir" or not isinstance(spec, dict):
                continue
            path = root / str(spec.get("path", ""))
            if path.exists():
                text = path.read_text(encoding="utf-8", errors="ignore")
                if (canary and canary in text) or "N99_CANARY_DO_NOT_EMIT" in text:
                    issues.append({"severity": "error", "code": "ORDO-TARGET-009", "message": f"canary leaked into AI-facing target: {name}", "location": str(spec.get("path", ""))})
    except Exception:
        pass

    report = {
        "status": "passed" if not issues else "failed",
        "mode": "m60_1_target_verification",
        "manifest": "compiled/targets.manifest.json",
        "canonical_ir_hash": actual_ir_hash,
        "target_results": target_results,
        "terminal_line": "target-set: consistent" if not issues else "target-set: inconsistent",
        "issues": issues,
    }
    report = attach_report_digest(report)
    target = Path(out).resolve() if out else root / "reports" / "target_verification_report.json"
    write_json(target, report)
    return report
