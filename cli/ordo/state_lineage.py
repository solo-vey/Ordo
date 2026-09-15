from __future__ import annotations

"""State producer/consumer closure for canonical Ordo source.

The validator is deliberately source-level. It does not infer business meaning;
instead it makes every state path's owner, shape, collection mode and consumers
auditable before a package is compiled or executed.
"""

from collections import defaultdict
import re
from typing import Any


COLLECTION_MODES = frozenset({"analyst_answer", "system", "derived", "reference", "default"})
LINEAGE_MODES = frozenset({"advisory", "strict"})
STATE_PATH = re.compile(r"\bstate\.([A-Za-z_][A-Za-z0-9_\.]*)")


def _issues() -> list[dict[str, Any]]:
    return []


def _issue(issues: list[dict[str, Any]], code: str, message: str, location: str, *, severity: str = "error", path: str | None = None) -> None:
    value: dict[str, Any] = {"severity": severity, "code": code, "message": message, "location": location}
    if path:
        value["path"] = path
    issues.append(value)


def _walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


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


def _schema_paths(source: dict[str, Any]) -> dict[str, str]:
    schema = (source.get("state") or {}).get("schema") or {}
    if not isinstance(schema, dict):
        return {}
    return {str(path): _shape(value) for path, value in schema.items()}


def _updates(vertex: dict[str, Any], vertex_id: str, kind: str) -> list[dict[str, Any]]:
    produced: list[dict[str, Any]] = []
    for value in _walk(vertex.get("on_answer", {})):
        update = value.get("update_state") if isinstance(value, dict) else None
        if isinstance(update, dict):
            for path in update:
                produced.append({"path": str(path), "owner": vertex_id, "kind": kind, "location": f"{kind}s[{vertex_id}].on_answer.update_state.{path}", "collection_mode": vertex.get("collection_mode")})
    writes = vertex.get("writes") or []
    if isinstance(writes, list):
        for path in writes:
            if isinstance(path, str):
                produced.append({"path": path, "owner": vertex_id, "kind": kind, "location": f"{kind}s[{vertex_id}].writes", "collection_mode": vertex.get("collection_mode")})
    return produced


def _reads(vertex: dict[str, Any], vertex_id: str, kind: str) -> list[dict[str, Any]]:
    paths: set[str] = set()
    for key in ("reads", "inputs", "required_fields"):
        value = vertex.get(key) or []
        if isinstance(value, list):
            paths.update(str(item) for item in value if isinstance(item, str))
    context = vertex.get("node_context") or {}
    if isinstance(context, dict):
        paths.update(str(item) for item in context.get("required_state", []) or [] if isinstance(item, str))
    condition = vertex.get("condition")
    if isinstance(condition, str):
        paths.update(STATE_PATH.findall(condition))
    return [{"path": path, "consumer": vertex_id, "kind": kind, "location": f"{kind}s[{vertex_id}]"} for path in sorted(paths)]


