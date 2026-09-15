from __future__ import annotations

"""Canonical analyst-input and clarification contracts.

The contract is intentionally source-level and opt-in.  Once a package enables
it, a state update originating from an analyst-facing node must name the input
concept it accepts.  This prevents a plausible-looking answer from being
silently written to a different state concept.
"""

from typing import Any


INPUT_MODES = frozenset({"advisory", "strict"})
INPUT_SHAPES = frozenset({"any", "string", "number", "boolean", "array", "object"})
AMBIGUITY_POLICIES = frozenset({"clarify", "reject"})


def _issue(
    issues: list[dict[str, Any]],
    code: str,
    message: str,
    location: str,
    *,
    severity: str = "error",
    input_id: str | None = None,
) -> None:
    item: dict[str, Any] = {"severity": severity, "code": code, "message": message, "location": location}
    if input_id:
        item["input_id"] = input_id
    issues.append(item)


def _shape(value: Any) -> str:
    if isinstance(value, dict) and isinstance(value.get("type"), str):
        return str(value["type"])
    if value is None:
        return "any"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, str):
        return "string"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "any"


def _state_schema(source: dict[str, Any]) -> dict[str, str]:
    raw = ((source.get("state") or {}).get("schema") or {})
    return {str(path): _shape(value) for path, value in raw.items()} if isinstance(raw, dict) else {}


def _node_updates(node: dict[str, Any]) -> set[str]:
    on_answer = node.get("on_answer") or {}
    paths: set[str] = set()
    if not isinstance(on_answer, dict):
        return paths
    direct = on_answer.get("update_state")
    if isinstance(direct, dict):
        paths.update(str(path) for path in direct)
    for branch in on_answer.values():
        if isinstance(branch, dict) and isinstance(branch.get("update_state"), dict):
            paths.update(str(path) for path in branch["update_state"])
    return paths


