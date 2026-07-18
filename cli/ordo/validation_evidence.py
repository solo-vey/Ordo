from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from .build_identity import bind_report, validate_report_binding


def write_bound_validation_report(
    report: dict[str, Any],
    identity: dict[str, Any],
    path: str | Path,
) -> dict[str, Any]:
    payload = bind_report(dict(report), identity)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def read_and_validate_bound_report(
    path: str | Path,
    identity: dict[str, Any],
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    target = Path(path)
    if not target.exists():
        return None, [{
            "severity": "error",
            "code": "ORDO-BUILD-003",
            "message": "required validation report is missing",
            "location": str(target),
        }]
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, [{
            "severity": "error",
            "code": "ORDO-BUILD-004",
            "message": f"validation report is invalid JSON: {exc}",
            "location": str(target),
        }]
    issues = validate_report_binding(payload, identity)
    for item in issues:
        item.setdefault("location", str(target))
    return payload, issues
