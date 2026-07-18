from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from benchmark_replay import verify_run_directory


def evaluate_closure_gate(
    run_dirs: list[str | Path],
    schema_path: str | Path,
    *,
    minimum_runs: int = 1,
    require_distinct_models: int = 1,
) -> dict[str, Any]:
    reports = [verify_run_directory(path, schema_path) for path in run_dirs]
    issues: list[dict[str, Any]] = []

    if len(reports) < minimum_runs:
        issues.append({
            "code": "ORDO-CLOSURE-001",
            "message": f"requires at least {minimum_runs} runs",
        })

    for report in reports:
        if report.get("status") != "passed":
            issues.append({
                "code": "ORDO-CLOSURE-002",
                "message": f"replay verification failed for {report.get('run_id')}",
            })

    models = set()
    for path in run_dirs:
        evidence_path = Path(path) / "evidence.json"
        if evidence_path.exists():
            try:
                evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
                models.add(evidence.get("model", {}).get("resolved_id"))
            except Exception:
                pass

    models.discard(None)
    if len(models) < require_distinct_models:
        issues.append({
            "code": "ORDO-CLOSURE-003",
            "message": f"requires at least {require_distinct_models} distinct resolved models",
        })

    return {
        "schema_version": "ordo.benchmark_closure_gate.v1",
        "status": "passed" if not issues else "failed",
        "verified_runs": len(reports),
        "distinct_models": len(models),
        "issues": issues,
        "replay_reports": reports,
    }
