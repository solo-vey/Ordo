#!/usr/bin/env python3
"""
Ordo Visual Graph Generator

Standalone utility that reads an Ordo YAML/IR module and generates a workflow /
decision-tree graph.

Supported output formats:
- mmd
- svg
- png

The utility does not execute Ordo, call LLM, call MCP, or mutate source YAML.
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
import tempfile
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping


try:
    import yaml
except ImportError:
    yaml = None


ID_RE = re.compile(r"[^a-zA-Z0-9_]")


@dataclass
class Finding:
    level: str
    code: str
    location: str
    message: str

    def render(self) -> str:
        return f"[{self.level.upper()}] {self.code} at {self.location}: {self.message}"


@dataclass
class Edge:
    source: str
    target: str
    label: str | None = None
    kind: str = "normal"


@dataclass
class GNode:
    id: str
    type: str
    label: str
    raw: Any
    synthetic: bool = False


@dataclass
class Graph:
    title: str
    nodes: dict[str, GNode] = field(default_factory=dict)
    order: list[str] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    entry: str | None = None

    @property
    def has_errors(self) -> bool:
        return any(f.level == "error" for f in self.findings)


def safe_id(raw: str) -> str:
    s = ID_RE.sub("_", str(raw)).strip("_")
    if not s:
        s = "node"
    if s[0].isdigit():
        s = "n_" + s
    return s


def load_yaml(path: Path) -> Mapping[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required. Install: pip install pyyaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return {}
    if not isinstance(data, Mapping):
        raise ValueError("Top-level YAML must be a mapping/object.")
    return data


def get_title(data: Mapping[str, Any], input_path: Path) -> str:
    agent = data.get("agent")
    if isinstance(agent, Mapping) and agent.get("name"):
        return str(agent["name"])
    intent = data.get("intent")
    if isinstance(intent, Mapping) and intent.get("id"):
        return str(intent["id"])
    ordo = data.get("ordo")
    if isinstance(ordo, Mapping) and ordo.get("package"):
        return str(ordo["package"])
    return input_path.stem


def first_question_line(text: Any, limit: int = 76) -> str:
    if not isinstance(text, str):
        return ""
    for line in text.strip().splitlines():
        line = line.strip()
        if line:
            return line[:limit] + ("…" if len(line) > limit else "")
    return ""


def target_to_node_id(target: str) -> str:
    if target.startswith(("STOP_", "ERROR_", "REPAIR_")):
        return "terminal_" + safe_id(target)
    if target.startswith(("error:", "repair:", "terminal:")):
        return "terminal_" + safe_id(target.replace(":", "_"))
    return safe_id(target)


def add_node_once(g: Graph, node: GNode) -> str:
    if node.id not in g.nodes:
        g.nodes[node.id] = node
        g.order.append(node.id)
    return node.id


def add_synthetic_terminal(g: Graph, target: str) -> str:
    tid = target_to_node_id(target)
    if tid in g.nodes:
        return tid

    if target.startswith("error:") or target.startswith("ERROR_"):
        label, typ = target.replace("error:", "ERROR\n"), "error"
    elif target.startswith("repair:") or target.startswith("REPAIR_"):
        label, typ = target.replace("repair:", "REPAIR\n"), "repair"
    elif target.startswith("STOP_"):
        label, typ = "Terminal\n" + target[5:].replace("_", " ").title(), "terminal"
    elif target.startswith("terminal:"):
        label, typ = target.replace("terminal:", "TERMINAL\n"), "terminal"
    else:
        label, typ = target, "terminal"

    return add_node_once(g, GNode(tid, typ, label, {}, True))


def options_from_question_text(question: Any) -> dict[str, str]:
    """Extract answer option labels from a question body.

    Supported examples:
      A — text
      B - text
      1. text
      2) text
      3 — text
    """
    if not isinstance(question, str):
        return {}

    result: dict[str, str] = {}

    for raw_line in question.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        patterns = (
            r"^([A-Za-zА-Яа-яІіЇїЄєҐґ])\s*[—–-]\s*(.+)$",
            r"^([0-9]+)\s*[\.\)]\s*(.+)$",
            r"^([0-9]+)\s*[—–-]\s*(.+)$",
        )

        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                if key and value and key not in result:
                    result[key] = value
                break

    return result


def option_label(node: Mapping[str, Any], answer_key: str, branch_spec: Any) -> str:
    # 1. Explicit branch-level label wins.
    if isinstance(branch_spec, Mapping):
        for key in ("label", "title", "text", "description"):
            if branch_spec.get(key):
                return f"{answer_key} — {branch_spec[key]}"

    # 2. Structured answer options.
    answer_options = node.get("answer_options") or node.get("options")
    if isinstance(answer_options, Mapping) and answer_options.get(answer_key):
        return f"{answer_key} — {answer_options[answer_key]}"
    if isinstance(answer_options, list):
        for item in answer_options:
            if isinstance(item, Mapping) and str(item.get("id")) == str(answer_key):
                text = item.get("label") or item.get("text") or item.get("title")
                if text:
                    return f"{answer_key} — {text}"

    # 3. Legacy fallback: options embedded in question text.
    from_question = options_from_question_text(node.get("question"))
    if from_question.get(answer_key):
        return f"{answer_key} — {from_question[answer_key]}"

    # 4. update_state route labels / semantic labels.
    if isinstance(branch_spec, Mapping):
        update_state = branch_spec.get("update_state")
        if isinstance(update_state, Mapping):
            preferred_keys = (
                "selected_path_label",
                "test_coverage_level",
                "coverage_level",
                "strategy_label",
                "path_label",
                "route_label",
                "decision_label",
                "choice_label",
                "label",
                "title",
                "description",
            )
            for key in preferred_keys:
                if update_state.get(key):
                    return f"{answer_key} — {update_state[key]}"

            for key, value in update_state.items():
                if str(key).endswith("_label") and value:
                    return f"{answer_key} — {value}"

    # 5. Object-style allowed_answers.
    allowed = node.get("allowed_answers")
    if isinstance(allowed, list):
        for item in allowed:
            if isinstance(item, Mapping) and str(item.get("id")) == str(answer_key):
                text = item.get("label") or item.get("text") or item.get("title")
                if text:
                    return f"{answer_key} — {text}"

    # 6. Last fallback: raw key.
    return str(answer_key)


def transition_label_for_direct_answer(node: Mapping[str, Any], on_answer: Mapping[str, Any]) -> str | None:
    """Free-text direct transitions are unlabeled unless explicitly labeled."""
    for source in (on_answer, node):
        if not isinstance(source, Mapping):
            continue
        for key in ("transition_label", "edge_label", "label"):
            if source.get(key):
                return str(source[key])
    return None


def artifacts_from_question_text(question: Any) -> list[dict[str, str]]:
    """Compatibility fallback: extract artifact filenames from markdown-like bullets."""
    if not isinstance(question, str):
        return []

    artifacts: list[dict[str, str]] = []
    seen: set[str] = set()

    for line in question.splitlines():
        item = line.strip()
        if not item.startswith("-"):
            continue

        item = item.lstrip("-").strip()
        if not item:
            continue

        looks_like_artifact = (
            re.search(r"\.(md|json|yaml|yml|zip|archive)\b", item, re.IGNORECASE)
            or re.match(r"\d{2}_[A-Z0-9_<>-]+", item)
            or item.endswith("_PACKAGE")
        )
        if not looks_like_artifact:
            continue

        artifact_id = re.sub(r"[^a-zA-Z0-9_]+", "_", item).strip("_")
        if not artifact_id or artifact_id in seen:
            continue
        seen.add(artifact_id)

        ext_match = re.search(r"\.([a-zA-Z0-9]+)\b", item)
        artifact_type = f"{ext_match.group(1).lower()}_document" if ext_match else "artifact"
        artifacts.append({"id": artifact_id, "title": item, "type": artifact_type})

    return artifacts


def artifact_label(artifact: Any) -> tuple[str, str]:
    if isinstance(artifact, Mapping):
        raw_id = (
            artifact.get("id")
            or artifact.get("artifact_id")
            or artifact.get("name")
            or artifact.get("title")
            or artifact.get("path_pattern")
            or artifact.get("path")
            or "artifact"
        )
        title = (
            artifact.get("path_pattern")
            or artifact.get("path")
            or artifact.get("title")
            or artifact.get("name")
            or raw_id
        )
        kind = artifact.get("format") or artifact.get("type") or artifact.get("kind") or "artifact"
        return str(raw_id), f"Artifact\n{title}\n{kind}"

    raw = str(artifact)
    return raw, f"Artifact\n{raw}"


def output_label(output: Any) -> tuple[str, str]:
    if isinstance(output, Mapping):
        raw_id = output.get("id") or output.get("name") or output.get("title") or "output"
        typ = output.get("type") or output.get("kind") or "output"
        title = output.get("title") or output.get("name") or raw_id
        return str(raw_id), f"Package / Output\n{title}\n{typ}"

    raw = str(output)
    return raw, f"Package / Output\n{raw}"


def add_artifact_nodes(g: Graph, artifacts: Any, from_node: str | None = None, edge_label: str | None = None) -> list[str]:
    if artifacts is None:
        return []
    if isinstance(artifacts, (str, Mapping)):
        artifacts = [artifacts]
    if not isinstance(artifacts, list):
        return []

    result: list[str] = []
    for artifact in artifacts:
        raw_id, label = artifact_label(artifact)
        aid = "artifact_" + safe_id(raw_id)
        add_node_once(g, GNode(aid, "artifact", label, artifact, True))
        result.append(aid)
        if from_node:
            g.edges.append(Edge(from_node, aid, edge_label or "produces", "dashed"))

    return result


def add_output_nodes(g: Graph, outputs: Any, from_node: str | None = None, edge_label: str | None = None) -> list[str]:
    if outputs is None:
        return []
    if isinstance(outputs, (str, Mapping)):
        outputs = [outputs]
    if not isinstance(outputs, list):
        return []

    result: list[str] = []
    for output in outputs:
        raw_id, label = output_label(output)
        oid = "output_" + safe_id(raw_id)
        add_node_once(g, GNode(oid, "output", label, output, True))
        result.append(oid)
        if from_node:
            g.edges.append(Edge(from_node, oid, edge_label or "packages", "dashed"))
    return result


def collect_gate_ids(data: Mapping[str, Any]) -> set[str]:
    gate_ids: set[str] = set()
    gates = data.get("gates") or []
    if isinstance(gates, list):
        for gate in gates:
            if isinstance(gate, Mapping) and gate.get("id"):
                gate_ids.add(str(gate["id"]))
    return gate_ids


def register_gates(g: Graph, gate_ids: set[str]) -> None:
    for gate_id in sorted(gate_ids):
        node_id = safe_id(gate_id)
        add_node_once(g, GNode(node_id, "gate", f"{gate_id}\nGate", {}, True))


def resolve_target(g: Graph, target: str, location: str) -> str:
    tid = target_to_node_id(target)

    if tid in g.nodes:
        return tid
    if safe_id(target) in g.nodes:
        return safe_id(target)

    if target.startswith(("STOP_", "ERROR_", "REPAIR_", "error:", "repair:", "terminal:")):
        return add_synthetic_terminal(g, target)

    g.findings.append(Finding("error", "UNKNOWN_TARGET", location, f"Unknown target: {target}"))
    return tid


def parse_nodes(data: Mapping[str, Any], input_path: Path, artifact_mode: str) -> Graph:
    g = Graph(get_title(data, input_path))
    nodes = data.get("nodes") or []

    if not isinstance(nodes, list):
        g.findings.append(Finding("error", "INVALID_NODES", "nodes", "`nodes` must be a list."))
        return g
    if not nodes:
        g.findings.append(Finding("error", "MISSING_NODES", "nodes", "No nodes found."))
        return g

    gate_ids = collect_gate_ids(data)

    for index, node in enumerate(nodes):
        loc = f"nodes[{index}]"
        if not isinstance(node, Mapping):
            g.findings.append(Finding("error", "INVALID_NODE", loc, "Node must be an object."))
            continue

        sid = node.get("id")
        if not sid:
            g.findings.append(Finding("error", "MISSING_ID", loc, "Node has no id."))
            continue

        nid = safe_id(str(sid))
        if nid in g.nodes:
            g.findings.append(Finding("error", "DUPLICATE_ID", loc, f"Duplicate id: {sid}"))
            continue

        question = first_question_line(node.get("question")) or str(sid)
        add_node_once(g, GNode(nid, "question", f"{sid}\n{question}", node))

    register_gates(g, gate_ids)
    g.entry = safe_id(str(nodes[0].get("id"))) if nodes and isinstance(nodes[0], Mapping) and nodes[0].get("id") else (g.order[0] if g.order else None)

    for index, node in enumerate(nodes):
        if not isinstance(node, Mapping) or not node.get("id"):
            continue

        src = safe_id(str(node["id"]))
        on_answer = node.get("on_answer")

        if not isinstance(on_answer, Mapping):
            continue

        # Free-text/direct form: on_answer: {update_state: ..., next: ...}
        if "next" in on_answer and isinstance(on_answer.get("next"), str):
            target = str(on_answer["next"])
            tgt = resolve_target(g, target, f"nodes[{index}].on_answer.next")
            g.edges.append(Edge(src, tgt, transition_label_for_direct_answer(node, on_answer)))

            if artifact_mode in {"terminal", "all"}:
                artifacts = on_answer.get("artifacts") or on_answer.get("output_artifacts") or artifacts_from_question_text(node.get("question"))
                add_artifact_nodes(g, artifacts, tgt, "produces")

        # Enum form: on_answer: {A: {next: ...}, B: ...}
        for ans, spec in on_answer.items():
            if ans in {"update_state", "next", "artifacts", "output_artifacts"}:
                continue

            target = None
            artifacts = None
            if isinstance(spec, str):
                target = spec
            elif isinstance(spec, Mapping):
                target = spec.get("next")
                artifacts = spec.get("artifacts") or spec.get("output_artifacts")
                if artifacts is None:
                    artifacts = artifacts_from_question_text(node.get("question"))

            if not isinstance(target, str):
                g.findings.append(Finding("warning", "NO_BRANCH_NEXT", f"nodes[{index}].on_answer.{ans}", "No branch `next` target."))
                continue

            edge_label = option_label(node, str(ans), spec)
            tgt = resolve_target(g, target, f"nodes[{index}].on_answer.{ans}")
            g.edges.append(Edge(src, tgt, edge_label))

            if artifact_mode in {"terminal", "all"}:
                add_artifact_nodes(g, artifacts, tgt, "produces")

    # Canonical concrete artifacts. In terminal mode, keep them only if connected
    # by branch-level artifacts. In all mode, show all of them.
    if artifact_mode == "all":
        add_artifact_nodes(g, data.get("artifacts"))

    if artifact_mode in {"package", "all"}:
        output_ids = add_output_nodes(g, data.get("outputs"))
        artifact_ids = []
        if artifact_mode == "all":
            artifact_ids = add_artifact_nodes(g, data.get("artifacts"))
        for oid in output_ids:
            for aid in artifact_ids:
                g.edges.append(Edge(oid, aid, "contains", "dashed"))

    return g


def parse_steps(data: Mapping[str, Any], input_path: Path, artifact_mode: str) -> Graph:
    g = Graph(get_title(data, input_path))
    steps = data.get("steps") or []

    if not isinstance(steps, list):
        g.findings.append(Finding("error", "INVALID_STEPS", "steps", "`steps` must be a list."))
        return g
    if not steps:
        g.findings.append(Finding("error", "MISSING_STEPS", "steps", "No steps found."))
        return g

    gate_ids = collect_gate_ids(data)

    for index, step in enumerate(steps):
        loc = f"steps[{index}]"
        if not isinstance(step, Mapping):
            g.findings.append(Finding("error", "INVALID_STEP", loc, "Step must be an object."))
            continue

        sid = step.get("id")
        if not sid:
            g.findings.append(Finding("error", "MISSING_ID", loc, "Step has no id."))
            continue

        nid = safe_id(str(sid))
        if nid in g.nodes:
            g.findings.append(Finding("error", "DUPLICATE_ID", loc, f"Duplicate id: {sid}"))
            continue

        label = str(step.get("label") or step.get("name") or step.get("title") or sid)
        stype = str(step.get("type") or "step")
        add_node_once(g, GNode(nid, stype, f"{sid}\n{label}", step))

    register_gates(g, gate_ids)
    g.entry = safe_id(str(steps[0].get("id"))) if steps and isinstance(steps[0], Mapping) and steps[0].get("id") else (g.order[0] if g.order else None)

    for index, step in enumerate(steps):
        if not isinstance(step, Mapping) or not step.get("id"):
            continue

        src = safe_id(str(step["id"]))

        if isinstance(step.get("next"), str):
            target = str(step["next"])
            tgt = resolve_target(g, target, f"steps[{index}].next")
            g.edges.append(Edge(src, tgt))

        branches = step.get("branches")
        if isinstance(branches, Mapping):
            for branch, value in branches.items():
                target = value.get("next") if isinstance(value, Mapping) else value
                if not isinstance(target, str):
                    g.findings.append(Finding("error", "INVALID_BRANCH", f"steps[{index}].branches.{branch}", "Branch target must be string or object with next."))
                    continue

                label = str(value.get("label")) if isinstance(value, Mapping) and value.get("label") else str(branch)
                tgt = resolve_target(g, target, f"steps[{index}].branches.{branch}")
                g.edges.append(Edge(src, tgt, label))

                if artifact_mode in {"terminal", "all"} and isinstance(value, Mapping):
                    add_artifact_nodes(g, value.get("artifacts") or value.get("output_artifacts"), tgt, "produces")

    if artifact_mode == "all":
        add_artifact_nodes(g, data.get("artifacts"))

    if artifact_mode in {"package", "all"}:
        output_ids = add_output_nodes(g, data.get("outputs"))
        artifact_ids = []
        if artifact_mode == "all":
            artifact_ids = add_artifact_nodes(g, data.get("artifacts"))
        for oid in output_ids:
            for aid in artifact_ids:
                g.edges.append(Edge(oid, aid, "contains", "dashed"))

    return g


def build_graph(data: Mapping[str, Any], input_path: Path, artifact_mode: str) -> Graph:
    if isinstance(data.get("nodes"), list):
        return parse_nodes(data, input_path, artifact_mode)
    if isinstance(data.get("steps"), list):
        return parse_steps(data, input_path, artifact_mode)

    g = Graph(get_title(data, input_path))
    g.findings.append(Finding("error", "MISSING_WORKFLOW", "module", "Expected `steps:` or `nodes:` list."))
    return g


def adjacency(g: Graph) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {node_id: [] for node_id in g.nodes}
    for edge in g.edges:
        result.setdefault(edge.source, []).append(edge.target)
    return result


def descendants(g: Graph, start: str, depth: int | None = None) -> set[str]:
    adj = adjacency(g)
    seen = {start}
    queue = deque([(start, 0)])

    while queue:
        node, current_depth = queue.popleft()
        if depth is not None and current_depth >= depth:
            continue
        for nxt in adj.get(node, []):
            if nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, current_depth + 1))
    return seen


def shortest_path(g: Graph, source: str, target: str) -> list[str] | None:
    adj = adjacency(g)
    queue = deque([[source]])
    seen = {source}

    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == target:
            return path
        for nxt in adj.get(node, []):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(path + [nxt])

    return None


def focus_graph(g: Graph, start: str | None, focus: str | None, mode: str, depth: int | None) -> Graph:
    if start is None and focus is None:
        return g

    root = g.entry
    if root is None:
        return g

    start_id = safe_id(start) if start else None
    focus_id = safe_id(focus) if focus else None

    for raw, node_id, option_name in ((start, start_id, "--start"), (focus, focus_id, "--focus")):
        if raw is not None and node_id not in g.nodes:
            g.findings.append(Finding("error", "UNKNOWN_FOCUS_NODE", option_name, f"Node id not found: {raw}"))
            return g

    if mode == "subtree":
        anchor = start_id or focus_id or root
        selected = descendants(g, anchor, depth)
    elif mode == "path":
        anchor = focus_id or start_id or root
        path = shortest_path(g, root, anchor)
        if path is None:
            g.findings.append(Finding("error", "NO_PATH_TO_FOCUS", "--focus/--start", f"No path from entry to {anchor}."))
            return g
        selected = set(path)
    elif mode == "context":
        anchor = focus_id or start_id or root
        path = shortest_path(g, root, anchor)
        if path is None:
            g.findings.append(Finding("error", "NO_PATH_TO_FOCUS", "--focus/--start", f"No path from entry to {anchor}."))
            return g
        selected = set(path)
        selected |= descendants(g, anchor, depth)
    else:
        g.findings.append(Finding("error", "INVALID_MODE", "--mode", f"Unsupported focus mode: {mode}"))
        return g

    focused = Graph(title=f"{g.title} — {mode} view")
    focused.nodes = {node_id: node for node_id, node in g.nodes.items() if node_id in selected}
    focused.order = [node_id for node_id in g.order if node_id in selected]
    focused.edges = [edge for edge in g.edges if edge.source in selected and edge.target in selected]
    focused.findings = list(g.findings)

    if mode in {"context", "path"}:
        focused.entry = root if root in selected else (focused.order[0] if focused.order else None)
    else:
        focused.entry = (start_id or focus_id or root) if (start_id or focus_id or root) in selected else (focused.order[0] if focused.order else None)

    anchor = focus_id or start_id
    if anchor and anchor in focused.nodes:
        old = focused.nodes[anchor]
        focused.nodes[anchor] = GNode(old.id, old.type + "_focus", old.label, old.raw, old.synthetic)

    return focused


def write_mmd(g: Graph, out: Path) -> None:
    lines = ["flowchart TD", f"    %% Ordo Visual Graph Generator: {g.title}"]
    lines.append(f'    ENTRY["ENTRY\\n{html.escape(g.title)}"]')

    if g.entry:
        lines.append(f"    ENTRY --> {g.entry}")

    for node_id in g.order:
        node = g.nodes[node_id]
        label = html.escape(node.label).replace("\n", "\\n")
        lines.append(f'    {node_id}["{label}"]')

    for edge in g.edges:
        style = "-.->" if edge.kind == "dashed" else "-->"
        if edge.label:
            lines.append(f'    {edge.source} {style}|"{html.escape(edge.label)}"| {edge.target}')
        else:
            lines.append(f"    {edge.source} {style} {edge.target}")

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def q(s: str) -> str:
    value = str(s).replace("\\", "\\\\").replace('"', '\\"')
    value = value.replace("\n", "\\n")
    return '"' + value + '"'


def dot_attrs(node: GNode) -> tuple[str, str, str, str]:
    shape = "box"
    style = "rounded,filled"
    color = "#475569"

    if node.type.endswith("_focus"):
        return shape, "#FFF4D6", style + ",bold", "#B45309"
    if node.type == "artifact":
        return "folder", "#E8F8EC", style, color
    if node.type == "output":
        return "folder", "#E0F2FE", style, color
    if node.type == "gate":
        return shape, "#FFE3E3", style, color
    if node.type in {"terminal", "stop", "error", "repair"}:
        fill = "#FFF3BF" if node.type == "repair" else "#FFE2E2"
        return shape, fill, style, color

    return shape, "#F8FAFC", style, color


def write_dot(g: Graph, out: Path) -> None:
    lines = [
        "digraph OrdoWorkflow {",
        "  rankdir=TB;",
        f"  graph [fontname=\"Helvetica\", bgcolor=\"white\", label={q(g.title)}, labelloc=t, fontsize=22, pad=0.3, nodesep=0.55, ranksep=0.75];",
        "  node [fontname=\"Helvetica\", shape=box, style=\"rounded,filled\", color=\"#475569\", penwidth=1.2, margin=\"0.18,0.12\", fontsize=10];",
        "  edge [fontname=\"Helvetica\", color=\"#475569\", arrowsize=0.7, fontsize=9];",
        f"  ENTRY [label={q('ENTRY\n' + g.title)}, shape=box, fillcolor=\"#DCEBFF\", style=\"rounded,filled\"];",
    ]

    for node_id in g.order:
        node = g.nodes[node_id]
        shape, fill, style, color = dot_attrs(node)
        lines.append(
            f"  {node_id} [label={q(node.label)}, shape={shape}, fillcolor={q(fill)}, "
            f"style={q(style)}, color={q(color)}];"
        )

    if g.entry:
        lines.append(f"  ENTRY -> {g.entry};")

    for edge in g.edges:
        attrs = []
        if edge.label:
            attrs.append(f"label={q(edge.label)}")
        if edge.kind == "dashed":
            attrs.append("style=dashed")
        attr = " [" + ", ".join(attrs) + "]" if attrs else ""
        lines.append(f"  {edge.source} -> {edge.target}{attr};")

    lines.append("}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_dot(g: Graph, out: Path, fmt: str) -> None:
    dot = shutil.which("dot")
    if not dot:
        raise RuntimeError("Graphviz `dot` is required for PNG/SVG rendering.")

    with tempfile.TemporaryDirectory() as tmpdir:
        dot_path = Path(tmpdir) / "graph.dot"
        write_dot(g, dot_path)
        proc = subprocess.run([dot, f"-T{fmt}", str(dot_path), "-o", str(out)], capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr or proc.stdout or f"dot failed with code {proc.returncode}")


def print_validation(g: Graph) -> None:
    if not g.findings:
        print("Validation passed: no structural issues found.")
        return

    print("Validation report:")
    for finding in g.findings:
        print("-", finding.render())

    errors = sum(1 for finding in g.findings if finding.level == "error")
    warnings = sum(1 for finding in g.findings if finding.level == "warning")
    print(f"Summary: {errors} error(s), {warnings} warning(s).")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ordo_graph.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Generate a Mermaid/SVG/PNG graph from an Ordo YAML/IR workflow.",
        epilog="""Examples:
  Full tree as SVG:
    python ordo_graph.py input.ordo.yaml --format svg --out graph.svg

  Context view: direct path from root to N3, then N3 subtree:
    python ordo_graph.py input.ordo.yaml --focus N3_EVENT_IDENTITY_CONTRACT --mode context --format svg --out context.svg

  Subtree from a selected node:
    python ordo_graph.py input.ordo.yaml --start N2_SOURCE_CONTRACT --format svg --out subtree.svg

  Path only:
    python ordo_graph.py input.ordo.yaml --focus N3_EVENT_IDENTITY_CONTRACT --mode path --format svg --out path.svg

  Show package/archive outputs:
    python ordo_graph.py input.ordo.yaml --artifact-mode package --format svg --out packages.svg