def _field_specs(contract: dict[str, Any], issues: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    raw = contract.get("fields") or []
    result: dict[str, dict[str, Any]] = {}
    entries: list[dict[str, Any]] = []
    if isinstance(raw, dict):
        entries = [{"path": key, **(value if isinstance(value, dict) else {})} for key, value in raw.items()]
    elif isinstance(raw, list):
        entries = [item for item in raw if isinstance(item, dict)]
    else:
        _issue(issues, "STATE_LINEAGE_FIELDS_INVALID", "state_lineage.fields must be a list or mapping.", "state_lineage.fields")
    for index, spec in enumerate(entries):
        path = spec.get("path") or spec.get("field")
        location = f"state_lineage.fields[{index}]"
        if not isinstance(path, str) or not path:
            _issue(issues, "STATE_LINEAGE_PATH_REQUIRED", "State lineage field requires a non-empty path.", f"{location}.path")
            continue
        if path in result:
            _issue(issues, "STATE_LINEAGE_PATH_DUPLICATE", "State lineage paths must be unique.", f"{location}.path", path=path)
            continue
        result[path] = {**spec, "path": path, "location": location}
    return result


def validate_state_lineage(source: dict[str, Any]) -> dict[str, Any]:
    """Validate declared and observed state ownership without mutating source."""
    contract = source.get("state_lineage")
    if contract is None:
        return {"status": "not_enabled", "mode": "not_enabled", "summary": {"errors": 0, "warnings": 0, "fields": 0}, "issues": [], "fields": []}
    issues = _issues()
    if not isinstance(contract, dict):
        _issue(issues, "STATE_LINEAGE_CONTRACT_INVALID", "state_lineage must be an object.", "state_lineage")
        return {"status": "failed", "mode": "invalid", "summary": {"errors": 1, "warnings": 0, "fields": 0}, "issues": issues, "fields": []}
    mode = contract.get("mode", "strict")
    if mode not in LINEAGE_MODES:
        _issue(issues, "STATE_LINEAGE_MODE_INVALID", f"state_lineage.mode must be one of {sorted(LINEAGE_MODES)}.", "state_lineage.mode")
        mode = "strict"
    schema = _schema_paths(source)
    specs = _field_specs(contract, issues)
    vertices: dict[str, tuple[str, dict[str, Any]]] = {}
    for kind in ("nodes", "gates"):
        for vertex in source.get(kind, []) or []:
            if isinstance(vertex, dict) and isinstance(vertex.get("id"), str):
                vertices[vertex["id"]] = (kind[:-1], vertex)
    producers: dict[str, list[dict[str, Any]]] = defaultdict(list)
    consumers: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for vertex_id, (kind, vertex) in vertices.items():
        for item in _updates(vertex, vertex_id, kind):
            producers[item["path"]].append(item)
        for item in _reads(vertex, vertex_id, kind):
            consumers[item["path"]].append(item)

    bindings = contract.get("template_bindings", []) or []
    if not isinstance(bindings, list):
        _issue(issues, "STATE_LINEAGE_BINDINGS_INVALID", "state_lineage.template_bindings must be a list.", "state_lineage.template_bindings")
        bindings = []
    binding_paths: dict[str, list[str]] = defaultdict(list)
    for index, binding in enumerate(bindings):
        if not isinstance(binding, dict) or not isinstance(binding.get("id"), str):
            _issue(issues, "STATE_LINEAGE_BINDING_INVALID", "Template binding requires an id and fields.", f"state_lineage.template_bindings[{index}]")
            continue
        for path in binding.get("fields", []) or []:
            if isinstance(path, str):
                binding_paths[path].append(binding["id"])

    registries = contract.get("registries", []) or []
    if not isinstance(registries, list):
        _issue(issues, "STATE_LINEAGE_REGISTRIES_INVALID", "state_lineage.registries must be a list.", "state_lineage.registries")
        registries = []
    registry_paths: dict[str, list[str]] = defaultdict(list)
    for index, registry in enumerate(registries):
        if not isinstance(registry, dict) or not isinstance(registry.get("id"), str):
            _issue(issues, "STATE_LINEAGE_REGISTRY_INVALID", "State registry requires an id and fields.", f"state_lineage.registries[{index}]")
            continue
        for path in registry.get("fields", []) or []:
            if isinstance(path, str):
                registry_paths[path].append(registry["id"])

    for path in producers:
        if path not in schema:
            _issue(issues, "STATE_LINEAGE_WRITE_UNDECLARED", "A node or gate writes a path absent from state.schema.", producers[path][0]["location"], path=path)
    for path in consumers:
        if path not in schema:
            _issue(issues, "STATE_LINEAGE_READ_UNDECLARED", "A node or gate consumes a path absent from state.schema.", consumers[path][0]["location"], path=path)
    for path in set(binding_paths) | set(registry_paths):
        if path not in schema:
            _issue(issues, "STATE_LINEAGE_BINDING_UNDECLARED", "A registry or template binding references a path absent from state.schema.", "state_lineage", path=path)

    if mode == "strict":
        for path in sorted(schema):
            if path not in specs:
                _issue(issues, "STATE_LINEAGE_FIELD_UNOWNED", "Every state.schema path requires a state_lineage declaration in strict mode.", "state_lineage.fields", path=path)
    reports: list[dict[str, Any]] = []
    for path, spec in sorted(specs.items()):
        declared_shape = str(spec.get("shape", "any"))
        actual_shape = schema.get(path)
        field_producers = producers.get(path, [])
        field_consumers = consumers.get(path, [])
        explicit_consumers = [value for value in spec.get("consumers", []) or [] if isinstance(value, str)]
        owner = spec.get("owner")
        collection_mode = spec.get("collection_mode")
        report = {"path": path, "shape": actual_shape, "owner": owner, "producers": field_producers, "consumers": field_consumers, "template_bindings": binding_paths.get(path, []), "registries": registry_paths.get(path, []), "status": "ok"}
        if actual_shape is None:
            report["status"] = "error"
            _issue(issues, "STATE_LINEAGE_FIELD_UNDECLARED", "State lineage path is absent from state.schema.", spec["location"], path=path)
        elif declared_shape != "any" and actual_shape != "any" and declared_shape != actual_shape:
            report["status"] = "error"
            _issue(issues, "STATE_LINEAGE_SHAPE_MISMATCH", f"Declared shape {declared_shape!r} does not match state.schema shape {actual_shape!r}.", spec["location"], path=path)
        if not isinstance(owner, str) or not owner:
            report["status"] = "error"
            _issue(issues, "STATE_LINEAGE_OWNER_REQUIRED", "State lineage field requires one owning node or gate.", spec["location"], path=path)
        elif owner not in vertices:
            report["status"] = "error"
            _issue(issues, "STATE_LINEAGE_OWNER_MISSING", "Declared state owner does not exist as a node or gate.", spec["location"], path=path)
        elif owner not in {item["owner"] for item in field_producers}:
            report["status"] = "error"
            _issue(issues, "STATE_LINEAGE_MISSING_PRODUCER", "Declared state owner has no matching update_state/writes producer.", spec["location"], path=path)
        unique_producers = {item["owner"] for item in field_producers}
        if len(unique_producers) > 1 and not spec.get("allow_multiple_producers", False):
            report["status"] = "error"
            _issue(issues, "STATE_LINEAGE_MULTIPLE_OWNERS", "Multiple producers require explicit allow_multiple_producers to prevent node-split ownership loss.", spec["location"], path=path)
        if collection_mode not in COLLECTION_MODES:
            report["status"] = "error"
            _issue(issues, "STATE_LINEAGE_COLLECTION_MODE_REQUIRED", f"collection_mode must be one of {sorted(COLLECTION_MODES)}.", spec["location"], path=path)
        for producer in field_producers:
            actual_mode = producer.get("collection_mode")
            if actual_mode and actual_mode != collection_mode:
                report["status"] = "error"
                _issue(issues, "STATE_LINEAGE_COLLECTION_MODE_MISMATCH", "Producer collection_mode differs from the declared state field collection_mode.", producer["location"], path=path)
        for consumer in explicit_consumers:
            if consumer not in vertices:
                report["status"] = "error"
                _issue(issues, "STATE_LINEAGE_CONSUMER_MISSING", "Declared consumer does not exist as a node or gate.", spec["location"], path=path)
        declared_registries = [value for value in spec.get("registries", []) or [] if isinstance(value, str)]
        for registry_id in declared_registries:
            if registry_id not in registry_paths.get(path, []):
                report["status"] = "error"
                _issue(issues, "STATE_LINEAGE_REGISTRY_BINDING_MISSING", "Declared registry does not bind this state path.", spec["location"], path=path)
        declared_bindings = [value for value in spec.get("bindings", []) or [] if isinstance(value, str)]
        for binding_id in declared_bindings:
            if binding_id not in binding_paths.get(path, []):
                report["status"] = "error"
                _issue(issues, "STATE_LINEAGE_TEMPLATE_BINDING_MISSING", "Declared template binding does not bind this state path.", spec["location"], path=path)
        downstream_consumers = [item for item in field_consumers if item.get("consumer") != owner]
        if field_producers and not downstream_consumers and not explicit_consumers and not binding_paths.get(path) and not registry_paths.get(path):
            report["status"] = "error" if mode == "strict" else "warning"
            _issue(issues, "STATE_LINEAGE_COLLECTED_UNUSED", "Collected state path has no declared consumer, registry, or template binding.", spec["location"], severity="error" if mode == "strict" else "warning", path=path)
        reports.append(report)

    errors = [issue for issue in issues if issue["severity"] == "error"]
    warnings = [issue for issue in issues if issue["severity"] == "warning"]
    return {"status": "passed" if not errors else "failed", "mode": mode, "summary": {"errors": len(errors), "warnings": len(warnings), "fields": len(specs), "schema_paths": len(schema)}, "issues": issues, "fields": reports}
