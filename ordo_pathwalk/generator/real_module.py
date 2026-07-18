from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

GRAPH_SCHEMA_VERSION = "ordo.pathwalk.real_module_graph_summary.v1"
PATHS_SCHEMA_VERSION = "ordo.pathwalk.real_module_terminal_paths.v1"
CLEAN_CASES_SCHEMA_VERSION = "ordo.pathwalk.real_module_clean_path_cases.v1"
VALIDATION_SCHEMA_VERSION = "ordo.pathwalk.real_module_graph_validation.v1"
PATH_VALIDATION_SCHEMA_VERSION = "ordo.pathwalk.real_module_terminal_paths_validation.v1"
CLEAN_CASE_VALIDATION_SCHEMA_VERSION = "ordo.pathwalk.real_module_clean_path_cases_validation.v1"
NOISE_CASES_SCHEMA_VERSION = "ordo.pathwalk.real_module_noise_cases.v1"
NOISE_CASE_VALIDATION_SCHEMA_VERSION = "ordo.pathwalk.real_module_noise_cases_validation.v1"

TERMINAL_PREFIXES = ("STOP", "END", "OUT", "G_")


def _read_yaml(path: Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Ordo source YAML must be a mapping/object: {path}")
    return data


def _is_terminal_like(target: str | None) -> bool:
    if not target:
        return False
    return target == "END" or target.startswith(TERMINAL_PREFIXES)


def _target_type(target: str | None, node_ids: set[str], gate_ids: set[str], output_ids: set[str]) -> str:
    if not target:
        return "missing"
    if target in node_ids:
        return "node"
    if target in gate_ids:
        return "gate"
    if target in output_ids:
        return "output"
    if _is_terminal_like(target):
        return "terminal"
    return "unresolved"


def _state_update_keys(spec: Any) -> list[str]:
    if not isinstance(spec, dict):
        return []
    update = spec.get("update_state") or {}
    if isinstance(update, dict):
        return sorted(str(k) for k in update.keys())
    return []


def _extract_on_answer_edges(node: dict[str, Any], node_ids: set[str], gate_ids: set[str], output_ids: set[str]) -> list[dict[str, Any]]:
    node_id = str(node.get("id"))
    on_answer = node.get("on_answer")
    edges: list[dict[str, Any]] = []
    if not isinstance(on_answer, dict):
        return edges

    # Free-text/list/simple form:
    # on_answer:
    #   update_state: ...
    #   next: N_NEXT
    if "next" in on_answer:
        target = on_answer.get("next")
        edges.append({
            "from": node_id,
            "answer": "*",
            "to": target,
            "edge_type": "on_answer.default",
            "target_type": _target_type(target, node_ids, gate_ids, output_ids),
            "state_updates": _state_update_keys(on_answer),
        })
        return edges

    # Enum/branch form:
    # on_answer:
    #   A1:
    #     update_state: ...
    #     next: N_NEXT
    for answer, spec in on_answer.items():
        if answer in {"update_state", "action", "strategy", "max_attempts", "on_exhausted"}:
            continue
        if not isinstance(spec, dict):
            continue
        target = spec.get("next")
        edges.append({
            "from": node_id,
            "answer": str(answer),
            "to": target,
            "edge_type": "on_answer.branch",
            "target_type": _target_type(target, node_ids, gate_ids, output_ids),
            "state_updates": _state_update_keys(spec),
        })
    return edges


def _extract_unmatched_edge(node: dict[str, Any]) -> dict[str, Any] | None:
    spec = node.get("on_unmatched_input")
    if not isinstance(spec, dict):
        return None
    exhausted = spec.get("on_exhausted") or {}
    return {
        "from": str(node.get("id")),
        "edge_type": "on_unmatched_input",
        "action": spec.get("action"),
        "strategy": spec.get("strategy"),
        "max_attempts": spec.get("max_attempts"),
        "on_exhausted_action": exhausted.get("action") if isinstance(exhausted, dict) else None,
        "on_exhausted_reason": exhausted.get("reason") if isinstance(exhausted, dict) else None,
    }


def summarize_real_module_source(source_path: str | Path) -> dict[str, Any]:
    """Load a real Ordo source YAML and produce a PathWalk graph summary.

    This is authoring/testcase-generation analysis. It intentionally reads
    source/program.ordo.yaml and never reads compiled/* runtime artifacts.
    """
    path = Path(source_path)
    source = _read_yaml(path)
    meta = source.get("ordo") or {}
    nodes_raw = source.get("nodes") or []
    gates_raw = source.get("gates") or []
    assertions_raw = source.get("assertions") or []
    outputs_raw = source.get("outputs") or []

    if not isinstance(nodes_raw, list):
        raise ValueError("Ordo source field 'nodes' must be a list")
    if not isinstance(gates_raw, list):
        raise ValueError("Ordo source field 'gates' must be a list")
    if not isinstance(outputs_raw, list):
        raise ValueError("Ordo source field 'outputs' must be a list")

    node_ids = {str(n.get("id")) for n in nodes_raw if isinstance(n, dict) and n.get("id")}
    gate_ids = {str(g.get("id")) for g in gates_raw if isinstance(g, dict) and g.get("id")}
    output_ids = {str(o.get("id")) for o in outputs_raw if isinstance(o, dict) and o.get("id")}

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    unmatched_edges: list[dict[str, Any]] = []
    duplicate_node_ids: list[str] = []
    seen: set[str] = set()

    for raw in nodes_raw:
        if not isinstance(raw, dict):
            continue
        node_id = str(raw.get("id"))
        if node_id in seen:
            duplicate_node_ids.append(node_id)
        seen.add(node_id)
        out_edges = _extract_on_answer_edges(raw, node_ids, gate_ids, output_ids)
        edges.extend(out_edges)
        unmatched = _extract_unmatched_edge(raw)
        if unmatched:
            unmatched_edges.append(unmatched)
        nodes.append({
            "id": node_id,
            "question": raw.get("question"),
            "answer_type": raw.get("answer_type"),
            "allowed_answers": raw.get("allowed_answers") or [],
            "outgoing_edge_count": len(out_edges),
            "branch_answers": [e.get("answer") for e in out_edges],
            "has_unmatched_handler": unmatched is not None,
            "allow_unmatched_input": bool(raw.get("allow_unmatched_input", False)),
            "terminal": raw.get("terminal") is True,
            "lifecycle_status": raw.get("lifecycle_status"),
            "active_runtime_node": raw.get("active_runtime_node", True),
        })

    target_counts: dict[str, int] = {}
    unresolved_targets: list[dict[str, Any]] = []
    terminal_targets: list[dict[str, Any]] = []
    for edge in edges:
        target_type = str(edge.get("target_type"))
        target_counts[target_type] = target_counts.get(target_type, 0) + 1
        if target_type == "unresolved":
            unresolved_targets.append({"from": edge.get("from"), "answer": edge.get("answer"), "to": edge.get("to")})
        if target_type in {"gate", "output", "terminal"}:
            terminal_targets.append({"from": edge.get("from"), "answer": edge.get("answer"), "to": edge.get("to"), "target_type": target_type})

    graph_contract = source.get("graph_contract") or {}
    incoming_node_targets = {str(e.get("to")) for e in edges if e.get("target_type") == "node"}
    start_candidates = [n["id"] for n in nodes if n["id"] not in incoming_node_targets]
    declared_entry = graph_contract.get("entry_node")
    start_node = declared_entry if declared_entry in node_ids else (start_candidates[0] if start_candidates else (nodes[0]["id"] if nodes else None))

    branching_nodes = [n["id"] for n in nodes if n["outgoing_edge_count"] > 1]
    linear_nodes = [n["id"] for n in nodes if n["outgoing_edge_count"] == 1]
    dead_end_nodes = [
        n["id"] for n in nodes
        if n["outgoing_edge_count"] == 0
        and not n.get("terminal")
        and n.get("active_runtime_node") is not False
        and not str(n.get("lifecycle_status") or "").startswith("deprecated")
    ]

    summary = {
        "schema_version": GRAPH_SCHEMA_VERSION,
        "milestone": "M60.7.2",
        "source_kind": "source/program.ordo.yaml",
        "source_path": str(path),
        "package": meta.get("package"),
        "ordo_version": meta.get("version"),
        "control_level": meta.get("control_level"),
        "execution_mode": meta.get("execution_mode"),
        "start_node": start_node,
        "start_candidates": start_candidates,
        "graph_contract": graph_contract,
        "counts": {
            "nodes": len(nodes),
            "edges": len(edges),
            "gates": len(gates_raw),
            "assertions": len(assertions_raw) if isinstance(assertions_raw, list) else 0,
            "outputs": len(outputs_raw),
            "unmatched_handlers": len(unmatched_edges),
            "branching_nodes": len(branching_nodes),
            "linear_nodes": len(linear_nodes),
            "dead_end_nodes": len(dead_end_nodes),
        },
        "edge_target_counts": target_counts,
        "nodes": nodes,
        "edges": edges,
        "unmatched_edges": unmatched_edges,
        "terminal_targets": terminal_targets,
        "unresolved_targets": unresolved_targets,
        "duplicate_node_ids": duplicate_node_ids,
        "gates": [
            {
                "id": g.get("id"),
                "method": g.get("method"),
                "trust_class": g.get("trust_class"),
                "on_fail": g.get("on_fail"),
            }
            for g in gates_raw if isinstance(g, dict)
        ],
        "outputs": [
            {
                "id": o.get("id"),
                "type": o.get("type"),
                "allowed_after": o.get("allowed_after") or [],
            }
            for o in outputs_raw if isinstance(o, dict)
        ],
        "readiness": {
            "graph_summary_ready": not duplicate_node_ids and not unresolved_targets and bool(nodes),
            "path_enumeration_ready": not duplicate_node_ids and not unresolved_targets and bool(nodes),
            "testcase_generation_ready": False,
            "reason": "M60.7.2 implements loader, graph summary, and terminal path enumeration; testcase generation remains a future step.",
        },
    }
    return summary


def render_graph_summary_markdown(summary: dict[str, Any]) -> str:
    counts = summary.get("counts") or {}
    readiness = summary.get("readiness") or {}
    lines = [
        "# Real Module Graph Summary",
        "",
        f"Milestone: `{summary.get('milestone')}`",
        f"Package: `{summary.get('package')}`",
        f"Source: `{summary.get('source_path')}`",
        f"Start node: `{summary.get('start_node')}`",
        "",
        "## Counts",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key in ["nodes", "edges", "branching_nodes", "linear_nodes", "dead_end_nodes", "gates", "assertions", "outputs", "unmatched_handlers"]:
        lines.append(f"| {key} | {counts.get(key, 0)} |")
    lines.extend([
        "",
        "## Branching nodes",
        "",
    ])
    branching = [n for n in summary.get("nodes", []) if n.get("outgoing_edge_count", 0) > 1]
    if branching:
        lines.extend(["| Node | Answer type | Branch answers |", "|---|---|---|"])
        for node in branching:
            answers = ", ".join(str(a) for a in node.get("branch_answers", []))
            lines.append(f"| `{node.get('id')}` | `{node.get('answer_type')}` | {answers} |")
    else:
        lines.append("No branching nodes detected.")
    lines.extend([
        "",
        "## Terminal / gate targets",
        "",
    ])
    terminals = summary.get("terminal_targets") or []
    if terminals:
        lines.extend(["| From | Answer | To | Target type |", "|---|---|---|---|"])
        for t in terminals:
            lines.append(f"| `{t.get('from')}` | `{t.get('answer')}` | `{t.get('to')}` | `{t.get('target_type')}` |")
    else:
        lines.append("No terminal/gate targets detected from node answers.")
    unresolved = summary.get("unresolved_targets") or []
    lines.extend(["", "## Readiness", ""])
    lines.append(f"Graph summary ready: `{readiness.get('graph_summary_ready')}`")
    lines.append(f"Path enumeration ready: `{readiness.get('path_enumeration_ready')}`")
    lines.append(f"Testcase generation ready: `{readiness.get('testcase_generation_ready')}`")
    if unresolved:
        lines.extend(["", "## Unresolved targets", "", "| From | Answer | To |", "|---|---|---|"])
        for u in unresolved:
            lines.append(f"| `{u.get('from')}` | `{u.get('answer')}` | `{u.get('to')}` |")
    lines.append("")
    return "\n".join(lines)


def write_real_module_graph_summary(source_path: str | Path, out_dir: str | Path, *, force: bool = False) -> dict[str, Any]:
    out = Path(out_dir)
    if out.exists() and any(out.iterdir()) and not force:
        raise FileExistsError(f"Output directory is not empty: {out}. Use --force to overwrite generated summary files.")
    out.mkdir(parents=True, exist_ok=True)
    summary = summarize_real_module_source(source_path)
    summary_path = out / "REAL_MODULE_GRAPH_SUMMARY.json"
    summary_md_path = out / "REAL_MODULE_GRAPH_SUMMARY.md"
    validation_path = out / "VALIDATION_REPORT.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    summary_md_path.write_text(render_graph_summary_markdown(summary), encoding="utf-8")
    validation = {
        "schema_version": VALIDATION_SCHEMA_VERSION,
        "milestone": "M60.7.2",
        "status": "passed" if (summary.get("readiness") or {}).get("graph_summary_ready") else "blocked",
        "checks": [
            {"check": "source_yaml_loaded", "status": "passed"},
            {"check": "nodes_present", "status": "passed" if (summary.get("counts") or {}).get("nodes", 0) > 0 else "blocked"},
            {"check": "duplicate_node_ids_absent", "status": "passed" if not summary.get("duplicate_node_ids") else "blocked"},
            {"check": "unresolved_targets_absent", "status": "passed" if not summary.get("unresolved_targets") else "blocked"},
            {"check": "compiled_artifacts_not_read", "status": "passed"},
            {"check": "testcase_generation_not_claimed", "status": "passed"},
        ],
        "blockers": [] if (summary.get("readiness") or {}).get("graph_summary_ready") else [
            "Graph summary is not ready; inspect duplicate_node_ids or unresolved_targets."
        ],
        "outputs": [
            "REAL_MODULE_GRAPH_SUMMARY.json",
            "REAL_MODULE_GRAPH_SUMMARY.md",
            "VALIDATION_REPORT.json",
        ],
    }
    validation_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "status": validation["status"],
        "out_dir": str(out),
        "summary": str(summary_path),
        "markdown": str(summary_md_path),
        "validation_report": str(validation_path),
        "counts": summary.get("counts"),
        "readiness": summary.get("readiness"),
    }



def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON artifact must be an object: {path}")
    return data


def _node_by_id(summary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(node.get("id")): node for node in summary.get("nodes", []) if isinstance(node, dict) and node.get("id")}


def _output_ids_allowed_after(summary: dict[str, Any], target: str | None, target_type: str | None) -> list[str]:
    outputs = summary.get("outputs") or []
    if target_type == "output" and target:
        return [str(target)]
    if target_type != "gate" or not target:
        return []
    allowed: list[str] = []
    for output in outputs:
        if not isinstance(output, dict):
            continue
        allowed_after = [str(item) for item in output.get("allowed_after") or []]
        if str(target) in allowed_after:
            allowed.append(str(output.get("id")))
    return sorted(allowed)


def enumerate_terminal_paths_from_summary(summary: dict[str, Any], *, max_depth: int = 100) -> dict[str, Any]:
    """Enumerate terminal decision paths from a real-module graph summary.

    This is still testcase-generation analysis, not runtime execution. It uses the
    M60.7.1 graph summary artifact and does not read compiled runtime outputs.
    """
    start = summary.get("start_node")
    node_index = _node_by_id(summary)
    graph_contract = summary.get("graph_contract") or {}
    terminal_node_ids = set(graph_contract.get("terminal_node_ids", []) or [])
    terminal_node_ids.update(
        node_id for node_id, node in node_index.items() if node.get("terminal") is True
    )
    allowed_cycle_regions = [
        set(region.get("nodes", []) or [])
        for region in graph_contract.get("allowed_cycle_regions", []) or []
        if isinstance(region, dict)
    ]
    edges = [edge for edge in summary.get("edges", []) if isinstance(edge, dict)]
    adjacency: dict[str, list[dict[str, Any]]] = {}
    for edge in edges:
        adjacency.setdefault(str(edge.get("from")), []).append(edge)
    for outgoing in adjacency.values():
        outgoing.sort(key=lambda e: (str(e.get("answer")), str(e.get("to"))))

    terminal_paths: list[dict[str, Any]] = []
    cycle_edges: list[dict[str, Any]] = []
    intentional_loop_edges: list[dict[str, Any]] = []
    dead_end_paths: list[dict[str, Any]] = []

    def is_allowed_cycle_edge(source_id: str, target_id: str, visited_nodes: set[str]) -> bool:
        return any(
            source_id in region and target_id in region and target_id in visited_nodes
            for region in allowed_cycle_regions
        )

    def build_record(path_edges: list[dict[str, Any]], node_sequence: list[str], terminal_target: Any, terminal_type: Any) -> dict[str, Any]:
        updates: list[str] = []
        for e in path_edges:
            for key in e.get("state_updates") or []:
                if key not in updates:
                    updates.append(str(key))
        encountered_unmatched = [node_id for node_id in node_sequence if (node_index.get(node_id) or {}).get("has_unmatched_handler")]
        answers = [
            {
                "node": e.get("from"),
                "answer": e.get("answer"),
                "to": e.get("to"),
                "target_type": e.get("target_type"),
                "edge_type": e.get("edge_type"),
            }
            for e in path_edges
        ]
        signature_parts = [f"{e.get('from')}={e.get('answer')}" for e in path_edges]
        signature_parts.append(str(terminal_target))
        return {
            "path_id": f"TP_{len(terminal_paths)+1:03d}",
            "start_node": start,
            "node_sequence": node_sequence,
            "answer_sequence": answers,
            "branch_signature": " -> ".join(signature_parts),
            "terminal_target": terminal_target,
            "terminal_type": terminal_type,
            "state_updates": updates,
            "encountered_unmatched_handlers": encountered_unmatched,
            "outputs_allowed_after_terminal": _output_ids_allowed_after(summary, terminal_target, terminal_type),
            "clean_path_case_ready": bool(path_edges) and terminal_type in {"gate", "output", "terminal", "node_terminal"},
            "testcase_generation_ready": False,
        }

    def dfs(node_id: str, path_edges: list[dict[str, Any]], node_sequence: list[str], visited: set[str]) -> None:
        if len(path_edges) > max_depth:
            cycle_edges.append({"from": node_id, "reason": "max_depth_exceeded", "max_depth": max_depth})
            return
        if node_id in terminal_node_ids:
            terminal_paths.append(build_record(path_edges, node_sequence, node_id, "node_terminal"))
            return
        outgoing = adjacency.get(node_id) or []
        if not outgoing:
            dead_end_paths.append({"node_sequence": node_sequence, "reason": "node_has_no_outgoing_edges", "node": node_id})
            return
        for edge in outgoing:
            target = edge.get("to")
            target_type = edge.get("target_type")
            next_edges = path_edges + [edge]
            if target_type == "node":
                target_id = str(target)
                if target_id in visited:
                    if is_allowed_cycle_edge(str(edge.get("from")), target_id, visited):
                        intentional_loop_edges.append({
                            "from": edge.get("from"),
                            "answer": edge.get("answer"),
                            "to": target,
                            "reason": "declared_intentional_cycle_pruned",
                        })
                    else:
                        cycle_edges.append({"from": edge.get("from"), "answer": edge.get("answer"), "to": target, "reason": "cycle_detected"})
                    continue
                if target_id in terminal_node_ids:
                    terminal_paths.append(build_record(next_edges, node_sequence + [target_id], target_id, "node_terminal"))
                else:
                    dfs(target_id, next_edges, node_sequence + [target_id], visited | {target_id})
            elif target_type in {"gate", "output", "terminal"}:
                terminal_paths.append(build_record(next_edges, node_sequence, target, target_type))
            else:
                dead_end_paths.append({
                    "node_sequence": node_sequence,
                    "from": edge.get("from"),
                    "answer": edge.get("answer"),
                    "to": target,
                    "target_type": target_type,
                    "reason": "non_terminal_unusable_target",
                })

    if start and str(start) in node_index:
        if graph_contract:
            # A graph contract explicitly models review/backtrack loops. For
            # testcase authoring, enumerate one canonical shortest route to
            # each reachable terminal edge/outcome instead of every simple
            # path through a cyclic review region (which is combinatorial).
            from collections import deque

            queue = deque([(str(start), [], [str(start)])])
            best_depth: dict[str, int] = {str(start): 0}
            selected_tree_edges: set[tuple[str, str, str]] = set()
            while queue:
                node_id, path_edges, node_sequence = queue.popleft()
                if node_id in terminal_node_ids:
                    terminal_paths.append(build_record(path_edges, node_sequence, node_id, "node_terminal"))
                    continue
                outgoing = adjacency.get(node_id) or []
                if not outgoing:
                    dead_end_paths.append({"node_sequence": node_sequence, "reason": "node_has_no_outgoing_edges", "node": node_id})
                    continue
                for edge in outgoing:
                    target = edge.get("to")
                    target_type = edge.get("target_type")
                    next_edges = path_edges + [edge]
                    if target_type == "node":
                        target_id = str(target)
                        edge_key = (node_id, str(edge.get("answer")), target_id)
                        if target_id in terminal_node_ids:
                            terminal_paths.append(build_record(next_edges, node_sequence + [target_id], target_id, "node_terminal"))
                            continue
                        next_depth = len(next_edges)
                        previous_depth = best_depth.get(target_id)
                        if previous_depth is None or next_depth < previous_depth:
                            best_depth[target_id] = next_depth
                            selected_tree_edges.add(edge_key)
                            queue.append((target_id, next_edges, node_sequence + [target_id]))
                        elif any(node_id in region and target_id in region for region in allowed_cycle_regions):
                            intentional_loop_edges.append({
                                "from": node_id,
                                "answer": edge.get("answer"),
                                "to": target_id,
                                "reason": "declared_intentional_cycle_noncanonical_route_pruned",
                            })
                        elif target_id in best_depth:
                            # A repeated non-loop route is a noncanonical
                            # alternate path, not a terminal-path blocker.
                            intentional_loop_edges.append({
                                "from": node_id,
                                "answer": edge.get("answer"),
                                "to": target_id,
                                "reason": "alternate_noncanonical_route_pruned",
                            })
                    elif target_type in {"gate", "output", "terminal"}:
                        terminal_paths.append(build_record(next_edges, node_sequence, target, target_type))
                    else:
                        dead_end_paths.append({
                            "node_sequence": node_sequence,
                            "from": edge.get("from"),
                            "answer": edge.get("answer"),
                            "to": target,
                            "target_type": target_type,
                            "reason": "non_terminal_unusable_target",
                        })
        else:
            dfs(str(start), [], [str(start)], {str(start)})

    # Stable deduplication is required because a terminal node can be observed
    # both as an explicit target and when dequeued.
    unique_terminal_paths: list[dict[str, Any]] = []
    seen_terminal_signatures: set[str] = set()
    for item in terminal_paths:
        signature = str(item.get("branch_signature"))
        if signature in seen_terminal_signatures:
            continue
        seen_terminal_signatures.add(signature)
        item["path_id"] = f"TP_{len(unique_terminal_paths)+1:03d}"
        unique_terminal_paths.append(item)
    terminal_paths = unique_terminal_paths

    readiness = {
        "terminal_path_enumeration_ready": bool(terminal_paths) and not cycle_edges and not dead_end_paths and not summary.get("unresolved_targets"),
        "clean_path_case_generation_ready": bool(terminal_paths) and not cycle_edges and not dead_end_paths and not summary.get("unresolved_targets"),
        "noise_case_generation_ready": False,
        "testcase_generation_ready": False,
        "reason": "M60.7.2 enumerates terminal paths and clean-path readiness metadata only; testcase/noise generation remains future work.",
    }
    return {
        "schema_version": PATHS_SCHEMA_VERSION,
        "milestone": "M60.7.2",
        "source_graph_schema_version": summary.get("schema_version"),
        "package": summary.get("package"),
        "source_path": summary.get("source_path"),
        "start_node": start,
        "counts": {
            "terminal_paths": len(terminal_paths),
            "cycle_edges": len(cycle_edges),
            "intentional_loop_edges_pruned": len(intentional_loop_edges),
            "dead_end_paths": len(dead_end_paths),
            "outputs_referenced": len({out for p in terminal_paths for out in p.get("outputs_allowed_after_terminal", [])}),
        },
        "terminal_paths": terminal_paths,
        "cycle_edges": cycle_edges,
        "intentional_loop_edges": intentional_loop_edges,
        "dead_end_paths": dead_end_paths,
        "readiness": readiness,
    }


def render_terminal_paths_markdown(paths: dict[str, Any]) -> str:
    counts = paths.get("counts") or {}
    readiness = paths.get("readiness") or {}
    lines = [
        "# Real Module Terminal Paths",
        "",
        f"Milestone: `{paths.get('milestone')}`",
        f"Package: `{paths.get('package')}`",
        f"Source: `{paths.get('source_path')}`",
        f"Start node: `{paths.get('start_node')}`",
        "",
        "## Counts",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| terminal_paths | {counts.get('terminal_paths', 0)} |",
        f"| outputs_referenced | {counts.get('outputs_referenced', 0)} |",
        f"| cycle_edges | {counts.get('cycle_edges', 0)} |",
        f"| dead_end_paths | {counts.get('dead_end_paths', 0)} |",
        "",
        "## Terminal paths",
        "",
    ]
    terminal_paths = paths.get("terminal_paths") or []
    if terminal_paths:
        lines.extend(["| Path | Branch signature | Terminal | Outputs |", "|---|---|---|---|"])
        for item in terminal_paths:
            outputs = ", ".join(f"`{o}`" for o in item.get("outputs_allowed_after_terminal", [])) or "—"
            lines.append(
                f"| `{item.get('path_id')}` | `{item.get('branch_signature')}` | `{item.get('terminal_target')}` / `{item.get('terminal_type')}` | {outputs} |"
            )
    else:
        lines.append("No terminal paths were enumerated.")
    lines.extend([
        "",
        "## Readiness",
        "",
        f"Terminal path enumeration ready: `{readiness.get('terminal_path_enumeration_ready')}`",
        f"Clean path case generation ready: `{readiness.get('clean_path_case_generation_ready')}`",
        f"Noise case generation ready: `{readiness.get('noise_case_generation_ready')}`",
        f"Testcase generation ready: `{readiness.get('testcase_generation_ready')}`",
        "",
    ])
    if paths.get("cycle_edges"):
        lines.extend(["## Cycle edges", "", "| From | Answer | To | Reason |", "|---|---|---|---|"])
        for c in paths.get("cycle_edges") or []:
            lines.append(f"| `{c.get('from')}` | `{c.get('answer')}` | `{c.get('to')}` | `{c.get('reason')}` |")
        lines.append("")
    if paths.get("dead_end_paths"):
        lines.extend(["## Dead-end paths", "", "| Node sequence / from | Target | Reason |", "|---|---|---|"])
        for d in paths.get("dead_end_paths") or []:
            seq = " -> ".join(d.get("node_sequence") or [str(d.get("from"))])
            lines.append(f"| `{seq}` | `{d.get('to')}` | `{d.get('reason')}` |")
        lines.append("")
    return "\n".join(lines)


def write_real_module_terminal_paths(summary_path: str | Path, out_dir: str | Path, *, force: bool = False) -> dict[str, Any]:
    out = Path(out_dir)
    if out.exists() and any(out.iterdir()) and not force:
        raise FileExistsError(f"Output directory is not empty: {out}. Use --force to overwrite generated terminal path files.")
    out.mkdir(parents=True, exist_ok=True)
    summary = _read_json(Path(summary_path))
    paths = enumerate_terminal_paths_from_summary(summary)
    paths_path = out / "REAL_MODULE_TERMINAL_PATHS.json"
    paths_md_path = out / "REAL_MODULE_TERMINAL_PATHS.md"
    validation_path = out / "VALIDATION_REPORT.json"
    paths_path.write_text(json.dumps(paths, ensure_ascii=False, indent=2), encoding="utf-8")
    paths_md_path.write_text(render_terminal_paths_markdown(paths), encoding="utf-8")
    ready = (paths.get("readiness") or {}).get("terminal_path_enumeration_ready")
    validation = {
        "schema_version": PATH_VALIDATION_SCHEMA_VERSION,
        "milestone": "M60.7.2",
        "status": "passed" if ready else "blocked",
        "checks": [
            {"check": "graph_summary_loaded", "status": "passed"},
            {"check": "terminal_paths_present", "status": "passed" if paths.get("terminal_paths") else "blocked"},
            {"check": "cycle_edges_absent", "status": "passed" if not paths.get("cycle_edges") else "blocked"},
            {"check": "dead_end_paths_absent", "status": "passed" if not paths.get("dead_end_paths") else "blocked"},
            {"check": "declared_intentional_loops_pruned", "status": "passed"},
            {"check": "unresolved_targets_absent", "status": "passed" if not summary.get("unresolved_targets") else "blocked"},
            {"check": "compiled_artifacts_not_read", "status": "passed"},
            {"check": "noise_generation_not_claimed", "status": "passed"},
            {"check": "testcase_generation_not_claimed", "status": "passed"},
        ],
        "blockers": [] if ready else [
            "Terminal path enumeration is not ready; inspect missing terminal_paths, cycle_edges, or unresolved graph targets."
        ],
        "outputs": [
            "REAL_MODULE_TERMINAL_PATHS.json",
            "REAL_MODULE_TERMINAL_PATHS.md",
            "VALIDATION_REPORT.json",
        ],
    }
    validation_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "status": validation["status"],
        "out_dir": str(out),
        "terminal_paths": str(paths_path),
        "markdown": str(paths_md_path),
        "validation_report": str(validation_path),
        "counts": paths.get("counts"),
        "readiness": paths.get("readiness"),
    }


