from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import copy
import hashlib
import json

from .reporter import write_json


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(data: Any) -> bytes:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def canonical_sha256(data: Any) -> str:
    return hashlib.sha256(canonical_json(data)).hexdigest()


def file_sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _without_digest_fields(data: Any) -> Any:
    cleaned = copy.deepcopy(data)
    if isinstance(cleaned, dict):
        cleaned.pop("report_digest", None)
        cleaned.pop("evidence_digest", None)
        evidence = cleaned.get("evidence")
        if isinstance(evidence, dict):
            evidence.pop("report_digest", None)
            evidence.pop("evidence_digest", None)
    return cleaned


def attach_report_digest(report: dict[str, Any]) -> dict[str, Any]:
    report = dict(report)
    report["report_digest"] = {
        "algorithm": "sha256",
        "scope": "canonical_json_without_report_digest",
        "value": canonical_sha256(_without_digest_fields(report)),
    }
    return report


def write_report_with_digest(path: str | Path, report: dict[str, Any]) -> dict[str, Any]:
    report = attach_report_digest(report)
    write_json(Path(path), report)
    return report


def write_node_evidence(
    root: str | Path,
    *,
    run_id: str,
    step_index: int,
    node_id: str,
    action: str,
    status: str,
    state: dict[str, Any],
    state_diff: dict[str, Any] | None = None,
    answer: Any = None,
    next_node: str | None = None,
    checkpoint: dict[str, Any] | None = None,
    gate: dict[str, Any] | None = None,
    snapshot_path: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root_path = Path(root)
    evidence_dir = root_path / "runtime" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    safe_node = "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in node_id)
    target = evidence_dir / f"{run_id}_{step_index:03d}_{safe_node}_evidence.json"
    evidence: dict[str, Any] = {
        "status": status,
        "mode": "runtime_incremental_intake_evidence",
        "trust_layer": "m59_2_per_node_evidence_reports",
        "created_at": utc_now(),
        "run_id": run_id,
        "step_index": step_index,
        "action": action,
        "node_id": node_id,
        "answer": answer,
        "next_node": next_node or "",
        "state_diff": state_diff or {},
        "checkpoint": checkpoint or {},
        "gate": gate,
        "state": state,
        "snapshot_path": snapshot_path or "",
        "evidence_policy": {
            "ai_must_report_path_and_sha256": True,
            "direct_compiled_ir_reading_is_not_runtime_evidence": True,
        },
    }
    if snapshot_path:
        snap = root_path / snapshot_path
        if snap.exists():
            evidence["snapshot_sha256"] = {"algorithm": "sha256", "value": file_sha256(snap)}
    if extra:
        evidence.update(extra)
    evidence["evidence_digest"] = {
        "algorithm": "sha256",
        "scope": "canonical_json_without_evidence_digest",
        "value": canonical_sha256(_without_digest_fields(evidence)),
    }
    write_json(target, evidence)
    evidence["evidence_path"] = str(target.relative_to(root_path)).replace("\\", "/")
    return evidence
