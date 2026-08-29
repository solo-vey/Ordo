from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import re

from .runtime import resolve_runtime_paths
from .runtime_evidence import file_sha256, canonical_sha256, utc_now, attach_report_digest

TRACE_FORMAT = "ordo-session-trace.v1"
TRACE_PATH = "runtime/session.ordo.trace"


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path)


def _safe_program_name(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"_", "-", "."} else "_" for ch in value)
    return cleaned or "ordo_session"


def _triple(text: Any) -> str:
    body = "" if text is None else str(text)
    body = body.replace('"""', '\"\"\"')
    return '"""\n' + body + '\n    """'


def trace_path(root: str | Path) -> Path:
    return Path(root) / TRACE_PATH


def trace_digest(root: str | Path) -> str:
    path = trace_path(root)
    if not path.exists():
        return ""
    return "sha256:" + file_sha256(path)


def _ir_hash_for_root(root: Path) -> str:
    ir = root / "compiled" / "program.ir.json"
    if not ir.exists():
        return ""
    return "sha256:" + file_sha256(ir)


def _package_name_from_ir(root: Path) -> str:
    ir = root / "compiled" / "program.ir.json"
    if not ir.exists():
        return root.name
    try:
        data = json.loads(ir.read_text(encoding="utf-8"))
        return str(data.get("package") or root.name)
    except Exception:
        return root.name


