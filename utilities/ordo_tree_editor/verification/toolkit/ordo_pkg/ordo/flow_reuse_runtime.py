from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any


class FlowReuseRuntimeError(RuntimeError):
    """Fail-closed runtime error for authored optional flow-reuse constructs."""


@dataclass(frozen=True)
class TransitionResult:
    next_node: str
    state: dict[str, Any]
    trace: list[dict[str, Any]]
    provenance: dict[str, Any]


def _event(event: str, **payload: Any) -> dict[str, Any]:
    return {"event": event, **payload}


def _resolve_incoming(join: dict[str, Any], *, from_node: str | None, branch_alias: str | None) -> dict[str, Any]:
    candidates = join.get("incoming") or []
    matches = []
    for item in candidates:
        if branch_alias is not None and item.get("alias") == branch_alias:
            matches.append(item)
        elif from_node is not None and item.get("node") == from_node:
            matches.append(item)
    if len(matches) != 1:
        raise FlowReuseRuntimeError(
            f"join {join.get('id')} requires one unambiguous incoming branch; matched {len(matches)}"
        )
    return matches[0]


def _merge_states(join: dict[str, Any], accumulated: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    contract = join.get("state_contract") or {}
    merge = join.get("merge_policy") or {}
    protected = set(contract.get("protected_fields") or [])
    required = set(contract.get("required_fields") or [])
    branch_local = set(contract.get("branch_local_fields") or [])
    field_rules = merge.get("fields") or {}
    default_rule = merge.get("default", "require_equal")

    result = deepcopy(accumulated)
    keys = set(accumulated) | set(incoming)
    for key in keys:
        if key in branch_local:
            continue
        old_present, new_present = key in accumulated, key in incoming
        old, new = accumulated.get(key), incoming.get(key)
        if key in protected and old_present and new_present and old != new:
            raise FlowReuseRuntimeError(f"protected field conflict at join {join.get('id')}: {key}")
        if not old_present:
            result[key] = deepcopy(new)
            continue
        if not new_present:
            continue
        if old == new:
            result[key] = deepcopy(old)
            continue
        rule = field_rules.get(key, default_rule)
        if rule == "prefer_non_null":
            if old is None and new is not None:
                result[key] = deepcopy(new)
            elif new is None:
                result[key] = deepcopy(old)
            else:
                raise FlowReuseRuntimeError(f"non-null conflict at join {join.get('id')}: {key}")
        elif rule == "prefer_incoming":
            if key in protected:
                raise FlowReuseRuntimeError(f"protected field cannot use prefer_incoming: {key}")
            result[key] = deepcopy(new)
        elif rule in {"explicit_resolver", "require_equal"}:
            raise FlowReuseRuntimeError(f"unresolved state conflict at join {join.get('id')}: {key}")
        else:
            raise FlowReuseRuntimeError(f"unsupported merge rule {rule!r} for field {key}")

    missing = sorted(k for k in required if k not in result or result[k] is None)
    if missing:
        raise FlowReuseRuntimeError(f"join {join.get('id')} missing required fields: {', '.join(missing)}")
    return result


def transition_through_join(
    join: dict[str, Any],
    *,
    from_node: str | None = None,
    branch_alias: str | None = None,
    incoming_state: dict[str, Any],
    accumulated_state: dict[str, Any] | None = None,
    prior_provenance: dict[str, Any] | None = None,
) -> TransitionResult:
    """Execute one deterministic transition through a lowered FLOW.JOIN.

    This does not wait for all branches. It merges the state of the actual path with
    any explicitly supplied accumulated join state, then emits provenance preserving
    the selected incoming branch.
    """
    endpoint = _resolve_incoming(join, from_node=from_node, branch_alias=branch_alias)
    merged = _merge_states(join, accumulated_state or {}, incoming_state)
    provenance = deepcopy(prior_provenance or {})
    entries = provenance.setdefault("join_inputs", [])
    entries.append({
        "join_id": join.get("id"),
        "incoming_node": endpoint.get("node"),
        "incoming_alias": endpoint.get("alias"),
        "source_provenance": deepcopy(endpoint.get("source") or {}),
    })
    trace = [
        _event("flow_join_entered", join_id=join.get("id"), incoming_node=endpoint.get("node"), incoming_alias=endpoint.get("alias")),
        _event("flow_join_state_merged", join_id=join.get("id"), fields=sorted(merged.keys())),
        _event("flow_join_exited", join_id=join.get("id"), target=join.get("target")),
    ]
    return TransitionResult(str(join.get("target")), merged, trace, provenance)


def _project_state(spec: dict[str, Any], state: dict[str, Any], *, label: str) -> dict[str, Any]:
    allow = list(spec.get("allow") or [])
    rename = dict(spec.get("rename") or {})
    required = list(spec.get("required") or [])
    missing = [k for k in required if k not in state or state[k] is None]
    if missing:
        raise FlowReuseRuntimeError(f"{label} missing required fields: {', '.join(sorted(missing))}")
    projected: dict[str, Any] = {}
    for source_key in allow:
        if source_key not in state:
            continue
        target_key = rename.get(source_key, source_key)
        if target_key in projected:
            raise FlowReuseRuntimeError(f"{label} maps multiple fields to {target_key}")
        projected[target_key] = deepcopy(state[source_key])
    return projected


def enter_shared_tail(
    reference: dict[str, Any],
    *,
    caller_state: dict[str, Any],
    path_history: list[str] | None = None,
) -> TransitionResult:
    history = list(path_history or [])
    tail_id = str(reference.get("tail_id"))
    max_depth = int(reference.get("max_call_depth", 16))
    if tail_id in history:
        raise FlowReuseRuntimeError(f"recursive shared-tail entry blocked: {tail_id}")
    if len(history) >= max_depth:
        raise FlowReuseRuntimeError(f"shared-tail call depth exceeded: {max_depth}")
    history.append(tail_id)
    imported = _project_state(reference.get("import_state") or {}, caller_state, label="shared-tail import")
    protected = set(reference.get("protected_fields") or [])
    protected_snapshot = {k: deepcopy(caller_state[k]) for k in protected if k in caller_state}
    provenance = {
        "reference_id": reference.get("id"),
        "tail_id": reference.get("tail_id"),
        "caller_namespace": reference.get("namespace"),
        "namespace_map": deepcopy(reference.get("namespace_map") or {}),
        "path_history": history,
        "protected_snapshot": protected_snapshot,
        "source_provenance": deepcopy(reference.get("source_provenance") or {}),
    }
    trace = [
        _event("shared_tail_reference_resolved", reference_id=reference.get("id"), tail_id=reference.get("tail_id")),
        _event("shared_tail_entered", reference_id=reference.get("id"), entry=reference.get("resolved_entry"), imported_fields=sorted(imported.keys())),
    ]
    return TransitionResult(str(reference.get("resolved_entry")), imported, trace, provenance)


def exit_shared_tail(
    reference: dict[str, Any],
    *,
    tail_state: dict[str, Any],
    caller_state: dict[str, Any],
    provenance: dict[str, Any],
    next_node: str | None = None,
) -> TransitionResult:
    next_node = next_node or reference.get("return_to")
    if not isinstance(next_node, str) or not next_node:
        raise FlowReuseRuntimeError("shared-tail return target is missing")
    exported = _project_state(reference.get("export_state") or {}, tail_state, label="shared-tail export")
    result = deepcopy(caller_state)
    protected_snapshot = provenance.get("protected_snapshot") or {}
    for key, expected in protected_snapshot.items():
        if key in result and result[key] != expected:
            raise FlowReuseRuntimeError(f"protected caller state changed before shared-tail return: {key}")
        if key in exported and exported[key] != expected:
            raise FlowReuseRuntimeError(f"shared tail attempted to overwrite protected field: {key}")
    result.update(exported)
    updated_provenance = deepcopy(provenance)
    updated_provenance["tail_exit"] = {
        "next_node": next_node,
        "exported_fields": sorted(exported.keys()),
    }
    trace = [
        _event("shared_tail_exited", reference_id=reference.get("id"), tail_id=reference.get("tail_id"), exported_fields=sorted(exported.keys())),
        _event("shared_tail_returned", reference_id=reference.get("id"), next_node=next_node),
    ]
    return TransitionResult(next_node, result, trace, updated_provenance)