def _clean_answer_value(step: dict[str, Any]) -> str:
    answer = step.get("answer")
    node_id = str(step.get("node") or "UNKNOWN_NODE")
    if answer == "*" or answer is None:
        return f"sample_answer_for_{node_id}"
    return str(answer)


def _case_filename(case_id: str, suffix: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in case_id)
    return f"{safe}{suffix}"


def generate_clean_path_cases_from_terminal_paths(paths: dict[str, Any]) -> dict[str, Any]:
    """Generate clean-path testcase artifacts from M60.7.2 terminal paths.

    This is source-level companion test authoring. It does not run the Ordo
    runtime, does not read compiled/*, and does not add noise patterns. Each
    generated case represents the shortest deterministic answer sequence that
    follows one enumerated terminal path.
    """
    terminal_paths = [p for p in paths.get("terminal_paths", []) if isinstance(p, dict)]
    cases: list[dict[str, Any]] = []
    for index, path in enumerate(terminal_paths, start=1):
        case_id = f"CLEAN_{path.get('path_id') or f'TP_{index:03d}'}"
        answer_steps = []
        for step_index, step in enumerate(path.get("answer_sequence") or [], start=1):
            if not isinstance(step, dict):
                continue
            answer_steps.append({
                "step": step_index,
                "node": step.get("node"),
                "answer": _clean_answer_value(step),
                "source_answer": step.get("answer"),
                "to": step.get("to"),
                "target_type": step.get("target_type"),
                "edge_type": step.get("edge_type"),
                "noise": "none",
            })
        cases.append({
            "schema_version": "ordo.pathwalk.real_module_clean_path_case.v1",
            "milestone": "M60.7.3",
            "case_id": case_id,
            "case_type": "clean_path",
            "noise_pattern": "none",
            "path_id": path.get("path_id"),
            "package": paths.get("package"),
            "source_path": paths.get("source_path"),
            "branch_signature": path.get("branch_signature"),
            "start_node": path.get("start_node") or paths.get("start_node"),
            "node_sequence": path.get("node_sequence") or [],
            "answer_steps": answer_steps,
            "expected_terminal": {
                "target": path.get("terminal_target"),
                "type": path.get("terminal_type"),
            },
            "expected_outputs": path.get("outputs_allowed_after_terminal") or [],
            "expected_state_updates": path.get("state_updates") or [],
            "encountered_unmatched_handlers": path.get("encountered_unmatched_handlers") or [],
            "readiness": {
                "case_artifact_ready": bool(answer_steps) and bool(path.get("clean_path_case_ready")),
                "runtime_execution_ready": False,
                "noise_generation_ready": False,
                "reason": "M60.7.3 emits clean-path testcase artifacts only; runtime execution and noise variants remain future milestones.",
            },
        })

    ready_cases = [c for c in cases if (c.get("readiness") or {}).get("case_artifact_ready")]
    readiness = {
        "clean_path_cases_ready": bool(cases) and len(ready_cases) == len(cases) and bool((paths.get("readiness") or {}).get("clean_path_case_generation_ready")),
        "runtime_execution_ready": False,
        "noise_case_generation_ready": False,
        "reason": "Clean path testcase artifacts were generated from terminal paths; no runtime execution or noise generation is claimed.",
    }
    return {
        "schema_version": CLEAN_CASES_SCHEMA_VERSION,
        "milestone": "M60.7.3",
        "source_terminal_paths_schema_version": paths.get("schema_version"),
        "package": paths.get("package"),
        "source_path": paths.get("source_path"),
        "start_node": paths.get("start_node"),
        "counts": {
            "clean_path_cases": len(cases),
            "ready_cases": len(ready_cases),
            "terminal_paths_input": len(terminal_paths),
            "noise_patterns": 0,
        },
        "cases": cases,
        "readiness": readiness,
    }


