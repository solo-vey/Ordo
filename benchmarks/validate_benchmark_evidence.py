from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from jsonschema import Draft202012Validator, FormatChecker


def load_schema(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_evidence(
    evidence: dict[str, Any],
    schema: dict[str, Any],
) -> list[dict[str, Any]]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    issues = []
    for error in sorted(validator.iter_errors(evidence), key=lambda e: list(e.path)):
        issues.append({
            "path": ".".join(str(x) for x in error.path),
            "message": error.message,
        })

    timestamps = evidence.get("timestamps") or {}
    started = timestamps.get("started_at")
    finished = timestamps.get("finished_at")
    if started and finished and finished < started:
        issues.append({
            "path": "timestamps",
            "message": "finished_at must not precede started_at",
        })

    result = evidence.get("result") or {}
    if result.get("status") in {"passed", "failed"} and result.get("score") is None:
        issues.append({
            "path": "result.score",
            "message": "score is required for completed benchmark runs",
        })
    if result.get("status") in {"error", "blocked"} and result.get("error") is None:
        issues.append({
            "path": "result.error",
            "message": "error details are required for error/blocked runs",
        })
    return issues
