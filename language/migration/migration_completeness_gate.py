from __future__ import annotations
from hashlib import sha256
from typing import Any

def _finding(clause_id, loss_type, severity, message, mapped_unit_ids):
    digest = sha256(f"{clause_id}|{loss_type}".encode()).hexdigest()[:16].upper()
    return {
        "schema_version": "ordo.migration_loss_finding.v1",
        "finding_id": f"LOSS-{digest}",
        "clause_id": clause_id,
        "loss_type": loss_type,
        "severity": severity,
        "message": message,
        "blocking": severity in {"error", "critical"},
        "mapped_unit_ids": mapped_unit_ids,
    }

def evaluate_migration_completeness(matrix, *, known_clause_ids, known_unit_ids, mandatory_clause_ids):
    rows = matrix.get("rows") or []
    findings = []
    row_ids = [r["clause_id"] for r in rows]

    for cid in sorted(known_clause_ids - set(row_ids)):
        findings.append(_finding(cid, "unmapped_clause", "critical" if cid in mandatory_clause_ids else "error", "Source clause has no traceability row.", []))

    for row in rows:
        cid = row["clause_id"]
        units = row.get("mapped_unit_ids") or []
        constructs = row.get("mapped_constructs") or []
        status = row["coverage_status"]
        p = row["semantic_preservation"]
        mandatory = bool(row.get("mandatory"))

        if set(units) - known_unit_ids:
            findings.append(_finding(cid, "construct_mapping_missing", "error", "Traceability row references unknown unit ids.", units))
        if status == "unmapped":
            findings.append(_finding(cid, "unmapped_clause", "critical" if mandatory else "error", "Clause is explicitly unmapped.", units))
        elif status == "partial":
            findings.append(_finding(cid, "partial_coverage", "critical" if mandatory else "warning", "Clause is only partially covered.", units))
        elif status == "full" and (not units or not constructs):
            findings.append(_finding(cid, "construct_mapping_missing", "error", "Full coverage requires mapped units and Ordo constructs.", units))
        elif status == "excluded_with_reason":
            if mandatory:
                findings.append(_finding(cid, "unsupported_exclusion", "critical", "Mandatory clause cannot be excluded.", units))
            elif len((row.get("exclusion_reason") or "").strip()) < 10:
                findings.append(_finding(cid, "unsupported_exclusion", "error", "Excluded clause lacks an explicit reason.", units))

        checks = [
            ("normativity_preserved", "mandatory_strength_downgrade", "Normativity was not preserved."),
            ("mandatory_strength_preserved", "mandatory_strength_downgrade", "Mandatory strength was not preserved."),
            ("authorization_boundary_preserved", "authorization_boundary_loss", "Authorization boundary was not preserved."),
            ("decision_semantics_preserved", "decision_semantic_loss", "Decision semantics were not preserved."),
            ("evidence_requirement_preserved", "evidence_requirement_loss", "Evidence requirement was not preserved."),
        ]
        for field, loss_type, message in checks:
            if not p[field]:
                severity = "critical" if mandatory or loss_type in {"authorization_boundary_loss","decision_semantic_loss"} else "error"
                findings.append(_finding(cid, loss_type, severity, message, units))

    blocking = [f for f in findings if f["blocking"]]
    return {
        "schema_version": "ordo.migration_completeness_gate.v1",
        "status": "passed" if not blocking else "blocked",
        "decision": "allow" if not blocking else "block",
        "summary": {
            "known_clause_count": len(known_clause_ids),
            "traceability_row_count": len(rows),
            "finding_count": len(findings),
            "blocking_finding_count": len(blocking),
            "warning_count": sum(not f["blocking"] for f in findings),
        },
        "blocking_finding_ids": [f["finding_id"] for f in blocking],
        "findings": findings,
    }
