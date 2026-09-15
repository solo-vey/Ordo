from __future__ import annotations

"""Canonical graph-contract projection shared by validation and lowering.

The source language deliberately supports several authored transition forms.
This module makes those forms explicit in one place so the graph validator,
compiler, runtime and tooling cannot each implement a divergent subset.
"""

from dataclasses import dataclass
from typing import Any


TRANSITION_TARGET_FIELDS = frozenset({"next", "to", "on_pass", "on_fail", "pass_to", "fail_to"})
INVALID_DYNAMIC_ROUTE_BEHAVIORS = frozenset({
    "block",
    "stay",
    "return_to_source",
    "block_and_keep_current_node",
    "block_and_return_to_last_valid_node",
})
DYNAMIC_ROUTE_KINDS = frozenset({"recovery", "correction", "retry"})


@dataclass(frozen=True)
class RouteDeclaration:
    source: str
    target: str
    location: str
    scope: str
    kind: str = "static"
    route_key: str | None = None


def _nested_targets(value: Any, *, path: str, scope: str) -> list[tuple[str, str, str]]:
    """Return transition targets from nested mappings and list-based forms."""
    found: list[tuple[str, str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in TRANSITION_TARGET_FIELDS and isinstance(child, str):
                found.append((child, child_path, scope))
            else:
                # Mapping branches (for example answer values) are distinct
                # transition scopes. A list intentionally retains its scope,
                # making duplicate items in one declared list an error.
                found.extend(_nested_targets(child, path=child_path, scope=child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_nested_targets(child, path=f"{path}[{index}]", scope=scope))
    return found


def vertex_route_declarations(vertex: dict[str, Any], *, vertex_id: str, vertex_kind: str) -> list[RouteDeclaration]:
    """Project every supported static route declaration for one graph vertex."""
    prefixes: list[tuple[Any, str, str]] = []
    if vertex_kind == "node":
        prefixes.extend([
            (vertex.get("on_answer"), f"nodes[{vertex_id}].on_answer", "on_answer"),
            (vertex.get("transitions"), f"nodes[{vertex_id}].transitions", "transitions"),
        ])
    else:
        prefixes.extend([
            (vertex.get("transitions"), f"gates[{vertex_id}].transitions", "transitions"),
        ])

    declarations: list[RouteDeclaration] = []
    for value, path, scope in prefixes:
        for target, location, declaration_scope in _nested_targets(value, path=path, scope=scope):
            declarations.append(RouteDeclaration(vertex_id, target, location, declaration_scope))

    direct_keys = {"next", "to"} if vertex_kind == "node" else {"on_pass", "on_fail", "pass_to", "fail_to"}
    for key in direct_keys:
        target = vertex.get(key)
        if isinstance(target, str):
            declarations.append(RouteDeclaration(vertex_id, target, f"{vertex_kind}s[{vertex_id}].{key}", "direct_fields"))

    navigation = vertex.get("navigation_contract") or {}
    allowed_to = navigation.get("allowed_to") if isinstance(navigation, dict) else None
    if isinstance(allowed_to, list):
        for index, target in enumerate(allowed_to):
            if isinstance(target, str):
                declarations.append(RouteDeclaration(
                    vertex_id,
                    target,
                    f"{vertex_kind}s[{vertex_id}].navigation_contract.allowed_to[{index}]",
                    "navigation_contract.allowed_to",
                ))
    return declarations


def dynamic_route_declarations(contract: dict[str, Any]) -> list[RouteDeclaration]:
    """Project declared dynamic routes into bounded, validation-visible edges."""
    declarations: list[RouteDeclaration] = []
    for index, route in enumerate(contract.get("dynamic_routes", []) or []):
        if not isinstance(route, dict):
            continue
        source = route.get("from")
        route_key = route.get("route_key")
        if not isinstance(source, str) or not isinstance(route_key, str):
            continue
        for target_index, target in enumerate(route.get("allowed_targets", []) or []):
            if isinstance(target, str):
                declarations.append(RouteDeclaration(
                    source,
                    target,
                    f"graph_contract.dynamic_routes[{index}].allowed_targets[{target_index}]",
                    f"dynamic_routes[{index}]",
                    "dynamic",
                    route_key,
                ))
    return declarations


def allowed_from(vertex: dict[str, Any]) -> Any:
    """Return the canonical incoming declaration, including navigation form."""
    navigation = vertex.get("navigation_contract") or {}
    if isinstance(navigation, dict) and "allowed_from" in navigation:
        return navigation.get("allowed_from")
    return vertex.get("allowed_from", vertex.get("incoming_from"))
