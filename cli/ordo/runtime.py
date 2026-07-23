from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import time

from .loader import load_yaml, resolve_package_root
from .compiler import compile_source
from .reporter import write_json

RUNTIME_STATUS_VALUES = {
    "ready",
    "missing_manifest",
    "missing_source",
    "missing_ir",
    "stale_ir",
    "invalid_manifest",
    "invalid_ir",
}

CLI_TRUTHFULNESS_STATUSES = {
    "executed_cli_passed",
    "executed_cli_failed",
    "logical_self_check_only",
    "not_run_cli_unavailable",
    "not_run_user_skipped",
}


def _rel(root: Path, path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path)


def _issue(code: str, message: str, *, location: str | None = None, severity: str = "error") -> dict[str, Any]:
    return {"severity": severity, "code": code, "message": message, "location": location}


def resolve_runtime_paths(package_path: str | Path) -> dict[str, Any]:
    p = Path(package_path).resolve()
    if p.is_file():
        p = p.parent

    try:
        root = resolve_package_root(p)
        manifest_path = root / "ordo.yml"
        manifest_kind = "ordo.yml"
        try:
            manifest = load_yaml(manifest_path)
        except Exception as exc:
            return {
                "status": "invalid_manifest",
                "root": str(root),
                "manifest_path": _rel(root, manifest_path),
                "issues": [_issue("ORDO-RUNTIME-001", f"ordo.yml is invalid: {exc}", location=_rel(root, manifest_path))],
            }
        if not isinstance(manifest, dict):
            return {
                "status": "invalid_manifest",
                "root": str(root),
                "manifest_path": _rel(root, manifest_path),
                "issues": [_issue("ORDO-RUNTIME-001", "ordo.yml must parse to a mapping", location=_rel(root, manifest_path))],
            }
        source_path = root / manifest.get("source", "source/program.ordo.yaml")
        compiled_path = root / manifest.get("compiled", "compiled/program.ir.json")
        reports_dir = root / manifest.get("reports", "reports")
    except FileNotFoundError:
        # Runtime profile packages intentionally omit ordo.yml and source YAML.
        # Their runtime entrypoint is ordo.runtime.json.
        root = p
        if not (root / "ordo.runtime.json").exists() and (root.parent / "ordo.runtime.json").exists():
            root = root.parent
        manifest_path = root / "ordo.runtime.json"
        manifest_kind = "ordo.runtime.json"
        if not manifest_path.exists():
            return {
                "status": "missing_manifest",
                "root": str(p),
                "issues": [_issue("ORDO-RUNTIME-001", f"ordo.yml or ordo.runtime.json missing near {p}", location=str(p))],
            }
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return {
                "status": "invalid_manifest",
                "root": str(root),
                "manifest_path": _rel(root, manifest_path),
                "issues": [_issue("ORDO-RUNTIME-001", f"ordo.runtime.json is invalid: {exc}", location=_rel(root, manifest_path))],
            }
        if not isinstance(manifest, dict):
            return {
                "status": "invalid_manifest",
                "root": str(root),
                "manifest_path": _rel(root, manifest_path),
                "issues": [_issue("ORDO-RUNTIME-001", "ordo.runtime.json must parse to a mapping", location=_rel(root, manifest_path))],
            }
        manifest = {
            "name": manifest.get("package_id"),
            "version": manifest.get("package_version"),
            "compiled": manifest.get("runtime_source", "compiled/program.ir.json"),
            "reports": "reports",
            "runtime_profile": True,
            "source_yaml_included": manifest.get("source_yaml_included", False),
            "runtime_manifest": manifest,
        }
        source_path = root / "source" / "program.ordo.yaml"
        compiled_path = root / manifest.get("compiled", "compiled/program.ir.json")
        reports_dir = root / "reports"
    return {
        "status": "resolved",
        "root": root,
        "manifest": manifest,
        "manifest_kind": manifest_kind,
        "manifest_path": manifest_path,
        "source_path": source_path,
        "compiled_path": compiled_path,
        "reports_dir": reports_dir,
        "issues": [],
    }


