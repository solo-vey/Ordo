#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, subprocess
from pathlib import Path
from typing import Any
import yaml

HIGHLIGHT_STYLES = {
    "new": {"color": "#16A34A", "fill": "#DCFCE7", "penwidth": "3"},
    "changed": {"color": "#F59E0B", "fill": "#FEF3C7", "penwidth": "3"},
    "important": {"color": "#DC2626", "fill": "#FEE2E2", "penwidth": "3"},
    "warning": {"color": "#EA580C", "fill": "#FFF7ED", "penwidth": "3"},
    "review": {"color": "#7C3AED", "fill": "#F3E8FF", "penwidth": "3"},
    "removed": {"color": "#64748B", "fill": "#F1F5F9", "penwidth": "3"},
}
SUPPORTED_KINDS = {"node","edge","gate","assertion","state","contract","repair","output","artifact","include","freeform","render","cluster"}

def safe_id(raw: Any) -> str:
    s = re.sub(r"[^a-zA-Z0-9_]", "_", str(raw)).strip("_")
    if not s: s = "node"
    if s[0].isdigit(): s = "n_" + s
    return s

def q(text: Any) -> str:
    return '"' + str(text).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'

def short(text: Any, n: int = 64) -> str:
    text = "" if text is None else str(text).strip().replace("\n", " ")
    return text[:n] + ("…" if len(text) > n else "")

def load_annotations(path: Path | None):
    if not path: return {}, []
    data = json.loads(path.read_text(encoding="utf-8"))
    warnings = []
    if data.get("schema") != "ordo.graph.annotations.v1":
        warnings.append("annotation schema is not ordo.graph.annotations.v1")
    by_target = {}
    for idx, ann in enumerate(data.get("annotations", [])):
        target = ann.get("target")
        highlight = ann.get("highlight")
        if not isinstance(target, str) or ":" not in target:
            warnings.append(f"annotation[{idx}] has invalid target")
            continue
        kind = target.split(":", 1)[0]
        if kind not in SUPPORTED_KINDS:
            warnings.append(f"annotation[{idx}] uses unsupported target kind: {kind}")
        if highlight not in HIGHLIGHT_STYLES:
            warnings.append(f"annotation[{idx}] uses unsupported highlight: {highlight}")
        by_target.setdefault(target, []).append(ann)
    return by_target, warnings

def style_for(target, annotations):
    anns = annotations.get(target)
    if not anns: return None
    return HIGHLIGHT_STYLES.get(anns[-1].get("highlight"), HIGHLIGHT_STYLES["review"])

def node_attrs(target, annotations, default_fill):
    st = style_for(target, annotations)
    if not st: return f'fillcolor="{default_fill}"'
    return f'fillcolor="{st["fill"]}", color="{st["color"]}", penwidth={st["penwidth"]}'

def edge_attrs(target, label, annotations):
    attrs = []
    if label: attrs.append(f"label={q(label)}")
    st = style_for(target, annotations)
    if st:
        attrs.extend([f'color="{st["color"]}"', f'penwidth={st["penwidth"]}', f'fontcolor="{st["color"]}"'])
    return " [" + ", ".join(attrs) + "]" if attrs else ""