def _input_specs(contract: dict[str, Any], issues: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    raw = contract.get("inputs") or []
    if not isinstance(raw, list):
        _issue(issues, "INPUT_CONTRACT_INPUTS_INVALID", "input_contract.inputs must be a list.", "input_contract.inputs")
        return {}
    specs: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(raw):
        location = f"input_contract.inputs[{index}]"
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
            _issue(issues, "INPUT_CONTRACT_ID_REQUIRED", "Each input contract requires a non-empty id.", location)
            continue
        input_id = item["id"]
        if input_id in specs:
            _issue(issues, "INPUT_CONTRACT_ID_DUPLICATE", "Input contract ids must be unique.", location, input_id=input_id)
            continue
        specs[input_id] = {**item, "location": location}
    return specs


def _node_bindings(node: dict[str, Any]) -> dict[str, str]:
    declaration = node.get("input_contract") or {}
    bindings = declaration.get("state_writes") or {} if isinstance(declaration, dict) else {}
    if not isinstance(bindings, dict):
        return {}
    return {
        str(path): str(input_id)
        for path, input_id in bindings.items()
        if isinstance(path, str) and isinstance(input_id, str)
    }


def validate_input_contract(source: dict[str, Any]) -> dict[str, Any]:
    """Validate input ownership, missing-data routes and clarification safety."""
    contract = source.get("input_contract")
    if contract is None:
        return {"status": "not_enabled", "mode": "not_enabled", "summary": {"errors": 0, "warnings": 0, "inputs": 0}, "issues": [], "inputs": []}
    issues: list[dict[str, Any]] = []
    if not isinstance(contract, dict):
        _issue(issues, "INPUT_CONTRACT_INVALID", "input_contract must be an object.", "input_contract")
        return {"status": "failed", "mode": "invalid", "summary": {"errors": 1, "warnings": 0, "inputs": 0}, "issues": issues, "inputs": []}
    mode = contract.get("mode", "strict")
    if mode not in INPUT_MODES:
        _issue(issues, "INPUT_CONTRACT_MODE_INVALID", f"input_contract.mode must be one of {sorted(INPUT_MODES)}.", "input_contract.mode")
        mode = "strict"
    if contract.get("version") != "1.0":
        _issue(issues, "INPUT_CONTRACT_VERSION_REQUIRED", "input_contract.version must be '1.0'.", "input_contract.version")
    schema = _state_schema(source)
    nodes = {node.get("id"): node for node in source.get("nodes", []) or [] if isinstance(node, dict) and isinstance(node.get("id"), str)}
    specs = _input_specs(contract, issues)
    reports: list[dict[str, Any]] = []
    for input_id, spec in sorted(specs.items()):
        location = spec["location"]
        path = spec.get("state_path")
        owner = spec.get("responsible_node")
        required = spec.get("required") is True
        expected_shape = str(spec.get("shape", "any"))
        report = {"id": input_id, "expected_state_contract": input_id, "state_path": path, "responsible_node": owner, "required": required, "status": "ok"}
        if not isinstance(path, str) or not path:
            report["status"] = "error"
            _issue(issues, "INPUT_CONTRACT_STATE_PATH_REQUIRED", "Input contract requires state_path.", f"{location}.state_path", input_id=input_id)
        elif path not in schema:
            report["status"] = "error"
            _issue(issues, "INPUT_CONTRACT_STATE_PATH_UNKNOWN", "Input state_path is absent from state.schema.", f"{location}.state_path", input_id=input_id)
        elif expected_shape not in INPUT_SHAPES:
            report["status"] = "error"
            _issue(issues, "INPUT_CONTRACT_SHAPE_INVALID", f"Input shape must be one of {sorted(INPUT_SHAPES)}.", f"{location}.shape", input_id=input_id)
        elif expected_shape != "any" and schema[path] not in {"any", expected_shape}:
            report["status"] = "error"
            _issue(issues, "INPUT_CONTRACT_SHAPE_MISMATCH", "Input shape is incompatible with the target state schema.", f"{location}.shape", input_id=input_id)
        if not isinstance(owner, str) or owner not in nodes:
            report["status"] = "error"
            _issue(issues, "INPUT_CONTRACT_RESPONSIBLE_NODE_MISSING", "Input contract must name an existing responsible_node.", f"{location}.responsible_node", input_id=input_id)
        else:
            bindings = _node_bindings(nodes[owner])
            if path and bindings.get(path) != input_id:
                report["status"] = "error"
                _issue(issues, "INPUT_CONTRACT_WRITE_BINDING_MISSING", "Responsible node must explicitly bind its state write to this input id.", f"nodes[{owner}].input_contract.state_writes", input_id=input_id)
        if required:
            missing_route = spec.get("missing_route")
            if not isinstance(missing_route, str) or missing_route not in nodes:
                report["status"] = "error"
                _issue(issues, "INPUT_CONTRACT_MISSING_ROUTE_REQUIRED", "Required input must route absent data to an existing collection or clarification node.", f"{location}.missing_route", input_id=input_id)
        ambiguity = spec.get("ambiguity") or {}
        if not isinstance(ambiguity, dict):
            report["status"] = "error"
            _issue(issues, "INPUT_CONTRACT_AMBIGUITY_INVALID", "ambiguity must be an object.", f"{location}.ambiguity", input_id=input_id)
        else:
            policy = ambiguity.get("policy", "clarify")
            if policy not in AMBIGUITY_POLICIES:
                report["status"] = "error"
                _issue(issues, "INPUT_CONTRACT_AMBIGUITY_POLICY_INVALID", f"ambiguity.policy must be one of {sorted(AMBIGUITY_POLICIES)}.", f"{location}.ambiguity.policy", input_id=input_id)
            if policy == "clarify":
                target = ambiguity.get("clarification_node")
                if not isinstance(target, str) or target not in nodes:
                    report["status"] = "error"
                    _issue(issues, "INPUT_CONTRACT_CLARIFICATION_ROUTE_REQUIRED", "Ambiguous input requires an existing clarification_node.", f"{location}.ambiguity.clarification_node", input_id=input_id)
        reports.append(report)

    for node_id, node in nodes.items():
        bindings = _node_bindings(node)
        for path, input_id in bindings.items():
            if input_id not in specs:
                _issue(issues, "INPUT_CONTRACT_WRITE_INPUT_UNKNOWN", "State-write binding references an unknown input contract.", f"nodes[{node_id}].input_contract.state_writes.{path}", input_id=input_id)
            elif specs[input_id].get("state_path") != path:
                _issue(issues, "INPUT_CONTRACT_WRITE_TARGET_MISMATCH", "State-write binding targets a path owned by a different input contract.", f"nodes[{node_id}].input_contract.state_writes.{path}", input_id=input_id)
            elif specs[input_id].get("responsible_node") != node_id:
                _issue(issues, "INPUT_CONTRACT_WRITE_OWNER_MISMATCH", "State-write binding is owned by a different responsible_node.", f"nodes[{node_id}].input_contract.state_writes.{path}", input_id=input_id)
        if mode == "strict":
            for path in _node_updates(node):
                if path in schema and path not in bindings:
                    _issue(issues, "INPUT_CONTRACT_SILENT_STATE_MAPPING", "State update has no explicit input-contract target binding.", f"nodes[{node_id}].on_answer.update_state.{path}")
    errors = [issue for issue in issues if issue["severity"] == "error"]
    warnings = [issue for issue in issues if issue["severity"] == "warning"]
    return {
        "status": "passed" if not errors else "failed",
        "mode": mode,
        "summary": {"errors": len(errors), "warnings": len(warnings), "inputs": len(specs)},
        "issues": issues,
        "inputs": reports,
    }


def evaluate_input_submission(source: dict[str, Any], node: dict[str, Any], answer: Any) -> dict[str, Any]:
    """Classify an input submission without changing state.

    An optional envelope may explicitly carry `concept`, `value`, and
    `ambiguous`.  Scalar values remain supported, but can only write through a
    node's explicit state_writes binding when input_contract is enabled.
    """
    contract = source.get("input_contract")
    if not isinstance(contract, dict) or not contract:
        return {"status": "passed", "answer": answer, "issues": []}
    specs = _input_specs(contract, [])
    bindings = _node_bindings(node)
    input_ids = sorted(set(bindings.values()))
    if not input_ids:
        return {
            "status": "blocked",
            "answer": answer,
            "issues": [{"severity": "error", "code": "ORDO-INPUT-001", "message": "Node has no explicit input-contract state-write binding.", "location": node.get("id", "node")}],
        }
    if len(input_ids) != 1:
        return {
            "status": "clarification_required",
            "answer": answer,
            "issues": [{"severity": "error", "code": "ORDO-INPUT-002", "message": "Node accepts multiple input concepts; an explicit answer concept is required.", "location": node.get("id", "node")}],
        }
    input_id = input_ids[0]
    spec = specs.get(input_id)
    if spec is None:
        return {"status": "blocked", "answer": answer, "issues": [{"severity": "error", "code": "ORDO-INPUT-003", "message": "Node binding references an unknown input contract.", "location": node.get("id", "node"), "input_id": input_id}]}
    envelope = answer if isinstance(answer, dict) and any(key in answer for key in {"value", "concept", "ambiguous"}) else None
    value = envelope.get("value") if envelope is not None else answer
    concept = envelope.get("concept") if envelope is not None else input_id
    ambiguity = spec.get("ambiguity") or {}
    clarify_target = ambiguity.get("clarification_node")
    if envelope is not None and envelope.get("ambiguous") is True:
        return {"status": "clarification_required", "answer": value, "input_id": input_id, "next_node": clarify_target, "issues": [{"severity": "error", "code": "ORDO-INPUT-AMBIGUOUS", "message": "Ambiguous analyst input must be clarified before state mutation.", "location": node.get("id", "node"), "input_id": input_id}]}
    if concept != input_id:
        return {"status": "blocked", "answer": value, "input_id": input_id, "issues": [{"severity": "error", "code": "ORDO-INPUT-CONCEPT-MISMATCH", "message": "Analyst answer concept is incompatible with the node input contract.", "location": node.get("id", "node"), "input_id": input_id, "received_concept": concept}]}
    if spec.get("required") is True and value in (None, "", [], {}):
        return {"status": "missing_required", "answer": value, "input_id": input_id, "next_node": spec.get("missing_route"), "issues": [{"severity": "error", "code": "ORDO-INPUT-MISSING", "message": "Required analyst input is absent; collect it before any state mutation.", "location": node.get("id", "node"), "input_id": input_id}]}
    return {"status": "passed", "answer": value, "input_id": input_id, "issues": []}