def runtime_status(package_path: str | Path, *, require_ir: bool = True, out: str | Path | None = None) -> dict[str, Any]:
    resolved = resolve_runtime_paths(package_path)
    if resolved.get("status") != "resolved":
        root_obj = resolved.get("root")
        root = Path(root_obj) if root_obj else Path(package_path).resolve()
        report = {
            "status": resolved.get("status"),
            "mode": "runtime_source_of_truth_check",
            "source_of_truth": {
                "manifest": "ordo.yml or ordo.runtime.json",
                "editable_source": "source/program.ordo.yaml",
                "runtime_ir": "compiled/program.ir.json",
                "run_state": "run_state.json or reports/*_report.json state",
                "generated_artifacts": "generated_outputs/",
            },
            "issues": resolved.get("issues", []),
        }
        if out:
            write_json(Path(out), report)
        return report

    root: Path = resolved["root"]
    manifest: dict[str, Any] = resolved["manifest"]
    source_path: Path = resolved["source_path"]
    compiled_path: Path = resolved["compiled_path"]
    issues: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    if not source_path.exists() and not manifest.get("runtime_profile"):
        issues.append(_issue("ORDO-RUNTIME-002", "source program not found", location=_rel(root, source_path)))
    if require_ir and not compiled_path.exists():
        issues.append(_issue("ORDO-RUNTIME-003", "compiled IR missing", location=_rel(root, compiled_path)))
    if source_path.exists() and compiled_path.exists():
        source_mtime = source_path.stat().st_mtime
        ir_mtime = compiled_path.stat().st_mtime
        if source_mtime > ir_mtime + 0.0001:
            issues.append(_issue("ORDO-RUNTIME-004", "IR is stale. Run ordo compile before guided execution.", location=_rel(root, compiled_path)))
    elif not require_ir and not compiled_path.exists():
        warnings.append(_issue("ORDO-RUNTIME-003", "compiled IR missing; non-runtime fallback mode only", location=_rel(root, compiled_path), severity="warning"))

    status = "ready" if not issues else (issues[0]["code"].replace("ORDO-RUNTIME-", "runtime_error_"))
    if issues:
        code = issues[0]["code"]
        status = {
            "ORDO-RUNTIME-001": "missing_manifest",
            "ORDO-RUNTIME-002": "missing_source",
            "ORDO-RUNTIME-003": "missing_ir",
            "ORDO-RUNTIME-004": "stale_ir",
        }.get(code, "runtime_error")

    report = {
        "status": status,
        "mode": "runtime_source_of_truth_check",
        "package": manifest.get("name"),
        "package_version": manifest.get("version"),
        "source_of_truth": {
            "manifest": _rel(root, resolved["manifest_path"]),
            "manifest_kind": resolved.get("manifest_kind", "ordo.yml"),
            "editable_source": _rel(root, source_path),
            "runtime_ir": _rel(root, compiled_path),
            "run_state": "run_state.json or reports/intake_report.json",
            "generated_artifacts": "generated_outputs/",
        },
        "freshness": {
            "source_exists": source_path.exists(),
            "compiled_ir_exists": compiled_path.exists(),
            "source_mtime": source_path.stat().st_mtime if source_path.exists() else None,
            "compiled_ir_mtime": compiled_path.stat().st_mtime if compiled_path.exists() else None,
            "checked_at_epoch": time.time(),
        },
        "issues": issues,
        "warnings": warnings,
    }
    target = Path(out).resolve() if out else root / "reports" / "runtime_status_report.json"
    write_json(target, report)
    return report


