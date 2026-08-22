"""Ordo alpha.20 runtime contracts.

This module intentionally contains only thin/strict runtime primitives:
- StatePatch validation + atomic application
- GateFailure normalization
- contract schemas exposed for debug/tooling

It does not perform semantic repair or recovery planning.
"""
from __future__ import annotations

import copy
import re
from typing import Any


NODE_EXECUTION_RESULT_SCHEMA = {
    "$id": "ordo.alpha20.NodeExecutionResult",
    "type": "object",
    "required": ["action", "assistant_message", "state_patch", "next_intent", "needs_analyst"],
    "additionalProperties": False,
}

STATE_PATCH_SCHEMA = {
    "$id": "ordo.alpha20.StatePatch",
    "type": "object",
    "required": ["base_revision", "operations"],
    "additionalProperties": False,
}

GATE_FAILURE_SCHEMA = {
    "$id": "ordo.alpha20.GateFailure",
    "type": "object",
    "required": [
        "gate_id", "status", "failed_checks", "invalid_state", "missing_information",
        "missing_coverage", "affected_state", "evidence",
    ],
    "additionalProperties": False,
}

RECOVERY_PLAN_SCHEMA = {"$id": "ordo.alpha20.RecoveryPlan", "type": "object"}
REVISIT_CONTEXT_SCHEMA = {"$id": "ordo.alpha20.RevisitContext", "type": "object"}
RECOVERY_SESSION_SCHEMA = {"$id": "ordo.alpha20.RecoverySession", "type": "object"}

ALLOWED_PATCH_OPS = {"set", "replace", "append", "merge", "merge_deep", "merge_row", "remove"}

RELEASE1_APPEND_ONLY_COLLECTION_PATHS = {
    "functional_test_catalog.rows",
    "unit_test_catalog.rows",
    "edge_case_catalog.rows",
}
ALLOWED_PATCH_BASIS = {"analyst_input", "confirmed_state", "derived", "generated", "recovery", "legacy_unknown"}


def _parts(path: str) -> list[str]:
    clean = str(path or "").strip().removeprefix("state.").removeprefix("$state.")
    return [p for p in clean.split(".") if p]


def _get(root: dict[str, Any], path: str) -> tuple[bool, Any]:
    cur: Any = root
    for part in _parts(path):
        if not isinstance(cur, dict) or part not in cur:
            return False, None
        cur = cur[part]
    return True, cur


def _set(root: dict[str, Any], path: str, value: Any) -> None:
    parts = _parts(path)
    if not parts:
        raise ValueError("state patch path is empty")
    cur = root
    for part in parts[:-1]:
        nxt = cur.get(part)
        if nxt is None:
            nxt = {}
            cur[part] = nxt
        if not isinstance(nxt, dict):
            raise ValueError(f"cannot descend through non-object state path: {part}")
        cur = nxt
    cur[parts[-1]] = copy.deepcopy(value)


def _remove(root: dict[str, Any], path: str) -> None:
    parts = _parts(path)
    if not parts:
        raise ValueError("state patch path is empty")
    cur: Any = root
    for part in parts[:-1]:
        if not isinstance(cur, dict) or part not in cur:
            return
        cur = cur[part]
    if isinstance(cur, dict):
        cur.pop(parts[-1], None)


def _path_allowed(path: str, allowed_paths: list[str] | None) -> bool:
    # Authority checks are fail-closed.  A missing allowlist is a configuration
    # error, never permission to write anywhere.
    if not allowed_paths:
        return False
    p = ".".join(_parts(path))
    for raw in allowed_paths:
        a = ".".join(_parts(raw))
        if not a:
            continue
        # Exact leaf, parent object containing allowed leaves, or a descendant of an allowed object.
        if p == a or p.startswith(a + ".") or a.startswith(p + "."):
            return True
    return False


