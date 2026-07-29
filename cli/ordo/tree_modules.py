"""Deterministic build-time support for reusable Ordo tree modules.

The library is deliberately not a runtime dependency.  An instance is expanded
into ordinary YAML before it is merged into an application playbook.
"""
from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from .loader import load_yaml, write_yaml


PLACEHOLDER = re.compile(r"{{\s*([A-Za-z_][A-Za-z0-9_]*)\s*}}")


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def library_root(package: Path) -> Path:
    root = package / "source" / "tree_module_library"
    if not root.is_dir():
        raise FileNotFoundError(f"tree module library is missing: {root}")
    return root


def load_library(package: Path) -> tuple[Path, dict[str, Any]]:
    root = library_root(package)
    manifest = load_yaml(root / "manifest.yaml")
    if manifest.get("kind") != "ordo_tree_module_library":
        raise ValueError("invalid tree module library manifest")
    return root, manifest


def _template(package: Path, template_id: str) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    root, manifest = load_library(package)
    entry = next((item for item in manifest.get("templates", []) if item.get("id") == template_id), None)
    if not entry:
        raise ValueError(f"unknown tree module template: {template_id}")
    template_path = root / str(entry["path"])
    template = load_yaml(template_path)
    if template.get("kind") != "ordo_tree_module_template" or template.get("template", {}).get("id") != template_id:
        raise ValueError(f"invalid tree module template: {template_path}")
    return template_path, manifest, template


def list_templates(package: Path) -> dict[str, Any]:
    _, manifest = load_library(package)
    return {
        "status": "passed",
        "library_id": manifest.get("library_id"),
        "library_version": manifest.get("version"),
        "templates": deepcopy(manifest.get("templates", [])),
    }


def inspect_template(package: Path, template_id: str) -> dict[str, Any]:
    path, manifest, template = _template(package, template_id)
    return {
        "status": "passed",
        "library_id": manifest.get("library_id"),
        "library_version": manifest.get("version"),
        "template_path": str(path.relative_to(package)),
        "template": template,
    }


def _substitute(value: Any, params: dict[str, Any]) -> Any:
    if isinstance(value, list):
        return [_substitute(item, params) for item in value]
    if isinstance(value, dict):
        return {key: _substitute(item, params) for key, item in value.items()}
    if not isinstance(value, str):
        return value
    exact = PLACEHOLDER.fullmatch(value)
    if exact:
        name = exact.group(1)
        if name not in params:
            return value
        return deepcopy(params[name])
    return PLACEHOLDER.sub(lambda match: str(params.get(match.group(1), match.group(0))), value)


def _unresolved(value: Any, path: str = "$") -> list[str]:
    if isinstance(value, dict):
        return [issue for key, item in value.items() for issue in _unresolved(item, f"{path}.{key}")]
    if isinstance(value, list):
        return [issue for index, item in enumerate(value) for issue in _unresolved(item, f"{path}[{index}]")]
    return [path] if isinstance(value, str) and PLACEHOLDER.search(value) else []


def _host_inventory(host_source: Path | None) -> dict[str, set[str]]:
    if host_source is None:
        return {"nodes": set(), "state_fields": set(), "gates": set()}
    source = load_yaml(host_source)
    nodes = {str(node.get("id")) for node in source.get("nodes", []) if isinstance(node, dict) and node.get("id")}
    state_schema = ((source.get("state") or {}).get("schema") or {})
    fields = set(state_schema) if isinstance(state_schema, dict) else set()
    gates = {str(gate.get("id")) for gate in source.get("gates", []) if isinstance(gate, dict) and gate.get("id")}
    return {"nodes": nodes, "state_fields": fields, "gates": gates}


def _instance_issues(fragment: dict[str, Any], host_source: Path | None = None) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    unresolved = _unresolved(fragment)
    issues.extend({"code": "TM-UNRESOLVED-PLACEHOLDER", "message": f"unresolved placeholder at {path}"} for path in unresolved)
    nodes = fragment.get("nodes", [])
    ids = [str(node.get("id")) for node in nodes if isinstance(node, dict) and node.get("id")]
    if len(ids) != len(set(ids)):
        issues.append({"code": "TM-DUPLICATE-NODE-ID", "message": "generated node IDs are not unique"})
    fields = list((fragment.get("state_schema") or {}).keys())
    if len(fields) != len(set(fields)):
        issues.append({"code": "TM-DUPLICATE-STATE-FIELD", "message": "generated state fields are not unique"})
    gates = [str(gate.get("id")) for gate in fragment.get("gates", []) if isinstance(gate, dict) and gate.get("id")]
    if len(gates) != len(set(gates)):
        issues.append({"code": "TM-DUPLICATE-GATE-ID", "message": "generated gate IDs are not unique"})
    inventory = _host_inventory(host_source)
    for node_id in ids:
        if node_id in inventory["nodes"]:
            issues.append({"code": "TM-NODE-ID-CONFLICT", "message": f"node ID already exists in host: {node_id}"})
    for field in fields:
        if field in inventory["state_fields"]:
            issues.append({"code": "TM-STATE-FIELD-CONFLICT", "message": f"state field already exists in host: {field}"})
    for gate in gates:
        if gate in inventory["gates"]:
            issues.append({"code": "TM-GATE-ID-CONFLICT", "message": f"gate ID already exists in host: {gate}"})
    bindings = fragment.get("bindings") or {}
    for name in ("entry_node", "success_exit_node"):
        value = bindings.get(name)
        if not value:
            issues.append({"code": "TM-MISSING-BINDING", "message": f"missing {name}"})
        elif host_source is not None and value not in inventory["nodes"]:
            issues.append({"code": "TM-UNKNOWN-BINDING", "message": f"{name} is not a host node: {value}"})
    return issues


