from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

from .compiler import FlowReuseCompileError, lower_flow_reuse


@dataclass
class FlowReuseIssue:
    severity: str
    code: str
    message: str
    location: str
    details: dict[str, Any] | None = None


def _next_targets(node: dict[str, Any]) -> list[str]:
    out: list[str] = []
    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "next" and isinstance(child, str):
                    out.append(child)
                else:
                    walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
    walk(node)
    return out


def _canonical_node(node: dict[str, Any], signatures: dict[str, str]) -> str:
    value = deepcopy(node)
    value.pop("id", None)

    def replace(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {
                k: (signatures.get(v, "<TARGET>") if k == "next" and isinstance(v, str) else replace(v))
                for k, v in sorted(obj.items())
            }
        if isinstance(obj, list):
            return [replace(v) for v in obj]
        return obj

    return json.dumps(replace(value), sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def detect_reuse_candidates(source: dict[str, Any], *, min_tail_length: int = 2) -> list[dict[str, Any]]:
    """Detect structurally identical linear tails with bounded memory.

    The implementation uses deterministic partition refinement instead of
    recursively embedding full successor signatures.  Each node stores one
    small integer colour per round, so cyclic graphs converge when the
    partition stabilises and cannot trigger signature-size explosion.
    Advisory only: it never mutates source or changes lint/compile status.
    """
    nodes = {n.get("id"): n for n in source.get("nodes", []) or [] if isinstance(n, dict) and n.get("id")}
    if not nodes:
        return []

    # Initial colour intentionally treats every transition target uniformly.
    colours: dict[str, int] = {node_id: 0 for node_id in nodes}
    max_rounds = max(1, len(nodes))
    for _ in range(max_rounds):
        canonical_by_node = {
            node_id: _canonical_node(node, {target: str(colour) for target, colour in colours.items()})
            for node_id, node in nodes.items()
        }
        palette = {value: idx for idx, value in enumerate(sorted(set(canonical_by_node.values())))}
        refined = {node_id: palette[value] for node_id, value in canonical_by_node.items()}
        # Partition equality, rather than hash equality, is the convergence
        # criterion. This is stable for SCCs even when colour numbers change.
        old_groups = sorted(sorted(n for n, c in colours.items() if c == colour) for colour in set(colours.values()))
        new_groups = sorted(sorted(n for n, c in refined.items() if c == colour) for colour in set(refined.values()))
        colours = refined
        if old_groups == new_groups:
            break

    groups: dict[int, list[str]] = {}
    for node_id, colour in colours.items():
        groups.setdefault(colour, []).append(node_id)

    candidates: list[dict[str, Any]] = []
    for node_ids in groups.values():
        if len(node_ids) < 2:
            continue
        first_targets = [_next_targets(nodes[n]) for n in node_ids]
        if any(len(t) != 1 for t in first_targets):
            continue
        if min_tail_length >= 2:
            successor_colours = [colours.get(t[0]) for t in first_targets]
            if any(c is None for c in successor_colours) or len(set(successor_colours)) != 1:
                continue
        candidates.append({
            "code": "FLOW_REUSE_CANDIDATE",
            "severity": "info",
            "nodes": sorted(node_ids),
            "tail_length_lower_bound": min_tail_length,
            "recommendation": "Consider FLOW.JOIN or SHARED.TAIL.REFERENCE only after explicit author review.",
            "automatic_rewrite": False,
        })
    return sorted(candidates, key=lambda x: x["nodes"])


def validate_flow_reuse(source: dict[str, Any]) -> dict[str, Any]:
    issues: list[FlowReuseIssue] = []
    package = str((source.get("ordo") or {}).get("package") or "unnamed.package")
    try:
        lowered = lower_flow_reuse(source, package)
    except FlowReuseCompileError as exc:
        issues.append(FlowReuseIssue(
            "error", "FLOW_REUSE_INVALID", str(exc), "flow_reuse"
        ))
        lowered = []

    candidates = detect_reuse_candidates(source)
    for candidate in candidates:
        issues.append(FlowReuseIssue(
            "info",
            candidate["code"],
            f"Structurally similar branch tails detected: {', '.join(candidate['nodes'])}.",
            "nodes",
            candidate,
        ))

    errors = [asdict(i) for i in issues if i.severity == "error"]
    warnings = [asdict(i) for i in issues if i.severity == "warning"]
    infos = [asdict(i) for i in issues if i.severity == "info"]
    return {
        "status": "passed" if not errors else "failed",
        "summary": {
            "errors": len(errors),
            "warnings": len(warnings),
            "infos": len(infos),
            "lowered_ops": len(lowered),
            "reuse_candidates": len(candidates),
        },
        "issues": [asdict(i) for i in issues],
        "reuse_candidates": candidates,
    }