def canonicalize_runtime_state(state: Any) -> dict[str, Any]:
    """Normalize mixed flat dotted and nested state into one nested representation.

    Nested values win on exact conflict; non-conflicting dotted descendants are merged.
    This prevents one patch from creating two divergent representations of the same object.
    """
    if not isinstance(state, dict):
        return {}
    result: dict[str, Any] = {}
    # First load flat keys, then overlay nested keys so explicit nested state wins.
    for key, value in state.items():
        if isinstance(key, str) and "." in key:
            try:
                _set(result, key, value)
            except ValueError:
                pass
    def deep_overlay(dst: dict[str, Any], src: dict[str, Any]) -> None:
        for key, value in src.items():
            if isinstance(key, str) and "." in key:
                continue
            if isinstance(value, dict) and isinstance(dst.get(key), dict):
                deep_overlay(dst[key], value)
            else:
                dst[key] = copy.deepcopy(value)
    deep_overlay(result, state)
    return result




def _schema_type_ok(value: Any, expected: Any) -> bool:
    allowed = expected if isinstance(expected, list) else [expected]
    for typ in allowed:
        if typ == "null" and value is None: return True
        if typ == "string" and isinstance(value, str): return True
        if typ == "boolean" and isinstance(value, bool): return True
        if typ == "integer" and isinstance(value, int) and not isinstance(value, bool): return True
        if typ == "number" and isinstance(value, (int, float)) and not isinstance(value, bool): return True
        if typ == "object" and isinstance(value, dict): return True
        if typ == "array" and isinstance(value, list): return True
    return False

