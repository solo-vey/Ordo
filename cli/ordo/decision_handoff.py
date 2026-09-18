from __future__ import annotations

"""Decision registry and source-bound cross-chat handoff contracts.

The handoff format deliberately contains only explicit, reviewable context.  It
does not reconstruct a route, mutate runtime state, or infer an accepted
decision from a chat transcript.  A receiving chat can therefore restore the
same active work context without replaying or rolling back a prior session.
"""

from hashlib import sha256
import copy
import json
from pathlib import Path
from typing import Any

from .canonical_source import validate_canonical_source
from .loader import load_package, load_yaml
from .reporter import write_json
from .runtime_context import runtime_from_session


REGISTRY_SCHEMA = "ordo.decision_registry.v1"
HANDOFF_SCHEMA = "ordo.cross_chat_handoff.v1"
_DECISION_STATUSES = {"accepted", "pending", "rejected", "superseded"}


def _sha256_json(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + sha256(payload).hexdigest()


def _issue(code: str, message: str, location: str) -> dict[str, str]:
    return {"severity": "error", "code": code, "message": message, "location": location}


def _safe_file(root: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def _load_json(path: Path, issues: list[dict[str, str]], location: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        issues.append(_issue("DECISION_RECORD_INVALID_JSON", f"cannot parse JSON: {exc}", location))
        return {}
    if not isinstance(data, dict):
        issues.append(_issue("DECISION_RECORD_INVALID", "record must be a JSON object", location))
        return {}
    return data


def _test_ids(tests: dict[str, Any]) -> set[str]:
    return {
        str(item["id"])
        for item in tests.get("test_cases", []) or []
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def _vertex_ids(source: dict[str, Any]) -> set[str]:
    return {
        str(item["id"])
        for key in ("nodes", "gates", "terminals")
        for item in source.get(key, []) or []
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def _identity_matches(expected: Any, actual: dict[str, Any] | None) -> bool:
    if not isinstance(expected, dict) or not isinstance(actual, dict):
        return False
    return expected.get("package") == actual.get("package") and expected.get("package_version") == actual.get("package_version") and expected.get("source_sha256") == actual.get("sha256")


def _package_identity(identity: dict[str, Any] | None) -> dict[str, Any]:
    identity = identity or {}
    return {
        "package": identity.get("package"),
        "package_version": identity.get("package_version"),
        "source_sha256": identity.get("sha256"),
    }


def validate_decision_registry(package: str | Path, registry_path: str | Path) -> dict[str, Any]:
    """Fail closed on stale, conflicting, unlinked, or malformed decisions."""
    root, _manifest, source, tests = load_package(package)
    identity_report = validate_canonical_source(root)
    identity = identity_report.get("source_identity") if identity_report.get("status") == "passed" else None
    issues: list[dict[str, str]] = list(identity_report.get("issues", []) or [])
    path = Path(registry_path).resolve()
    registry = _load_json(path, issues, str(path)) if path.is_file() else {}
    if not path.is_file():
        issues.append(_issue("DECISION_REGISTRY_MISSING", "decision registry file is missing", str(path)))
    if registry.get("schema_version") != REGISTRY_SCHEMA:
        issues.append(_issue("DECISION_REGISTRY_SCHEMA_INVALID", f"schema_version must be {REGISTRY_SCHEMA}", "schema_version"))
    if not _identity_matches(registry.get("package_identity"), identity):
        issues.append(_issue("DECISION_REGISTRY_STALE", "registry package identity does not match the canonical source", "package_identity"))
    decisions = registry.get("decisions")
    if not isinstance(decisions, list):
        issues.append(_issue("DECISION_REGISTRY_DECISIONS_INVALID", "decisions must be a list", "decisions"))
        decisions = []

    tests_by_id, vertices, seen = _test_ids(tests), _vertex_ids(source), {}
    accepted: list[dict[str, Any]] = []
    pending: list[dict[str, Any]] = []
    for index, raw in enumerate(decisions):
        location = f"decisions[{index}]"
        if not isinstance(raw, dict):
            issues.append(_issue("DECISION_RECORD_INVALID", "decision must be an object", location))
            continue
        decision = copy.deepcopy(raw)
        decision_id = decision.get("id")
        if not isinstance(decision_id, str) or not decision_id:
            issues.append(_issue("DECISION_ID_INVALID", "decision id is required", location + ".id"))
            continue
        comparable = {key: value for key, value in decision.items() if key != "recorded_at"}
        if decision_id in seen:
            issues.append(_issue("DECISION_RECORD_CONFLICT" if seen[decision_id] != comparable else "DECISION_RECORD_DUPLICATE", "decision id is duplicated with conflicting content" if seen[decision_id] != comparable else "decision id is duplicated", location + ".id"))
        else:
            seen[decision_id] = comparable
        status = decision.get("lifecycle_status")
        if status not in _DECISION_STATUSES:
            issues.append(_issue("DECISION_LIFECYCLE_INVALID", "lifecycle_status must be accepted, pending, rejected, or superseded", location + ".lifecycle_status"))
        node_id = decision.get("node_id")
        if not isinstance(node_id, str) or node_id not in vertices:
            issues.append(_issue("DECISION_NODE_UNKNOWN", "node_id must name a current node, gate, or terminal", location + ".node_id"))
        if status == "accepted" and not isinstance(decision.get("rationale"), str):
            issues.append(_issue("DECISION_RATIONALE_MISSING", "accepted decisions require rationale", location + ".rationale"))
        for field, code in (("implementing_files", "DECISION_IMPLEMENTING_FILE"), ("tests", "DECISION_TEST_LINK")):
            values = decision.get(field)
            if not isinstance(values, list) or not values:
                issues.append(_issue(code + "_MISSING", f"{field} must be a non-empty list", location + "." + field))
                continue
            for value in values:
                if field == "implementing_files":
                    file_path = _safe_file(root, value)
                    if file_path is None or not file_path.is_file():
                        issues.append(_issue(code + "_INVALID", "implementing file must exist inside the package", location + "." + field))
                elif not isinstance(value, str) or value not in tests_by_id:
                    issues.append(_issue(code + "_UNKNOWN", "linked test id is not declared in the package test catalog", location + "." + field))
        if status == "accepted":
            accepted.append(decision)
        elif status == "pending":
            pending.append(decision)
    return {
        "schema_version": "ordo.decision_registry_validation_report.v1",
        "status": "passed" if not issues else "blocked",
        "registry_path": str(path),
        "registry_sha256": "sha256:" + sha256(path.read_bytes()).hexdigest() if path.is_file() else None,
        "source_identity": identity,
        "accepted_decision_ids": sorted(str(item.get("id")) for item in accepted),
        "pending_decision_ids": sorted(str(item.get("id")) for item in pending),
        "issues": issues,
        "summary": {"errors": len(issues), "decisions": len(decisions), "accepted": len(accepted), "pending": len(pending)},
    }


def _load_context(root: Path, state_path: str | Path | None, issues: list[dict[str, str]]) -> dict[str, Any]:
    if state_path:
        path = Path(state_path).resolve()
        try:
            loaded = load_yaml(path)
        except Exception as exc:
            issues.append(_issue("HANDOFF_CONTEXT_INVALID", f"cannot load context: {exc}", str(path)))
            return {}
        return loaded if isinstance(loaded, dict) else {}
    live = root / "runtime" / "live_session_state.json"
    if not live.is_file():
        issues.append(_issue("HANDOFF_CONTEXT_MISSING", "provide --state or create runtime/live_session_state.json", "runtime/live_session_state.json"))
        return {}
    data = _load_json(live, issues, "runtime/live_session_state.json")
    runtime = runtime_from_session(data)
    business = data.get("business_state") if isinstance(data.get("business_state"), dict) else {}
    return {**business, **runtime}


def _handoff_context(context: dict[str, Any], pending_from_registry: list[str], issues: list[dict[str, str]]) -> dict[str, Any]:
    active_node = context.get("active_node", context.get("current_node"))
    fields = {
        "completed_artifacts": context.get("completed_artifacts"),
        "open_backlog": context.get("open_backlog"),
        "pending_decisions": context.get("pending_decisions", pending_from_registry),
    }
    if not isinstance(active_node, str) or not active_node:
        issues.append(_issue("HANDOFF_ACTIVE_NODE_MISSING", "context must declare active_node or current_node", "active_node"))
    normalized: dict[str, Any] = {"active_node": active_node or ""}
    for field, value in fields.items():
        if not isinstance(value, list):
            issues.append(_issue("HANDOFF_CONTEXT_FIELD_MISSING", f"context field {field} must be an explicit list", field))
            normalized[field] = []
        else:
            normalized[field] = copy.deepcopy(value)
    return normalized


def export_cross_chat_handoff(package: str | Path, *, registry_path: str | Path, state_path: str | Path | None, out: str | Path) -> dict[str, Any]:
    root, _manifest, source, _tests = load_package(package)
    registry_report = validate_decision_registry(root, registry_path)
    issues = list(registry_report.get("issues", []) or [])
    context = _load_context(root, state_path, issues)
    handoff_context = _handoff_context(context, list(registry_report.get("pending_decision_ids", [])), issues)
    if handoff_context.get("active_node") not in _vertex_ids(source):
        issues.append(_issue("HANDOFF_ACTIVE_NODE_UNKNOWN", "active_node does not exist in the current source graph", "active_node"))
    handoff = {
        "schema_version": HANDOFF_SCHEMA,
        "status": "ready" if not issues else "blocked",
        "package_identity": _package_identity(registry_report.get("source_identity")),
        "decision_registry": {"path": str(registry_path), "sha256": registry_report.get("registry_sha256"), "accepted_decision_ids": registry_report.get("accepted_decision_ids", [])},
        "restoration_context": handoff_context,
        "protocol": {"replay_performed": False, "rollback_performed": False, "restore_mode": "context_only"},
        "issues": issues,
    }
    handoff["handoff_sha256"] = _sha256_json(handoff)
    target = Path(out).resolve()
    write_json(target, handoff)
    return {**handoff, "output": str(target)}


def restore_cross_chat_handoff(package: str | Path, *, registry_path: str | Path, handoff_path: str | Path, out: str | Path | None = None) -> dict[str, Any]:
    """Verify a handoff and emit a context-only restoration report.

    The package runtime and its state snapshots remain untouched by design.
    """
    root, _manifest, source, _tests = load_package(package)
    registry_report = validate_decision_registry(root, registry_path)
    issues = list(registry_report.get("issues", []) or [])
    path = Path(handoff_path).resolve()
    handoff = _load_json(path, issues, str(path)) if path.is_file() else {}
    if not path.is_file():
        issues.append(_issue("HANDOFF_MISSING", "handoff file is missing", str(path)))
    received_digest = handoff.get("handoff_sha256")
    unsigned = {key: value for key, value in handoff.items() if key != "handoff_sha256"}
    if received_digest != _sha256_json(unsigned):
        issues.append(_issue("HANDOFF_DIGEST_MISMATCH", "handoff content changed after export", "handoff_sha256"))
    if handoff.get("schema_version") != HANDOFF_SCHEMA:
        issues.append(_issue("HANDOFF_SCHEMA_INVALID", f"schema_version must be {HANDOFF_SCHEMA}", "schema_version"))
    if not _identity_matches(handoff.get("package_identity"), registry_report.get("source_identity")):
        issues.append(_issue("HANDOFF_STALE", "handoff package identity does not match canonical source", "package_identity"))
    decision_ref = handoff.get("decision_registry") if isinstance(handoff.get("decision_registry"), dict) else {}
    if decision_ref.get("sha256") != registry_report.get("registry_sha256"):
        issues.append(_issue("HANDOFF_REGISTRY_STALE", "handoff references a different decision registry revision", "decision_registry.sha256"))
    if sorted(decision_ref.get("accepted_decision_ids") or []) != sorted(registry_report.get("accepted_decision_ids") or []):
        issues.append(_issue("HANDOFF_DECISION_SET_CONFLICT", "accepted decision set differs from the current registry", "decision_registry.accepted_decision_ids"))
    context = handoff.get("restoration_context") if isinstance(handoff.get("restoration_context"), dict) else {}
    restored = _handoff_context(context, list(registry_report.get("pending_decision_ids", [])), issues)
    if restored.get("active_node") not in _vertex_ids(source):
        issues.append(_issue("HANDOFF_ACTIVE_NODE_UNKNOWN", "active_node does not exist in the current source graph", "restoration_context.active_node"))
    protocol = handoff.get("protocol") if isinstance(handoff.get("protocol"), dict) else {}
    if protocol.get("replay_performed") is not False or protocol.get("rollback_performed") is not False or protocol.get("restore_mode") != "context_only":
        issues.append(_issue("HANDOFF_PROTOCOL_INVALID", "handoff must declare context_only with no replay and no rollback", "protocol"))
    report = {
        "schema_version": "ordo.cross_chat_handoff_restore_report.v1",
        "status": "restored" if not issues else "blocked",
        "handoff": str(path),
        "source_identity": registry_report.get("source_identity"),
        "restored_context": restored if not issues else {},
        "replay_performed": False,
        "rollback_performed": False,
        "issues": issues,
        "summary": {"errors": len(issues), "accepted_decisions": len(registry_report.get("accepted_decision_ids", []))},
    }
    target = Path(out).resolve() if out else root / "reports" / "cross_chat_handoff_restore_report.json"
    write_json(target, report)
    report["output"] = str(target)
    return report
