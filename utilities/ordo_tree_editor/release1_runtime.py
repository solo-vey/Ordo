from __future__ import annotations
import copy
from typing import Any

try:
    from .alpha20_runtime import _validate_value_schema, canonicalize_runtime_state
except ImportError:
    from alpha20_runtime import _validate_value_schema, canonicalize_runtime_state


def _get(root: dict[str, Any], path: str) -> tuple[bool, Any]:
    cur: Any = root
    for part in str(path).split('.'):
        if not isinstance(cur, dict) or part not in cur:
            return False, None
        cur = cur[part]
    return True, cur


def _set(root: dict[str, Any], path: str, value: Any) -> None:
    parts = str(path).split('.')
    cur = root
    for part in parts[:-1]:
        nxt = cur.get(part)
        if not isinstance(nxt, dict):
            nxt = {}
            cur[part] = nxt
        cur = nxt
    cur[parts[-1]] = copy.deepcopy(value)


def normalize_legacy_collections(state: Any, value_schemas: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Normalize unambiguous legacy nested-row shapes at explicit import boundaries.

    Never call this from StatePatch commit/write paths. If a nested list cannot be
    proven to be a list of valid row items, the import fails closed.
    """
    result = canonicalize_runtime_state(state)
    transforms: list[dict[str, Any]] = []
    non_normalizable: list[str] = []
    for path, schema in sorted((value_schemas or {}).items()):
        if not isinstance(schema, dict) or schema.get('type') != 'array' or not isinstance(schema.get('items'), dict):
            continue
        exists, value = _get(result, path)
        if not exists or not isinstance(value, list):
            continue
        item_schema = schema['items']
        # If arrays are legitimate row items, flattening would be ambiguous.
        item_types = item_schema.get('type')
        item_allows_array = item_types == 'array' or (isinstance(item_types, list) and 'array' in item_types)
        if item_allows_array:
            continue
        changed = False
        flat: list[Any] = []
        for idx, item in enumerate(value):
            if isinstance(item, list):
                if not item or any(_validate_value_schema(row, item_schema, f'{path}[{idx}]') for row in item):
                    non_normalizable.append(f'{path}[{idx}]')
                    flat.append(item)
                    continue
                flat.extend(copy.deepcopy(item))
                changed = True
            else:
                flat.append(copy.deepcopy(item))
        if changed and not any(x == path or x.startswith(path + '[') for x in non_normalizable):
            _set(result, path, flat)
            transforms.append({'path': path, 'transform': 'flatten_legacy_nested_rows', 'before_items': len(value), 'after_items': len(flat)})
    report = {
        'status': 'FAIL' if non_normalizable else 'PASS',
        'legacy_collection_normalization': transforms,
        'non_normalizable_paths': sorted(set(non_normalizable)),
        'boundary': 'load_import_only',
    }
    return result, report


def scan_collection_shapes(state: Any, value_schemas: dict[str, Any]) -> dict[str, Any]:
    canonical = canonicalize_runtime_state(state)
    findings: list[dict[str, Any]] = []
    for path, schema in sorted((value_schemas or {}).items()):
        if not isinstance(schema, dict) or schema.get('type') != 'array':
            continue
        exists, value = _get(canonical, path)
        if not exists:
            continue
        for err in _validate_value_schema(value, schema, path):
            findings.append({'code': 'COLLECTION_SCHEMA_VIOLATION', 'path': path, 'detail': err})
        item_schema = schema.get('items') if isinstance(schema.get('items'), dict) else None
        if isinstance(value, list) and item_schema:
            item_types = item_schema.get('type')
            arrays_allowed = item_types == 'array' or (isinstance(item_types, list) and 'array' in item_types)
            if not arrays_allowed:
                for idx, row in enumerate(value):
                    if isinstance(row, list):
                        findings.append({'code': 'NESTED_COLLECTION_ROW', 'path': f'{path}[{idx}]', 'detail': 'row is an array but item schema does not allow arrays'})
    return {'status': 'FAIL' if findings else 'PASS', 'findings': findings}