def initialize_session_trace(root: str | Path, *, ir_hash: str | None = None, package_name: str | None = None) -> dict[str, Any]:
    """Create an empty append-only Ordo trace file if it does not exist.

    The trace file is mutable runtime proof material. It is initialized at compile/package
    time, then only CLI runtime commands append step blocks.
    """
    root_path = Path(root).resolve()
    path = trace_path(root_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    actual_ir_hash = ir_hash or _ir_hash_for_root(root_path)
    program = _safe_program_name(package_name or _package_name_from_ir(root_path))
    should_initialize = not path.exists()
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        has_steps = "\nstep " in existing
        recorded = ""
        for line in existing.splitlines():
            if line.strip().startswith("ir_hash:"):
                recorded = line.split(":", 1)[1].strip()
                break
        if not has_steps and recorded != actual_ir_hash:
            should_initialize = True
    if should_initialize:
        path.write_text(
            "\n".join([
                f"session {program} {{",
                f"  trace_format: {TRACE_FORMAT}",
                f"  ir_hash: {actual_ir_hash}",
                "  source_of_truth: compiled/program.ir.json",
                "  ai_direct_write: false",
                "  written_by: cli",
                "  verified_by: verify-session",
                "}",
                "",
                "# steps are appended by `ordo intake --submit` only",
                "",
            ]),
            encoding="utf-8",
        )
    return {
        "path": _rel(root_path, path),
        "format": TRACE_FORMAT,
        "ir_hash": actual_ir_hash,
        "sha256": trace_digest(root_path),
        "initialized": True,
    }


def _next_step_index(root: Path) -> int:
    parsed = parse_session_trace(root)
    steps = parsed.get("steps") if isinstance(parsed, dict) else []
    return len(steps) + 1


def append_session_trace_step(
    root: str | Path,
    *,
    run_id: str,
    node_id: str,
    action: str,
    status: str,
    answer: Any = None,
    next_node: str | None = None,
    evidence_path: str = "",
    snapshot_path: str = "",
    snapshot_hash: str = "",
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    initialize_session_trace(root_path)
    path = trace_path(root_path)
    step_index = _next_step_index(root_path)
    answer_digest = ""
    if answer not in (None, ""):
        answer_digest = "sha256:" + canonical_sha256(answer)
    fragment = "\n".join([
        f"step {step_index:03d} {{",
        f"  run_id: {run_id}",
        f"  node: {node_id}",
        f"  action: {action}",
        f"  status: {status}",
        f"  answer_digest: {answer_digest}",
        f"  next: {next_node or 'END'}",
        f"  evidence: {evidence_path}",
        f"  snapshot: {snapshot_path}",
        f"  snapshot_hash: {snapshot_hash}",
        f"  timestamp_utc: {utc_now()}",
        "  answer: " + _triple(answer),
        "}",
        "",
    ])
    with path.open("a", encoding="utf-8") as f:
        f.write(fragment)
    digest = trace_digest(root_path)
    return {
        "path": _rel(root_path, path),
        "format": TRACE_FORMAT,
        "step_index": step_index,
        "step_id": f"step {step_index:03d}",
        "digest": digest,
        "fragment": fragment.rstrip(),
    }


_STEP_RE = re.compile(r"^step\s+(\d+)\s*\{$")
_FIELD_RE = re.compile(r"^\s*([A-Za-z0-9_\-]+):\s*(.*)$")


def parse_session_trace(root: str | Path) -> dict[str, Any]:
    root_path = Path(root).resolve()
    path = trace_path(root_path)
    result: dict[str, Any] = {
        "status": "missing" if not path.exists() else "parsed",
        "path": _rel(root_path, path),
        "format": "",
        "ir_hash": "",
        "steps": [],
        "issues": [],
    }
    if not path.exists():
        return result
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("trace_format:"):
            result["format"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("ir_hash:"):
            result["ir_hash"] = stripped.split(":", 1)[1].strip()
    steps: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    in_answer = False
    answer_lines: list[str] = []
    for line in lines:
        m = _STEP_RE.match(line.strip())
        if m:
            current = {"index": int(m.group(1)), "fields": {}, "answer": ""}
            in_answer = False
            answer_lines = []
            continue
        if current is None:
            continue
        if in_answer:
            if line.strip() == '"""':
                current["answer"] = "\n".join(answer_lines)
                in_answer = False
            else:
                answer_lines.append(line)
            continue
        if line.strip() == "}":
            steps.append(current)
            current = None
            continue
        if line.strip().startswith("answer:") and line.strip().endswith('"""'):
            in_answer = True
            answer_lines = []
            continue
        field = _FIELD_RE.match(line)
        if field:
            current["fields"][field.group(1)] = field.group(2).strip()
    result["steps"] = steps
    result["sha256"] = trace_digest(root_path)
    return result


def verify_session_trace(root: str | Path, *, actual_ir_hash: str = "") -> dict[str, Any]:
    root_path = Path(root).resolve()
    parsed = parse_session_trace(root_path)
    issues: list[dict[str, Any]] = []
    if parsed.get("status") == "missing":
        issues.append({"severity": "error", "code": "ORDO-TRACE-001", "message": "session trace missing", "location": TRACE_PATH})
    if parsed.get("format") and parsed.get("format") != TRACE_FORMAT:
        issues.append({"severity": "error", "code": "ORDO-TRACE-002", "message": "unsupported session trace format", "location": TRACE_PATH})
    expected_ir = actual_ir_hash or _ir_hash_for_root(root_path)
    if expected_ir and parsed.get("ir_hash") and parsed.get("ir_hash") != expected_ir:
        issues.append({"severity": "error", "code": "ORDO-TRACE-003", "message": "trace ir_hash does not match compiled/program.ir.json", "location": TRACE_PATH})
    steps = parsed.get("steps") if isinstance(parsed.get("steps"), list) else []
    for expected_index, step in enumerate(steps, start=1):
        idx = int(step.get("index", -1))
        fields = step.get("fields") if isinstance(step.get("fields"), dict) else {}
        if idx != expected_index:
            issues.append({"severity": "error", "code": "ORDO-TRACE-004", "message": f"trace step sequence gap: expected {expected_index}, got {idx}", "location": TRACE_PATH})
        node_field = str(fields.get("node") or "")
        evidence_rel = str(fields.get("evidence") or "")
        snapshot_rel = str(fields.get("snapshot") or "")
        snapshot_hash = str(fields.get("snapshot_hash") or "")
        if evidence_rel:
            evidence_path = root_path / evidence_rel
            if not evidence_path.exists():
                issues.append({"severity": "error", "code": "ORDO-TRACE-005", "message": "trace references missing evidence report", "location": evidence_rel})
            else:
                try:
                    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
                    trace_meta = evidence.get("session_trace") if isinstance(evidence, dict) else None
                    if isinstance(trace_meta, dict):
                        if int(trace_meta.get("step_index") or -1) != idx:
                            issues.append({"severity": "error", "code": "ORDO-TRACE-006", "message": "evidence trace step index does not match trace", "location": evidence_rel})
                        if trace_meta.get("path") != TRACE_PATH:
                            issues.append({"severity": "error", "code": "ORDO-TRACE-007", "message": "evidence trace path mismatch", "location": evidence_rel})
                    if node_field and isinstance(evidence, dict) and str(evidence.get("node_id") or "") != node_field:
                        issues.append({"severity": "error", "code": "ORDO-TRACE-018", "message": "trace node does not match evidence node_id", "location": evidence_rel})
                    if isinstance(evidence, dict) and isinstance(evidence.get("evidence_digest"), dict):
                        expected_digest = canonical_sha256({k: v for k, v in evidence.items() if k != "evidence_digest"})
                        if evidence["evidence_digest"].get("value") != expected_digest:
                            issues.append({"severity": "error", "code": "ORDO-TRACE-008", "message": "evidence_digest mismatch for trace-linked evidence", "location": evidence_rel})
                except Exception as exc:
                    issues.append({"severity": "error", "code": "ORDO-TRACE-009", "message": f"trace-linked evidence cannot be parsed: {exc}", "location": evidence_rel})
        else:
            issues.append({"severity": "error", "code": "ORDO-TRACE-010", "message": "trace step missing evidence path", "location": TRACE_PATH})
        if snapshot_rel:
            snapshot_path = root_path / snapshot_rel
            if not snapshot_path.exists():
                issues.append({"severity": "error", "code": "ORDO-TRACE-011", "message": "trace references missing snapshot", "location": snapshot_rel})
            else:
                try:
                    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
                    chain = snapshot.get("session_chain") if isinstance(snapshot, dict) else None
                    if not isinstance(chain, dict):
                        issues.append({"severity": "error", "code": "ORDO-TRACE-012", "message": "trace-linked snapshot has no session_chain", "location": snapshot_rel})
                    elif snapshot_hash and chain.get("snapshot_hash") != snapshot_hash:
                        issues.append({"severity": "error", "code": "ORDO-TRACE-013", "message": "trace snapshot_hash does not match snapshot chain", "location": snapshot_rel})
                    if isinstance(chain, dict) and node_field and str(chain.get("node") or "") != node_field:
                        issues.append({"severity": "error", "code": "ORDO-TRACE-019", "message": "trace node does not match snapshot chain node", "location": snapshot_rel})
                except Exception as exc:
                    issues.append({"severity": "error", "code": "ORDO-TRACE-014", "message": f"trace-linked snapshot cannot be parsed: {exc}", "location": snapshot_rel})
        else:
            issues.append({"severity": "error", "code": "ORDO-TRACE-015", "message": "trace step missing snapshot path", "location": TRACE_PATH})
    snapshot_count = len([p for p in (root_path / "runtime" / "state_snapshots").glob("SESSION-*.json") if "000_initial" not in p.name]) if (root_path / "runtime" / "state_snapshots").exists() else 0
    if steps and snapshot_count and len(steps) != snapshot_count:
        issues.append({"severity": "error", "code": "ORDO-TRACE-016", "message": "trace step count does not match non-initial session snapshots", "location": TRACE_PATH, "trace_steps": len(steps), "submit_snapshots": snapshot_count})
    report = {
        "status": "passed" if not issues else "failed",
        "mode": "m60_2_session_trace_verification",
        "path": TRACE_PATH,
        "format": parsed.get("format") or "",
        "ir_hash": parsed.get("ir_hash") or "",
        "trace_digest": parsed.get("sha256") or "",
        "steps_checked": len(steps),
        "issues": issues,
        "terminal_line": "session-trace: intact" if not issues else "session-trace: broken",
    }
    return attach_report_digest(report)
