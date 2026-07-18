from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

OPCODE_PATTERN = re.compile(r"`([A-Z][A-Z0-9_]*(?:\.[A-Z0-9_]+)+)`")


def find_repo_root(start: str | Path) -> Path | None:
    path = Path(start).resolve()
    if path.is_file():
        path = path.parent
    checked: list[Path] = []
    for candidate in [path, *path.parents, Path(__file__).resolve().parent, *Path(__file__).resolve().parents]:
        if candidate in checked:
            continue
        checked.append(candidate)
        if (candidate / "language" / "registry" / "OPCODE_CATALOG.md").exists():
            return candidate
    return None


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


def load_opcode_catalog(repo_root: str | Path) -> set[str]:
    catalog = Path(repo_root) / "language" / "registry" / "OPCODE_CATALOG.md"
    if not catalog.exists():
        return set()
    return set(OPCODE_PATTERN.findall(catalog.read_text(encoding="utf-8")))


def load_source_construct_catalog(repo_root: str | Path) -> set[str]:
    data = _load_yaml(Path(repo_root) / "language" / "registry" / "source_construct_catalog.yaml")
    return {str(item.get("key")) for item in data.get("constructs", []) if isinstance(item, dict) and item.get("key")}


def load_trace_event_catalog(repo_root: str | Path) -> set[str]:
    data = _load_yaml(Path(repo_root) / "language" / "registry" / "trace_event_catalog.yaml")
    return {str(item.get("id")) for item in data.get("events", []) if isinstance(item, dict) and item.get("id")}


def validate_source_constructs(source: dict[str, Any], repo_root: str | Path | None) -> dict[str, Any]:
    used = sorted(str(key) for key in source.keys())
    if repo_root is None:
        return {"status": "skipped", "reason": "source construct registry not found near package", "used": used, "unknown": [], "issues": []}
    registered = load_source_construct_catalog(repo_root)
    unknown = sorted(key for key in used if key not in registered)
    issues = [{
        "severity": "error",
        "code": "SOURCE_CONSTRUCT_NOT_IN_REGISTRY",
        "message": f"Top-level source construct is not registered: {key}",
        "location": key,
    } for key in unknown]
    return {
        "status": "passed" if not unknown else "failed",
        "catalog": str(Path(repo_root) / "language" / "registry" / "source_construct_catalog.yaml"),
        "used": used,
        "unknown": unknown,
        "issues": issues,
    }


def validate_capability_registry(repo_root: str | Path | None) -> dict[str, Any]:
    if repo_root is None:
        return {"status": "skipped", "reason": "capability registry not found near package", "issues": []}
    root = Path(repo_root)
    data = _load_yaml(root / "language" / "registry" / "capability_catalog.yaml")
    capabilities = data.get("capabilities", {}) if isinstance(data, dict) else {}
    source_constructs = load_source_construct_catalog(root)
    opcodes = load_opcode_catalog(root)
    trace_events = load_trace_event_catalog(root)
    issues: list[dict[str, Any]] = []
    for capability, declaration in sorted(capabilities.items()):
        if not isinstance(declaration, dict):
            issues.append({"severity":"error","code":"CAPABILITY_REGISTRY_ENTRY_INVALID","message":f"Capability entry must be an object: {capability}","location":f"capabilities.{capability}"})
            continue
        for construct in declaration.get("source_constructs", []) or []:
            if construct not in source_constructs:
                issues.append({"severity":"error","code":"CAPABILITY_SOURCE_CONSTRUCT_NOT_IN_REGISTRY","message":f"Capability {capability} references unregistered source construct {construct}","location":f"capabilities.{capability}.source_constructs"})
        for opcode in declaration.get("opcodes", []) or []:
            if opcode not in opcodes:
                issues.append({"severity":"error","code":"OPCODE_NOT_IN_REGISTRY","message":f"Capability {capability} references unregistered opcode {opcode}","location":f"capabilities.{capability}.opcodes"})
        for event in declaration.get("trace_events", []) or []:
            if event not in trace_events:
                issues.append({"severity":"error","code":"TRACE_EVENT_NOT_IN_REGISTRY","message":f"Capability {capability} references unregistered trace event {event}","location":f"capabilities.{capability}.trace_events"})
    return {
        "status":"passed" if not issues else "failed",
        "catalog":str(root / "language" / "registry" / "capability_catalog.yaml"),
        "capabilities":sorted(capabilities.keys()),
        "issues":issues,
    }


def validate_ir_opcodes(ir: dict[str, Any], repo_root: str | Path | None) -> dict[str, Any]:
    ops = sorted({op.get("op") for op in ir.get("ops", []) if isinstance(op, dict) and op.get("op")})
    if repo_root is None:
        return {
            "status": "skipped",
            "reason": "OPCODE_CATALOG.md not found near package; registry check skipped.",
            "ops": ops,
            "missing_ops": [],
        }
    registered = load_opcode_catalog(repo_root)
    missing = sorted(op for op in ops if op not in registered)
    return {
        "status": "passed" if not missing else "failed",
        "catalog": str(Path(repo_root) / "language" / "registry" / "OPCODE_CATALOG.md"),
        "ops": ops,
        "missing_ops": missing,
    }
