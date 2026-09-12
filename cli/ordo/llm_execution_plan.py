"""Deterministic compiled LLM Runtime Semantic Plan.

The plan is deliberately a projection, never an alternative playbook source.
It gives an LLM only the compact instructions and state/resources relevant to a
single conversational phase; graph traversal and all deterministic operations
remain the responsibility of the runtime.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any
import json


PLAN_SCHEMA = "ordo.llm_execution_plan.v1"
PLAN_COMPILER = {"name": "ordo.llm_execution_plan", "version": "0.1.0"}


def _hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def semantic_ir_sha256(path: Path) -> str:
    """Hash IR semantics while excluding deliberately random anti-leak canary data."""
    ir = json.loads(path.read_text(encoding="utf-8"))
    ir.pop("compiled_at", None)
    security = ir.get("security")
    if isinstance(security, dict):
        security = dict(security)
        security.pop("canary_secret", None)
        ir["security"] = security
    for op in ir.get("ops") or []:
        if isinstance(op, dict) and op.get("canary"):
            op.pop("question", None)
    return sha256(json.dumps(ir, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _targets(value: Any) -> list[str]:
    """Extract explicit route targets from canonical common forms."""
    result: list[str] = []
    if isinstance(value, str) and value:
        return [value]
    if isinstance(value, dict):
        for key in ("next", "to", "on_pass", "on_fail", "pass_to", "fail_to"):
            result.extend(_targets(value.get(key)))
        for item in value.values():
            if isinstance(item, dict):
                result.extend(_targets(item))
    if isinstance(value, list):
        for item in value:
            result.extend(_targets(item))
    return list(dict.fromkeys(result))


def _resource_closure(source: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    resources = source.get("resources") or []
    indexed = {str(item.get("id")): item for item in resources if isinstance(item, dict) and item.get("id")}
    issues: list[dict[str, Any]] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(resource_id: str, trail: list[str]) -> None:
        if resource_id in visiting:
            issues.append({"code": "ORDO-LLM-PLAN-RESOURCE-CYCLE", "message": "resource dependency cycle: " + " -> ".join(trail + [resource_id]), "location": resource_id})
            return
        if resource_id in visited:
            return
        item = indexed.get(resource_id)
        if not item:
            issues.append({"code": "ORDO-LLM-PLAN-RESOURCE-MISSING", "message": f"referenced resource not found: {resource_id}", "location": resource_id})
            return
        visiting.add(resource_id)
        for dependency in item.get("depends_on") or item.get("dependencies") or []:
            visit(str(dependency), trail + [resource_id])
        visiting.remove(resource_id)
        visited.add(resource_id)

    for resource_id in sorted(indexed):
        visit(resource_id, [])
    closure = [{"id": item["id"], "kind": item.get("kind"), "immutable": bool(item.get("immutable", False)), "depends_on": sorted(str(x) for x in (item.get("depends_on") or item.get("dependencies") or []))} for item in sorted(indexed.values(), key=lambda x: str(x["id"]))]
    return closure, issues


def _node_phase(node: dict[str, Any], state_schema: dict[str, Any]) -> dict[str, Any]:
    node_id = str(node.get("id") or "")
    node_type = str(node.get("node_type") or node.get("kind") or "")
    automatic = bool(node.get("automatic")) or "automatic" in node_type or "materialization" in node_type
    human = bool(node.get("human_required")) or node.get("actor") == "human"
    terminal = bool(node.get("terminal")) or node_id.startswith(("END_", "STOP_")) or "terminal" in node_type
    classification = "terminal" if terminal else ("runtime_only" if automatic else ("human" if human else "llm"))
    requested = node.get("required_fields") or node.get("inputs") or node.get("reads") or []
    projected_state = []
    for field in sorted(str(x) for x in requested):
        definition = state_schema.get(field) if isinstance(state_schema, dict) else None
        # Immutable values with a default are runtime-provided, not an LLM dependency.
        if isinstance(definition, dict) and definition.get("immutable") and "default" in definition:
            continue
        projected_state.append(field)
    return {
        "id": node_id,
        "classification": classification,
        "instruction": {
            "question": node.get("question"),
            "purpose": node.get("purpose") or node.get("responsibility"),
            "answer_type": node.get("answer_type"),
            "allowed_answers": node.get("allowed_answers"),
            "clarification": node.get("on_unmatched_input"),
        } if classification == "llm" else None,
        "projected_state": projected_state,
        "projected_resources": sorted(str(x) for x in (node.get("resources") or node.get("resource_refs") or [])),
        "runtime_routes": sorted(set(_targets(node.get("transitions")) + _targets(node.get("on_answer")) + _targets((node.get("navigation_contract") or {}).get("allowed_to")))),
    }


def build_llm_execution_plan(source: dict[str, Any], *, source_sha256: str, ir_sha256: str | None = None) -> dict[str, Any]:
    """Build a stable, compact semantic projection from canonical YAML."""
    meta = source.get("ordo") if isinstance(source.get("ordo"), dict) else {}
    state_schema = ((source.get("state") or {}).get("schema") or {})
    nodes = [_node_phase(node, state_schema) for node in (source.get("nodes") or []) if isinstance(node, dict)]
    gates = [{"id": str(gate.get("id") or ""), "classification": "deterministic_gate" if gate.get("method") == "mechanical" else "runtime_gate", "runtime_routes": sorted(set(_targets(gate.get("transitions")) + _targets(gate.get("on_pass")) + _targets(gate.get("on_fail")) + _targets((gate.get("navigation_contract") or {}).get("allowed_to"))))} for gate in (source.get("gates") or []) if isinstance(gate, dict)]
    operations = [{"id": str(item.get("id") or ""), "classification": "document_generation" if "document" in str(item.get("type") or item.get("kind") or "") else "runtime_operation"} for item in (source.get("outputs") or []) if isinstance(item, dict)]
    declared_terminals = list(source.get("terminals") or []) + list((source.get("graph_contract") or {}).get("external_terminal_targets") or [])
    vertex_ids = {item["id"] for item in nodes} | {item["id"] for item in gates}
    terminals = [{"id": str(item.get("id") if isinstance(item, dict) else item), "classification": "terminal"} for item in declared_terminals if str(item.get("id") if isinstance(item, dict) else item) not in vertex_ids]
    resources, resource_issues = _resource_closure(source)
    known_resources = {str(item.get("id")) for item in resources}
    for phase in nodes:
        for resource_id in phase["projected_resources"]:
            if resource_id not in known_resources:
                resource_issues.append({"code": "ORDO-LLM-PLAN-RESOURCE-MISSING", "message": f"phase references unresolved resource: {resource_id}", "location": phase["id"]})
    return {
        "schema_version": PLAN_SCHEMA,
        "compiler": PLAN_COMPILER,
        "compiled_from": {"package": meta.get("package"), "ordo_version": meta.get("version"), "execution_mode": meta.get("execution_mode"), "canonical_yaml_sha256": source_sha256, "compiled_ir_semantic_sha256": ir_sha256},
        "dependency_closure": {"resources": resources, "includes": sorted({str(x.get("library")) + "@" + str(x.get("version")) for x in (source.get("includes") or []) if isinstance(x, dict)})},
        "phases": sorted(nodes, key=lambda x: x["id"]),
        "runtime_elements": sorted(gates + operations + terminals, key=lambda x: (x["classification"], x["id"])),
        "build_issues": resource_issues,
    }


def validate_llm_execution_plan(plan_path: str | Path, *, source_path: str | Path | None = None, ir_path: str | Path | None = None) -> dict[str, Any]:
    path = Path(plan_path)
    issues: list[dict[str, Any]] = []
    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"status": "failed", "issues": [{"code": "ORDO-LLM-PLAN-001", "message": f"plan is unreadable: {exc}", "location": str(path)}]}
    if plan.get("schema_version") != PLAN_SCHEMA:
        issues.append({"code": "ORDO-LLM-PLAN-002", "message": "unsupported plan schema version", "location": "schema_version"})
    if plan.get("compiler") != PLAN_COMPILER:
        issues.append({"code": "ORDO-LLM-PLAN-003", "message": "unknown compiler metadata", "location": "compiler"})
    source_binding = plan.get("compiled_from") or {}
    if source_path and Path(source_path).exists() and source_binding.get("canonical_yaml_sha256") != _hash(Path(source_path)):
        issues.append({"code": "ORDO-LLM-PLAN-STALE", "message": "plan canonical YAML hash differs from current source", "location": "compiled_from.canonical_yaml_sha256"})
    if ir_path and Path(ir_path).exists() and source_binding.get("compiled_ir_semantic_sha256") != semantic_ir_sha256(Path(ir_path)):
        issues.append({"code": "ORDO-LLM-PLAN-STALE-IR", "message": "plan compiled IR semantic hash differs from current IR", "location": "compiled_from.compiled_ir_semantic_sha256"})
    phase_ids = [str(item.get("id") or "") for item in plan.get("phases") or [] if isinstance(item, dict)]
    all_elements = phase_ids + [str(item.get("id") or "") for item in plan.get("runtime_elements") or [] if isinstance(item, dict)]
    if not phase_ids:
        issues.append({"code": "ORDO-LLM-PLAN-004", "message": "plan has no node phases", "location": "phases"})
    if any(not item for item in all_elements) or len(all_elements) != len(set(all_elements)):
        issues.append({"code": "ORDO-LLM-PLAN-005", "message": "plan contains missing or duplicate element IDs", "location": "phases/runtime_elements"})
    known = set(all_elements) | {"$stay", "$terminal"}
    for phase in plan.get("phases") or []:
        if phase.get("classification") == "llm" and not (phase.get("instruction") or {}).get("question"):
            issues.append({"code": "ORDO-LLM-PLAN-006", "message": "LLM phase lacks compact question instruction", "location": str(phase.get("id"))})
        for target in phase.get("runtime_routes") or []:
            if target not in known:
                issues.append({"code": "ORDO-LLM-PLAN-007", "message": f"illegal route target: {target}", "location": str(phase.get("id"))})
    for element in plan.get("runtime_elements") or []:
        if element.get("classification") in {"deterministic_gate", "runtime_gate", "runtime_operation", "document_generation", "terminal"} and element.get("instruction"):
            issues.append({"code": "ORDO-LLM-PLAN-008", "message": "deterministic/runtime element must not contain an LLM prompt", "location": str(element.get("id"))})
    issues.extend(plan.get("build_issues") or [])
    return {"status": "passed" if not issues else "failed", "plan": str(path), "issues": issues}