def _validate_value_schema(value: Any, schema: Any, path: str = "value") -> list[str]:
    if not isinstance(schema, dict): return []
    errors: list[str] = []
    if "const" in schema and value != schema["const"]: errors.append(f"{path} must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]: errors.append(f"{path} is not in enum")
    if "oneOf" in schema:
        matches = [sub for sub in schema["oneOf"] if not _validate_value_schema(value, sub, path)]
        if len(matches) != 1: errors.append(f"{path} must match exactly one allowed schema")
        return errors
    if "anyOf" in schema:
        if not any(not _validate_value_schema(value, sub, path) for sub in schema["anyOf"]): errors.append(f"{path} does not match any allowed schema")
        return errors
    if "type" in schema and not _schema_type_ok(value, schema["type"]):
        return [f"{path} has invalid type; expected {schema['type']!r}"]
    if isinstance(value, dict):
        required = schema.get("required") or []
        for key in required:
            if key not in value: errors.append(f"{path}.{key} is required")
        props = schema.get("properties") or {}
        for key, sub in props.items():
            if key in value: errors.extend(_validate_value_schema(value[key], sub, f"{path}.{key}"))
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in props: errors.append(f"{path}.{key} is not allowed")
    if isinstance(value, list):
        if isinstance(schema.get("minItems"), int) and len(value) < schema["minItems"]: errors.append(f"{path} requires at least {schema['minItems']} items")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for idx, item in enumerate(value): errors.extend(_validate_value_schema(item, item_schema, f"{path}[{idx}]"))
    return errors

def _value_schema_for_operation(schema: Any, op: str) -> Any:
    """Select the value schema for the patch operation.

    Collection targets describe the array as a whole, but append/merge_row values are
    single rows and therefore must validate against the array item schema.
    """
    if isinstance(schema, dict) and schema.get("type") == "array" and op in {"append", "merge_row"}:
        item_schema = schema.get("items")
        return item_schema if isinstance(item_schema, dict) else schema
    return schema


def validate_state_patch(
    patch: Any,
    *,
    allowed_paths: list[str] | None = None,
    protected_paths: list[str] | None = None,
    current_revision: int | None = None,
    value_schemas: dict[str, Any] | None = None,
    operation_variants: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    protected = {".".join(_parts(p)) for p in (protected_paths or [])}
    if not isinstance(patch, dict):
        return {"valid": False, "errors": ["state_patch must be an object"]}
    if "base_revision" not in patch:
        errors.append("state_patch.base_revision is required")
    elif not isinstance(patch.get("base_revision"), int) or isinstance(patch.get("base_revision"), bool) or patch.get("base_revision") < 0:
        errors.append("state_patch.base_revision must be a non-negative integer")
    elif current_revision is not None and patch.get("base_revision") != current_revision:
        errors.append(f"state_patch.base_revision mismatch: expected {current_revision}, got {patch.get('base_revision')}")
    ops = patch.get("operations")
    if not isinstance(ops, list):
        return {"valid": False, "errors": ["state_patch.operations must be an array"]}
    for idx, item in enumerate(ops):
        prefix = f"operations[{idx}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        op = str(item.get("op") or "")
        path = ".".join(_parts(str(item.get("path") or "")))
        if op not in ALLOWED_PATCH_OPS:
            errors.append(f"{prefix}.op is invalid: {op!r}")
        if not path:
            errors.append(f"{prefix}.path is empty")
        elif not _path_allowed(path, allowed_paths):
            errors.append(f"{prefix}.path is outside write allowlist: {path}")
        if path in protected and op in {"set", "replace", "remove", "merge", "merge_deep", "merge_row"}:
            errors.append(f"{prefix}.path is protected confirmed state: {path}")
        if path in RELEASE1_APPEND_ONLY_COLLECTION_PATHS and op in {"set", "replace", "remove"}:
            errors.append(f"{prefix}.op={op} is forbidden for append-only Release 1 test catalogue path: {path}")
        basis = item.get("basis")
        if basis is not None and basis not in ALLOWED_PATCH_BASIS:
            errors.append(f"{prefix}.basis is invalid: {basis!r}")
        if op in {"set", "replace", "append", "merge", "merge_deep", "merge_row"} and "value" not in item:
            errors.append(f"{prefix}.value is required for op={op}")
        schema = (value_schemas or {}).get(path)
        if schema is None:
            for schema_path, candidate_schema in (value_schemas or {}).items():
                if path.startswith(schema_path + ".") or schema_path.startswith(path + "."):
                    schema = candidate_schema
                    break
        schema = _value_schema_for_operation(schema, op)
        if schema is not None and "value" in item and op != "remove":
            errors.extend(f"{prefix}.{msg}" for msg in _validate_value_schema(item.get("value"), schema))
        if op == "merge_row":
            row_key = item.get("row_key")
            row_match = item.get("row_match")
            if not isinstance(row_key, str) or not row_key.strip():
                errors.append(f"{prefix}.row_key is required for op=merge_row")
            if row_match is None:
                errors.append(f"{prefix}.row_match is required for op=merge_row")
            if "value" in item and not isinstance(item.get("value"), dict):
                errors.append(f"{prefix}.value must be an object for op=merge_row")
        if operation_variants:
            variants = [v for v in operation_variants if isinstance(v, dict)]
            if variants and not any(not _validate_value_schema(item, variant, prefix) for variant in variants):
                errors.append(f"{prefix} does not match any declared operation variant")
    return {"valid": not errors, "errors": errors}


UNRESOLVED_RUNTIME_EXPRESSION_RE = re.compile(r"^\$[A-Za-z_][\w.]*$")

def _find_unresolved_runtime_expression(value: Any, path: str = "value") -> list[str]:
    errors: list[str] = []
    if isinstance(value, str) and UNRESOLVED_RUNTIME_EXPRESSION_RE.fullmatch(value.strip()):
        errors.append(f"{path} contains unresolved runtime expression: {value}")
    elif isinstance(value, list):
        for i, item in enumerate(value):
            errors.extend(_find_unresolved_runtime_expression(item, f"{path}[{i}]"))
    elif isinstance(value, dict):
        for key, item in value.items():
            errors.extend(_find_unresolved_runtime_expression(item, f"{path}.{key}"))
    return errors

def apply_state_patch_atomic(
    state: Any,
    patch: Any,
    *,
    allowed_paths: list[str] | None = None,
    protected_paths: list[str] | None = None,
    current_revision: int | None = None,
    value_schemas: dict[str, Any] | None = None,
    operation_variants: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    base = canonicalize_runtime_state(state)
    validation = validate_state_patch(patch, allowed_paths=allowed_paths, protected_paths=protected_paths, current_revision=current_revision, value_schemas=value_schemas, operation_variants=operation_variants)
    if not validation["valid"]:
        return base, {"committed": False, **validation}
    residual_errors: list[str] = []
    for idx, item in enumerate(patch.get("operations", [])):
        if isinstance(item, dict) and item.get("op") != "remove" and "value" in item:
            residual_errors.extend(_find_unresolved_runtime_expression(item.get("value"), f"operations[{idx}].value"))
    if residual_errors:
        return base, {"committed": False, "valid": False, "errors": residual_errors}
    candidate = copy.deepcopy(base)
    try:
        for item in patch.get("operations", []):
            op = item["op"]
            path = item["path"]
            value = copy.deepcopy(item.get("value"))
            exists, current = _get(candidate, path)
            if op == "set":
                _set(candidate, path, value)
            elif op == "replace":
                if not exists:
                    raise ValueError(f"replace target does not exist: {path}")
                _set(candidate, path, value)
            elif op == "append":
                if not exists:
                    _set(candidate, path, [value])
                elif not isinstance(current, list):
                    raise ValueError(f"append target is not an array: {path}")
                else:
                    canonical_path = ".".join(_parts(path))
                    if canonical_path in RELEASE1_APPEND_ONLY_COLLECTION_PATHS and isinstance(value, dict):
                        tc_id = str(value.get("tc_id") or "").strip()
                        if tc_id and any(isinstance(row, dict) and str(row.get("tc_id") or "").strip() == tc_id for row in current):
                            raise ValueError(
                                f"append would duplicate tc_id {tc_id!r} at {canonical_path}; "
                                "use merge_row with row_key='tc_id' and row_match=<existing tc_id>"
                            )
                    current.append(value)
            elif op == "merge":
                if not isinstance(value, dict):
                    raise ValueError(f"merge value must be an object: {path}")
                if not exists or current is None:
                    _set(candidate, path, value)
                elif not isinstance(current, dict):
                    raise ValueError(f"merge target is not an object: {path}")
                else:
                    current.update(value)
            elif op == "merge_deep":
                if not isinstance(value, dict):
                    raise ValueError(f"merge_deep value must be an object: {path}")
                if not exists or current is None:
                    _set(candidate, path, value)
                elif not isinstance(current, dict):
                    raise ValueError(f"merge_deep target is not an object: {path}")
                else:
                    def deep_merge(dst: dict[str, Any], src: dict[str, Any]) -> None:
                        for key, val in src.items():
                            if isinstance(val, dict) and isinstance(dst.get(key), dict):
                                deep_merge(dst[key], val)
                            else:
                                dst[key] = copy.deepcopy(val)
                    deep_merge(current, value)
            elif op == "merge_row":
                if not exists or current is None:
                    _set(candidate, path, [value])
                    continue
                if not isinstance(current, list):
                    raise ValueError(f"merge_row target is not an array: {path}")
                row_key = str(item.get("row_key") or "")
                row_match = item.get("row_match")
                matches = [row for row in current if isinstance(row, dict) and row.get(row_key) == row_match]
                if len(matches) != 1:
                    raise ValueError(f"merge_row expected exactly one row at {path} where {row_key}={row_match!r}; found {len(matches)}")
                target = matches[0]
                for key, val in value.items():
                    if isinstance(val, dict) and isinstance(target.get(key), dict):
                        def deep_merge_row(dst: dict[str, Any], src: dict[str, Any]) -> None:
                            for k2, v2 in src.items():
                                if isinstance(v2, dict) and isinstance(dst.get(k2), dict):
                                    deep_merge_row(dst[k2], v2)
                                else:
                                    dst[k2] = copy.deepcopy(v2)
                        deep_merge_row(target[key], val)
                    else:
                        target[key] = copy.deepcopy(val)
            elif op == "remove":
                _remove(candidate, path)
    except Exception as exc:
        return base, {"committed": False, "valid": False, "errors": [str(exc)]}
    # Release 1 touched-path invariant: validate only collection targets written by
    # this patch. Full-state scanning belongs to verify_run_invariants, not commit.
    invariant_errors: list[str] = []
    touched = {".".join(_parts(str(item.get("path") or ""))) for item in patch.get("operations", []) if isinstance(item, dict)}
    for path in sorted(touched):
        schema = (value_schemas or {}).get(path)
        if isinstance(schema, dict) and schema.get("type") == "array":
            exists, current = _get(candidate, path)
            if exists:
                invariant_errors.extend(f"post_commit[{path}].{msg}" for msg in _validate_value_schema(current, schema, path))
    if invariant_errors:
        return base, {"committed": False, "valid": False, "errors": invariant_errors}
    return candidate, {"committed": True, "valid": True, "errors": []}


def legacy_updates_to_state_patch(updates: Any, *, basis: str = "legacy_unknown", base_revision: int = 0) -> dict[str, Any]:
    """Project legacy state_updates without inventing provenance.

    Top-level object writes preserve the legacy canonical deep-merge behavior; dotted
    writes remain leaf sets.  This bridge is compatibility-only and intentionally
    marks provenance as unknown.
    """
    operations: list[dict[str, Any]] = []
    if isinstance(updates, dict):
        for path, value in updates.items():
            op = "merge_deep" if isinstance(value, dict) and "." not in str(path) else "set"
            operations.append({"op": op, "path": str(path), "value": copy.deepcopy(value), "basis": basis})
    return {
        "base_revision": int(base_revision),
        "operations": operations,
        "semantic_summary": "compatibility projection of legacy state_updates; provenance is legacy_unknown",
    }


def normalize_gate_failure(
    gate_id: str,
    *,
    failed_checks: Any = None,
    invalid_state: Any = None,
    missing_information: Any = None,
    missing_coverage: Any = None,
    affected_state: Any = None,
    evidence: Any = None,
    suggested_recovery_scope: str = "unknown",
) -> dict[str, Any]:
    if suggested_recovery_scope not in {"local", "single_node", "multi_node", "context", "unknown"}:
        suggested_recovery_scope = "unknown"
    scope_v2={"local":"local","single_node":"state","multi_node":"branch","context":"context","unknown":"run"}.get(suggested_recovery_scope,"run")
    checks: list[dict[str, Any]] = []
    for item in failed_checks if isinstance(failed_checks, list) else []:
        if isinstance(item, dict):
            cid = str(item.get("check_id") or item.get("id") or "").strip()
            summary = str(item.get("summary") or item.get("message") or item.get("reason") or "").strip()
            if cid or summary:
                checks.append({"check_id": cid or "UNSPECIFIED", "summary": summary or cid, "severity": str(item.get("severity") or "error")})
        elif str(item).strip():
            text = str(item).strip()
            checks.append({"check_id": text, "summary": text, "severity": "error"})
    return {
        "gate_id": str(gate_id or ""),
        "status": "failed",
        "failed_checks": checks,
        "invalid_state": invalid_state if isinstance(invalid_state, list) else [],
        "missing_information": missing_information if isinstance(missing_information, list) else [],
        "missing_coverage": [str(x) for x in (missing_coverage if isinstance(missing_coverage, list) else [])],
        "affected_state": [str(x) for x in (affected_state if isinstance(affected_state, list) else [])],
        "evidence": evidence if isinstance(evidence, list) else [],
        "suggested_recovery_scope": suggested_recovery_scope,
        "recovery_scope_v2": scope_v2,
        "failure_class_v2": "CONTEXT_ERROR" if scope_v2 == "context" else ("STATE_VALIDATION_ERROR" if (invalid_state or missing_coverage) else "GATE_VALIDATION_ERROR"),
    }