Focus modes:
  subtree  Render selected node and everything reachable after it.
  context  Render direct path from root to selected node, then selected node subtree.
  path     Render only direct path from root to selected node.

Artifact modes:
  none      Do not render artifacts/outputs.
  terminal  Render branch-level and extracted terminal artifacts. Default.
  package   Render top-level outputs[] as package/archive containers.
  all       Render terminal artifacts, canonical artifacts[], and package outputs.

Defaults:
  If --start/--focus are not provided, the full tree is rendered from the root.
  If --format is omitted, format is inferred from --out extension.
""",
    )
    parser.add_argument("input", help="Path to Ordo YAML/IR module.")
    parser.add_argument("--out", default="graph.mmd", help="Output file path. Default: graph.mmd")
    parser.add_argument("--format", choices=["mmd", "svg", "png"], default=None, help="Output format. Defaults to --out extension.")
    parser.add_argument("--start", help="Render subtree starting from this node id.")
    parser.add_argument("--focus", help="Focus on a node. Usually used with --mode context or --mode path.")
    parser.add_argument("--mode", choices=["subtree", "context", "path"], default="subtree", help="Partial rendering mode. Default: subtree.")
    parser.add_argument("--depth", type=int, default=None, help="Optional descendant depth limit for subtree/context modes.")
    parser.add_argument("--artifact-mode", choices=["none", "terminal", "package", "all"], default="terminal", help="Artifact rendering mode. Default: terminal.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    out_path = Path(args.out)
    fmt = args.format or out_path.suffix.lstrip(".").lower() or "mmd"

    try:
        if args.depth is not None and args.depth < 0:
            raise ValueError("--depth must be >= 0")

        if args.artifact_mode == "none":
            artifact_mode = "none"
        else:
            artifact_mode = args.artifact_mode

        data = load_yaml(input_path)
        graph = build_graph(data, input_path, artifact_mode)

        if not graph.has_errors:
            graph = focus_graph(graph, args.start, args.focus, args.mode, args.depth)

        print_validation(graph)

        if graph.has_errors:
            print("Graph generation blocked because structural validation has errors.", file=sys.stderr)
            return 1

        if fmt == "mmd":
            write_mmd(graph, out_path)
        elif fmt in {"svg", "png"}:
            render_dot(graph, out_path, fmt)
        else:
            raise RuntimeError(f"Unsupported format: {fmt}")

        print(f"Generated {fmt} graph: {out_path}")
        return 0

    except Exception as exc:
        print(f"Failed to generate graph: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
