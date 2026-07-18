from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import copy
import json

from .loader import load_yaml
from .runtime import load_runtime_source
from .reporter import write_json
from .runtime_evidence import write_node_evidence, attach_report_digest, canonical_sha256
from .runner import state_diff
from .checkpoints import build_checkpoint_report, enrich_state_with_checkpoint
from .session_chain import _chain_snapshots, _snapshot_state, write_session_snapshot
from .session_trace import append_session_trace_step


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path)


def _load_runtime_root(package_path: str | Path) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    root, manifest, source, _ir = load_runtime_source(package_path)
    return root, manifest, source


def _live_session_path(root: Path) -> Path:
    return root / "runtime" / "live_session_state.json"


def _load_live_session(root: Path) -> dict[str, Any]:
    path = _live_session_path(root)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _write_live_session_state(
    root: Path,
    *,
    run_id: str,
    state: dict[str, Any],
    current_node: str,
    last_closed_node: str,
    last_snapshot: str,
    last_snapshot_hash: str,
    last_evidence_report: str,
    last_evidence_digest: dict[str, Any] | None,
    last_trace_path: str = "",
    last_trace_digest: str = "",
    last_trace_step: int | None = None,
    restore: dict[str, Any] | None = None,
) -> str:
    doc = {
        "status": "active" if current_node else "complete_or_gate_ready",
        "mode": "m60_4_live_runtime_session_state_after_restore" if restore else "m59_4_live_runtime_session_state",
        "run_id": run_id,
        "current_node": current_node or "",
        "last_closed_node": last_closed_node,
        "state": state,
        "last_snapshot": last_snapshot,
        "last_snapshot_hash": last_snapshot_hash,
        "last_evidence_report": last_evidence_report,
        "last_evidence_digest": last_evidence_digest or {},
        "last_trace_path": last_trace_path,
        "last_trace_digest": last_trace_digest,
        "last_trace_step": last_trace_step,
        "updated_at": utc_now(),
        "resume_policy": "If --state is omitted, runtime helpers may resume from runtime/live_session_state.json.",
    }
    if restore:
        doc["restore"] = restore
    target = _live_session_path(root)
    write_json(target, doc)
    return _rel(root, target)


def _evidence_digest_without_self(evidence_doc: dict[str, Any]) -> dict[str, Any]:
    return {
        "algorithm": "sha256",
        "scope": "canonical_json_without_evidence_digest",
        "value": canonical_sha256({k: v for k, v in evidence_doc.items() if k != "evidence_digest"}),
    }


