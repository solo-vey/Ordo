from __future__ import annotations

from pathlib import Path
from typing import Any
import copy
import json

from .reporter import write_json
from .runtime import resolve_runtime_paths
from .runtime_evidence import attach_report_digest, canonical_sha256, file_sha256, utc_now

ZERO_PREV_HASH = "sha256:" + ("0" * 64)
PROTOCOL_LINE = "[protocol] raw compiled/* read is a violation; this output is the only valid source"


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path)


def _safe_id(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in value) or "snapshot"


def _copy_without_snapshot_hash(data: Any) -> Any:
    cleaned = copy.deepcopy(data)
    if isinstance(cleaned, dict):
        chain = cleaned.get("session_chain")
        if isinstance(chain, dict):
            chain.pop("snapshot_hash", None)
    return cleaned


def _snapshot_hash(data: dict[str, Any]) -> str:
    return "sha256:" + canonical_sha256(_copy_without_snapshot_hash(data))


def _snapshot_state(data: dict[str, Any]) -> dict[str, Any]:
    """Return the runtime state from either M59.4 envelope snapshots or
    older M59.3 flat snapshots.
    """
    if isinstance(data, dict):
        embedded = data.get("state")
        if isinstance(embedded, dict):
            return embedded
        flat = dict(data)
        flat.pop("session_chain", None)
        return flat
    return {}


def _runtime_root_and_ir(package_path: str | Path) -> tuple[Path, Path | None]:
    resolved = resolve_runtime_paths(package_path)
    if resolved.get("status") == "resolved":
        return resolved["root"], resolved.get("compiled_path")
    root = Path(resolved.get("root") or package_path).resolve()
    return root, None


def _actual_ir_hash(root: Path, compiled_path: Path | None = None) -> str:
    compiled = compiled_path or root / "compiled" / "program.ir.json"
    if not compiled.exists():
        return ""
    return "sha256:" + file_sha256(compiled)


def _chain_snapshots(root: Path) -> list[tuple[Path, dict[str, Any], dict[str, Any]]]:
    snapshots_dir = root / "runtime" / "state_snapshots"
    result: list[tuple[Path, dict[str, Any], dict[str, Any]]] = []
    if not snapshots_dir.exists():
        return result
    for path in snapshots_dir.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        chain = data.get("session_chain") if isinstance(data, dict) else None
        if isinstance(chain, dict) and isinstance(chain.get("seq"), int):
            result.append((path, data, chain))
    return sorted(result, key=lambda item: (int(item[2].get("seq", -1)), item[0].name))


def has_chain_snapshots(package_path: str | Path) -> bool:
    root, _compiled = _runtime_root_and_ir(package_path)
    return bool(_chain_snapshots(root))


def write_session_snapshot(
    package_path: str | Path,
    state: dict[str, Any],
    *,
    node_id: str,
    action: str,
    answer: Any = None,
    status: str = "passed",
    extra: dict[str, Any] | None = None,
) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    root, compiled_path = _runtime_root_and_ir(package_path)
    snapshots = _chain_snapshots(root)
    seq = len(snapshots)
    prev_hash = ZERO_PREV_HASH if not snapshots else str(snapshots[-1][2].get("snapshot_hash") or "")
    ir_hash = _actual_ir_hash(root, compiled_path)
    answer_digest = ""
    if answer not in (None, ""):
        answer_digest = "sha256:" + canonical_sha256(answer)

    chain_meta: dict[str, Any] = {
        "seq": seq,
        "node": node_id,
        "action": action,
        "status": status,
        "answer_digest": answer_digest,
        "prev_snapshot_hash": prev_hash,
        "ir_hash": ir_hash,
        "cli_version": _read_cli_version(root),
        "timestamp_utc": utc_now(),
        "protocol": "m59_4_tamper_evident_session_chain_envelope",
    }
    if extra:
        chain_meta.update(extra)
    snapshot = {
        "session_chain": chain_meta,
        "state": copy.deepcopy(state),
    }
    snapshot["session_chain"]["snapshot_hash"] = _snapshot_hash(snapshot)

    snapshots_dir = root / "runtime" / "state_snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    path = snapshots_dir / f"SESSION-{seq:03d}_{_safe_id(node_id)}.json"
    write_json(path, snapshot)
    return path, copy.deepcopy(state), snapshot["session_chain"]


