from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

ALLOWED_CONTRACT_STATUSES = {"missing", "candidate", "proposed", "confirmed", "blocked", "not_applicable"}
ALLOWED_ARTIFACT_FORMATS = {"markdown", "json", "yaml", "text", "other"}
ALLOWED_FAILURE_POLICIES = {"warn", "fail", "no_go"}


@dataclass
class CoverageIssue:
    severity: str
    code: str
    message: str
    location: str
    contract: str | None = None
    artifact: str | None = None
    field: str | None = None


def _add(
    issues: list[CoverageIssue],
    severity: str,
    code: str,
    message: str,
    location: str,
    contract: str | None = None,
    artifact: str | None = None,
    field: str | None = None,
) -> None:
    issues.append(CoverageIssue(severity, code, message, location, contract, artifact, field))


def _contracts(source: dict[str, Any]) -> list[dict[str, Any]]:
    return source.get("contracts", []) or []


def _artifacts(source: dict[str, Any]) -> list[dict[str, Any]]:
    return source.get("artifacts", []) or []


def _artifact_requirements(source: dict[str, Any]) -> list[dict[str, Any]]:
    return source.get("artifact_requirements", []) or []


def _coverage_rules(source: dict[str, Any]) -> list[dict[str, Any]]:
    return source.get("coverage_rules", []) or []


def _rendered_assertions(source: dict[str, Any]) -> list[dict[str, Any]]:
    return source.get("rendered_artifact_assertions", []) or []


def _contract_ids(source: dict[str, Any]) -> set[str]:
    return {c.get("id") for c in _contracts(source) if c.get("id")}


def _artifact_ids(source: dict[str, Any]) -> set[str]:
    # output template ids are valid artifact targets too, because M46.2 is a
    # compile/coverage layer, not rendered-output validation yet.
    ids = {a.get("id") for a in _artifacts(source) if a.get("id")}
    ids |= {o.get("id") for o in source.get("outputs", []) or [] if o.get("id")}
    return ids


def _contract_field_ids(contract: dict[str, Any]) -> set[str]:
    fields = contract.get("fields", {}) or {}
    return set(fields.keys())


def _split_contract_field(ref: str) -> tuple[str | None, str | None]:
    if not isinstance(ref, str) or "." not in ref:
        return None, None
    contract, field = ref.split(".", 1)
    return contract, field


def _field_known(field: str, known_fields: set[str]) -> bool:
    if field in known_fields:
        return True
    # Allows mapping a parent field such as item.values when concrete keys are
    # item.values.old#value and item.values.new#value, but not unrelated fields.
    return any(k.startswith(field + ".") or field.startswith(k + ".") for k in known_fields)