def render_clean_path_case_markdown(case: dict[str, Any]) -> str:
    lines = [
        f"# Clean Path Testcase — {case.get('case_id')}",
        "",
        f"Milestone: `{case.get('milestone')}`",
        f"Package: `{case.get('package')}`",
        f"Path: `{case.get('path_id')}`",
        f"Noise pattern: `{case.get('noise_pattern')}`",
        f"Branch signature: `{case.get('branch_signature')}`",
        "",
        "## Answer steps",
        "",
    ]
    steps = case.get("answer_steps") or []
    if steps:
        lines.extend(["| Step | Node | Answer | To |", "|---:|---|---|---|"])
        for step in steps:
            lines.append(f"| {step.get('step')} | `{step.get('node')}` | `{step.get('answer')}` | `{step.get('to')}` / `{step.get('target_type')}` |")
    else:
        lines.append("No answer steps generated.")
    expected_terminal = case.get("expected_terminal") or {}
    outputs = ", ".join(f"`{o}`" for o in case.get("expected_outputs") or []) or "—"
    updates = ", ".join(f"`{u}`" for u in case.get("expected_state_updates") or []) or "—"
    readiness = case.get("readiness") or {}
    lines.extend([
        "",
        "## Expected outcome",
        "",
        f"Terminal: `{expected_terminal.get('target')}` / `{expected_terminal.get('type')}`",
        f"Expected outputs: {outputs}",
        f"Expected state updates: {updates}",
        "",
        "## Readiness",
        "",
        f"Case artifact ready: `{readiness.get('case_artifact_ready')}`",
        f"Runtime execution ready: `{readiness.get('runtime_execution_ready')}`",
        f"Noise generation ready: `{readiness.get('noise_generation_ready')}`",
        "",
    ])
    return "\n".join(lines)


