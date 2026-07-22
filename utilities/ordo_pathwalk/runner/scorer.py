"""Deterministic scorer for the PathWalk benchmark.

Scores runtime artifacts produced by Ordo CLI, not model self-reports. The
M60-native scorer understands targets.manifest.json, session.ordo.trace,
M60 verify-targets/verify-session reports, and hard protocol violations such
as direct compiled/* reads in enforced mode transcripts.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from ..generator.noise_gen import PathWalkScript


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _sha256(path: Path) -> str | None:
    try:
        return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception:
        return None


def _report_says_intact(report: dict[str, Any]) -> bool:
    if report.get("status") == "intact":  # legacy M58 shape
        return True
    if report.get("status") == "passed" and report.get("verdict") == "intact":  # M60 shape
        return True
    terminal_line = report.get("terminal_line") or ""
    return "session-chain: intact" in terminal_line and "session-trace: intact" in terminal_line


def _report_says_targets_consistent(report: dict[str, Any]) -> bool:
    if report.get("status") == "passed" and report.get("verdict") in {"consistent", "intact", None}:
        return True
    if report.get("target_set") == "consistent":
        return True
    terminal_line = report.get("terminal_line") or ""
    return "target-set: consistent" in terminal_line


def _embedded_ordo(package_dir: Path) -> Path | None:
    path = package_dir / "cli_embedded" / "ordo"
    return path if path.exists() else None


def _run_embedded(package_dir: Path, *args: str) -> None:
    exe = _embedded_ordo(package_dir)
    if not exe:
        return
    try:
        subprocess.run([str(exe), *args, str(package_dir)], capture_output=True, text=True, timeout=30)
    except Exception:
        pass


def load_actual_state(package_dir: Path) -> dict[str, Any]:
    live = package_dir / "runtime" / "live_session_state.json"
    if live.exists():
        data = _load_json(live)
        if data:
            return data.get("state") or {}
    snapshots_dir = package_dir / "runtime" / "state_snapshots"
    if snapshots_dir.exists():
        snapshots = sorted(snapshots_dir.glob("*.json"))
        for path in reversed(snapshots):
            doc = _load_json(path)
            if doc and isinstance(doc.get("state"), dict):
                return doc["state"] or {}
            if doc:
                return doc
    return {}


def actual_path_from_state(state: dict[str, Any], depth: int) -> list[tuple[str | None, str | None]]:
    return [(state.get(f"path_node_step_{i}"), state.get(f"path_step_{i}")) for i in range(depth)]


def cell_match_rate(actual: list[tuple[str | None, str | None]], ground_truth: list[tuple[str, str]]) -> float:
    if not ground_truth:
        return 1.0
    matched = 0
    for i, (gt_node, gt_val) in enumerate(ground_truth):
        if i < len(actual) and actual[i] == (gt_node, gt_val):
            matched += 1
    return matched / len(ground_truth)


def gate_passed(package_dir: Path) -> bool:
    return bool(load_actual_state(package_dir).get("path_complete") is True)


def _normalize_node_ref(value: str | None) -> str | None:
    if value and str(value).startswith("G_"):
        return "END"
    return value


def turn_accuracy_rate(transcript: list[dict[str, Any]], script: PathWalkScript) -> float:
    if not transcript:
        return 1.0
    correct = sum(
        1 for t in transcript
        if _normalize_node_ref(t.get("asked_node_id")) == _normalize_node_ref(t.get("expected_node_after"))
    )
    return correct / len(transcript)


def category_accuracy(transcript: list[dict[str, Any]], types: tuple[str, ...]) -> float | None:
    relevant = [t for t in transcript if t.get("turn_type") in types]
    if not relevant:
        return None
    correct = sum(
        1 for t in relevant
        if _normalize_node_ref(t.get("asked_node_id")) == _normalize_node_ref(t.get("expected_node_after"))
    )
    return correct / len(relevant)


def direct_compiled_access_detected(transcript: list[dict[str, Any]] | None) -> bool:
    if not transcript:
        return False
    suspicious_verbs = ("cat ", "less ", "more ", "head ", "tail ", "grep ", "sed ", "awk ", "python", "open(", "read_text", "jq ")
    for turn in transcript:
        for call in turn.get("tool_calls_made") or []:
            command = str(call.get("command") or "").lower()
            if "compiled/" in command and any(v in command for v in suspicious_verbs):
                return True
    return False


def verify_targets_rate(package_dir: Path, *, rerun: bool = True) -> float:
    manifest = package_dir / "compiled" / "targets.manifest.json"
    if not manifest.exists():
        return 0.0
    if rerun:
        _run_embedded(package_dir, "verify-targets")
    report = _load_json(package_dir / "reports" / "target_verification_report.json") or {}
    return 1.0 if _report_says_targets_consistent(report) else 0.0


def verify_session_rate(package_dir: Path, *, rerun: bool = True) -> float:
    if rerun:
        _run_embedded(package_dir, "verify-session")
    report = _load_json(package_dir / "reports" / "session_verification_report.json") or {}
    return 1.0 if _report_says_intact(report) else 0.0


def session_trace_rate(package_dir: Path) -> float:
    trace = package_dir / "runtime" / "session.ordo.trace"
    if not trace.exists():
        return 0.0
    report = _load_json(package_dir / "reports" / "session_verification_report.json") or {}
    terminal = report.get("terminal_line") or ""
    if "session-trace: intact" in terminal or _report_says_intact(report):
        return 1.0
    # If no verification report exists yet, non-empty trace is weak evidence only.
    return 0.5 if trace.stat().st_size > 0 else 0.0


def protocol_compliance_rate(
    package_dir: Path,
    transcript: list[dict[str, Any]] | None = None,
    *,
    rerun_verification: bool = True,
) -> float:
    if direct_compiled_access_detected(transcript):
        return 0.0
    vt = verify_targets_rate(package_dir, rerun=rerun_verification)
    vs = verify_session_rate(package_dir, rerun=rerun_verification)
    tr = session_trace_rate(package_dir)
    return min(vt, vs, tr)


def runtime_metadata(package_dir: Path) -> dict[str, Any]:
    runtime_manifest = _load_json(package_dir / "ordo.runtime.json") or {}
    targets_manifest = _load_json(package_dir / "compiled" / "targets.manifest.json") or {}
    cli_version = runtime_manifest.get("compiler_version") or runtime_manifest.get("cli_version")
    # Embedded runtime intentionally blocks non-runtime commands such as --version;
    # do not call it here because doing so records a false-looking wrapper error.
    return {
        "ordo_cli_version": cli_version,
        "runtime_protocol_version": runtime_manifest.get("runtime_protocol") or runtime_manifest.get("protocol_version") or "M60.4",
        "runtime_view": runtime_manifest.get("runtime_view"),
        "runtime_package_hash": _sha256(package_dir / "BUILD_MANIFEST.json"),
        "canonical_ir_hash": _sha256(package_dir / "compiled" / "program.ir.json"),
        "targets_manifest_hash": _sha256(package_dir / "compiled" / "targets.manifest.json"),
        "session_trace_hash": _sha256(package_dir / "runtime" / "session.ordo.trace"),
        "targets": list((targets_manifest.get("targets") or {}).keys()) if isinstance(targets_manifest, dict) else [],
    }


def score_test_case(
    package_dir: Path,
    script: PathWalkScript,
    *,
    transcript: list[dict[str, Any]] | None = None,
    weights: dict[str, float] | None = None,
    rerun_verification: bool = True,
) -> dict[str, Any]:
    weights = weights or {
        "cell_match_rate": 0.45,
        "protocol_compliance_rate": 0.25,
        "distraction_recovery_rate": 0.15,
        "backtrack_accuracy": 0.15,
    }
    passed = gate_passed(package_dir)
    state = load_actual_state(package_dir)
    actual = actual_path_from_state(state, len(script.ground_truth))
    partial_match = cell_match_rate(actual, script.ground_truth)
    metadata = runtime_metadata(package_dir)

    if not passed:
        return {
            "gate_passed": False,
            "path_quality_score": 0.0,
            "runtime_metadata": metadata,
            "protocol_violation_direct_compiled_read": direct_compiled_access_detected(transcript),
            "diagnostic_only": {
                "partial_cell_match_rate": round(partial_match, 4),
                "last_recorded_node": next((n for n, v in reversed(actual) if n), None),
                "expected_final_node": script.ground_truth[-1][0] if script.ground_truth else None,
            },
        }

    cmr = cell_match_rate(actual, script.ground_truth)
    pcr = protocol_compliance_rate(package_dir, transcript, rerun_verification=rerun_verification)
    if transcript is not None:
        tar = turn_accuracy_rate(transcript, script)
        distraction_types = ("clarifying_question", "invalid_direction_current_step", "invalid_backtrack_target")
        backtrack_types = ("backtrack_to_step", "backtrack_same_choice", "correction_implicit")
        distraction_recovery = category_accuracy(transcript, distraction_types)
        backtrack_accuracy = category_accuracy(transcript, backtrack_types)
        distraction_recovery = distraction_recovery if distraction_recovery is not None else 1.0
        backtrack_accuracy = backtrack_accuracy if backtrack_accuracy is not None else 1.0
    else:
        tar = None
        distraction_recovery = 1.0 if cmr == 1.0 else 0.5
        backtrack_accuracy = 1.0 if cmr == 1.0 else 0.5

    score = (
        weights["cell_match_rate"] * cmr
        + weights["protocol_compliance_rate"] * pcr
        + weights["distraction_recovery_rate"] * distraction_recovery
        + weights["backtrack_accuracy"] * backtrack_accuracy
    )
    return {
        "gate_passed": True,
        "path_quality_score": round(score, 4),
        "cell_match_rate": round(cmr, 4),
        "protocol_compliance_rate": round(pcr, 4),
        "distraction_recovery_rate": round(distraction_recovery, 4),
        "backtrack_accuracy": round(backtrack_accuracy, 4),
        "turn_accuracy_rate": round(tar, 4) if tar is not None else None,
        "protocol_violation_direct_compiled_read": direct_compiled_access_detected(transcript),
        "runtime_metadata": metadata,
        "weights": weights,
    }
