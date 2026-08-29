from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any
import json

import yaml


def _load(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8")) if path.suffix in {".yaml", ".yml"} else json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected mapping: {path}")
    return value


def _source_path(package: str | Path) -> Path:
    root = Path(package)
    if root.is_dir() and (root / "source/program.ordo.yaml").exists():
        return root / "source/program.ordo.yaml"
    if root.is_file():
        return root
    raise FileNotFoundError(f"source/program.ordo.yaml not found: {root}")


def _walk_values(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_values(child)


def _node_edges(node: dict[str, Any]) -> set[str]:
    edges: set[str] = set()
    for value in _walk_values(node.get("on_answer", {})):
        next_node = value.get("next") if isinstance(value, dict) else None
        if isinstance(next_node, str):
            edges.add(next_node)
    if isinstance(node.get("next"), str):
        edges.add(node["next"])
    return edges


def _producers(node: dict[str, Any]) -> dict[str, dict[str, Any]]:
    found: dict[str, dict[str, Any]] = {}
    for value in _walk_values(node.get("on_answer", {})):
        updates = value.get("update_state") if isinstance(value, dict) else None
        if not isinstance(updates, dict):
            continue
        for field in updates:
            found[field] = {
                "node_id": node.get("id"),
                "collection_mode": node.get("collection_mode", "analyst_answer"),
                "required": field in set(node.get("required_fields", []) or [])
                or field in set((node.get("node_context") or {}).get("required_state", []) or [])
                or bool((node.get("field_contracts") or {}).get(field, {}).get("required")),
                "location": f"nodes[{node.get('id')}].on_answer.update_state.{field}",
            }
    return found


def _all_paths_to(nodes: dict[str, dict[str, Any]], target: str) -> list[list[str]]:
    predecessors: dict[str, set[str]] = defaultdict(set)
    for node_id, node in nodes.items():
        for child in _node_edges(node):
            if child in nodes:
                predecessors[child].add(node_id)
    starts = set(nodes) - set(predecessors)
    paths: list[list[str]] = []

    def visit(current: str, path: list[str]) -> None:
        if len(paths) >= 256 or current not in nodes or current in path:
            return
        next_path = [current, *path]
        if current in starts:
            paths.append(next_path)
            return
        for parent in sorted(predecessors[current]):
            visit(parent, next_path)

    visit(target, [])
    return paths


def _bindings(value: dict[str, Any]) -> list[dict[str, Any]]:
    raw = value.get("documents", value.get("document_bindings", []))
    return raw if isinstance(raw, list) else []


def validate_document_field_bindings(package: str | Path, bindings: str | Path) -> dict[str, Any]:
    source_file = _source_path(package)
    source = _load(source_file)
    binding_file = Path(bindings)
    documents = _bindings(_load(binding_file))
    nodes = {node.get("id"): node for node in source.get("nodes", []) if isinstance(node, dict) and node.get("id")}
    producers: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for node in nodes.values():
        for field, producer in _producers(node).items():
            producers[field].append(producer)

    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    documents_report: list[dict[str, Any]] = []
    state_schema = (source.get("state") or {}).get("schema", {})
    if not isinstance(state_schema, dict):
        state_schema = {}
    for index, document in enumerate(documents):
        document_id = document.get("document_id", document.get("id", f"document[{index}]"))
        target = document.get("materialization_node", document.get("node_id"))
        paths = _all_paths_to(nodes, target) if isinstance(target, str) and target in nodes else []
        required_fields = document.get("required_fields", document.get("fields", [])) or []
        normalized_fields = []
        for item in required_fields:
            normalized_fields.append(item if isinstance(item, dict) else {"field": item, "required": True})
        document_report = {"document_id": document_id, "materialization_node": target, "paths": paths, "fields": []}
        if not paths:
            errors.append({"code": "ORDO-DOC-FIELD-001", "document": document_id, "message": "materialization node is unknown or unreachable", "location": str(target)})
        for field_spec in normalized_fields:
            field = field_spec.get("field", field_spec.get("name"))
            if not field or not field_spec.get("required", True):
                continue
            field_producers = producers.get(field, [])
            preceding = [p for p in field_producers if any(p["node_id"] in path[:-1] for path in paths)]
            field_report = {"field": field, "required": True, "producers": preceding, "status": "ok"}
            if field not in state_schema:
                field_report["status"] = "error"
                errors.append({"code": "ORDO-DOC-FIELD-002", "document": document_id, "field": field, "message": "required document field is absent from state.schema", "location": str(source_file)})
            elif not preceding:
                field_report["status"] = "error"
                errors.append({"code": "ORDO-DOC-FIELD-003", "document": document_id, "field": field, "message": "required document field has no producer before materialization on an applicable path", "location": str(target)})
            elif not all(any(p["node_id"] in path[:-1] for p in preceding) for path in paths):
                field_report["status"] = "error"
                errors.append({"code": "ORDO-DOC-FIELD-004", "document": document_id, "field": field, "message": "required document field is not produced on every applicable path", "location": str(target)})
            elif not any(p.get("required") for p in preceding):
                field_report["status"] = "warning"
                warnings.append({"code": "ORDO-DOC-FIELD-005", "document": document_id, "field": field, "message": "producer exists but collection is not marked required or gated upstream", "location": str(preceding[0].get("location"))})
            document_report["fields"].append(field_report)
        documents_report.append(document_report)
    status = "failed" if errors else "passed_with_warnings" if warnings else "passed"
    return {"status": status, "source": str(source_file), "bindings": str(binding_file), "errors": errors, "warnings": warnings, "documents": documents_report}
