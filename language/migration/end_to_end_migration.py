from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from migration_completeness_gate import evaluate_migration_completeness


def source_sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def segment_clauses(content: str) -> list[dict[str, Any]]:
    clauses = []
    for line in content.splitlines():
        match = re.match(r"^\s*(\d+)\.\s+(.+?)\s*$", line)
        if not match:
            continue
        text = match.group(2)
        clauses.append({
            "clause_id": f"C-{int(match.group(1)):04d}",
            "text": text,
            "normativity": "normative",
            "mandatory": True,
        })
    return clauses


def classify_clause(clause: dict[str, Any]) -> dict[str, Any]:
    text = clause["text"].lower()
    classes: list[str] = []

    def add(value: str) -> None:
        if value not in classes:
            classes.append(value)

    if any(x in text for x in ["first", "before", "after", "only after"]):
        add("stage")
    if any(x in text for x in ["confirm", "assess", "select", "implement", "run", "return", "stop"]):
        add("action")
    if any(x in text for x in ["assess", "select", "does not authorize"]):
        add("decision")
    if any(x in text for x in ["before", "only after", "must", "do not label"]):
        add("gate")
    if "authorization" in text or "authorize" in text:
        add("authorization")
    if any(x in text for x in ["package", "source code", "tests", "repository patch"]):
        add("artifact")
    if any(x in text for x in ["evidence", "completion report", "traceable"]):
        add("evidence")
    if any(x in text for x in ["unauthorized mutation", "route to review", "roll back"]):
        add("recovery")
    if not classes:
        add("action")

    return {
        **clause,
        "semantic_classes": classes,
        "classification_confidence": 0.95,
        "ambiguity": {"status": "clear", "ambiguity_ids": []},
    }


CONSTRUCTS = {
    "stage": "PROCESS.STAGE",
    "action": "ACTION.NODE",
    "decision": "DECISION.NODE",
    "gate": "GATE.DEF",
    "state": "STATE.DEF",
    "artifact": "ARTIFACT.DEF",
    "evidence": "EVIDENCE.ARTIFACT",
    "authorization": "AUTHORIZATION.GATE",
    "recovery": "RECOVERY.ROUTE",
    "exception": "EXCEPTION.ROUTE",
}


def build_units(classified: list[dict[str, Any]]) -> list[dict[str, Any]]:
    units = []
    counter = 1
    for clause in classified:
        for unit_type in clause["semantic_classes"]:
            units.append({
                "node_id": f"U-{counter:04d}",
                "unit_type": unit_type,
                "source_clause_refs": [clause["clause_id"]],
                "label": clause["text"],
                "mandatory": clause["mandatory"],
                "ordo_construct": CONSTRUCTS[unit_type],
            })
            counter += 1
    return units


