from __future__ import annotations

from pathlib import Path
from typing import Any
import json
from jsonschema import Draft202012Validator


def validate_dataset(dataset: dict[str, Any], schema: dict[str, Any]) -> list[dict[str, Any]]:
    issues = []
    validator = Draft202012Validator(schema)
    for error in sorted(validator.iter_errors(dataset), key=lambda e: list(e.path)):
        issues.append({
            "path": ".".join(str(x) for x in error.path),
            "message": error.message,
        })

    cases = dataset.get("cases") or []
    ids = [case.get("case_id") for case in cases]
    if len(ids) != len(set(ids)):
        issues.append({"path": "cases", "message": "case_id values must be unique"})

    if dataset.get("case_count") != len(cases):
        issues.append({"path": "case_count", "message": "case_count must equal len(cases)"})

    categories = [case.get("category") for case in cases]
    if len(set(categories)) < 10:
        issues.append({"path": "cases", "message": "dataset must cover at least 10 distinct adversarial categories"})

    positive = sum(1 for case in cases if case.get("expected", {}).get("semantic_match") is True)
    negative = sum(1 for case in cases if case.get("expected", {}).get("semantic_match") is False)
    if positive < 2:
        issues.append({"path": "cases", "message": "dataset must include at least two positive semantic-equivalence controls"})
    if negative < 10:
        issues.append({"path": "cases", "message": "dataset must include at least ten negative adversarial cases"})

    return issues
