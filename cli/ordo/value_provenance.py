from __future__ import annotations

"""Value-level provenance and explicit analyst-confirmation controls."""

from typing import Any


MODES = frozenset({"strict", "advisory"})
PROVENANCE_KINDS = frozenset({"analyst", "model_derived", "automatic", "default", "reference"})


def _issue(issues: list[dict[str, Any]], code: str, message: str, location: str) -> None:
    issues.append({"severity": "error", "code": code, "message": message, "location": location})


def _nodes(source: dict[str, Any]) -> set[str]:
    return {str(item["id"]) for item in source.get("nodes", []) or [] if isinstance(item, dict) and isinstance(item.get("id"), str)}


def _writes(node: dict[str, Any]) -> set[str]:
    on_answer = node.get("on_answer") or {}
    if not isinstance(on_answer, dict):
        return set()
    result: set[str] = set()
    values = [on_answer, *[value for value in on_answer.values() if isinstance(value, dict)]]
    for value in values:
        update = value.get("update_state") if isinstance(value, dict) else None
        if isinstance(update, dict):
            result.update(str(path) for path in update)
    return result


def _specs(contract: dict[str, Any], issues: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    raw = contract.get("fields") or []
    if not isinstance(raw, list):
        _issue(issues, "VALUE_PROVENANCE_FIELDS_INVALID", "value_provenance_contract.fields must be a list.", "value_provenance_contract.fields")
        return {}
    result: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(raw):
        location = f"value_provenance_contract.fields[{index}]"
        path = item.get("state_path") if isinstance(item, dict) else None
        if not isinstance(path, str) or not path:
            _issue(issues, "VALUE_PROVENANCE_PATH_REQUIRED", "Each provenance field requires state_path.", f"{location}.state_path")
            continue
        if path in result:
            _issue(issues, "VALUE_PROVENANCE_PATH_DUPLICATE", "Each state_path may have one provenance declaration.", f"{location}.state_path")
            continue
        result[path] = {**item, "location": location}
    return result


def validate_value_provenance_contract(source: dict[str, Any]) -> dict[str, Any]:
    contract = source.get("value_provenance_contract")
    if contract is None:
        return {"status": "not_enabled", "mode": "not_enabled", "summary": {"errors": 0, "fields": 0}, "issues": [], "fields": []}
    issues: list[dict[str, Any]] = []
    if not isinstance(contract, dict):
        _issue(issues, "VALUE_PROVENANCE_CONTRACT_INVALID", "value_provenance_contract must be an object.", "value_provenance_contract")
        return {"status": "failed", "mode": "invalid", "summary": {"errors": 1, "fields": 0}, "issues": issues, "fields": []}
    mode = contract.get("mode", "strict")
    if mode not in MODES:
        _issue(issues, "VALUE_PROVENANCE_MODE_INVALID", "mode must be strict or advisory.", "value_provenance_contract.mode")
        mode = "strict"
    if contract.get("version") != "1.0":
        _issue(issues, "VALUE_PROVENANCE_VERSION_REQUIRED", "version must be '1.0'.", "value_provenance_contract.version")
    schema = ((source.get("state") or {}).get("schema") or {})
    schema_paths = set(schema) if isinstance(schema, dict) else set()
    nodes = _nodes(source)
    specs = _specs(contract, issues)
    reports: list[dict[str, Any]] = []
    for path, spec in sorted(specs.items()):
        location = spec["location"]
        report = {"state_path": path, "status": "ok"}
        if path not in schema_paths:
            report["status"] = "error"; _issue(issues, "VALUE_PROVENANCE_PATH_UNKNOWN", "state_path must exist in state.schema.", f"{location}.state_path")
        allowed = spec.get("allowed_provenance") or []
        if not isinstance(allowed, list) or not allowed or any(item not in PROVENANCE_KINDS for item in allowed):
            report["status"] = "error"; _issue(issues, "VALUE_PROVENANCE_ALLOWED_INVALID", f"allowed_provenance must be a non-empty subset of {sorted(PROVENANCE_KINDS)}.", f"{location}.allowed_provenance")
        if spec.get("reference_policy") != "draft_only":
            report["status"] = "error"; _issue(issues, "VALUE_PROVENANCE_REFERENCE_ISOLATION_REQUIRED", "reference_policy must be draft_only; reference data can never become a silent default.", f"{location}.reference_policy")
        if spec.get("default_policy") != "explicit_only":
            report["status"] = "error"; _issue(issues, "VALUE_PROVENANCE_DEFAULT_POLICY_REQUIRED", "default_policy must be explicit_only.", f"{location}.default_policy")
        confirmation = spec.get("confirmation_node")
        if not isinstance(confirmation, str) or confirmation not in nodes:
            report["status"] = "error"; _issue(issues, "VALUE_PROVENANCE_CONFIRMATION_NODE_REQUIRED", "Each value provenance field requires an existing analyst confirmation node.", f"{location}.confirmation_node")
        reports.append(report)
    if mode == "strict":
        for node in source.get("nodes", []) or []:
            if not isinstance(node, dict):
                continue
            for path in _writes(node):
                if path in schema_paths and path not in specs:
                    _issue(issues, "VALUE_PROVENANCE_WRITE_UNDECLARED", "State writes require an explicit value provenance declaration in strict mode.", f"nodes[{node.get('id')}].on_answer.update_state.{path}")
    errors = [item for item in issues if item["severity"] == "error"]
    return {"status": "passed" if not errors else "failed", "mode": mode, "summary": {"errors": len(errors), "fields": len(specs)}, "issues": issues, "fields": reports}


def evaluate_value_provenance(source: dict[str, Any], node: dict[str, Any], answer: Any) -> dict[str, Any]:
    """Fail closed before a non-confirmed value can mutate business state."""
    contract = source.get("value_provenance_contract")
    if not isinstance(contract, dict) or not contract:
        return {"status": "passed", "answer": answer, "records": {}, "issues": []}
    specs = _specs(contract, [])
    paths = sorted(_writes(node) & set(specs))
    if not paths:
        return {"status": "passed", "answer": answer, "records": {}, "issues": []}
    if not isinstance(answer, dict) or "value" not in answer or "provenance" not in answer:
        return {
            "status": "provenance_required",
            "answer": answer,
            "records": {},
            "issues": [{
                "severity": "error",
                "code": "ORDO-PROVENANCE-REQUIRED",
                "message": "A state-changing answer must explicitly include value and provenance.",
                "location": node.get("id", "node"),
            }],
        }
    provenance = answer.get("provenance")
    value = answer.get("value")
    allowed = set().union(*(set(specs[path].get("allowed_provenance") or []) for path in paths))
    if provenance not in PROVENANCE_KINDS or provenance not in allowed:
        return {
            "status": "provenance_rejected",
            "answer": value,
            "records": {},
            "issues": [{
                "severity": "error",
                "code": "ORDO-PROVENANCE-REJECTED",
                "message": "The supplied provenance is not allowed for this state value.",
                "location": node.get("id", "node"),
                "provenance": provenance,
            }],
        }
    confirmed = answer.get("analyst_confirmed") is True and provenance == "analyst"
    records = {
        path: {
            "value": value,
            "provenance": provenance,
            "lifecycle": "confirmed" if confirmed else "draft",
            "analyst_confirmed": confirmed,
        }
        for path in paths
    }
    if not confirmed:
        next_node = specs[paths[0]].get("confirmation_node")
        code = "ORDO-PROVENANCE-REFERENCE-ISOLATED" if provenance == "reference" else "ORDO-PROVENANCE-DRAFT-CONFIRMATION-REQUIRED"
        return {
            "status": "draft_confirmation_required",
            "answer": value,
            "records": records,
            "next_node": next_node,
            "issues": [{
                "severity": "error",
                "code": code,
                "message": "Draft/reference values remain unconfirmed until explicit analyst confirmation and cannot mutate accepted state.",
                "location": node.get("id", "node"),
                "provenance": provenance,
            }],
        }
    return {"status": "passed", "answer": value, "records": records, "issues": []}


def attach_value_provenance(state: dict[str, Any], records: dict[str, Any]) -> None:
    if not records:
        return
    catalog = state.setdefault("_value_provenance", {})
    if isinstance(catalog, dict):
        catalog.update(records)