def render_clean_path_cases_summary_markdown(summary: dict[str, Any]) -> str:
    counts = summary.get("counts") or {}
    readiness = summary.get("readiness") or {}
    lines = [
        "# Real Module Clean Path Testcases",
        "",
        f"Milestone: `{summary.get('milestone')}`",
        f"Package: `{summary.get('package')}`",
        f"Source: `{summary.get('source_path')}`",
        f"Start node: `{summary.get('start_node')}`",
        "",
        "## Counts",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| clean_path_cases | {counts.get('clean_path_cases', 0)} |",
        f"| ready_cases | {counts.get('ready_cases', 0)} |",
        f"| terminal_paths_input | {counts.get('terminal_paths_input', 0)} |",
        f"| noise_patterns | {counts.get('noise_patterns', 0)} |",
        "",
        "## Cases",
        "",
    ]
    cases = summary.get("cases") or []
    if cases:
        lines.extend(["| Case | Path | Terminal | Outputs | Ready |", "|---|---|---|---|---|"])
        for case in cases:
            terminal = case.get("expected_terminal") or {}
            outputs = ", ".join(f"`{o}`" for o in case.get("expected_outputs") or []) or "—"
            ready = (case.get("readiness") or {}).get("case_artifact_ready")
            lines.append(f"| `{case.get('case_id')}` | `{case.get('path_id')}` | `{terminal.get('target')}` / `{terminal.get('type')}` | {outputs} | `{ready}` |")
    else:
        lines.append("No clean path cases generated.")
    lines.extend([
        "",
        "## Readiness",
        "",
        f"Clean path cases ready: `{readiness.get('clean_path_cases_ready')}`",
        f"Runtime execution ready: `{readiness.get('runtime_execution_ready')}`",
        f"Noise case generation ready: `{readiness.get('noise_case_generation_ready')}`",
        "",
    ])
    return "\n".join(lines)


