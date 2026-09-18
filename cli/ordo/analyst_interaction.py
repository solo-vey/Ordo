from __future__ import annotations

"""Executable analyst-interaction contract for guided Ordo runtime sessions.

The contract keeps conversational affordances explicit without treating natural
language itself as deterministic control flow.  Authors declare what a field
means, the response shape they expect, when a draft requires confirmation, and
where an incomplete or semantically insufficient answer must be retried.
"""

from typing import Any


MODES = frozenset({"strict", "advisory"})
RESPONSE_MODES = frozenset({"structured", "free_text"})
SIDE_QUESTION_POLICIES = frozenset({"return_to_active_node"})


def _issue(issues: list[dict[str, Any]], code: str, message: str, location: str) -> None:
    issues.append({"severity": "error", "code": code, "message": message, "location": location})


def _node_map(source: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["id"]): node
        for node in source.get("nodes", []) or []
        if isinstance(node, dict) and isinstance(node.get("id"), str)
    }


def _specs(contract: dict[str, Any], issues: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    raw = contract.get("interactions") or []
    if not isinstance(raw, list):
        _issue(issues, "ANALYST_INTERACTION_LIST_INVALID", "analyst_interaction_contract.interactions must be a list.", "analyst_interaction_contract.interactions")
        return {}
    result: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(raw):
        location = f"analyst_interaction_contract.interactions[{index}]"
        if not isinstance(item, dict) or not isinstance(item.get("node"), str) or not item["node"]:
            _issue(issues, "ANALYST_INTERACTION_NODE_REQUIRED", "Each interaction declaration requires an existing node id.", f"{location}.node")
            continue
        node_id = item["node"]
        if node_id in result:
            _issue(issues, "ANALYST_INTERACTION_NODE_DUPLICATE", "Each node may have only one interaction declaration.", f"{location}.node")
            continue
        result[node_id] = {**item, "location": location}
    return result


def validate_analyst_interaction_contract(source: dict[str, Any]) -> dict[str, Any]:
    contract = source.get("analyst_interaction_contract")
    if contract is None:
        return {"status": "not_enabled", "mode": "not_enabled", "summary": {"errors": 0, "interactions": 0}, "issues": [], "interactions": []}
    issues: list[dict[str, Any]] = []
    if not isinstance(contract, dict):
        _issue(issues, "ANALYST_INTERACTION_CONTRACT_INVALID", "analyst_interaction_contract must be an object.", "analyst_interaction_contract")
        return {"status": "failed", "mode": "invalid", "summary": {"errors": 1, "interactions": 0}, "issues": issues, "interactions": []}
    mode = contract.get("mode", "strict")
    if mode not in MODES:
        _issue(issues, "ANALYST_INTERACTION_MODE_INVALID", "mode must be strict or advisory.", "analyst_interaction_contract.mode")
        mode = "strict"
    if contract.get("version") != "1.0":
        _issue(issues, "ANALYST_INTERACTION_VERSION_REQUIRED", "version must be '1.0'.", "analyst_interaction_contract.version")
    policy = contract.get("side_question_policy", "return_to_active_node")
    if policy not in SIDE_QUESTION_POLICIES:
        _issue(issues, "ANALYST_INTERACTION_SIDE_QUESTION_POLICY_INVALID", "side_question_policy must be return_to_active_node.", "analyst_interaction_contract.side_question_policy")
    nodes = _node_map(source)
    gates = {
        str(gate["id"])
        for gate in source.get("gates", []) or []
        if isinstance(gate, dict) and isinstance(gate.get("id"), str)
    }
    vertices = set(nodes) | gates
    specs = _specs(contract, issues)
    reports: list[dict[str, Any]] = []
    for node_id, spec in sorted(specs.items()):
        location = spec["location"]
        report = {"node": node_id, "response_mode": spec.get("response_mode"), "status": "ok"}
        if node_id not in nodes:
            report["status"] = "error"; _issue(issues, "ANALYST_INTERACTION_NODE_UNKNOWN", "Interaction declaration references an unknown node.", f"{location}.node")
        if not isinstance(spec.get("field_meaning"), str) or not spec["field_meaning"].strip():
            report["status"] = "error"; _issue(issues, "ANALYST_INTERACTION_FIELD_MEANING_REQUIRED", "Every interaction must state the analyst-facing field meaning.", f"{location}.field_meaning")
        response_mode = spec.get("response_mode")
        if response_mode not in RESPONSE_MODES:
            report["status"] = "error"; _issue(issues, "ANALYST_INTERACTION_RESPONSE_MODE_INVALID", "response_mode must be structured or free_text.", f"{location}.response_mode")
        sufficiency = spec.get("semantic_sufficiency")
        if not isinstance(sufficiency, dict) or sufficiency.get("required") is not True:
            report["status"] = "error"; _issue(issues, "ANALYST_INTERACTION_SUFFICIENCY_REQUIRED", "semantic_sufficiency.required: true is required.", f"{location}.semantic_sufficiency")
        retry_node = spec.get("on_rejected_semantics")
        if not isinstance(retry_node, str) or retry_node not in nodes:
            report["status"] = "error"; _issue(issues, "ANALYST_INTERACTION_RETRY_ROUTE_REQUIRED", "Semantically rejected input requires an existing retry node.", f"{location}.on_rejected_semantics")
        draft = spec.get("draft_confirmation") or {}
        if not isinstance(draft, dict):
            report["status"] = "error"; _issue(issues, "ANALYST_INTERACTION_DRAFT_CONFIRMATION_INVALID", "draft_confirmation must be an object.", f"{location}.draft_confirmation")
        elif draft.get("required") is True:
            target = draft.get("confirmation_node")
            if not isinstance(target, str) or target not in nodes:
                report["status"] = "error"; _issue(issues, "ANALYST_INTERACTION_DRAFT_CONFIRMATION_ROUTE_REQUIRED", "A required draft confirmation needs an existing confirmation_node.", f"{location}.draft_confirmation.confirmation_node")
        reports.append(report)
    gate_failures = contract.get("gate_failures") or []
    if not isinstance(gate_failures, list):
        _issue(issues, "ANALYST_INTERACTION_GATE_FAILURES_INVALID", "gate_failures must be a list.", "analyst_interaction_contract.gate_failures")
        gate_failures = []
    declared_gates: set[str] = set()
    for index, item in enumerate(gate_failures):
        location = f"analyst_interaction_contract.gate_failures[{index}]"
        if not isinstance(item, dict) or not isinstance(item.get("gate"), str) or item["gate"] not in gates:
            _issue(issues, "ANALYST_INTERACTION_GATE_FAILURE_GATE_UNKNOWN", "Each gate failure declaration must name an existing gate.", f"{location}.gate")
            continue
        gate_id = item["gate"]
        if gate_id in declared_gates:
            _issue(issues, "ANALYST_INTERACTION_GATE_FAILURE_DUPLICATE", "Each gate may have one actionable failure declaration.", f"{location}.gate")
        declared_gates.add(gate_id)
        for field in ("message", "remedy"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                _issue(issues, "ANALYST_INTERACTION_GATE_FAILURE_ACTION_REQUIRED", "A gate failure must provide a human-readable message and remedy.", f"{location}.{field}")
        if not isinstance(item.get("retry_node"), str) or item["retry_node"] not in nodes:
            _issue(issues, "ANALYST_INTERACTION_GATE_FAILURE_RETRY_REQUIRED", "A gate failure must route the analyst to an existing retry node.", f"{location}.retry_node")
    if mode == "strict" and gates and gates - declared_gates:
        _issue(issues, "ANALYST_INTERACTION_GATE_FAILURE_COVERAGE_REQUIRED", "Every gate requires an actionable failure declaration in strict mode.", "analyst_interaction_contract.gate_failures")
    route_labels = contract.get("route_labels") or []
    if not isinstance(route_labels, list):
        _issue(issues, "ANALYST_INTERACTION_ROUTE_LABELS_INVALID", "route_labels must be a list.", "analyst_interaction_contract.route_labels")
        route_labels = []
    for index, item in enumerate(route_labels):
        location = f"analyst_interaction_contract.route_labels[{index}]"
        if not isinstance(item, dict) or item.get("from") not in vertices or item.get("to") not in vertices:
            _issue(issues, "ANALYST_INTERACTION_ROUTE_LABEL_TARGET_UNKNOWN", "A route label must reference known source and target vertices.", location)
        if not isinstance(item, dict) or not isinstance(item.get("label"), str) or not item["label"].strip():
            _issue(issues, "ANALYST_INTERACTION_ROUTE_LABEL_REQUIRED", "A route label requires human-readable label text.", f"{location}.label")
    errors = [item for item in issues if item["severity"] == "error"]
    return {"status": "passed" if not errors else "failed", "mode": mode, "side_question_policy": policy, "summary": {"errors": len(errors), "interactions": len(specs)}, "issues": issues, "interactions": reports}


def _semantic_failure(spec: dict[str, Any], value: Any) -> str | None:
    rule = spec.get("semantic_sufficiency") or {}
    if value in (None, "", [], {}):
        return "answer is empty"
    response_mode = spec.get("response_mode")
    if response_mode == "structured" and not isinstance(value, (dict, list)):
        return "answer must use the declared structured response mode"
    if response_mode == "free_text" and not isinstance(value, str):
        return "answer must use the declared free_text response mode"
    if rule.get("min_length") is not None and (not isinstance(value, str) or len(value.strip()) < int(rule["min_length"])):
        return f"answer is shorter than semantic_sufficiency.min_length={rule['min_length']}"
    if rule.get("min_items") is not None and (not isinstance(value, list) or len(value) < int(rule["min_items"])):
        return f"answer has fewer items than semantic_sufficiency.min_items={rule['min_items']}"
    required_keys = rule.get("required_keys") or []
    if required_keys and (not isinstance(value, dict) or any(key not in value or value[key] in (None, "", [], {}) for key in required_keys)):
        return "answer lacks one or more semantic_sufficiency.required_keys"
    return None


def evaluate_analyst_submission(source: dict[str, Any], node: dict[str, Any], answer: Any) -> dict[str, Any]:
    """Return a non-mutating semantic verdict for an analyst-facing answer."""
    contract = source.get("analyst_interaction_contract")
    if not isinstance(contract, dict) or not contract:
        return {"status": "passed", "answer": answer, "issues": []}
    specs = _specs(contract, [])
    spec = specs.get(str(node.get("id")))
    if spec is None:
        return {"status": "passed", "answer": answer, "issues": []}
    value = answer.get("value") if isinstance(answer, dict) and "value" in answer else answer
    failure = _semantic_failure(spec, value)
    if failure:
        return {
            "status": "semantic_rejected",
            "answer": value,
            "next_node": spec.get("on_rejected_semantics"),
            "issues": [{
                "severity": "error",
                "code": "ORDO-INTERACTION-SEMANTIC-REJECTED",
                "message": f"Analyst input is insufficient: {failure}.",
                "location": node.get("id", "node"),
                "field_meaning": spec.get("field_meaning"),
            }],
        }
    draft = spec.get("draft_confirmation") or {}
    if draft.get("required") is True and isinstance(answer, dict) and answer.get("draft_confirmed") is not True:
        return {
            "status": "draft_confirmation_required",
            "answer": value,
            "next_node": draft.get("confirmation_node"),
            "issues": [{
                "severity": "error",
                "code": "ORDO-INTERACTION-DRAFT-CONFIRMATION-REQUIRED",
                "message": "The analyst must explicitly confirm the draft before it becomes accepted state.",
                "location": node.get("id", "node"),
            }],
        }
    return {"status": "passed", "answer": value, "issues": []}


def route_side_question(source: dict[str, Any], *, active_node: str, question: str) -> dict[str, Any]:
    """Record the only supported side-question disposition: preserve and resume."""
    contract = source.get("analyst_interaction_contract") or {}
    policy = contract.get("side_question_policy", "return_to_active_node") if isinstance(contract, dict) else "return_to_active_node"
    return {
        "status": "resumed",
        "policy": policy,
        "side_question": question,
        "active_node_preserved": active_node,
        "next_node": active_node,
        "state_mutation": False,
        "event": "side_question_answered_resume_active_node",
    }


def describe_gate_failure(source: dict[str, Any], gate_id: str) -> dict[str, Any]:
    """Render the declared analyst-facing remedy for a failed gate."""
    contract = source.get("analyst_interaction_contract") or {}
    failures = contract.get("gate_failures") or [] if isinstance(contract, dict) else []
    item = next((entry for entry in failures if isinstance(entry, dict) and entry.get("gate") == gate_id), None)
    if item is None:
        return {"status": "not_declared", "gate": gate_id, "message": "No actionable gate failure contract is declared."}
    return {"status": "actionable", "gate": gate_id, "message": item.get("message"), "remedy": item.get("remedy"), "retry_node": item.get("retry_node")}
