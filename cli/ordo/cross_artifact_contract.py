from __future__ import annotations

"""Fail-closed validation for authored template-to-output contracts.

The existing artifact validator checks a rendered artifact against business
state.  This module complements it by validating the authoring surfaces that
must agree before rendering: template headings, bindings, state paths,
validator expectations, finalization writes and rendered values.
"""

from pathlib import Path
import json
import re
from typing import Any

import yaml


MODES = frozenset({"advisory", "strict"})
PLACEHOLDER = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_.]*)\s*\}\}")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)


def _issue(
    issues: list[dict[str, Any]],
    code: str,
    message: str,
    location: str,
    *,
    layer: str,
    mismatch_class: str,
    remediation_target: str,
    severity: str = "error",
    document_id: str | None = None,
    defect_class: str | None = None,
) -> None:
    item: dict[str, Any] = {
        "severity": severity,
        "code": code,
        "message": message,
        "location": location,
        "source_artifact": location,
        "owner_layer": layer,
        "mismatch_class": mismatch_class,
        "remediation_target": remediation_target,
        "defect_class": defect_class or ("validator" if layer == "validator" else "contract"),
    }
    if document_id:
        item["document_id"] = document_id
    issues.append(item)


def _normalize(value: Any) -> str:
    text = str(value or "").casefold()
    return " ".join(re.sub(r"[^\w\s]", " ", text).split())


def _equivalent(actual: str, expected: str, aliases: dict[str, list[str]]) -> bool:
    normal_actual, normal_expected = _normalize(actual), _normalize(expected)
    if normal_actual == normal_expected:
        return True
    return normal_actual in {_normalize(item) for item in aliases.get(expected, [])}


