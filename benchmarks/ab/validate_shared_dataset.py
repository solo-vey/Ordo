from __future__ import annotations

from typing import Any
from jsonschema import Draft202012Validator

def validate_dataset(dataset: dict[str, Any], schema: dict[str, Any]) -> list[dict[str, str]]:
    issues = []
    validator = Draft202012Validator(schema)
    for error in sorted(validator.iter_errors(dataset), key=lambda e: list(e.path)):
        issues.append({
            "path": ".".join(str(x) for x in error.path),
            "message": error.message,
        })

    tasks = dataset.get("tasks") or []
    ids = [task.get("task_id") for task in tasks]
    if len(ids) != len(set(ids)):
        issues.append({"path": "tasks", "message": "task_id values must be unique"})

    if dataset.get("task_count") != len(tasks):
        issues.append({"path": "task_count", "message": "task_count must equal len(tasks)"})

    categories = {task.get("category") for task in tasks}
    if len(categories) < 10:
        issues.append({"path": "tasks", "message": "dataset must cover at least 10 categories"})

    hard = sum(1 for task in tasks if task.get("difficulty") == "hard")
    if hard < 8:
        issues.append({"path": "tasks", "message": "dataset must contain at least 8 hard tasks"})

    return issues