def _read_cli_version(root: Path) -> str:
    try:
        from . import __version__
        return str(__version__)
    except Exception:
        manifest = root / "ordo.runtime.json"
        if manifest.exists():
            try:
                return str(json.loads(manifest.read_text(encoding="utf-8")).get("compiler_version") or "unknown")
            except Exception:
                return "unknown"
        return "unknown"


def extract_canary(ir: dict[str, Any]) -> str:
    security = ir.get("security") if isinstance(ir, dict) else None
    if isinstance(security, dict) and security.get("canary_secret"):
        return str(security.get("canary_secret"))
    for op in (ir.get("ops", []) if isinstance(ir, dict) else []):
        if isinstance(op, dict) and op.get("canary") and op.get("question"):
            return str(op.get("question"))
    return ""


def _scan_canary_leaks(root: Path, canary: str) -> list[str]:
    if not canary:
        return []
    roots = [root / "generated_outputs", root / "runtime", root / "reports"]
    leaks: list[str] = []
    for scan_root in roots:
        if not scan_root.exists():
            continue
        for path in scan_root.rglob("*"):
            if not path.is_file():
                continue
            rel = _rel(root, path)
            if rel in {"reports/session_verification_report.json"}:
                continue
            if "compiled/" in rel or rel == "compiled/program.ir.json":
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if canary in text:
                leaks.append(rel)
    return sorted(set(leaks))