def _coerce_params(raw: dict[str, Any]) -> dict[str, Any]:
    params = raw.get("params", raw)
    if not isinstance(params, dict):
        raise ValueError("tree module parameters must be a mapping")
    return deepcopy(params)


def instantiate_template(package: Path, template_id: str, params_path: Path, output: Path, host_source: Path | None = None) -> dict[str, Any]:
    _, manifest, template = _template(package, template_id)
    params = _coerce_params(load_yaml(params_path))
    required = (template.get("parameters") or {}).get("required", {})
    missing = [name for name in required if name not in params or params[name] in (None, "", [])]
    if missing:
        return {"status": "failed", "issues": [{"code": "TM-MISSING-PARAMETER", "message": f"missing required parameter: {name}"} for name in missing]}
    optional = (template.get("parameters") or {}).get("optional", {})
    for name, spec in optional.items():
        if name not in params and isinstance(spec, dict) and "default" in spec:
            params[name] = deepcopy(spec["default"])
    generated = _substitute(deepcopy(template.get("generated") or {}), params)
    fragment = {
        "kind": "ordo_tree_module_instance.v1",
        "template_id": template_id,
        "template_version": str(template.get("template", {}).get("version")),
        "instance_id": params.get("instance_id"),
        "bindings": {key: params.get(key) for key in ("entry_node", "success_exit_node")},
        "state_schema": generated.get("state_schema") or {},
        "nodes": generated.get("nodes") or [],
        "gates": generated.get("gates") or [],
    }
    issues = _instance_issues(fragment, host_source)
    if issues:
        return {"status": "failed", "issues": issues}
    provenance = {
        "template_id": template_id,
        "template_version": fragment["template_version"],
        "library_id": manifest.get("library_id"),
        "library_version": str(manifest.get("version")),
        "instance_id": fragment["instance_id"],
        "parameters": params,
        "parameters_sha256": _digest(params),
        "local_overrides": [],
    }
    fragment["provenance"] = provenance
    fragment["provenance"]["generated_fragment_sha256"] = _digest({key: value for key, value in fragment.items() if key != "provenance"})
    write_yaml(output, fragment)
    return {"status": "passed", "output": str(output), "instance": fragment}


def validate_instance(instance_path: Path, host_source: Path | None = None) -> dict[str, Any]:
    fragment = load_yaml(instance_path)
    if fragment.get("kind") != "ordo_tree_module_instance.v1":
        return {"status": "failed", "issues": [{"code": "TM-INVALID-INSTANCE", "message": "invalid instance kind"}]}
    issues = _instance_issues(fragment, host_source)
    expected = ((fragment.get("provenance") or {}).get("generated_fragment_sha256"))
    actual = _digest({key: value for key, value in fragment.items() if key != "provenance"})
    if expected and expected != actual:
        issues.append({"code": "TM-PROVENANCE-DIGEST-MISMATCH", "message": "generated fragment differs from recorded provenance"})
    return {"status": "failed" if issues else "passed", "issues": issues, "instance": str(instance_path)}


def diff_instance(package: Path, instance_path: Path) -> dict[str, Any]:
    fragment = load_yaml(instance_path)
    provenance = fragment.get("provenance") or {}
    template_id = provenance.get("template_id")
    if not template_id:
        return {"status": "failed", "issues": [{"code": "TM-MISSING-PROVENANCE", "message": "instance has no template provenance"}]}
    _, _, template = _template(package, str(template_id))
    params = provenance.get("parameters") or {}
    expected = _substitute(deepcopy(template.get("generated") or {}), params)
    actual = {"state_schema": fragment.get("state_schema") or {}, "nodes": fragment.get("nodes") or [], "gates": fragment.get("gates") or []}
    expected_view = {"state_schema": expected.get("state_schema") or {}, "nodes": expected.get("nodes") or [], "gates": expected.get("gates") or []}
    changed = _canonical(actual) != _canonical(expected_view)
    return {"status": "passed", "template_id": template_id, "has_local_overrides": changed, "local_overrides": provenance.get("local_overrides") or []}
