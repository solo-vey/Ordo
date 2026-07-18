from __future__ import annotations
from typing import Any

def evaluate_closure(
    package: dict[str, Any],
    *,
    regression_passed: bool,
    package_materialized: bool,
) -> dict[str, Any]:
    issues = []
    clauses = package.get("clause_inventory", {}).get("clauses", [])
    units = package.get("dependency_graph", {}).get("nodes", [])
    mappings = package.get("ordo_mapping", {}).get("entries", [])
    rows = package.get("traceability_matrix", {}).get("rows", [])
    gate = package.get("gate_report", {})

    if not clauses:
        issues.append({"code": "MIG-CLOSE-001", "message": "clause inventory is empty"})
    if not units:
        issues.append({"code": "MIG-CLOSE-002", "message": "dependency graph is empty"})
    if len(mappings) != len(units):
        issues.append({"code": "MIG-CLOSE-003", "message": "not every unit has an Ordo mapping"})
    if len(rows) != len(clauses):
        issues.append({"code": "MIG-CLOSE-004", "message": "traceability rows do not cover all clauses"})
    if gate.get("status") != "passed":
        issues.append({"code": "MIG-CLOSE-005", "message": "migration completeness gate did not pass"})
    if any(r.get("coverage_status") != "full" for r in rows):
        issues.append({"code": "MIG-CLOSE-006", "message": "not all clauses have full coverage"})
    if not regression_passed:
        issues.append({"code": "MIG-CLOSE-007", "message": "regression suite failed"})
    if not package_materialized:
        issues.append({"code": "MIG-CLOSE-008", "message": "migration package was not materialized"})

    return {
        "schema_version": "ordo.bl_ordo_021_closure_gate.v1",
        "status": "passed" if not issues else "blocked",
        "issues": issues,
        "requirements": {
            "clause_inventory": True,
            "dependency_graph": True,
            "complete_ordo_mapping": True,
            "full_traceability": True,
            "zero_blocking_loss_findings": True,
            "materialized_package": True,
            "regression_passed": True,
        },
    }