def verify_session(package_path: str | Path, *, out: str | Path | None = None) -> dict[str, Any]:
    root, compiled_path = _runtime_root_and_ir(package_path)
    issues: list[dict[str, Any]] = []
    actual_ir_hash = _actual_ir_hash(root, compiled_path)
    ir: dict[str, Any] = {}
    if compiled_path and compiled_path.exists():
        try:
            ir = json.loads(compiled_path.read_text(encoding="utf-8"))
        except Exception as exc:
            issues.append({"severity": "error", "code": "ORDO-CHAIN-006", "message": f"compiled IR cannot be parsed: {exc}", "location": _rel(root, compiled_path)})
    else:
        issues.append({"severity": "error", "code": "ORDO-CHAIN-005", "message": "compiled IR missing; session cannot be verified", "location": "compiled/program.ir.json"})

    snapshots = _chain_snapshots(root)
    if not snapshots:
        issues.append({"severity": "error", "code": "ORDO-CHAIN-001", "message": "no M59.3 session-chain snapshots found", "location": "runtime/state_snapshots/"})

    expected_prev = ZERO_PREV_HASH
    broken_seq: int | None = None
    seen_nodes: set[str] = set()
    last_state: dict[str, Any] = {}
    for expected_seq, (path, data, chain) in enumerate(snapshots):
        seq = int(chain.get("seq", -1))
        if seq != expected_seq:
            issues.append({"severity": "error", "code": "ORDO-CHAIN-002", "message": f"snapshot sequence gap or reorder: expected {expected_seq}, got {seq}", "location": _rel(root, path)})
            broken_seq = expected_seq if broken_seq is None else broken_seq
        if chain.get("prev_snapshot_hash") != expected_prev:
            issues.append({"severity": "error", "code": "ORDO-CHAIN-003", "message": "prev_snapshot_hash does not match previous snapshot", "location": _rel(root, path), "seq": seq})
            broken_seq = seq if broken_seq is None else broken_seq
        expected_hash = _snapshot_hash(data)
        if chain.get("snapshot_hash") != expected_hash:
            issues.append({"severity": "error", "code": "ORDO-CHAIN-004", "message": "snapshot_hash mismatch; snapshot content was modified", "location": _rel(root, path), "seq": seq})
            broken_seq = seq if broken_seq is not None else seq
        if actual_ir_hash and chain.get("ir_hash") != actual_ir_hash:
            issues.append({"severity": "error", "code": "ORDO-CHAIN-007", "message": "snapshot ir_hash does not match current compiled/program.ir.json", "location": _rel(root, path), "seq": seq})
            broken_seq = seq if broken_seq is not None else seq
        expected_prev = str(chain.get("snapshot_hash") or "")
        if chain.get("node"):
            seen_nodes.add(str(chain.get("node")))
        last_state = _snapshot_state(data)

    gates = last_state.get("gates") if isinstance(last_state, dict) else None
    if isinstance(gates, dict):
        for gate_id, gate_data in gates.items():
            passed = gate_data == "passed" or (isinstance(gate_data, dict) and gate_data.get("status") == "passed")
            if passed and str(gate_id) not in seen_nodes:
                issues.append({"severity": "error", "code": "ORDO-CHAIN-008", "message": "passed gate has no corresponding chain snapshot", "location": str(gate_id)})

    target_report = {}
    try:
        from .targets import verify_targets
        target_report = verify_targets(root)
        if target_report.get("status") != "passed":
            issues.extend(target_report.get("issues", []) or [])
    except Exception as exc:
        target_report = {"status": "failed", "issues": [{"severity": "error", "code": "ORDO-TARGET-011", "message": f"target verification could not run: {exc}"}]}
        issues.extend(target_report.get("issues", []) or [])

    trace_report = {}
    try:
        from .session_trace import verify_session_trace
        trace_report = verify_session_trace(root, actual_ir_hash=actual_ir_hash)
        if trace_report.get("status") != "passed":
            issues.extend(trace_report.get("issues", []) or [])
    except Exception as exc:
        trace_report = {"status": "failed", "terminal_line": "session-trace: broken", "issues": [{"severity": "error", "code": "ORDO-TRACE-017", "message": f"session trace verification could not run: {exc}"}]}
        issues.extend(trace_report.get("issues", []) or [])

    canary = extract_canary(ir)
    canary_leaks = _scan_canary_leaks(root, canary)
    if canary_leaks:
        issues.append({"severity": "error", "code": "ORDO-CANARY-001", "message": "compiled IR canary leaked into runtime-visible files; raw IR was likely read", "location": ", ".join(canary_leaks[:5])})

    if canary_leaks:
        verdict = "CANARY LEAK — raw IR was read"
        terminal_line = "session-chain: CANARY LEAK — raw IR was read"
        status = "failed"
    elif issues:
        seq_label = broken_seq if broken_seq is not None else "unknown"
        verdict = f"broken at seq {seq_label}"
        terminal_line = f"session-chain: broken at seq {seq_label}"
        status = "failed"
    else:
        verdict = "intact"
        terminal_line = "session-chain: intact"
        status = "passed"

    report = {
        "status": status,
        "mode": "m60_2_session_verification_with_targets_and_trace",
        "verdict": verdict,
        "terminal_line": terminal_line,
        "package_root": str(root),
        "compiled_ir_hash": actual_ir_hash,
        "target_set_status": target_report.get("status", "unknown") if isinstance(target_report, dict) else "unknown",
        "target_terminal_line": target_report.get("terminal_line", "") if isinstance(target_report, dict) else "",
        "targets_checked": sorted(((target_report.get("target_results") or {}) if isinstance(target_report, dict) else {}).keys()),
        "session_trace_status": trace_report.get("status", "unknown") if isinstance(trace_report, dict) else "unknown",
        "session_trace_terminal_line": trace_report.get("terminal_line", "") if isinstance(trace_report, dict) else "",
        "session_trace_digest": trace_report.get("trace_digest", "") if isinstance(trace_report, dict) else "",
        "session_trace_steps_checked": trace_report.get("steps_checked", 0) if isinstance(trace_report, dict) else 0,
        "snapshots_checked": len(snapshots),
        "chain_start": _rel(root, snapshots[0][0]) if snapshots else "",
        "chain_end": _rel(root, snapshots[-1][0]) if snapshots else "",
        "canary_present": bool(canary),
        "canary_leaks": canary_leaks,
        "issues": issues,
        "human_verify_policy": "Gate approval requires the user to run cli_embedded/ordo verify-session <package> and paste the terminal_line verbatim.",
    }
    report = attach_report_digest(report)
    target = Path(out).resolve() if out else root / "reports" / "session_verification_report.json"
    write_json(target, report)
    return report
