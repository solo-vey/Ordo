from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .artifact_validator import (
    _artifact_by_id,
    _artifact_texts,
    _contract_by_id,
    _field_status,
    _load_state,
    _values_for_field,
    validate_artifacts,
)
from .loader import load_package
from .reporter import write_json


@dataclass
class ConsistencyIssue:
    severity: str
    code: str
    message: str
    location: str
    contract: str | None = None
    artifact: str | None = None
    field: str | None = None
    expected_value: str | None = None


def _issue(
    issues: list[ConsistencyIssue],
    severity: str,
    code: str,
    message: str,
    location: str,
    *,
    contract: str | None = None,
    artifact: str | None = None,
    field: str | None = None,
    expected_value: str | None = None,
) -> None:
    issues.append(ConsistencyIssue(severity, code, message, location, contract, artifact, field, expected_value))


def _artifact_requirements(source: dict[str, Any]) -> list[dict[str, Any]]:
    return source.get("artifact_requirements", []) or []


def _rendered_assertions(source: dict[str, Any]) -> list[dict[str, Any]]:
    return source.get("rendered_artifact_assertions", []) or []


def _split_contract_field(ref: str) -> tuple[str | None, str | None]:
    if not isinstance(ref, str) or "." not in ref:
        return None, None
    return ref.split(".", 1)


def _status_from_presence(presence: dict[str, bool]) -> str:
    if not presence:
        return "not_checked"
    values = set(presence.values())
    if values == {True}:
        return "passed"
    if values == {False}:
        return "failed_missing_everywhere"
    return "failed_inconsistent"