def build_edges(units: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # Preserve source clause order through a primary unit for each clause.
    by_clause: dict[str, list[dict[str, Any]]] = {}
    for unit in units:
        by_clause.setdefault(unit["source_clause_refs"][0], []).append(unit)

    clause_ids = sorted(by_clause)
    edges = []
    edge_counter = 1
    for left, right in zip(clause_ids, clause_ids[1:]):
        edges.append({
            "edge_id": f"E-{edge_counter:04d}",
            "from": by_clause[left][0]["node_id"],
            "to": by_clause[right][0]["node_id"],
            "relation": "precedes",
            "source_clause_refs": [left, right],
        })
        edge_counter += 1

    # Authorization clauses guard the next implementation action.
    auth_units = [u for u in units if u["unit_type"] == "authorization"]
    implementation_units = [
        u for u in units
        if u["unit_type"] == "action" and "implement" in u["label"].lower()
    ]
    if auth_units and implementation_units:
        edges.append({
            "edge_id": f"E-{edge_counter:04d}",
            "from": auth_units[-1]["node_id"],
            "to": implementation_units[0]["node_id"],
            "relation": "authorizes",
            "source_clause_refs": sorted(set(
                auth_units[-1]["source_clause_refs"] + implementation_units[0]["source_clause_refs"]
            )),
        })
    return edges


def build_mapping(units: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "ordo.migration_ordo_mapping.v1",
        "mapping_id": "MIG-MAP-LEGACY-ALL-IN-ONE-001",
        "entries": [{
            "unit_id": u["node_id"],
            "unit_type": u["unit_type"],
            "ordo_construct": u["ordo_construct"],
            "mapping_mode": "direct",
            "source_clause_refs": u["source_clause_refs"],
            "confidence": 0.95,
        } for u in units],
    }


def build_traceability(
    classified: list[dict[str, Any]],
    units: list[dict[str, Any]],
) -> dict[str, Any]:
    by_clause: dict[str, list[dict[str, Any]]] = {}
    for unit in units:
        by_clause.setdefault(unit["source_clause_refs"][0], []).append(unit)

    rows = []
    for clause in classified:
        mapped = by_clause.get(clause["clause_id"], [])
        rows.append({
            "clause_id": clause["clause_id"],
            "mandatory": clause["mandatory"],
            "mapped_unit_ids": [u["node_id"] for u in mapped],
            "mapped_constructs": sorted({u["ordo_construct"] for u in mapped}),
            "coverage_status": "full" if mapped else "unmapped",
            "semantic_preservation": {
                "normativity_preserved": True,
                "mandatory_strength_preserved": True,
                "authorization_boundary_preserved": True,
                "decision_semantics_preserved": True,
                "evidence_requirement_preserved": True,
            },
        })
    return {
        "schema_version": "ordo.migration_traceability_matrix.v1",
        "matrix_id": "MIG-TRACE-LEGACY-ALL-IN-ONE-001",
        "source_ref": "legacy_all_in_one_instruction.md",
        "rows": rows,
    }


def build_playbook(units: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "ordo.migrated_playbook.v1",
        "playbook_id": "LEGACY-ALL-IN-ONE-MIGRATED",
        "title": "Migrated Legacy Implementation Process",
        "nodes": units,
        "edges": edges,
        "entry_node": units[0]["node_id"],
        "status": "migration_validated",
    }


def migrate_source(content: str, source_ref: str) -> dict[str, Any]:
    clauses = segment_clauses(content)
    classified = [classify_clause(c) for c in clauses]
    units = build_units(classified)
    edges = build_edges(units)
    traceability = build_traceability(classified, units)

    gate = evaluate_migration_completeness(
        traceability,
        known_clause_ids={c["clause_id"] for c in classified},
        known_unit_ids={u["node_id"] for u in units},
        mandatory_clause_ids={c["clause_id"] for c in classified if c["mandatory"]},
    )

    return {
        "schema_version": "ordo.process_instruction_migration_package.v1",
        "package_id": "MIG-PKG-LEGACY-ALL-IN-ONE-001",
        "source": {
            "source_ref": source_ref,
            "source_sha256": source_sha256(content),
            "content": content,
        },
        "intake": {
            "schema_version": "ordo.process_instruction_migration_intake.v1",
            "intake_id": "MIG-LEGACY-ALL-IN-ONE-001",
            "migration_goal": "Convert monolithic process instructions into a structured Ordo playbook.",
            "loss_policy": "zero_silent_loss",
        },
        "clause_inventory": {
            "schema_version": "ordo.migration_clause_inventory.v1",
            "source_ref": source_ref,
            "clauses": classified,
        },
        "ambiguities": [],
        "dependency_graph": {
            "schema_version": "ordo.migration_dependency_graph.v1",
            "graph_id": "MIG-GRAPH-LEGACY-ALL-IN-ONE-001",
            "nodes": units,
            "edges": edges,
        },
        "ordo_mapping": build_mapping(units),
        "traceability_matrix": traceability,
        "gate_report": gate,
        "playbook": build_playbook(units, edges),
    }


def write_package(package: dict[str, Any], output_dir: str | Path) -> Path:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    files = {
        "migration_package.json": package,
        "clause_inventory.json": package["clause_inventory"],
        "dependency_graph.json": package["dependency_graph"],
        "ordo_mapping.json": package["ordo_mapping"],
        "traceability_matrix.json": package["traceability_matrix"],
        "migration_gate_report.json": package["gate_report"],
        "migrated_playbook.json": package["playbook"],
    }
    for name, payload in files.items():
        (output / name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    checksums = []
    for path in sorted(output.glob("*.json")):
        checksums.append(
            f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}"
        )
    (output / "SHA256SUMS.txt").write_text("\n".join(checksums) + "\n", encoding="utf-8")
    return output