def restore_session(
    package_path: str | Path,
    *,
    to_seq: int,
    out: str | Path | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    """Append a restore-session event without deleting earlier proof material.

    M60.4 restore is intentionally append-only. It copies state from an existing
    session snapshot, writes a new restore snapshot, writes restore evidence,
    appends a restore step to runtime/session.ordo.trace, and updates the live
    session cache. It never truncates runtime/state_snapshots or the trace.
    """
    root, manifest, source = _load_runtime_root(package_path)
    (root / "reports").mkdir(parents=True, exist_ok=True)
    (root / "runtime" / "evidence").mkdir(parents=True, exist_ok=True)
    (root / "runtime" / "state_snapshots").mkdir(parents=True, exist_ok=True)

    snapshots = _chain_snapshots(root)
    issues: list[dict[str, Any]] = []
    status = "passed"
    target_snapshot: tuple[Path, dict[str, Any], dict[str, Any]] | None = None

    if not snapshots:
        status = "blocked"
        issues.append({"severity": "error", "code": "ORDO-RESTORE-001", "message": "cannot restore without session snapshots", "location": "runtime/state_snapshots/"})
    elif to_seq < 0 or to_seq >= len(snapshots):
        status = "blocked"
        issues.append({"severity": "error", "code": "ORDO-RESTORE-002", "message": f"restore target seq out of range: {to_seq}", "location": "--to-seq", "available_seq_min": 0, "available_seq_max": len(snapshots) - 1})
    else:
        target_snapshot = snapshots[to_seq]

    live = _load_live_session(root)
    run_id = str(live.get("run_id") or f"LIVE-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}")
    current_state = _snapshot_state(snapshots[-1][1]) if snapshots else {}
    target_state = copy.deepcopy(_snapshot_state(target_snapshot[1])) if target_snapshot else current_state
    restore_node_id = f"RESTORE_TO_SEQ_{to_seq:03d}"
    restore_info = {
        "to_seq": to_seq,
        "reason": reason or "",
        "target_snapshot": _rel(root, target_snapshot[0]) if target_snapshot else "",
        "target_snapshot_hash": str((target_snapshot[2] if target_snapshot else {}).get("snapshot_hash") or ""),
        "target_node": str((target_snapshot[2] if target_snapshot else {}).get("node") or ""),
        "append_only": True,
        "history_truncated": False,
    }
    checkpoint_after = build_checkpoint_report(source, target_state) if status == "passed" else {}
    if status == "passed":
        target_state = enrich_state_with_checkpoint(target_state, checkpoint_after)
        if not target_state.get("current_node"):
            target_state["current_node"] = checkpoint_after.get("earliest_incomplete_node") or checkpoint_after.get("current_node") or ""
    diff = state_diff(current_state, target_state) if status == "passed" else {}

    snapshot_path, chained_state, chain_meta = write_session_snapshot(
        root,
        target_state,
        node_id=restore_node_id,
        action="restore_session",
        answer={"to_seq": to_seq, "reason": reason or ""},
        status=status,
        extra={"run_id": run_id, "restore": restore_info, "protocol": "m60_4_append_only_restore_session"},
    )
    target_state = chained_state

    evidence = write_node_evidence(
        root,
        run_id=run_id,
        step_index=1,
        node_id=restore_node_id,
        action="restore_session",
        status=status,
        state=target_state,
        state_diff=diff,
        answer={"to_seq": to_seq, "reason": reason or ""},
        next_node=str(target_state.get("current_node") or ""),
        checkpoint=checkpoint_after,
        snapshot_path=_rel(root, snapshot_path),
        extra={"issues": issues, "restore": restore_info},
    )
    trace = append_session_trace_step(
        root,
        run_id=run_id,
        node_id=restore_node_id,
        action="restore_session",
        status=status,
        answer={"to_seq": to_seq, "reason": reason or ""},
        next_node=str(target_state.get("current_node") or ""),
        evidence_path=str(evidence.get("evidence_path") or ""),
        snapshot_path=_rel(root, snapshot_path),
        snapshot_hash=str(chain_meta.get("snapshot_hash") or ""),
    )
    if evidence.get("evidence_path"):
        evidence_file = root / str(evidence.get("evidence_path"))
        if evidence_file.exists():
            evidence_doc = json.loads(evidence_file.read_text(encoding="utf-8"))
            evidence_doc["session_trace"] = {
                "path": trace.get("path"),
                "format": trace.get("format"),
                "step_index": trace.get("step_index"),
                "step_id": trace.get("step_id"),
                "trace_digest": trace.get("digest"),
                "trace_fragment": trace.get("fragment"),
            }
            evidence_doc["evidence_digest"] = _evidence_digest_without_self(evidence_doc)
            write_json(evidence_file, evidence_doc)
            evidence_doc["evidence_path"] = str(evidence.get("evidence_path"))
            evidence = evidence_doc

    live_session_file = ""
    if status == "passed":
        live_session_file = _write_live_session_state(
            root,
            run_id=run_id,
            state=target_state,
            current_node=str(target_state.get("current_node") or ""),
            last_closed_node=str(target_state.get("last_closed_node") or ""),
            last_snapshot=_rel(root, snapshot_path),
            last_snapshot_hash=str(chain_meta.get("snapshot_hash") or ""),
            last_evidence_report=str(evidence.get("evidence_path") or ""),
            last_evidence_digest=evidence.get("evidence_digest") if isinstance(evidence.get("evidence_digest"), dict) else {},
            last_trace_path=str(trace.get("path") or ""),
            last_trace_digest=str(trace.get("digest") or ""),
            last_trace_step=int(trace.get("step_index") or 0),
            restore=restore_info,
        )

    report = {
        "status": status,
        "mode": "m60_4_append_only_restore_session",
        "run_id": run_id,
        "restore": restore_info,
        "target_state": target_state if status == "passed" else {},
        "state_diff": diff,
        "next_node": str(target_state.get("current_node") or "") if isinstance(target_state, dict) else "",
        "snapshot": _rel(root, snapshot_path),
        "session_chain": chain_meta,
        "evidence_report": evidence.get("evidence_path"),
        "evidence_digest": evidence.get("evidence_digest"),
        "session_trace": {
            "path": trace.get("path"),
            "format": trace.get("format"),
            "step_index": trace.get("step_index"),
            "step_id": trace.get("step_id"),
            "trace_digest": trace.get("digest"),
            "trace_fragment": trace.get("fragment"),
        },
        "live_session_state": live_session_file,
        "issues": issues,
        "restore_policy": "append_only: previous snapshots and trace steps are not deleted; verify-session must validate the restore event.",
    }
    report = attach_report_digest(report)
    target = Path(out).resolve() if out else root / "reports" / "restore_session_report.json"
    write_json(target, report)
    return report