def _csv_cell(value: Any) -> str:
    text = "" if value is None else str(value)
    if any(ch in text for ch in [",", "\"", "\n"]):
        text = '"' + text.replace('"', '""') + '"'
    return text


def render_clean_path_matrix_csv(summary: dict[str, Any]) -> str:
    columns = [
        "case_id",
        "path_id",
        "noise_pattern",
        "terminal_target",
        "terminal_type",
        "expected_outputs",
        "answer_step_count",
        "node_count",
        "state_update_count",
        "case_artifact_ready",
    ]
    rows = [",".join(columns)]
    for case in summary.get("cases") or []:
        terminal = case.get("expected_terminal") or {}
        row = [
            case.get("case_id"),
            case.get("path_id"),
            case.get("noise_pattern"),
            terminal.get("target"),
            terminal.get("type"),
            ";".join(str(o) for o in case.get("expected_outputs") or []),
            len(case.get("answer_steps") or []),
            len(case.get("node_sequence") or []),
            len(case.get("expected_state_updates") or []),
            (case.get("readiness") or {}).get("case_artifact_ready"),
        ]
        rows.append(",".join(_csv_cell(v) for v in row))
    return "\n".join(rows) + "\n"


def write_real_module_clean_path_cases(paths_path: str | Path, out_dir: str | Path, *, force: bool = False) -> dict[str, Any]:
    out = Path(out_dir)
    if out.exists() and any(out.iterdir()) and not force:
        raise FileExistsError(f"Output directory is not empty: {out}. Use --force to overwrite generated clean testcase files.")
    out.mkdir(parents=True, exist_ok=True)
    paths = _read_json(Path(paths_path))
    summary = generate_clean_path_cases_from_terminal_paths(paths)
    cases_dir = out / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)

    for case in summary.get("cases") or []:
        case_id = str(case.get("case_id"))
        (cases_dir / _case_filename(case_id, ".json")).write_text(json.dumps(case, ensure_ascii=False, indent=2), encoding="utf-8")
        (cases_dir / _case_filename(case_id, ".md")).write_text(render_clean_path_case_markdown(case), encoding="utf-8")

    summary_path = out / "SUMMARY.json"
    summary_md_path = out / "SUMMARY.md"
    matrix_path = out / "RAW_TESTCASE_MATRIX.csv"
    validation_path = out / "VALIDATION_REPORT.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    summary_md_path.write_text(render_clean_path_cases_summary_markdown(summary), encoding="utf-8")
    matrix_path.write_text(render_clean_path_matrix_csv(summary), encoding="utf-8")

    ready = (summary.get("readiness") or {}).get("clean_path_cases_ready")
    validation = {
        "schema_version": CLEAN_CASE_VALIDATION_SCHEMA_VERSION,
        "milestone": "M60.7.3",
        "status": "passed" if ready else "blocked",
        "checks": [
            {"check": "terminal_paths_loaded", "status": "passed"},
            {"check": "clean_cases_present", "status": "passed" if summary.get("cases") else "blocked"},
            {"check": "one_case_per_terminal_path", "status": "passed" if (summary.get("counts") or {}).get("clean_path_cases") == (summary.get("counts") or {}).get("terminal_paths_input") else "blocked"},
            {"check": "raw_testcase_matrix_written", "status": "passed"},
            {"check": "compiled_artifacts_not_read", "status": "passed"},
            {"check": "runtime_execution_not_claimed", "status": "passed"},
            {"check": "noise_generation_not_claimed", "status": "passed"},
        ],
        "blockers": [] if ready else [
            "Clean path testcase artifact generation is not ready; inspect terminal paths readiness and case_artifact_ready flags."
        ],
        "outputs": [
            "cases/*.json",
            "cases/*.md",
            "RAW_TESTCASE_MATRIX.csv",
            "SUMMARY.json",
            "SUMMARY.md",
            "VALIDATION_REPORT.json",
        ],
    }
    validation_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "status": validation["status"],
        "out_dir": str(out),
        "cases_dir": str(cases_dir),
        "summary": str(summary_path),
        "markdown": str(summary_md_path),
        "matrix": str(matrix_path),
        "validation_report": str(validation_path),
        "counts": summary.get("counts"),
        "readiness": summary.get("readiness"),
    }



SUPPORTED_NOISE_PATTERNS = ("distraction", "invalid_branch", "clarification_without_submit", "skip_ahead")


def _normalize_noise_patterns(patterns: list[str] | tuple[str, ...] | None = None) -> list[str]:
    if patterns is None:
        return list(SUPPORTED_NOISE_PATTERNS)
    normalized: list[str] = []
    for item in patterns:
        value = str(item).strip()
        if value not in SUPPORTED_NOISE_PATTERNS:
            raise ValueError(f"Unsupported real-module noise pattern: {value}. Supported: {', '.join(SUPPORTED_NOISE_PATTERNS)}")
        if value not in normalized:
            normalized.append(value)
    if not normalized:
        raise ValueError("At least one noise pattern is required")
    return normalized


def _noise_case_id(path_id: str, pattern: str) -> str:
    suffix = {
        "distraction": "DISTRACTION",
        "invalid_branch": "INVALID_BRANCH",
        "clarification_without_submit": "CLARIFICATION_WITHOUT_SUBMIT",
        "skip_ahead": "SKIP_AHEAD",
    }[pattern]
    return f"NOISE_{path_id}_{suffix}"