def load_runtime_source(package_path: str | Path) -> tuple[Path, dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Load the runtime representation from compiled/program.ir.json.

    The returned source-like mapping is intentionally minimal: it contains the
    Process Rail units needed by deterministic helper commands. This prevents
    helper commands such as next-step from silently using edited YAML when a
    compiled IR exists.
    """
    status = runtime_status(package_path, require_ir=True)
    if status.get("status") != "ready":
        raise RuntimeError(json.dumps(status.get("issues", []), ensure_ascii=False))
    resolved = resolve_runtime_paths(package_path)
    root: Path = resolved["root"]
    manifest: dict[str, Any] = resolved["manifest"]
    compiled_path: Path = resolved["compiled_path"]
    ir = json.loads(compiled_path.read_text(encoding="utf-8"))
    ops = ir.get("ops", []) or []
    source: dict[str, Any] = {
        "ordo": {"version": ir.get("ordo_version"), "package": ir.get("package")},
        "contract": {},
        "state": {},
        "nodes": [],
        "gates": [],
        "assertions": [],
        "outputs": [],
        "execution_trace": None,
        "conversation_scope_guard": None,
        "runtime_source": "compiled_ir",
        "graph_contract": {},
    }
    for op in ops:
        op_name = op.get("op")
        if op_name == "CONTRACT.DEF":
            source["contract"] = {"id": op.get("source_local_id") or op.get("id"), "required": op.get("required", [])}
        elif op_name == "STATE.SCHEMA":
            source["state"] = {"id": op.get("source_local_id") or op.get("id"), "schema": op.get("schema", {})}
        elif op_name == "EXECUTION_TRACE.DEF":
            source["execution_trace"] = {
                "id": op.get("source_local_id") or op.get("id"),
                "enabled": op.get("enabled", True),
                "version": op.get("version", "1.0"),
                "capture_level": op.get("capture_level", "standard"),
                "storage": op.get("storage", {}),
                "replay": op.get("replay", {}),
            }
        elif op_name == "CONVERSATION.SCOPE.DEF":
            source["conversation_scope_guard"] = {
                "id": op.get("source_local_id") or op.get("id"),
                "supported": op.get("supported", False),
                "enabled": op.get("enabled", False),
                "mode": op.get("mode"),
                "scope": op.get("scope"),
                "out_of_scope_behavior": op.get("out_of_scope_behavior"),
                "state_change_on_out_of_scope": op.get("state_change_on_out_of_scope", False),
                "escalation": op.get("escalation", {}),
                "trace": op.get("trace", {}),
            }
        elif op_name == "GRAPH.CONTRACT":
            source["graph_contract"] = {k: v for k, v in op.items() if k not in {"op", "id"}}
        elif op_name == "NODE.DEF":
            if op.get("canary") or (op.get("source_local_id") == "N99_CANARY_DO_NOT_EMIT"):
                continue
            on_answer = op.get("on_answer")
            allowed_answers = op.get("allowed_answers")
            if allowed_answers is None and isinstance(on_answer, dict) and "update_state" not in on_answer:
                allowed_answers = [str(k) for k in on_answer.keys()]
            source["nodes"].append({
                "id": op.get("source_local_id") or str(op.get("id", "")).split(".")[-1],
                "question": op.get("question"),
                "answer_type": op.get("answer_type"),
                "allowed_answers": allowed_answers,
                "on_answer": on_answer,
                "on_unmatched_input": op.get("on_unmatched_input"),
                "allow_unmatched_input": op.get("allow_unmatched_input", False),
                "required_fields": op.get("required_fields"),
                "allow_batch_confirmation": op.get("allow_batch_confirmation", False),
                "antipattern_hooks": op.get("antipattern_hooks") or [],
                "allowed_from": op.get("allowed_from") or [],
                "entry_modes": op.get("entry_modes") or [],
                "node_context": op.get("node_context") or {},
            })
        elif op_name == "GATE.DEF":
            source["gates"].append({
                "id": op.get("source_local_id") or str(op.get("id", "")).split(".")[-1],
                "method": op.get("method"),
                "trust_class": op.get("trust_class"),
                "condition": op.get("condition"),
                "on_fail": op.get("on_fail"),
            })
        elif op_name == "ASSERTION.DEF":
            source["assertions"].append({
                "id": op.get("source_local_id") or str(op.get("id", "")).split(".")[-1],
                "polarity": op.get("polarity"),
                "condition": op.get("condition"),
                "phase": op.get("phase"),
                "severity": op.get("severity"),
                "on_fail": op.get("on_fail"),
            })
        elif op_name == "OUTPUT.DEF":
            source["outputs"].append({
                "id": op.get("source_local_id") or str(op.get("id", "")).split(".")[-1],
                "type": op.get("type"),
                "allowed_after": [str(g).split(".")[-1] for g in op.get("allowed_after", [])],
            })
    return root, manifest, source, ir


def default_run_state(package: str = "", version: str = "") -> dict[str, Any]:
    return {
        "package_id": package,
        "package_version": version,
        "current_node": "",
        "last_closed_node": "",
        "earliest_incomplete_node": "",
        "checkpoint_table": {},
        "forward_allowed": False,
        "open_required_fields": [],
        "node_merge_attempt_detected": False,
        "answered_questions": [],
        "contracts": {},
        "gates": {},
        "decisions": [],
        "open_questions": [],
        "blocked": False,
        "go_no_go": "unknown",
    }



def validate_runtime_start_files_standard(package_path: str | Path) -> dict[str, Any]:
    """Validate package-owned Runtime Mode start files.

    This validates that Runtime Mode rules live inside the package and that the
    short prompt remains short. It intentionally does not require compiled IR;
    freshness is handled by runtime-status/runtime-entry.
    """
    try:
        resolved = resolve_runtime_paths(package_path)
        if resolved.get("status") != "resolved":
            root = Path(resolved.get("root") or package_path).resolve()
            return {"status": "failed", "mode": "runtime_start_files_standard", "issues": resolved.get("issues", []), "warnings": []}
        root: Path = resolved["root"]
    except Exception as exc:
        return {"status": "failed", "mode": "runtime_start_files_standard", "issues": [_issue("ORDO-RUNTIME-001", str(exc))], "warnings": []}

    issues: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    start_here = root / "START_HERE_RUNTIME_MODE.md"
    start_prompt = root / "START_PROMPT_RUNTIME_MODE.md"
    readme = root / "README.md"
    cli_summary = root / "reports" / "CLI_VALIDATION_SUMMARY.md"

    required_here = [
        ("runtime loading protocol", "runtime loading protocol"),
        ("source of truth", "source of truth"),
        ("CLI truthfulness", "CLI truthfulness"),
        ("Fallback mode", "hard-stop fallback mode"),
        ("cli_embedded/ordo", "embedded runtime CLI"),
        ("DETERMINISM_NOT_ENFORCED", "non-enforced determinism marker"),
        ("gate discipline", "gate discipline"),
        ("artifact validation", "artifact validation"),
        ("checkpoint discipline", "checkpoint discipline"),
        ("one node at a time", "one node at a time"),
        ("One question", "one question protocol"),
        ("Do not conduct guided intake", "no memory mode"),
        ("IR ACCESS PROTOCOL", "hard IR access protocol"),
        ("verify-session", "session verification command"),
        ("session-chain", "session-chain terminal verdict"),
        ("CANARY", "canary leak detection"),
    ]
    if not start_here.exists():
        issues.append(_issue("ORDO-RUNTIME-010", "START_HERE_RUNTIME_MODE.md missing", location="START_HERE_RUNTIME_MODE.md"))
        here_text = ""
    else:
        here_text = start_here.read_text(encoding="utf-8")
        for token, label in required_here:
            if token.lower() not in here_text.lower():
                issues.append(_issue("ORDO-RUNTIME-011", f"START_HERE_RUNTIME_MODE.md missing {label}", location="START_HERE_RUNTIME_MODE.md"))

    if not start_prompt.exists():
        issues.append(_issue("ORDO-RUNTIME-012", "START_PROMPT_RUNTIME_MODE.md missing", location="START_PROMPT_RUNTIME_MODE.md"))
        prompt_text = ""
    else:
        prompt_text = start_prompt.read_text(encoding="utf-8")
        if "START_HERE_RUNTIME_MODE.md" not in prompt_text:
            issues.append(_issue("ORDO-RUNTIME-013", "minimal runtime prompt must point to START_HERE_RUNTIME_MODE.md", location="START_PROMPT_RUNTIME_MODE.md"))
        if len(prompt_text.split()) > 256:
            issues.append(_issue("ORDO-RUNTIME-014", "START_PROMPT_RUNTIME_MODE.md is too long; detailed runtime rules belong in START_HERE_RUNTIME_MODE.md", location="START_PROMPT_RUNTIME_MODE.md"))
        forbidden_detail_tokens = ["Gate discipline", "Artifact validation discipline", "CLI pipeline", "Hard-stop fallback mode", "DETERMINISM_NOT_ENFORCED"]
        for token in forbidden_detail_tokens:
            if token.lower() in prompt_text.lower():
                issues.append(_issue("ORDO-RUNTIME-014", f"START_PROMPT_RUNTIME_MODE.md duplicates runtime detail: {token}", location="START_PROMPT_RUNTIME_MODE.md"))

    if not readme.exists():
        warnings.append(_issue("ORDO-RUNTIME-015", "README.md missing", location="README.md", severity="warning"))
    else:
        readme_text = readme.read_text(encoding="utf-8")
        for token in ("START_HERE_RUNTIME_MODE.md", "START_PROMPT_RUNTIME_MODE.md", "compiled/program.ir.json", "source/program.ordo.yaml"):
            if token not in readme_text:
                warnings.append(_issue("ORDO-RUNTIME-015", f"README.md should mention {token}", location="README.md", severity="warning"))

    if not cli_summary.exists():
        issues.append(_issue("ORDO-RUNTIME-016", "reports/CLI_VALIDATION_SUMMARY.md missing", location="reports/CLI_VALIDATION_SUMMARY.md"))
    else:
        summary_text = cli_summary.read_text(encoding="utf-8")
        if "CLI status:" not in summary_text:
            issues.append(_issue("ORDO-RUNTIME-016", "CLI validation summary must contain 'CLI status:'", location="reports/CLI_VALIDATION_SUMMARY.md"))

    return {
        "status": "passed" if not issues else "failed",
        "mode": "runtime_start_files_standard",
        "checked_files": [
            "START_HERE_RUNTIME_MODE.md",
            "START_PROMPT_RUNTIME_MODE.md",
            "README.md",
            "reports/CLI_VALIDATION_SUMMARY.md",
        ],
        "issues": issues,
        "warnings": warnings,
    }

def validate_cli_truthfulness(report: dict[str, Any]) -> dict[str, Any]:
    status = report.get("cli_status") or report.get("CLI status") or report.get("cli_validation_status")
    issues: list[dict[str, Any]] = []
    if status is None:
        return {"status": "failed", "warnings": [], "issues": [_issue("ORDO-RUNTIME-TRUTH-001", "report does not declare CLI status")] }
    if status not in CLI_TRUTHFULNESS_STATUSES:
        issues.append(_issue("ORDO-RUNTIME-TRUTH-002", f"invalid CLI truthfulness status: {status}"))
    if status == "executed_cli_passed" and not report.get("executed_commands") and not report.get("cli_evidence"):
        issues.append(_issue("ORDO-RUNTIME-TRUTH-003", "report claims executed_cli_passed without executed command evidence"))
    return {"status": "passed" if not issues else "failed", "issues": issues, "warnings": []}


def _load_state_file_for_entry(state_path: str | Path | None) -> dict[str, Any]:
    if not state_path:
        return {}
    path = Path(state_path).resolve()
    try:
        data = load_yaml(path)
    except Exception:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    if isinstance(data, dict) and isinstance(data.get("state"), dict):
        return data["state"]
    return data if isinstance(data, dict) else {}


def _runtime_next_node_from_ir(ir: dict[str, Any], state: dict[str, Any]) -> tuple[str | None, dict[str, Any] | None]:
    nodes: list[dict[str, Any]] = []
    for op in ir.get("ops", []) or []:
        if op.get("op") == "NODE.DEF":
            nodes.append(op)
    if not nodes:
        return None, None
    current = state.get("current_node")
    answered = set(state.get("answered_questions") or [])
    for node in nodes:
        local_id = node.get("source_local_id") or str(node.get("id", "")).split(".")[-1]
        if current and local_id == current:
            return local_id, node
    for node in nodes:
        local_id = node.get("source_local_id") or str(node.get("id", "")).split(".")[-1]
        if local_id not in answered:
            return local_id, node
    return None, None


def runtime_entry_protocol(package_path: str | Path, *, state_path: str | Path | None = None, out: str | Path | None = None) -> dict[str, Any]:
    """Validate the required AI Runtime Mode entry sequence.

    This command is intentionally conservative: it does not conduct the guided
    intake. It proves that an AI Ordo Developer/Executor has a readable
    START_HERE_RUNTIME_MODE.md, a valid manifest, a current compiled IR, and a
    next step derived from IR + run_state instead of memory.
    """
    status = runtime_status(package_path, require_ir=True)
    resolved = resolve_runtime_paths(package_path)
    auto_compiled = False
    if resolved.get("status") == "resolved" and status.get("status") in {"missing_ir", "stale_ir"}:
        try:
            source = load_yaml(resolved["source_path"])
            ir_obj = compile_source(source)
            Path(resolved["compiled_path"]).parent.mkdir(parents=True, exist_ok=True)
            write_json(resolved["compiled_path"], ir_obj)
            auto_compiled = True
            status = runtime_status(package_path, require_ir=True)
            resolved = resolve_runtime_paths(package_path)
        except Exception as exc:
            status.setdefault("issues", []).append(_issue("ORDO-RUNTIME-003", f"compiled IR missing or stale and auto-compile failed: {exc}", location="compiled/program.ir.json"))
    root_obj = resolved.get("root") or status.get("root") or package_path
    root = Path(root_obj).resolve() if not isinstance(root_obj, Path) else root_obj
    start_here = root / "START_HERE_RUNTIME_MODE.md"
    issues: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    if not start_here.exists():
        issues.append(_issue("ORDO-RUNTIME-007", "START_HERE_RUNTIME_MODE.md missing; runtime session must not start from memory", location="START_HERE_RUNTIME_MODE.md"))
    elif not start_here.read_text(encoding="utf-8").strip():
        issues.append(_issue("ORDO-RUNTIME-007", "START_HERE_RUNTIME_MODE.md is empty", location="START_HERE_RUNTIME_MODE.md"))
    if status.get("status") != "ready":
        issues.extend(status.get("issues", []))
        ir = {}
        manifest = resolved.get("manifest") if isinstance(resolved.get("manifest"), dict) else {}
    else:
        try:
            ir = json.loads(Path(resolved["compiled_path"]).read_text(encoding="utf-8"))
        except Exception as exc:
            ir = {}
            issues.append(_issue("ORDO-RUNTIME-008", f"compiled IR cannot be loaded: {exc}", location=_rel(root, resolved.get("compiled_path"))))
        manifest = resolved.get("manifest") if isinstance(resolved.get("manifest"), dict) else {}
    run_state = default_run_state(str(manifest.get("name") or ir.get("package") or ""), str(manifest.get("version") or ""))
    run_state.update(_load_state_file_for_entry(state_path))
    node_id, node = _runtime_next_node_from_ir(ir, run_state)
    if status.get("status") == "ready" and not node_id:
        warnings.append(_issue("ORDO-RUNTIME-009", "No next NODE.DEF found in compiled IR", severity="warning"))
    report = {
        "status": "ready" if not issues else "blocked",
        "mode": "runtime_guided_intake_entry_protocol",
        "cli_status": "executed_cli_passed" if not issues else "executed_cli_failed",
        "executed_commands": (["runtime-entry", "compile"] if auto_compiled else ["runtime-entry"]),
        "auto_compiled_ir": auto_compiled,
        "entry_sequence": [
            "read START_HERE_RUNTIME_MODE.md",
            "read ordo.yml or ordo.runtime.json",
            "resolve source/program.ordo.yaml",
            "verify compiled/program.ir.json freshness",
            "load compiled IR as runtime",
            "initialize/load run_state",
            "derive next step from IR + run_state",
        ],
        "runtime_status": status,
        "workspace": {
            "loaded_manifest": _rel(root, resolved.get("manifest_path")) if resolved.get("manifest_path") else None,
            "loaded_source": _rel(root, resolved.get("source_path")) if resolved.get("source_path") else None,
            "loaded_ir": _rel(root, resolved.get("compiled_path")) if resolved.get("compiled_path") else None,
            "run_state": str(state_path) if state_path else "default_runtime_state",
            "generated_outputs": "generated_outputs/",
        },
        "guardrails": {
            "must_use_compiled_ir_when_ready": True,
            "must_not_invent_question_order": True,
            "must_check_gate_before_advancing": True,
            "must_not_generate_draft_before_validate_state": True,
            "must_not_generate_final_before_validate_output_and_consistency": True,
            "after_A_path_use_runtime_A_flow_without_A1_A5_subquestions": True,
            "human_protocol_fields": ["Step", "Action", "Result", "Decision", "One question"],
            "checkpoint_discipline": "one node at a time; earliest incomplete node wins",
        },
        "next_step": {
            "source": "compiled_ir" if status.get("status") == "ready" else "unavailable",
            "node_id": node_id,
            "question": node.get("question") if node else None,
            "answer_type": node.get("answer_type") if node else None,
        },
        "issues": issues,
        "warnings": warnings,
    }
    target = Path(out).resolve() if out else root / "reports" / "runtime_entry_report.json"
    write_json(target, report)
    return report