def add_annotation_notes(lines, target_to_dot_id, annotations):
    i = 0
    for target, anns in annotations.items():
        dot_id = target_to_dot_id.get(target)
        if not dot_id: continue
        for ann in anns:
            comment = ann.get("comment")
            if not comment: continue
            i += 1
            st = HIGHLIGHT_STYLES.get(ann.get("highlight"), HIGHLIGHT_STYLES["review"])
            note_id = f"annotation_note_{i}"
            label = f"{ann.get('highlight', 'annotation')} annotation\n{comment}"
            lines.append(f'  {note_id} [label={q(label)}, shape=note, fillcolor="{st["fill"]}", color="{st["color"]}", fontsize=9];')
            lines.append(f'  {dot_id} -> {note_id} [style=dashed, label="annotation", color="{st["color"]}"];')
            lines.append(f'  {{ rank=same; {dot_id}; {note_id}; }}')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("yaml_file")
    ap.add_argument("--annotations")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    yaml_path, out_path = Path(args.yaml_file), Path(args.out)
    annotations, warnings = load_annotations(Path(args.annotations) if args.annotations else None)
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    nodes = data.get("nodes", [])
    gates = {g.get("id"): g for g in data.get("gates", []) if isinstance(g, dict)}
    outputs = {o.get("id"): o for o in data.get("outputs", []) if isinstance(o, dict)}
    edges, state_writers = [], {}
    def target_id(t): return safe_id(t)
    for node in nodes:
        nid = node["id"]
        oa = node.get("on_answer") or {}
        if isinstance(oa.get("update_state"), dict):
            for field in oa["update_state"]: state_writers[field] = nid
        if isinstance(oa.get("next"), str):
            edges.append((safe_id(nid), target_id(oa["next"]), None, f"edge:{nid}::{oa['next']}"))
        for ans, spec in oa.items():
            if ans in {"update_state","next","artifacts","output_artifacts"}: continue
            target = spec.get("next") if isinstance(spec, dict) else spec
            if isinstance(target, str):
                if isinstance(spec, dict) and isinstance(spec.get("update_state"), dict):
                    for field in spec["update_state"]: state_writers[field] = nid
                edges.append((safe_id(nid), target_id(target), str(ans), f"edge:{nid}:{ans}:{target}"))
    lines = [
        "digraph AnnotationOverlayDemo {", "  rankdir=TB;",
        '  graph [fontname="Helvetica", bgcolor="white", label="Demo Support Triage — annotation overlay", labelloc=t, fontsize=22, pad=0.3, nodesep=0.6, ranksep=0.75];',
        '  node [fontname="Helvetica", shape=box, style="rounded,filled", color="#475569", penwidth=1.2, fontsize=10];',
        '  edge [fontname="Helvetica", color="#475569", arrowsize=0.7, fontsize=9];',
        '  ENTRY [label="ENTRY\\nDemo Support Triage", fillcolor="#DBEAFE", color="#2563EB"];',
    ]
    target_to_dot_id = {}
    for node in nodes:
        nid = safe_id(node["id"])
        target = f"node:{node['id']}"
        target_to_dot_id[target] = nid
        lines.append(f'  {nid} [label={q(node["id"] + chr(10) + short(node.get("question")))}, {node_attrs(target, annotations, "#F8FAFC")}];')
        contract_id = "contract_" + nid
        ctarget = f"contract:{node['id']}"
        target_to_dot_id[ctarget] = contract_id
        required = node.get("required_fields") or []
        lines.append(f'  {contract_id} [label={q("Contract" + chr(10) + "requires: " + ", ".join(required))}, shape=note, {node_attrs(ctarget, annotations, "#EEF2FF")}];')
        lines.append(f'  {nid} -> {contract_id} [style=dashed, label="contract", color="#4F46E5"];')
    for field, owner in state_writers.items():
        sid = "state_" + safe_id(field)
        target = f"state:{field}"
        target_to_dot_id[target] = sid
        lines.append(f'  {sid} [label={q("state." + field)}, shape=note, {node_attrs(target, annotations, "#E8F8EC")}];')
        lines.append(f'  {safe_id(owner)} -> {sid} [style=dashed, label="writes", color="#16A34A"];')
    for gid, gate in gates.items():
        dot_id = safe_id(gid)
        target = f"gate:{gid}"
        target_to_dot_id[target] = dot_id
        lines.append(f'  {dot_id} [label={q(gid + chr(10) + short(gate.get("condition")))}, shape=note, {node_attrs(target, annotations, "#FEF3C7")}];')
    for oid, output in outputs.items():
        dot_id = "output_" + safe_id(oid)
        target = f"output:{oid}"
        target_to_dot_id[target] = dot_id
        lines.append(f'  {dot_id} [label={q(oid + chr(10) + output.get("type", "output"))}, shape=folder, {node_attrs(target, annotations, "#E0F2FE")}];')
        for gid in output.get("allowed_after", []):
            if gid in gates:
                lines.append(f'  {safe_id(gid)} -> {dot_id} [style=dotted, label="allowed_after", color="#0284C7"];')
    if nodes: lines.append(f'  ENTRY -> {safe_id(nodes[0]["id"])};')
    for s, t, label, edge_target in edges:
        target_to_dot_id[edge_target] = s
        lines.append(f"  {s} -> {t}{edge_attrs(edge_target, label, annotations)};")
    add_annotation_notes(lines, target_to_dot_id, annotations)
    lines.append("}")
    dot_path = out_path.with_suffix(".dot")
    dot_path.write_text("\n".join(lines), encoding="utf-8")
    subprocess.run(["dot", "-Tsvg", str(dot_path), "-o", str(out_path)], check=True)
    out_path.with_suffix(".report.json").write_text(json.dumps({
        "schema": "ordo.graph.annotations.v1",
        "annotation_count": sum(len(v) for v in annotations.values()),
        "warnings": warnings,
        "rendered_svg": str(out_path)
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