def validate_contract_artifact_references(source: dict[str, Any]) -> dict[str, Any]:
    """Compile-time reference checks for M46.2 contract/artifact model.

    This validates source model references only. It does not inspect rendered
    artifact files; that belongs to validate-artifacts in a later M46 step.
    """
    issues: list[CoverageIssue] = []
    contracts = _contracts(source)
    artifacts = _artifacts(source)
    requirements = _artifact_requirements(source)
    rules = _coverage_rules(source)
    rendered_assertions = _rendered_assertions(source)

    contract_by_id = {c.get("id"): c for c in contracts if c.get("id")}
    artifact_ids = _artifact_ids(source)

    for i, contract in enumerate(contracts):
        loc = f"contracts[{i}]"
        if contract.get("kind") != "contract":
            _add(issues, "error", "ORDO-COV-SCHEMA-001", "Contract kind must be 'contract'.", f"{loc}.kind")
        cid = contract.get("id")
        if not cid:
            _add(issues, "error", "ORDO-COV-SCHEMA-002", "Contract id is required.", f"{loc}.id")
        status = contract.get("status")
        if status not in ALLOWED_CONTRACT_STATUSES:
            _add(issues, "error", "ORDO-COV-SCHEMA-003", "Contract status is not allowed.", f"{loc}.status", cid)
        fields = contract.get("fields")
        if not isinstance(fields, dict) or not fields:
            _add(issues, "error", "ORDO-COV-SCHEMA-004", "Contract fields must be a non-empty map.", f"{loc}.fields", cid)
        else:
            for field_id, field in fields.items():
                f_status = (field or {}).get("status") if isinstance(field, dict) else None
                if f_status not in ALLOWED_CONTRACT_STATUSES:
                    _add(issues, "error", "ORDO-COV-SCHEMA-005", "Contract field status is not allowed.", f"{loc}.fields.{field_id}.status", cid, field=field_id)

    for i, artifact in enumerate(artifacts):
        loc = f"artifacts[{i}]"
        if artifact.get("kind") != "artifact":
            _add(issues, "error", "ORDO-COV-SCHEMA-006", "Artifact kind must be 'artifact'.", f"{loc}.kind")
        if not artifact.get("id"):
            _add(issues, "error", "ORDO-COV-SCHEMA-007", "Artifact id is required.", f"{loc}.id")
        if not artifact.get("path_pattern"):
            _add(issues, "error", "ORDO-COV-SCHEMA-008", "Artifact path_pattern is required.", f"{loc}.path_pattern", artifact=artifact.get("id"))
        if artifact.get("format") not in ALLOWED_ARTIFACT_FORMATS:
            _add(issues, "error", "ORDO-COV-SCHEMA-009", "Artifact format is not allowed.", f"{loc}.format", artifact=artifact.get("id"))

    for i, req in enumerate(requirements):
        loc = f"artifact_requirements[{i}]"
        if req.get("kind") != "artifact_requirement":
            _add(issues, "error", "ORDO-COV-SCHEMA-010", "Artifact requirement kind must be 'artifact_requirement'.", f"{loc}.kind")
        when = req.get("when", {}) or {}
        contract_id = when.get("contract")
        if contract_id not in contract_by_id:
            _add(issues, "error", "ORDO-COV-REF-001", "Artifact requirement references unknown contract.", f"{loc}.when.contract", contract_id)
            known_fields: set[str] = set()
        else:
            known_fields = _contract_field_ids(contract_by_id[contract_id])
        if when.get("status") not in ALLOWED_CONTRACT_STATUSES:
            _add(issues, "error", "ORDO-COV-SCHEMA-011", "Artifact requirement when.status is not allowed.", f"{loc}.when.status", contract_id)
        requires = req.get("requires", []) or []
        if not requires:
            _add(issues, "error", "ORDO-COV-SCHEMA-012", "Artifact requirement must declare at least one target artifact.", f"{loc}.requires", contract_id)
        for j, target in enumerate(requires):
            artifact_id = target.get("artifact")
            tloc = f"{loc}.requires[{j}]"
            if artifact_id not in artifact_ids:
                _add(issues, "error", "ORDO-COV-REF-002", "Artifact requirement references unknown artifact.", f"{tloc}.artifact", contract_id, artifact_id)
            for field in target.get("must_include_fields", []) or []:
                if known_fields and not _field_known(field, known_fields):
                    _add(issues, "error", "ORDO-COV-REF-003", "Artifact requirement references unknown contract field.", f"{tloc}.must_include_fields", contract_id, artifact_id, field)

    for i, rule in enumerate(rules):
        loc = f"coverage_rules[{i}]"
        if rule.get("kind") != "coverage_rule":
            _add(issues, "error", "ORDO-COV-SCHEMA-013", "Coverage rule kind must be 'coverage_rule'.", f"{loc}.kind")
        if rule.get("failure_policy") not in ALLOWED_FAILURE_POLICIES:
            _add(issues, "error", "ORDO-COV-SCHEMA-014", "Coverage rule failure_policy is not allowed.", f"{loc}.failure_policy")

    for i, assertion in enumerate(rendered_assertions):
        loc = f"rendered_artifact_assertions[{i}]"
        contract_id, field_id = _split_contract_field(assertion.get("field"))
        if contract_id not in contract_by_id:
            _add(issues, "error", "ORDO-COV-REF-004", "Rendered artifact assertion references unknown contract.", f"{loc}.field", contract_id, field=field_id)
        elif field_id and not _field_known(field_id, _contract_field_ids(contract_by_id[contract_id])):
            _add(issues, "error", "ORDO-COV-REF-005", "Rendered artifact assertion references unknown contract field.", f"{loc}.field", contract_id, field=field_id)
        for artifact_id in assertion.get("must_appear_in", []) or []:
            if artifact_id not in artifact_ids:
                _add(issues, "error", "ORDO-COV-REF-006", "Rendered artifact assertion references unknown artifact.", f"{loc}.must_appear_in", contract_id, artifact_id, field_id)

    errors = [asdict(i) for i in issues if i.severity == "error"]
    warnings = [asdict(i) for i in issues if i.severity == "warning"]
    return {
        "status": "passed" if not errors else "failed",
        "summary": {
            "contracts": len(contracts),
            "artifacts": len(artifacts),
            "artifact_requirements": len(requirements),
            "coverage_rules": len(rules),
            "rendered_artifact_assertions": len(rendered_assertions),
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "issues": [asdict(i) for i in issues],
    }


def validate_contract_artifact_coverage(source: dict[str, Any]) -> dict[str, Any]:
    """Coverage checks for confirmed contracts to required artifact mappings.

    M46.2 scope: validate mapping completeness, not rendered file content.
    """
    reference_report = validate_contract_artifact_references(source)
    issues: list[CoverageIssue] = []
    for issue in reference_report.get("issues", []) or []:
        if issue.get("severity") == "error":
            issues.append(CoverageIssue(**issue))

    contracts = _contracts(source)
    requirements = _artifact_requirements(source)
    contract_by_id = {c.get("id"): c for c in contracts if c.get("id")}

    requirements_by_contract: dict[str, list[dict[str, Any]]] = {}
    mapped_fields_by_contract: dict[str, set[str]] = {}
    for req in requirements:
        cid = (req.get("when", {}) or {}).get("contract")
        status = (req.get("when", {}) or {}).get("status")
        if not cid or status != "confirmed":
            continue
        requirements_by_contract.setdefault(cid, []).append(req)
        for target in req.get("requires", []) or []:
            mapped_fields_by_contract.setdefault(cid, set()).update(target.get("must_include_fields", []) or [])

    for i, contract in enumerate(contracts):
        cid = contract.get("id")
        if not cid or contract.get("status") != "confirmed":
            continue
        loc = f"contracts[{i}]"
        if cid not in requirements_by_contract:
            _add(issues, "error", "ORDO-COV-001", "Confirmed contract has no artifact mapping.", loc, cid)
            continue
        fields = contract.get("fields", {}) or {}
        mapped = mapped_fields_by_contract.get(cid, set())
        for field_id, field in fields.items():
            if not isinstance(field, dict):
                continue
            if field.get("required") is True and field.get("status") == "confirmed":
                if not _field_known(field_id, mapped):
                    _add(issues, "error", "ORDO-COV-011", "Confirmed required contract field has no artifact mapping.", f"{loc}.fields.{field_id}", cid, field=field_id)

    errors = [asdict(i) for i in issues if i.severity == "error"]
    warnings = [asdict(i) for i in issues if i.severity == "warning"]
    return {
        "status": "passed" if not errors else "failed",
        "mode": "contract_artifact_mapping",
        "summary": {
            "contracts_total": len(contracts),
            "confirmed_contracts": sum(1 for c in contracts if c.get("status") == "confirmed"),
            "artifact_requirements_total": len(requirements),
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "issues": [asdict(i) for i in issues],
        "checked_contracts": sorted(contract_by_id),
        "known_limitation": "M46.2 validates declared mappings only; rendered artifact content validation is planned for a later M46 step.",
    }