def _read_mapping(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    data = json.loads(text) if path.suffix.lower() == ".json" else yaml.safe_load(text)
    return data if isinstance(data, dict) else {}


def _safe_path(root: Path, relative: str) -> Path | None:
    if not isinstance(relative, str) or not relative:
        return None
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def _state_path_exists(schema: dict[str, Any], path: str) -> bool:
    current: Any = schema
    for part in path.removeprefix("state.").split("."):
        if not isinstance(current, dict) or part not in current:
            return False
        current = current[part]
    return True


def _state_value(state: dict[str, Any], path: str) -> Any:
    current: Any = state
    for part in path.removeprefix("state.").split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def _node_writes(node: dict[str, Any]) -> set[str]:
    found: set[str] = set()
    on_answer = node.get("on_answer") or {}
    if not isinstance(on_answer, dict):
        return found
    branches = [on_answer, *[value for value in on_answer.values() if isinstance(value, dict)]]
    for branch in branches:
        update = branch.get("update_state") if isinstance(branch, dict) else None
        if isinstance(update, dict):
            found.update(str(path) for path in update)
    return found


def _documents(contract: dict[str, Any], issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    documents = contract.get("documents") or []
    if not isinstance(documents, list):
        _issue(issues, "XAC-CONTRACT-001", "cross_artifact_contract.documents must be a list.", "cross_artifact_contract.documents", layer="contract", mismatch_class="invalid_contract", remediation_target="cross_artifact_contract.documents")
        return []
    return [item for item in documents if isinstance(item, dict)]


def _load_runtime_state(root: Path, state_path: str | Path | None) -> tuple[dict[str, Any], str | None]:
    if state_path:
        explicit = Path(state_path).resolve()
        return (_read_mapping(explicit), str(explicit)) if explicit.exists() else ({}, None)
    candidates = [root / "reports" / "intake_report.json", root / "reports" / "run_report.json"]
    for path in candidates:
        if not path.exists():
            continue
        data = _read_mapping(path)
        if path.name == "intake_report.json":
            return data.get("state") or {}, str(path)
        return ((data.get("state") or {}).get("final") or {}), str(path)
    return {}, None


def validate_cross_artifact_contract(
    root: str | Path,
    source: dict[str, Any],
    *,
    state_path: str | Path | None = None,
) -> dict[str, Any]:
    """Validate an opt-in `cross_artifact_contract` without mutating files."""
    root = Path(root).resolve()
    contract = source.get("cross_artifact_contract")
    if contract is None:
        return {"status": "not_enabled", "mode": "not_enabled", "summary": {"errors": 0, "warnings": 0, "documents": 0}, "issues": [], "documents": []}
    issues: list[dict[str, Any]] = []
    if not isinstance(contract, dict):
        _issue(issues, "XAC-CONTRACT-002", "cross_artifact_contract must be an object.", "cross_artifact_contract", layer="contract", mismatch_class="invalid_contract", remediation_target="cross_artifact_contract")
        return {"status": "failed", "mode": "invalid", "summary": {"errors": 1, "warnings": 0, "documents": 0}, "issues": issues, "documents": []}
    mode = contract.get("mode", "strict")
    if mode not in MODES:
        _issue(issues, "XAC-CONTRACT-003", f"cross_artifact_contract.mode must be one of {sorted(MODES)}.", "cross_artifact_contract.mode", layer="contract", mismatch_class="invalid_contract", remediation_target="cross_artifact_contract.mode")
        mode = "strict"
    if contract.get("version") != "1.0":
        _issue(issues, "XAC-CONTRACT-004", "cross_artifact_contract.version must be '1.0'.", "cross_artifact_contract.version", layer="contract", mismatch_class="invalid_contract", remediation_target="cross_artifact_contract.version")
    schema = ((source.get("state") or {}).get("schema") or {})
    schema = schema if isinstance(schema, dict) else {}
    state, state_source = _load_runtime_state(root, state_path)
    nodes = {item.get("id"): item for item in source.get("nodes", []) or [] if isinstance(item, dict) and isinstance(item.get("id"), str)}
    aliases = contract.get("semantic_aliases") or {}
    aliases = aliases if isinstance(aliases, dict) else {}
    reports: list[dict[str, Any]] = []

    for index, document in enumerate(_documents(contract, issues)):
        document_id = document.get("id") or f"document[{index}]"
        location = f"cross_artifact_contract.documents[{index}]"
        report: dict[str, Any] = {"id": document_id, "source_artifacts": [], "checks": [], "status": "ok"}
        template_ref = document.get("template")
        template_path = _safe_path(root, template_ref)
        if template_path is None or not template_path.exists():
            report["status"] = "error"
            _issue(issues, "XAC-TEMPLATE-001", "Document template is missing or outside package root.", f"{location}.template", layer="template", mismatch_class="template_missing", remediation_target=str(template_ref), document_id=document_id)
            reports.append(report)
            continue
        report["source_artifacts"].append(str(template_path.relative_to(root)))
        text = template_path.read_text(encoding="utf-8")
        headings = [match.group(1) for match in HEADING.finditer(text)]
        validator = document.get("validator") or {}
        expected_headings = validator.get("expected_headings") or [] if isinstance(validator, dict) else []
        if not isinstance(expected_headings, list):
            expected_headings = []
            report["status"] = "error"
            _issue(issues, "XAC-VALIDATOR-001", "validator.expected_headings must be a list.", f"{location}.validator.expected_headings", layer="validator", mismatch_class="validator_contract_invalid", remediation_target=f"{location}.validator", document_id=document_id)
        missing = [heading for heading in expected_headings if not any(_equivalent(actual, heading, aliases) for actual in headings)]
        unexpected = [heading for heading in headings if not any(_equivalent(heading, expected, aliases) for expected in expected_headings)]
        if missing:
            report["status"] = "error"
            _issue(issues, "XAC-HEADINGS-001", "Validator expects template headings that are absent.", str(template_path.relative_to(root)), layer="validator", mismatch_class="expected_heading_missing", remediation_target=f"{location}.validator.expected_headings", document_id=document_id)
        if mode == "strict" and unexpected:
            report["status"] = "error"
            _issue(issues, "XAC-HEADINGS-002", "Template has headings not covered by validator expectations.", str(template_path.relative_to(root)), layer="template", mismatch_class="template_heading_unvalidated", remediation_target=f"{location}.validator.expected_headings", document_id=document_id)
        report["checks"].append({"kind": "headings", "actual": headings, "expected": expected_headings, "missing": missing, "unvalidated": unexpected})

        bindings = document.get("bindings") or {}
        bindings = bindings if isinstance(bindings, dict) else {}
        placeholders = [match.group(1) for match in PLACEHOLDER.finditer(text)]
        for placeholder in placeholders:
            binding = bindings.get(placeholder) or bindings.get(placeholder.removeprefix("state."))
            if not isinstance(binding, str):
                report["status"] = "error"
                _issue(issues, "XAC-BINDING-001", "Template placeholder has no declared binding.", str(template_path.relative_to(root)), layer="binding", mismatch_class="placeholder_unbound", remediation_target=f"{location}.bindings.{placeholder}", document_id=document_id)
                continue
            if not _state_path_exists(schema, binding):
                report["status"] = "error"
                _issue(issues, "XAC-BINDING-002", "Binding target is absent from state.schema.", f"{location}.bindings.{placeholder}", layer="state", mismatch_class="binding_state_path_unknown", remediation_target="state.schema", document_id=document_id)
        report["checks"].append({"kind": "bindings", "placeholders": placeholders, "bindings": bindings})

        finalization = document.get("finalization") or {}
        if not isinstance(finalization, dict):
            finalization = {}
        if finalization:
            node_id = finalization.get("node")
            writes = finalization.get("writes") or []
            writes = list(writes.values()) if isinstance(writes, dict) else writes
            writes = [str(path).removeprefix("state.") for path in writes] if isinstance(writes, list) else []
            node = nodes.get(node_id)
            actual_writes = _node_writes(node) if node else set()
            if not isinstance(node_id, str) or node_id not in nodes:
                report["status"] = "error"
                _issue(issues, "XAC-FINALIZATION-000", "Finalization must name an existing node.", f"{location}.finalization.node", layer="finalization", mismatch_class="finalization_node_unknown", remediation_target="nodes", document_id=document_id)
            if mode == "strict" and not writes:
                report["status"] = "error"
                _issue(issues, "XAC-FINALIZATION-003", "Strict finalization requires at least one declared state write.", f"{location}.finalization.writes", layer="finalization", mismatch_class="finalization_writes_undeclared", remediation_target=f"nodes[{node_id}].on_answer.update_state", document_id=document_id)
            for path in writes:
                if path not in actual_writes:
                    report["status"] = "error"
                    _issue(issues, "XAC-FINALIZATION-001", "Finalization contract names a state write absent from its node.", f"{location}.finalization.writes", layer="finalization", mismatch_class="finalization_write_missing", remediation_target=f"nodes[{node_id}].on_answer.update_state", document_id=document_id)
            rendered_ref = finalization.get("rendered_artifact")
            rendered_path = _safe_path(root, rendered_ref) if rendered_ref else None
            fields = finalization.get("rendered_fields") or writes
            fields = [str(path).removeprefix("state.") for path in fields] if isinstance(fields, list) else []
            if rendered_ref and (rendered_path is None or not rendered_path.exists()):
                report["status"] = "error"
                _issue(issues, "XAC-RENDERED-001", "Finalization declares a rendered artifact that is missing.", f"{location}.finalization.rendered_artifact", layer="rendered_output", mismatch_class="rendered_artifact_missing", remediation_target=str(rendered_ref), document_id=document_id)
            elif rendered_path is not None:
                report["source_artifacts"].append(str(rendered_path.relative_to(root)))
                rendered_text = rendered_path.read_text(encoding="utf-8")
                for path in fields:
                    value = _state_value(state, path)
                    if value in (None, "", [], {}):
                        _issue(issues, "XAC-BUSINESS-001", "Rendered-value comparison is deferred because current business state has no concrete value.", path, layer="state", mismatch_class="business_value_unavailable", remediation_target="runtime_state", severity="warning", document_id=document_id, defect_class="business_data")
                    elif _normalize(value) not in _normalize(rendered_text):
                        report["status"] = "error"
                        _issue(issues, "XAC-RENDERED-002", "Rendered artifact does not contain the finalization state value.", str(rendered_path.relative_to(root)), layer="rendered_output", mismatch_class="rendered_value_mismatch", remediation_target=str(rendered_ref), document_id=document_id)
            report["checks"].append({"kind": "finalization", "node": node_id, "expected_writes": writes, "actual_writes": sorted(actual_writes), "rendered_artifact": rendered_ref})
        reports.append(report)

    errors = [item for item in issues if item["severity"] == "error"]
    warnings = [item for item in issues if item["severity"] == "warning"]
    return {
        "status": "passed" if not errors else "failed",
        "mode": mode,
        "state_source": state_source,
        "summary": {"errors": len(errors), "warnings": len(warnings), "documents": len(reports)},
        "issues": issues,
        "documents": reports,
    }
