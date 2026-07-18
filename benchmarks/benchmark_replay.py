from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import json

from validate_benchmark_evidence import load_schema, validate_evidence


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reproducibility_fingerprint(evidence: dict[str, Any]) -> str:
    stable = {
        "schema_version": evidence.get("schema_version"),
        "benchmark_id": evidence.get("benchmark_id"),
        "benchmark_mode": evidence.get("benchmark_mode"),
        "dataset_version": evidence.get("dataset_version"),
        "protocol_version": evidence.get("protocol_version"),
        "provider": evidence.get("provider"),
        "model": evidence.get("model"),
        "invocation": evidence.get("invocation"),
        "artifacts": {
            "prompt_sha256": evidence.get("artifacts", {}).get("prompt_sha256"),
            "input_sha256": evidence.get("artifacts", {}).get("input_sha256"),
            "raw_output_sha256": evidence.get("artifacts", {}).get("raw_output_sha256"),
            "normalized_output_sha256": evidence.get("artifacts", {}).get("normalized_output_sha256"),
        },
        "result": evidence.get("result"),
        "provenance": evidence.get("provenance"),
    }
    raw = json.dumps(stable, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def verify_run_directory(
    run_dir: str | Path,
    schema_path: str | Path,
) -> dict[str, Any]:
    run_dir = Path(run_dir)
    issues: list[dict[str, Any]] = []
    evidence_path = run_dir / "evidence.json"

    if not evidence_path.exists():
        return {
            "schema_version": "ordo.benchmark_replay_report.v1",
            "status": "failed",
            "issues": [{"code": "ORDO-REPLAY-001", "message": "evidence.json is missing"}],
        }

    try:
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "schema_version": "ordo.benchmark_replay_report.v1",
            "status": "failed",
            "issues": [{"code": "ORDO-REPLAY-002", "message": f"invalid evidence JSON: {exc}"}],
        }

    schema = load_schema(schema_path)
    for item in validate_evidence(evidence, schema):
        issues.append({
            "code": "ORDO-REPLAY-003",
            "message": item["message"],
            "location": item["path"],
        })

    artifacts = evidence.get("artifacts") or {}
    mapping = [
        ("prompt_path", "prompt_sha256"),
        ("input_path", "input_sha256"),
        ("raw_output_path", "raw_output_sha256"),
        ("normalized_output_path", "normalized_output_sha256"),
    ]
    output_root = run_dir.parent
    for path_key, hash_key in mapping:
        rel = artifacts.get(path_key)
        expected = artifacts.get(hash_key)
        if not rel or not expected:
            issues.append({
                "code": "ORDO-REPLAY-004",
                "message": f"missing artifact reference: {path_key}/{hash_key}",
            })
            continue
        target = output_root / rel
        if not target.exists():
            issues.append({
                "code": "ORDO-REPLAY-005",
                "message": f"artifact is missing: {rel}",
            })
            continue
        if _sha256(target) != expected:
            issues.append({
                "code": "ORDO-REPLAY-006",
                "message": f"artifact hash mismatch: {rel}",
            })

    return {
        "schema_version": "ordo.benchmark_replay_report.v1",
        "status": "passed" if not issues else "failed",
        "run_id": evidence.get("run_id"),
        "reproducibility_fingerprint": reproducibility_fingerprint(evidence),
        "issues": issues,
    }


def compare_replays(first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
    fields = [
        ("artifacts.prompt_sha256", first.get("artifacts", {}).get("prompt_sha256"), second.get("artifacts", {}).get("prompt_sha256")),
        ("artifacts.input_sha256", first.get("artifacts", {}).get("input_sha256"), second.get("artifacts", {}).get("input_sha256")),
        ("artifacts.normalized_output_sha256", first.get("artifacts", {}).get("normalized_output_sha256"), second.get("artifacts", {}).get("normalized_output_sha256")),
        ("result", first.get("result"), second.get("result")),
        ("dataset_version", first.get("dataset_version"), second.get("dataset_version")),
        ("protocol_version", first.get("protocol_version"), second.get("protocol_version")),
    ]
    differences = [
        {"field": name, "first": a, "second": b}
        for name, a, b in fields if a != b
    ]
    return {
        "schema_version": "ordo.benchmark_replay_comparison.v1",
        "status": "passed" if not differences else "failed",
        "differences": differences,
    }