def _distraction_steps(answer_steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not answer_steps:
        return []
    first = answer_steps[0]
    return [
        {
            "step": 0,
            "node": first.get("node"),
            "input_kind": "distraction",
            "answer": "Before answering, the user asks an unrelated side question.",
            "expected_behavior": "acknowledge_or_ignore_distraction_and_return_to_current_node",
            "submit_expected": False,
        }
    ] + [dict(step, step=int(step.get("step", 0)) + 1) for step in answer_steps]


def _invalid_branch_steps(answer_steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not answer_steps:
        return []
    first = answer_steps[0]
    return [
        {
            "step": 0,
            "node": first.get("node"),
            "input_kind": "invalid_branch",
            "answer": "__INVALID_BRANCH_SENTINEL__",
            "expected_behavior": "reject_invalid_branch_without_advancing_current_node",
            "submit_expected": False,
        }
    ] + [dict(step, step=int(step.get("step", 0)) + 1) for step in answer_steps]


def _clarification_without_submit_steps(answer_steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not answer_steps:
        return []
    first = answer_steps[0]
    return [
        {
            "step": 0,
            "node": first.get("node"),
            "input_kind": "clarification_without_submit",
            "answer": "The user asks for clarification before giving an answer.",
            "expected_behavior": "answer_or_acknowledge_clarification_without_submitting_or_advancing",
            "submit_expected": False,
        }
    ] + [dict(step, step=int(step.get("step", 0)) + 1) for step in answer_steps]


def _skip_ahead_steps(answer_steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not answer_steps:
        return []
    first = answer_steps[0]
    future_answer = answer_steps[1].get("answer") if len(answer_steps) > 1 else "__SKIP_AHEAD_SENTINEL__"
    return [
        {
            "step": 0,
            "node": first.get("node"),
            "input_kind": "skip_ahead",
            "answer": future_answer,
            "expected_behavior": "do_not_skip_required_current_node_or_advance_out_of_order",
            "submit_expected": False,
        }
    ] + [dict(step, step=int(step.get("step", 0)) + 1) for step in answer_steps]


def _noise_steps(pattern: str, answer_steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if pattern == "distraction":
        return _distraction_steps(answer_steps)
    if pattern == "invalid_branch":
        return _invalid_branch_steps(answer_steps)
    if pattern == "clarification_without_submit":
        return _clarification_without_submit_steps(answer_steps)
    if pattern == "skip_ahead":
        return _skip_ahead_steps(answer_steps)
    raise ValueError(f"Unsupported real-module noise pattern: {pattern}")


def generate_noise_cases_from_terminal_paths(paths: dict[str, Any], *, patterns: list[str] | tuple[str, ...] | None = None) -> dict[str, Any]:
    """Generate first-noise testcase artifacts from M60.7.2 terminal paths.

    M60.7.5 intentionally emits artifact-only noise cases. It does not execute
    runtime, score model behavior, or claim calibration readiness.
    """
    selected_patterns = _normalize_noise_patterns(patterns)
    terminal_paths = [p for p in paths.get("terminal_paths") or [] if isinstance(p, dict)]
    cases: list[dict[str, Any]] = []

    for path in terminal_paths:
        clean_steps = [
            {
                "step": int(index),
                "node": step.get("node"),
                "answer": _clean_answer_value(step),
                "to": step.get("to"),
                "target_type": step.get("target_type"),
                "edge_type": step.get("edge_type"),
                "input_kind": "clean_answer",
                "submit_expected": True,
            }
            for index, step in enumerate(path.get("answer_sequence") or [], start=1)
        ]
        for pattern in selected_patterns:
            case_id = _noise_case_id(str(path.get("path_id")), pattern)
            scripted_steps = _noise_steps(pattern, clean_steps)
            cases.append({
                "schema_version": "ordo.pathwalk.real_module_noise_case.v1",
                "milestone": "M60.7.5",
                "case_id": case_id,
                "case_type": "noise_path",
                "noise_pattern": pattern,
                "package": paths.get("package"),
                "source_path": paths.get("source_path"),
                "path_id": path.get("path_id"),
                "branch_signature": path.get("branch_signature"),
                "node_sequence": path.get("node_sequence") or [],
                "scripted_steps": scripted_steps,
                "clean_answer_steps": clean_steps,
                "expected_terminal": {
                    "target": path.get("terminal_target"),
                    "type": path.get("terminal_type"),
                },
                "expected_outputs": path.get("outputs_allowed_after_terminal") or [],
                "expected_state_updates": path.get("state_updates") or [],
                "expected_noise_handling": {
                    "distraction": "do_not_advance_until_valid_answer" if pattern == "distraction" else None,
                    "invalid_branch": "reject_invalid_branch_and_keep_current_node" if pattern == "invalid_branch" else None,
                    "clarification_without_submit": "do_not_submit_or_advance_until_actual_answer" if pattern == "clarification_without_submit" else None,
                    "skip_ahead": "reject_or_ignore_out_of_order_answer_and_keep_current_node" if pattern == "skip_ahead" else None,
                },
                "readiness": {
                    "case_artifact_ready": bool(scripted_steps) and bool(path.get("clean_path_case_ready")),
                    "runtime_execution_ready": False,
                    "scoring_ready": False,
                    "calibration_ready": False,
                    "reason": "M60.7.5 emits bounded noise testcase artifacts only; no runtime execution, scoring, or calibration is claimed.",
                },
            })

    ready_cases = [c for c in cases if (c.get("readiness") or {}).get("case_artifact_ready")]
    terminal_path_count = len(terminal_paths)
    expected_count = terminal_path_count * len(selected_patterns)
    readiness = {
        "noise_cases_ready": bool(cases) and len(cases) == expected_count and len(ready_cases) == len(cases),
        "runtime_execution_ready": False,
        "scoring_ready": False,
        "calibration_ready": False,
        "reason": "Noise testcase artifacts were generated from terminal paths. Runtime execution remains explicitly out of scope.",
    }
    pattern_counts = {pattern: len([c for c in cases if c.get("noise_pattern") == pattern]) for pattern in selected_patterns}
    return {
        "schema_version": NOISE_CASES_SCHEMA_VERSION,
        "milestone": "M60.7.5",
        "source_terminal_paths_schema_version": paths.get("schema_version"),
        "package": paths.get("package"),
        "source_path": paths.get("source_path"),
        "start_node": paths.get("start_node"),
        "patterns": selected_patterns,
        "pattern_counts": pattern_counts,
        "counts": {
            "noise_cases": len(cases),
            "ready_cases": len(ready_cases),
            "terminal_paths_input": terminal_path_count,
            "patterns": len(selected_patterns),
            "clean_path_cases_included": 0,
        },
        "cases": cases,
        "readiness": readiness,
    }


def render_noise_case_markdown(case: dict[str, Any]) -> str:
    lines = [
        f"# Noise Testcase — {case.get('case_id')}",
        "",
        f"Milestone: `{case.get('milestone')}`",
        f"Package: `{case.get('package')}`",
        f"Path: `{case.get('path_id')}`",
        f"Noise pattern: `{case.get('noise_pattern')}`",
        f"Branch signature: `{case.get('branch_signature')}`",
        "",
        "## Scripted steps",
        "",
    ]
    steps = case.get("scripted_steps") or []
    if steps:
        lines.extend(["| Step | Node | Input kind | Answer | Expected behavior | Submit expected |", "|---:|---|---|---|---|---|"])
        for step in steps:
            lines.append(
                f"| {step.get('step')} | `{step.get('node')}` | `{step.get('input_kind')}` | `{step.get('answer')}` | `{step.get('expected_behavior', '')}` | `{step.get('submit_expected')}` |"
            )
    else:
        lines.append("No scripted steps generated.")
    expected_terminal = case.get("expected_terminal") or {}
    outputs = ", ".join(f"`{o}`" for o in case.get("expected_outputs") or []) or "—"
    readiness = case.get("readiness") or {}
    lines.extend([
        "",
        "## Expected outcome",
        "",
        f"Terminal after recovery: `{expected_terminal.get('target')}` / `{expected_terminal.get('type')}`",
        f"Expected outputs: {outputs}",
        "",
        "## Readiness",
        "",
        f"Case artifact ready: `{readiness.get('case_artifact_ready')}`",
        f"Runtime execution ready: `{readiness.get('runtime_execution_ready')}`",
        f"Scoring ready: `{readiness.get('scoring_ready')}`",
        f"Calibration ready: `{readiness.get('calibration_ready')}`",
        "",
    ])
    return "\n".join(lines)


def render_noise_cases_summary_markdown(summary: dict[str, Any]) -> str:
    counts = summary.get("counts") or {}
    readiness = summary.get("readiness") or {}
    lines = [
        "# Real Module Noise Testcases",
        "",
        f"Milestone: `{summary.get('milestone')}`",
        f"Package: `{summary.get('package')}`",
        f"Source: `{summary.get('source_path')}`",
        f"Start node: `{summary.get('start_node')}`",
        f"Patterns: `{', '.join(summary.get('patterns') or [])}`",
        "",
        "## Counts",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| noise_cases | {counts.get('noise_cases', 0)} |",
        f"| ready_cases | {counts.get('ready_cases', 0)} |",
        f"| terminal_paths_input | {counts.get('terminal_paths_input', 0)} |",
        f"| patterns | {counts.get('patterns', 0)} |",
        "",
        "## Pattern counts",
        "",
        "| Pattern | Cases |",
        "|---|---:|",
    ]
    for pattern, count in (summary.get("pattern_counts") or {}).items():
        lines.append(f"| `{pattern}` | {count} |")
    lines.extend(["", "## Cases", ""])
    cases = summary.get("cases") or []
    if cases:
        lines.extend(["| Case | Pattern | Path | Terminal | Ready |", "|---|---|---|---|---|"])
        for case in cases:
            terminal = case.get("expected_terminal") or {}
            ready = (case.get("readiness") or {}).get("case_artifact_ready")
            lines.append(f"| `{case.get('case_id')}` | `{case.get('noise_pattern')}` | `{case.get('path_id')}` | `{terminal.get('target')}` / `{terminal.get('type')}` | `{ready}` |")
    else:
        lines.append("No noise cases generated.")
    lines.extend([
        "",
        "## Readiness",
        "",
        f"Noise cases ready: `{readiness.get('noise_cases_ready')}`",
        f"Runtime execution ready: `{readiness.get('runtime_execution_ready')}`",
        f"Scoring ready: `{readiness.get('scoring_ready')}`",
        f"Calibration ready: `{readiness.get('calibration_ready')}`",
        "",
    ])
    return "\n".join(lines)


def render_noise_matrix_csv(summary: dict[str, Any]) -> str:
    columns = [
        "case_id",
        "path_id",
        "noise_pattern",
        "terminal_target",
        "terminal_type",
        "expected_outputs",
        "scripted_step_count",
        "clean_answer_step_count",
        "case_artifact_ready",
        "runtime_execution_ready",
        "scoring_ready",
        "calibration_ready",
    ]
    rows = [",".join(columns)]
    for case in summary.get("cases") or []:
        terminal = case.get("expected_terminal") or {}
        readiness = case.get("readiness") or {}
        row = [
            case.get("case_id"),
            case.get("path_id"),
            case.get("noise_pattern"),
            terminal.get("target"),
            terminal.get("type"),
            ";".join(str(o) for o in case.get("expected_outputs") or []),
            len(case.get("scripted_steps") or []),
            len(case.get("clean_answer_steps") or []),
            readiness.get("case_artifact_ready"),
            readiness.get("runtime_execution_ready"),
            readiness.get("scoring_ready"),
            readiness.get("calibration_ready"),
        ]
        rows.append(",".join(_csv_cell(v) for v in row))
    return "\n".join(rows) + "\n"


def write_real_module_noise_cases(paths_path: str | Path, out_dir: str | Path, *, patterns: list[str] | tuple[str, ...] | None = None, force: bool = False) -> dict[str, Any]:
    out = Path(out_dir)
    if out.exists() and any(out.iterdir()) and not force:
        raise FileExistsError(f"Output directory is not empty: {out}. Use --force to overwrite generated noise testcase files.")
    out.mkdir(parents=True, exist_ok=True)
    paths = _read_json(Path(paths_path))
    summary = generate_noise_cases_from_terminal_paths(paths, patterns=patterns)
    cases_dir = out / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)

    for case in summary.get("cases") or []:
        case_id = str(case.get("case_id"))
        (cases_dir / _case_filename(case_id, ".json")).write_text(json.dumps(case, ensure_ascii=False, indent=2), encoding="utf-8")
        (cases_dir / _case_filename(case_id, ".md")).write_text(render_noise_case_markdown(case), encoding="utf-8")

    summary_path = out / "SUMMARY.json"
    summary_md_path = out / "SUMMARY.md"
    matrix_path = out / "RAW_NOISE_TESTCASE_MATRIX.csv"
    validation_path = out / "VALIDATION_REPORT.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    summary_md_path.write_text(render_noise_cases_summary_markdown(summary), encoding="utf-8")
    matrix_path.write_text(render_noise_matrix_csv(summary), encoding="utf-8")

    ready = (summary.get("readiness") or {}).get("noise_cases_ready")
    expected_cases = (summary.get("counts") or {}).get("terminal_paths_input", 0) * (summary.get("counts") or {}).get("patterns", 0)
    validation = {
        "schema_version": NOISE_CASE_VALIDATION_SCHEMA_VERSION,
        "milestone": "M60.7.5",
        "status": "passed" if ready else "blocked",
        "checks": [
            {"check": "terminal_paths_loaded", "status": "passed"},
            {"check": "supported_noise_patterns_only", "status": "passed"},
            {"check": "noise_cases_present", "status": "passed" if summary.get("cases") else "blocked"},
            {"check": "one_case_per_terminal_path_per_pattern", "status": "passed" if (summary.get("counts") or {}).get("noise_cases") == expected_cases else "blocked"},
            {"check": "raw_noise_testcase_matrix_written", "status": "passed"},
            {"check": "compiled_artifacts_not_read", "status": "passed"},
            {"check": "runtime_execution_not_claimed", "status": "passed"},
            {"check": "scoring_not_claimed", "status": "passed"},
            {"check": "calibration_not_claimed", "status": "passed"},
        ],
        "blockers": [] if ready else [
            "Noise testcase artifact generation is not ready; inspect terminal paths readiness and case_artifact_ready flags."
        ],
        "outputs": [
            "cases/*.json",
            "cases/*.md",
            "RAW_NOISE_TESTCASE_MATRIX.csv",
            "SUMMARY.json",
            "SUMMARY.md",
            "VALIDATION_REPORT.json",
        ],
    }
    validation_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "status": validation["status"],
        "out_dir": str(out),
        "cases_dir": str(cases_dir),
        "summary": str(summary_path),
        "markdown": str(summary_md_path),
        "matrix": str(matrix_path),
        "validation_report": str(validation_path),
        "counts": summary.get("counts"),
        "readiness": summary.get("readiness"),
    }


REVIEW_CARDS_SCHEMA_VERSION = "ordo.pathwalk.real_module_review_cards.v1"
REVIEW_CARD_VALIDATION_SCHEMA_VERSION = "ordo.pathwalk.real_module_review_cards_validation.v1"


def _review_steps_from_case(case: dict[str, Any]) -> list[dict[str, Any]]:
    if case.get("case_type") == "clean_path":
        steps = case.get("answer_steps") or []
        return [
            {
                "step": step.get("step"),
                "node": step.get("node"),
                "input_kind": "clean_answer",
                "input": step.get("answer"),
                "expected_behavior": "accept_answer_and_advance_along_terminal_path",
                "submit_expected": True,
                "target": step.get("to"),
                "target_type": step.get("target_type"),
            }
            for step in steps if isinstance(step, dict)
        ]
    steps = case.get("scripted_steps") or []
    return [
        {
            "step": step.get("step"),
            "node": step.get("node"),
            "input_kind": step.get("input_kind"),
            "input": step.get("answer"),
            "expected_behavior": step.get("expected_behavior") or ("accept_answer_and_advance_along_terminal_path" if step.get("submit_expected") else "do_not_submit_or_advance"),
            "submit_expected": step.get("submit_expected"),
            "target": step.get("to"),
            "target_type": step.get("target_type"),
        }
        for step in steps if isinstance(step, dict)
    ]


def _case_review_focus(case: dict[str, Any]) -> list[str]:
    pattern = case.get("noise_pattern")
    if pattern in {None, "none"}:
        return [
            "Follow the expected path without extra detours.",
            "Reach the expected terminal target.",
            "Expose any expected output only after its allowed terminal/gate.",
        ]
    focus = [
        "Do not advance on steps where submit_expected is false.",
        "Recover to the current required node after the noisy turn.",
        "Complete the same terminal path after recovery.",
    ]
    if pattern == "distraction":
        focus.insert(0, "Handle an unrelated side question without losing path state.")
    elif pattern == "invalid_branch":
        focus.insert(0, "Reject an invalid branch answer without mutating path state.")
    elif pattern == "clarification_without_submit":
        focus.insert(0, "Answer or acknowledge clarification without submitting a node answer.")
    elif pattern == "skip_ahead":
        focus.insert(0, "Do not accept a future-step answer before the current node is complete.")
    return focus


def generate_review_cards_from_case_summaries(case_summaries: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate human-review scenario cards from clean/noise testcase summaries.

    This is a QA/developer reading layer. It intentionally does not execute
    cases, score behavior, invoke a model/API, or read compiled runtime outputs.
    """
    cards: list[dict[str, Any]] = []
    source_summaries: list[dict[str, Any]] = []
    for summary_index, summary in enumerate(case_summaries, start=1):
        if not isinstance(summary, dict):
            continue
        cases = [case for case in summary.get("cases") or [] if isinstance(case, dict)]
        source_summaries.append({
            "schema_version": summary.get("schema_version"),
            "milestone": summary.get("milestone"),
            "package": summary.get("package"),
            "source_path": summary.get("source_path"),
            "case_count": len(cases),
        })
        for case in cases:
            terminal = case.get("expected_terminal") or {}
            steps = _review_steps_from_case(case)
            non_submit_steps = [step for step in steps if step.get("submit_expected") is False]
            card_id = f"CARD_{len(cards)+1:03d}_{case.get('case_id')}"
            card = {
                "schema_version": "ordo.pathwalk.real_module_review_card.v1",
                "milestone": "M61.0",
                "card_id": card_id,
                "case_id": case.get("case_id"),
                "case_type": case.get("case_type"),
                "noise_pattern": case.get("noise_pattern"),
                "path_id": case.get("path_id"),
                "package": case.get("package") or summary.get("package"),
                "source_path": case.get("source_path") or summary.get("source_path"),
                "branch_signature": case.get("branch_signature"),
                "review_goal": "Human QA/developer review of expected model behavior for a generated real-module testcase.",
                "review_focus": _case_review_focus(case),
                "scripted_steps": steps,
                "expected_terminal": {
                    "target": terminal.get("target"),
                    "type": terminal.get("type"),
                },
                "expected_outputs": case.get("expected_outputs") or [],
                "expected_state_updates": case.get("expected_state_updates") or [],
                "checklist": [
                    {"item": "Current-node state remains coherent through the card.", "required": True},
                    {"item": "No step with submit_expected=false advances the path.", "required": bool(non_submit_steps)},
                    {"item": "Expected terminal target is reached after all valid submits.", "required": True},
                    {"item": "No runtime execution, model scoring, or calibration is implied by this card.", "required": True},
                ],
                "readiness": {
                    "review_card_ready": bool(steps),
                    "runtime_execution_ready": False,
                    "scoring_ready": False,
                    "calibration_ready": False,
                    "reason": "M61.0 emits human-review cards only; runtime execution, scoring, and calibration remain future milestones.",
                },
            }
            cards.append(card)

    cards_ready = [card for card in cards if (card.get("readiness") or {}).get("review_card_ready")]
    pattern_counts: dict[str, int] = {}
    type_counts: dict[str, int] = {}
    for card in cards:
        pattern = str(card.get("noise_pattern") or "none")
        case_type = str(card.get("case_type") or "unknown")
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        type_counts[case_type] = type_counts.get(case_type, 0) + 1

    return {
        "schema_version": REVIEW_CARDS_SCHEMA_VERSION,
        "milestone": "M61.0",
        "source_summaries": source_summaries,
        "counts": {
            "review_cards": len(cards),
            "ready_cards": len(cards_ready),
            "source_summaries": len(source_summaries),
            "runtime_executions": 0,
            "scores": 0,
        },
        "case_type_counts": type_counts,
        "noise_pattern_counts": pattern_counts,
        "cards": cards,
        "readiness": {
            "review_cards_ready": bool(cards) and len(cards_ready) == len(cards),
            "runtime_execution_ready": False,
            "scoring_ready": False,
            "calibration_ready": False,
            "reason": "Human review cards are ready for QA/developer reading. They are not executable benchmark results.",
        },
    }


def render_review_card_markdown(card: dict[str, Any]) -> str:
    expected_terminal = card.get("expected_terminal") or {}
    readiness = card.get("readiness") or {}
    outputs = ", ".join(f"`{item}`" for item in card.get("expected_outputs") or []) or "—"
    updates = ", ".join(f"`{item}`" for item in card.get("expected_state_updates") or []) or "—"
    lines = [
        f"# Human Review Scenario Card — {card.get('card_id')}",
        "",
        f"Milestone: `{card.get('milestone')}`",
        f"Case: `{card.get('case_id')}`",
        f"Case type: `{card.get('case_type')}`",
        f"Noise pattern: `{card.get('noise_pattern')}`",
        f"Package: `{card.get('package')}`",
        f"Path: `{card.get('path_id')}`",
        "",
        "## Review goal",
        "",
        str(card.get("review_goal") or "Review expected behavior for this generated testcase."),
        "",
        "## Review focus",
        "",
    ]
    for item in card.get("review_focus") or []:
        lines.append(f"- {item}")
    lines.extend(["", "## Scripted steps", ""])
    steps = card.get("scripted_steps") or []
    if steps:
        lines.extend(["| Step | Node | Input kind | Input | Expected behavior | Submit expected |", "|---:|---|---|---|---|---|"])
        for step in steps:
            lines.append(
                f"| {step.get('step')} | `{step.get('node')}` | `{step.get('input_kind')}` | `{step.get('input')}` | {step.get('expected_behavior')} | `{step.get('submit_expected')}` |"
            )
    else:
        lines.append("No scripted steps available.")
    lines.extend([
        "",
        "## Expected outcome",
        "",
        f"Terminal: `{expected_terminal.get('target')}` / `{expected_terminal.get('type')}`",
        f"Expected outputs: {outputs}",
        f"Expected state updates: {updates}",
        "",
        "## Review checklist",
        "",
    ])
    for item in card.get("checklist") or []:
        required = "required" if item.get("required") else "optional/contextual"
        lines.append(f"- [{required}] {item.get('item')}")
    lines.extend([
        "",
        "## Readiness",
        "",
        f"Review card ready: `{readiness.get('review_card_ready')}`",
        f"Runtime execution ready: `{readiness.get('runtime_execution_ready')}`",
        f"Scoring ready: `{readiness.get('scoring_ready')}`",
        f"Calibration ready: `{readiness.get('calibration_ready')}`",
        "",
    ])
    return "\n".join(lines)


def render_review_cards_summary_markdown(summary: dict[str, Any]) -> str:
    counts = summary.get("counts") or {}
    readiness = summary.get("readiness") or {}
    lines = [
        "# Human Review Scenario Cards",
        "",
        f"Milestone: `{summary.get('milestone')}`",
        "",
        "## Counts",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| review_cards | {counts.get('review_cards', 0)} |",
        f"| ready_cards | {counts.get('ready_cards', 0)} |",
        f"| source_summaries | {counts.get('source_summaries', 0)} |",
        f"| runtime_executions | {counts.get('runtime_executions', 0)} |",
        f"| scores | {counts.get('scores', 0)} |",
        "",
        "## Noise pattern counts",
        "",
        "| Pattern | Cards |",
        "|---|---:|",
    ]
    for pattern, count in (summary.get("noise_pattern_counts") or {}).items():
        lines.append(f"| `{pattern}` | {count} |")
    lines.extend(["", "## Cards", ""])
    cards = summary.get("cards") or []
    if cards:
        lines.extend(["| Card | Case | Type | Pattern | Terminal | Ready |", "|---|---|---|---|---|---|"])
        for card in cards:
            terminal = card.get("expected_terminal") or {}
            ready = (card.get("readiness") or {}).get("review_card_ready")
            lines.append(
                f"| [`{card.get('card_id')}`](cards/{_case_filename(str(card.get('card_id')), '.md')}) | `{card.get('case_id')}` | `{card.get('case_type')}` | `{card.get('noise_pattern')}` | `{terminal.get('target')}` / `{terminal.get('type')}` | `{ready}` |"
            )
    else:
        lines.append("No review cards generated.")
    lines.extend([
        "",
        "## Readiness",
        "",
        f"Review cards ready: `{readiness.get('review_cards_ready')}`",
        f"Runtime execution ready: `{readiness.get('runtime_execution_ready')}`",
        f"Scoring ready: `{readiness.get('scoring_ready')}`",
        f"Calibration ready: `{readiness.get('calibration_ready')}`",
        "",
    ])
    return "\n".join(lines)


def render_review_cards_matrix_csv(summary: dict[str, Any]) -> str:
    columns = [
        "card_id",
        "case_id",
        "case_type",
        "noise_pattern",
        "path_id",
        "terminal_target",
        "terminal_type",
        "scripted_step_count",
        "expected_outputs",
        "review_card_ready",
        "runtime_execution_ready",
        "scoring_ready",
        "calibration_ready",
    ]
    rows = [",".join(columns)]
    for card in summary.get("cards") or []:
        terminal = card.get("expected_terminal") or {}
        readiness = card.get("readiness") or {}
        row = [
            card.get("card_id"),
            card.get("case_id"),
            card.get("case_type"),
            card.get("noise_pattern"),
            card.get("path_id"),
            terminal.get("target"),
            terminal.get("type"),
            len(card.get("scripted_steps") or []),
            ";".join(str(o) for o in card.get("expected_outputs") or []),
            readiness.get("review_card_ready"),
            readiness.get("runtime_execution_ready"),
            readiness.get("scoring_ready"),
            readiness.get("calibration_ready"),
        ]
        rows.append(",".join(_csv_cell(v) for v in row))
    return "\n".join(rows) + "\n"


def write_real_module_review_cards(summary_paths: list[str | Path] | tuple[str | Path, ...], out_dir: str | Path, *, force: bool = False) -> dict[str, Any]:
    out = Path(out_dir)
    if out.exists() and any(out.iterdir()) and not force:
        raise FileExistsError(f"Output directory is not empty: {out}. Use --force to overwrite generated review card files.")
    out.mkdir(parents=True, exist_ok=True)
    if not summary_paths:
        raise ValueError("At least one clean/noise testcase SUMMARY.json path is required")
    summaries = [_read_json(Path(path)) for path in summary_paths]
    summary = generate_review_cards_from_case_summaries(summaries)
    cards_dir = out / "cards"
    cards_dir.mkdir(parents=True, exist_ok=True)

    for card in summary.get("cards") or []:
        card_id = str(card.get("card_id"))
        (cards_dir / _case_filename(card_id, ".json")).write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")
        (cards_dir / _case_filename(card_id, ".md")).write_text(render_review_card_markdown(card), encoding="utf-8")

    summary_path = out / "REVIEW_CARDS.json"
    index_path = out / "REVIEW_CARDS.md"
    matrix_path = out / "RAW_REVIEW_CARD_MATRIX.csv"
    validation_path = out / "VALIDATION_REPORT.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    index_path.write_text(render_review_cards_summary_markdown(summary), encoding="utf-8")
    matrix_path.write_text(render_review_cards_matrix_csv(summary), encoding="utf-8")

    ready = (summary.get("readiness") or {}).get("review_cards_ready")
    validation = {
        "schema_version": REVIEW_CARD_VALIDATION_SCHEMA_VERSION,
        "milestone": "M61.0",
        "status": "passed" if ready else "blocked",
        "checks": [
            {"check": "case_summaries_loaded", "status": "passed"},
            {"check": "review_cards_present", "status": "passed" if summary.get("cards") else "blocked"},
            {"check": "one_card_per_input_case", "status": "passed" if (summary.get("counts") or {}).get("review_cards") == sum(item.get("case_count", 0) for item in summary.get("source_summaries") or []) else "blocked"},
            {"check": "review_card_matrix_written", "status": "passed"},
            {"check": "runtime_execution_not_claimed", "status": "passed"},
            {"check": "scoring_not_claimed", "status": "passed"},
            {"check": "calibration_not_claimed", "status": "passed"},
            {"check": "compiled_artifacts_not_read", "status": "passed"},
        ],
        "blockers": [] if ready else [
            "Human review cards are not ready; inspect missing input cases or review_card_ready flags."
        ],
        "outputs": [
            "cards/*.json",
            "cards/*.md",
            "REVIEW_CARDS.json",
            "REVIEW_CARDS.md",
            "RAW_REVIEW_CARD_MATRIX.csv",
            "VALIDATION_REPORT.json",
        ],
    }
    validation_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "status": validation["status"],
        "out_dir": str(out),
        "cards_dir": str(cards_dir),
        "review_cards": str(summary_path),
        "markdown": str(index_path),
        "matrix": str(matrix_path),
        "validation_report": str(validation_path),
        "counts": summary.get("counts"),
        "readiness": summary.get("readiness"),
    }