def consistency(
    package_path: str | Path,
    *,
    artifacts: str | Path | None = None,
    state_path: str | None = None,
    out: str | Path | None = None,
) -> dict[str, Any]:
    """Build CONSISTENCY_CHECK_REPORT.json for rendered artifacts.

    M46.4 intentionally performs deterministic cross-artifact consistency checks
    only. It compares rendered artifacts against confirmed contract values and
    reports whether required artifacts agree on the same contract fields. It does
    not execute external systems or business/runtime code.
    """
    root, manifest, source, tests = load_package(package_path)
    artifacts_dir = Path(artifacts).resolve() if artifacts else root / "generated_outputs"
    reports_dir = root / manifest.get("reports", "reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    state, state_source = _load_state(root, state_path)

    artifact_validation = validate_artifacts(
        root,
        artifacts=artifacts_dir,
        state_path=state_path,
        out=reports_dir / "artifact_validation_report.json",
    )

    contracts = _contract_by_id(source)
    artifacts_by_id = _artifact_by_id(source)
    issues: list[ConsistencyIssue] = []
    warnings: list[ConsistencyIssue] = []
    checked_contracts: set[str] = set()
    checked_artifacts: set[str] = set()
    cross_artifact_consistency: dict[str, dict[str, Any]] = {}

    for req in _artifact_requirements(source):
        when = req.get("when", {}) or {}
        contract_id = when.get("contract")
        if when.get("status") != "confirmed":
            continue
        contract = contracts.get(contract_id)
        if not contract or contract.get("status") != "confirmed":
            continue
        checked_contracts.add(contract_id)
        for target in req.get("requires", []) or []:
            artifact_id = target.get("artifact")
            artifact = artifacts_by_id.get(artifact_id)
            if not artifact:
                _issue(issues, "error", "ORDO-COV-REF-002", "Artifact requirement references unknown artifact.", req.get("id") or "artifact_requirement", contract=contract_id, artifact=artifact_id)
                continue
            checked_artifacts.add(artifact_id)
            texts = _artifact_texts(root, artifacts_dir, artifact, state)
            combined = "\n".join(text for _path, text in texts)
            for field_id in target.get("must_include_fields", []) or []:
                if _field_status(contract, field_id) != "confirmed":
                    continue
                values = _values_for_field(contract, field_id, state)
                key = f"{contract_id}.{field_id}"
                entry = cross_artifact_consistency.setdefault(
                    key,
                    {
                        "contract": contract_id,
                        "field": field_id,
                        "expected_values": values,
                        "artifacts": {},
                        "status": "not_checked",
                    },
                )
                if not values:
                    _issue(warnings, "warning", "ORDO-COV-W03", "Confirmed field has no concrete value for consistency comparison.", key, contract=contract_id, artifact=artifact_id, field=field_id)
                    entry["artifacts"][artifact_id] = "not_checked_no_value"
                    continue
                present = bool(combined) and all(value in combined for value in values)
                entry["artifacts"][artifact_id] = "present" if present else "missing"

    # Rendered assertions are also part of consistency, even if not included in
    # artifact_requirements. They usually represent critical repeated values such
    # as alias or test strategy.
    for assertion in _rendered_assertions(source):
        contract_id, field_id = _split_contract_field(assertion.get("field"))
        contract = contracts.get(contract_id or "")
        if not contract or not field_id:
            continue
        checked_contracts.add(contract_id)
        values = _values_for_field(contract, field_id, state)
        key = f"{contract_id}.{field_id}"
        entry = cross_artifact_consistency.setdefault(
            key,
            {
                "contract": contract_id,
                "field": field_id,
                "expected_values": values,
                "artifacts": {},
                "status": "not_checked",
            },
        )
        for artifact_id in assertion.get("must_appear_in", []) or []:
            artifact = artifacts_by_id.get(artifact_id)
            if not artifact:
                _issue(issues, "error", "ORDO-COV-REF-006", "Rendered artifact assertion references unknown artifact.", assertion.get("id") or "rendered_artifact_assertion", contract=contract_id, artifact=artifact_id, field=field_id)
                continue
            checked_artifacts.add(artifact_id)
            texts = _artifact_texts(root, artifacts_dir, artifact, state)
            combined = "\n".join(text for _path, text in texts)
            if not values:
                entry["artifacts"][artifact_id] = "not_checked_no_value"
                continue
            present = bool(combined) and all(value in combined for value in values)
            entry["artifacts"][artifact_id] = "present" if present else "missing"

    for key, entry in cross_artifact_consistency.items():
        presence = {artifact_id: status == "present" for artifact_id, status in entry.get("artifacts", {}).items() if status in {"present", "missing"}}
        status = _status_from_presence(presence)
        entry["status"] = status
        if status == "failed_inconsistent":
            _issue(
                issues,
                "error",
                "ORDO-COV-004",
                "Generated artifacts disagree on the same confirmed contract field.",
                key,
                contract=entry.get("contract"),
                field=entry.get("field"),
                expected_value=", ".join(entry.get("expected_values") or []),
            )
        elif status == "failed_missing_everywhere":
            _issue(
                issues,
                "error",
                "ORDO-COV-002",
                "Confirmed contract field is missing from all checked artifacts.",
                key,
                contract=entry.get("contract"),
                field=entry.get("field"),
                expected_value=", ".join(entry.get("expected_values") or []),
            )

    artifact_validation_failed = artifact_validation.get("status") != "passed"
    error_items = [asdict(i) for i in issues if i.severity == "error"]
    warning_items = [asdict(i) for i in warnings] + artifact_validation.get("warnings", [])
    status = "failed" if error_items or artifact_validation_failed else ("passed_with_warnings" if warning_items else "passed")
    go_no_go = "go" if status == "passed" else "no_go_requires_artifact_fix"

    report = {
        "status": status,
        "mode": "cross_artifact_consistency",
        "package": {"name": manifest.get("name"), "version": manifest.get("version")},
        "artifacts_dir": str(artifacts_dir),
        "state_source": state_source,
        "go_no_go": go_no_go,
        "checked_contracts": sorted(checked_contracts),
        "checked_artifacts": sorted(checked_artifacts),
        "blocking_issues": error_items + artifact_validation.get("issues", []),
        "warnings": warning_items,
        "cross_artifact_consistency": cross_artifact_consistency,
        "artifact_validation": {
            "status": artifact_validation.get("status"),
            "summary": artifact_validation.get("summary", {}),
            "report": str((reports_dir / "artifact_validation_report.json").relative_to(root)),
        },
        "summary": {
            "checked_contracts": len(checked_contracts),
            "checked_artifacts": len(checked_artifacts),
            "consistency_fields": len(cross_artifact_consistency),
            "blocking_issues": len(error_items) + len(artifact_validation.get("issues", [])),
            "warnings": len(warning_items),
        },
        "known_limitation": "M46.4 compares rendered artifacts against declared confirmed contract values. It does not infer arbitrary contradictory business values that are not mapped as contract fields.",
    }
    output = Path(out).resolve() if out else reports_dir / "CONSISTENCY_CHECK_REPORT.json"
    write_json(output, report)
    return report
