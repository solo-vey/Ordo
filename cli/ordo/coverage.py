from __future__ import annotations

from typing import Any

from .contract_coverage import validate_contract_artifact_coverage


def build_coverage(source: dict[str, Any], tests: dict[str, Any] | None = None) -> dict[str, Any]:
    tests = tests or {}
    test_cases = tests.get("test_cases", []) if isinstance(tests, dict) else []

    gates = source.get("gates", []) or []
    assertions = source.get("assertions", []) or []
    nodes = source.get("nodes", []) or []
    freeforms = source.get("freeform", []) or []

    expected_gates = set()
    expected_assertions = set()
    expected_nodes = set()
    for tc in test_cases:
        exp = tc.get("expected", {}) or {}
        for g in exp.get("gates", []) or []:
            if isinstance(g, dict) and g.get("id"):
                expected_gates.add(g["id"])
            elif isinstance(g, str):
                expected_gates.add(g)
        for a in exp.get("assertions", []) or []:
            if isinstance(a, dict) and a.get("id"):
                expected_assertions.add(a["id"])
            elif isinstance(a, str):
                expected_assertions.add(a)
        if exp.get("node"):
            expected_nodes.add(exp["node"])

    def pct(covered: int, total: int) -> float:
        return 100.0 if total == 0 else round(covered * 100.0 / total, 2)

    gate_ids = {g.get("id") for g in gates if g.get("id")}
    assertion_ids = {a.get("id") for a in assertions if a.get("id")}
    node_ids = {n.get("id") for n in nodes if n.get("id")}

    contract_artifact_coverage = validate_contract_artifact_coverage(source)
    status = "failed" if contract_artifact_coverage["status"] == "failed" else "passed"

    return {
        "status": status,
        "summary": {
            "test_cases": len(test_cases),
            "gates_total": len(gate_ids),
            "gates_covered": len(gate_ids & expected_gates),
            "assertions_total": len(assertion_ids),
            "assertions_covered": len(assertion_ids & expected_assertions),
            "nodes_total": len(node_ids),
            "nodes_covered": len(node_ids & expected_nodes),
            "freeform_total": len(freeforms),
        },
        "coverage": {
            "gates_percent": pct(len(gate_ids & expected_gates), len(gate_ids)),
            "assertions_percent": pct(len(assertion_ids & expected_assertions), len(assertion_ids)),
            "nodes_percent": pct(len(node_ids & expected_nodes), len(node_ids)),
        },
        "uncovered": {
            "gates": sorted(gate_ids - expected_gates),
            "assertions": sorted(assertion_ids - expected_assertions),
            "nodes": sorted(node_ids - expected_nodes),
        },
        "contract_artifact_coverage": contract_artifact_coverage,
        "freeform_maturity": [
            {
                "id": f.get("id"),
                "maturity": f.get("maturity"),
                "incident_count": f.get("incident_count", 0),
                "incident_threshold": f.get("incident_threshold", 3),
            }
            for f in freeforms
        ],
    }
