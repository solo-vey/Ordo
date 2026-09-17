from __future__ import annotations

"""Safe, dependency-aware correction planning for Ordo packages.

Corrections are deliberately plan-first: the supplied state file is never
changed.  A caller can explicitly materialize the returned corrected state in
a new file after reviewing the invalidation and gate-replay evidence.
"""

from copy import deepcopy
from typing import Any

from .runner import evaluate_gates


CORRECTION_MODES = frozenset({"strict", "advisory"})


def _issue(issues: list[dict[str, Any]], code: str, message: str, location: str, severity: str = "error") -> None:
    issues.append({"severity": severity, "code": code, "message": message, "location": location})


def _ids(source: dict[str, Any], key: str) -> set[str]:
    return {str(item["id"]) for item in source.get(key, []) or [] if isinstance(item, dict) and isinstance(item.get("id"), str)}


def _rules(contract: dict[str, Any], issues: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    raw = contract.get("rules") or []
    if not isinstance(raw, list):
        _issue(issues, "CORRECTION_RULES_INVALID", "correction_contract.rules must be a list.", "correction_contract.rules")
        return {}
    result: dict[str, dict[str, Any]] = {}
    for index, value in enumerate(raw):
        location = f"correction_contract.rules[{index}]"
        if not isinstance(value, dict) or not isinstance(value.get("source"), str) or not value["source"]:
            _issue(issues, "CORRECTION_SOURCE_REQUIRED", "Each correction rule requires a source state path.", f"{location}.source")
            continue
        source = value["source"]
        if source in result:
            _issue(issues, "CORRECTION_SOURCE_DUPLICATE", "A source state path may have only one correction rule.", f"{location}.source")
            continue
        result[source] = {**value, "location": location}
    return result


def validate_correction_contract(source: dict[str, Any], tests: dict[str, Any] | None = None) -> dict[str, Any]:
    contract = source.get("correction_contract")
    if contract is None:
        return {"status": "not_enabled", "mode": "not_enabled", "summary": {"errors": 0, "warnings": 0, "rules": 0}, "issues": [], "rules": []}
    issues: list[dict[str, Any]] = []
    if not isinstance(contract, dict):
        _issue(issues, "CORRECTION_CONTRACT_INVALID", "correction_contract must be an object.", "correction_contract")
        return {"status": "failed", "mode": "invalid", "summary": {"errors": 1, "warnings": 0, "rules": 0}, "issues": issues, "rules": []}
    mode = contract.get("mode", "strict")
    if mode not in CORRECTION_MODES:
        _issue(issues, "CORRECTION_MODE_INVALID", "correction_contract.mode must be strict or advisory.", "correction_contract.mode")
        mode = "strict"
    if contract.get("version") != "1.0":
        _issue(issues, "CORRECTION_VERSION_REQUIRED", "correction_contract.version must be '1.0'.", "correction_contract.version")
    schema = ((source.get("state") or {}).get("schema") or {})
    schema_paths = set(schema) if isinstance(schema, dict) else set()
    gates, nodes = _ids(source, "gates"), _ids(source, "nodes")
    test_ids = {str(item["id"]) for item in (tests or {}).get("test_cases", []) or [] if isinstance(item, dict) and isinstance(item.get("id"), str)}
    artifact_ids = _ids(source, "artifacts") | _ids(source, "outputs")
    rules = _rules(contract, issues)
    reports: list[dict[str, Any]] = []
    for path, rule in sorted(rules.items()):
        location = rule["location"]
        invalidates = rule.get("invalidate") or {}
        replay = rule.get("replay") or {}
        report = {"source": path, "status": "ok", "invalidate": invalidates, "replay": replay}
        if path not in schema_paths:
            report["status"] = "error"; _issue(issues, "CORRECTION_SOURCE_UNKNOWN", "Correction source must exist in state.schema.", f"{location}.source")
        if not isinstance(invalidates, dict):
            report["status"] = "error"; _issue(issues, "CORRECTION_INVALIDATE_INVALID", "invalidate must be an object.", f"{location}.invalidate"); invalidates = {}
        if not isinstance(replay, dict):
            report["status"] = "error"; _issue(issues, "CORRECTION_REPLAY_INVALID", "replay must be an object.", f"{location}.replay"); replay = {}
        state_paths = invalidates.get("state", []) or []
        if not isinstance(state_paths, list) or not state_paths:
            report["status"] = "error"; _issue(issues, "CORRECTION_INVALIDATED_STATE_REQUIRED", "Each correction rule must explicitly invalidate at least one downstream state path.", f"{location}.invalidate.state"); state_paths = []
        for target in state_paths:
            if not isinstance(target, str) or target not in schema_paths or target == path:
                report["status"] = "error"; _issue(issues, "CORRECTION_INVALIDATED_STATE_UNKNOWN", "Invalidated state must be a distinct path from state.schema.", f"{location}.invalidate.state")
        for key, known, code in (("gates", gates, "CORRECTION_GATE_UNKNOWN"), ("tests", test_ids, "CORRECTION_TEST_UNKNOWN"), ("artifacts", artifact_ids, "CORRECTION_ARTIFACT_UNKNOWN"), ("derivations", nodes, "CORRECTION_DERIVATION_UNKNOWN")):
            values = invalidates.get(key, []) or []
            if not isinstance(values, list):
                report["status"] = "error"; _issue(issues, f"{code}_LIST", f"invalidate.{key} must be a list.", f"{location}.invalidate.{key}"); continue
            for target in values:
                if not isinstance(target, str) or target not in known:
                    report["status"] = "error"; _issue(issues, code, f"invalidate.{key} references an unknown id.", f"{location}.invalidate.{key}")
        replay_gates = replay.get("gates", []) or []
        if not isinstance(replay_gates, list) or not replay_gates:
            report["status"] = "error"; _issue(issues, "CORRECTION_REPLAY_GATE_REQUIRED", "Each correction rule must explicitly replay its affected source gates.", f"{location}.replay.gates")
        for gate_id in replay_gates if isinstance(replay_gates, list) else []:
            if gate_id not in gates:
                report["status"] = "error"; _issue(issues, "CORRECTION_REPLAY_GATE_UNKNOWN", "replay.gates references an unknown gate.", f"{location}.replay.gates")
        reports.append(report)
    errors = [item for item in issues if item["severity"] == "error"]
    warnings = [item for item in issues if item["severity"] == "warning"]
    return {"status": "passed" if not errors else "failed", "mode": mode, "summary": {"errors": len(errors), "warnings": len(warnings), "rules": len(rules)}, "issues": issues, "rules": reports}


def plan_correction(source: dict[str, Any], state: dict[str, Any], *, path: str, value: Any, tests: dict[str, Any] | None = None) -> dict[str, Any]:
    """Produce a corrected copy and bounded invalidation/replay evidence."""
    validation = validate_correction_contract(source, tests)
    contract = source.get("correction_contract") if isinstance(source.get("correction_contract"), dict) else {}
    rules = _rules(contract, [])
    rule = rules.get(path)
    if validation["status"] != "passed" or rule is None:
        return {"status": "blocked", "source_path": path, "validation": validation, "issues": validation.get("issues", []) + ([] if rule else [{"severity": "error", "code": "CORRECTION_SOURCE_UNDECLARED", "message": "No correction rule permits this source path.", "location": "correction_contract.rules"}])}
    corrected = deepcopy(state)
    before = deepcopy(state)
    corrected[path] = value
    invalidates = rule.get("invalidate") or {}
    invalidated_state: list[dict[str, Any]] = []
    for dependent in invalidates.get("state", []) or []:
        previous = corrected.get(dependent)
        corrected[dependent] = None
        invalidated_state.append({"path": dependent, "before": previous, "after": None, "reason": f"depends_on:{path}"})
    replay_ids = set((rule.get("replay") or {}).get("gates", []) or [])
    replayed_gates = [item for item in evaluate_gates(source, corrected) if item.get("id") in replay_ids]
    return {
        "status": "planned",
        "source_path": path,
        "source_change": {"before": before.get(path), "after": value},
        "corrected_state": corrected,
        "preserved_state_paths": sorted(key for key in before if key not in {path, *(item["path"] for item in invalidated_state)} and before.get(key) == corrected.get(key)),
        "invalidation": {"state": invalidated_state, "derivations": invalidates.get("derivations", []), "gates": invalidates.get("gates", []), "tests": invalidates.get("tests", []), "artifacts": invalidates.get("artifacts", [])},
        "gate_replay": replayed_gates,
        "validation": validation,
        "non_mutation": {"input_state_unchanged": state == before},
    }
