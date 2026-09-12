"""Fail-closed runtime/session context for executable Ordo packages.

Business state belongs to the playbook state schema.  Session mechanics belong
to this envelope and are bound to the exact source/IR representation that
started the session.  Keeping these namespaces separate prevents a stale cache
from silently becoming a second source of truth.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any


FORMAT = "ordo-runtime-session.v1"
RUNTIME_CONTEXT_KEYS = {
    "run_id", "current_node", "previous_node_id", "last_closed_node",
    "active_node", "active_question", "execution_mode", "source_binding",
    "session_id", "checkpoint_sequence",
}


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def execution_mode(source: dict[str, Any]) -> str:
    meta = source.get("ordo") if isinstance(source.get("ordo"), dict) else {}
    return str(meta.get("execution_mode") or "full_runtime")


def source_binding(root: Path, source: dict[str, Any]) -> dict[str, Any]:
    source_path = root / "source" / "program.ordo.yaml"
    compiled_path = root / "compiled" / "program.ir.json"
    return {
        "execution_mode": execution_mode(source),
        "canonical_yaml": {
            "path": "source/program.ordo.yaml",
            "sha256": file_sha256(source_path) if source_path.exists() else None,
        },
        "compiled_ir": {
            "path": "compiled/program.ir.json",
            "sha256": file_sha256(compiled_path) if compiled_path.exists() else None,
        },
    }


def split_business_state(state: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return business state and legacy runtime fields without mixing them."""
    business = dict(state)
    runtime = {key: business.pop(key) for key in list(business) if key in RUNTIME_CONTEXT_KEYS}
    return business, runtime


def build_live_session(
    root: Path,
    source: dict[str, Any],
    *,
    run_id: str,
    business_state: dict[str, Any],
    runtime: dict[str, Any],
    evidence: dict[str, Any],
    status: str,
    resume_policy: str,
    restore: dict[str, Any] | None = None,
) -> dict[str, Any]:
    doc: dict[str, Any] = {
        "format": FORMAT,
        "status": status,
        "business_state": business_state,
        "runtime_context": {
            "run_id": run_id,
            "execution_mode": execution_mode(source),
            "source_binding": source_binding(root, source),
            **runtime,
        },
        "evidence": evidence,
        "resume_policy": resume_policy,
    }
    if restore:
        doc["restore"] = restore
    return doc


def state_from_session(loaded: Any) -> dict[str, Any]:
    if not isinstance(loaded, dict):
        return {}
    if isinstance(loaded.get("business_state"), dict):
        return dict(loaded["business_state"])
    embedded = loaded.get("state")
    return dict(embedded) if isinstance(embedded, dict) else dict(loaded)


def runtime_from_session(loaded: Any) -> dict[str, Any]:
    if isinstance(loaded, dict) and isinstance(loaded.get("runtime_context"), dict):
        return dict(loaded["runtime_context"])
    return {}


def validate_live_session(root: Path, source: dict[str, Any], loaded: Any) -> list[dict[str, Any]]:
    """Reject legacy, stale, or mode-mismatched session caches before resume."""
    if not loaded:
        return []
    if not isinstance(loaded, dict) or loaded.get("format") != FORMAT:
        return [{"severity": "error", "code": "ORDO-RUNTIME-CONTEXT-001", "message": "live session is legacy or has no runtime-context contract; explicit migration is required", "location": "runtime/live_session_state.json"}]
    runtime = runtime_from_session(loaded)
    binding = runtime.get("source_binding") if isinstance(runtime.get("source_binding"), dict) else {}
    expected = source_binding(root, source)
    issues: list[dict[str, Any]] = []
    if runtime.get("execution_mode") != expected["execution_mode"]:
        issues.append({"severity": "error", "code": "ORDO-RUNTIME-CONTEXT-002", "message": "session execution mode differs from the current package", "location": "runtime_context.execution_mode"})
    for name in ("canonical_yaml", "compiled_ir"):
        actual = binding.get(name) if isinstance(binding.get(name), dict) else {}
        wanted = expected[name]
        if actual.get("sha256") != wanted.get("sha256"):
            issues.append({"severity": "error", "code": "ORDO-RUNTIME-CONTEXT-003", "message": f"session {name} binding is stale or mismatched", "location": f"runtime_context.source_binding.{name}"})
    if not runtime.get("run_id"):
        issues.append({"severity": "error", "code": "ORDO-RUNTIME-CONTEXT-004", "message": "runtime context has no run_id", "location": "runtime_context.run_id"})
    return issues
