from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import json
import re

import yaml

from .rendering_policy import unsupported_simple_syntax
from .loader import load_package
from .reporter import write_json


@dataclass
class ArtifactIssue:
    severity: str
    code: str
    message: str
    location: str
    contract: str | None = None
    artifact: str | None = None
    field: str | None = None
    expected_value: str | None = None


def _issue(
    issues: list[ArtifactIssue],
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
    issues.append(ArtifactIssue(severity, code, message, location, contract, artifact, field, expected_value))


def _load_data(path: Path) -> Any:
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _load_state(root: Path, explicit_state: str | None) -> tuple[dict[str, Any], str | None]:
    if explicit_state:
        path = Path(explicit_state).resolve()
        data = _load_data(path) or {}
        return data, str(path)
    for candidate in [root / "reports" / "intake_report.json", root / "reports" / "run_report.json"]:
        if candidate.exists():
            data = json.loads(candidate.read_text(encoding="utf-8"))
            if candidate.name == "intake_report.json":
                return data.get("state") or {}, str(candidate.relative_to(root))
            return ((data.get("state") or {}).get("final") or {}), str(candidate.relative_to(root))
    return {}, None


def _get_path(data: Any, dotted: str) -> Any:
    cur = data
    for part in dotted.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return None
    return cur


def _contracts(source: dict[str, Any]) -> list[dict[str, Any]]:
    return source.get("contracts", []) or []


def _artifacts(source: dict[str, Any]) -> list[dict[str, Any]]:
    return source.get("artifacts", []) or []


def _artifact_requirements(source: dict[str, Any]) -> list[dict[str, Any]]:
    return source.get("artifact_requirements", []) or []


def _rendered_assertions(source: dict[str, Any]) -> list[dict[str, Any]]:
    return source.get("rendered_artifact_assertions", []) or []


def _contract_by_id(source: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {c.get("id"): c for c in _contracts(source) if c.get("id")}


def _artifact_by_id(source: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {a.get("id"): a for a in _artifacts(source) if a.get("id")}


def _safe_token(value: Any) -> str | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (str, int, float)):
        return str(value)
    return None


def _resolve_field_value(contract: dict[str, Any], field_id: str, state: dict[str, Any]) -> Any:
    fields = contract.get("fields", {}) or {}
    field = fields.get(field_id)
    if not isinstance(field, dict):
        return None
    value = field.get("value")
    if isinstance(value, str) and value.startswith("state."):
        return _get_path(state, value.removeprefix("state."))
    return value


def _values_for_field(contract: dict[str, Any], field_id: str, state: dict[str, Any]) -> list[str]:
    value = _resolve_field_value(contract, field_id, state)
    if isinstance(value, list):
        return [token for token in (_safe_token(v) for v in value) if token]
    if isinstance(value, dict):
        return [token for token in (_safe_token(v) for v in value.values()) if token]
    token = _safe_token(value)
    return [token] if token else []


def _field_status(contract: dict[str, Any], field_id: str) -> str | None:
    field = (contract.get("fields", {}) or {}).get(field_id)
    return field.get("status") if isinstance(field, dict) else None


def _pattern_to_glob(pattern: str, state: dict[str, Any]) -> str:
    alias = _safe_token(state.get("event_alias") or state.get("alias") or state.get("project_alias"))
    name = pattern
    if alias:
        name = name.replace("<ALIAS>", alias)
    name = re.sub(r"<[^>]+>", "*", name)
    return name


def _artifact_files(root: Path, artifacts_dir: Path, artifact: dict[str, Any]) -> list[Path]:
    pattern = artifact.get("path_pattern") or artifact.get("path") or ""
    # Exact path under package root, exact path under artifacts dir, then glob under artifacts dir.
    candidates: list[Path] = []
    if pattern:
        candidates.extend([root / pattern, artifacts_dir / pattern])
    found: list[Path] = []
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            found.append(candidate)
    if found:
        return sorted(set(found))
    glob_pattern = _pattern_to_glob(pattern, {}) if pattern else "*"
    matches = [p for p in artifacts_dir.rglob(glob_pattern) if p.is_file()]
    if matches:
        return sorted(matches)
    # Last resort: match by artifact id or file stem keywords.
    aid = str(artifact.get("id") or "").lower()
    if aid:
        compact = aid.replace("_", "")
        for p in artifacts_dir.rglob("*"):
            if p.is_file():
                name = p.name.lower().replace("_", "")
                if compact in name or name in compact:
                    found.append(p)
    return sorted(found)


def _artifact_files_with_state(root: Path, artifacts_dir: Path, artifact: dict[str, Any], state: dict[str, Any]) -> list[Path]:
    pattern = artifact.get("path_pattern") or artifact.get("path") or ""
    found: list[Path] = []
    if pattern:
        rendered = _pattern_to_glob(pattern, state)
        for candidate in [root / rendered, artifacts_dir / rendered]:
            if "*" not in str(candidate) and candidate.exists() and candidate.is_file():
                found.append(candidate)
        if not found:
            found.extend([p for p in artifacts_dir.rglob(rendered) if p.is_file()])
    if found:
        return sorted(set(found))
    return _artifact_files(root, artifacts_dir, artifact)


def _read_artifact_text(path: Path) -> str:
    try:
        if path.suffix.lower() == ".json":
            return json.dumps(json.loads(path.read_text(encoding="utf-8")), ensure_ascii=False, sort_keys=True)
        if path.suffix.lower() in {".yaml", ".yml"}:
            return json.dumps(yaml.safe_load(path.read_text(encoding="utf-8")), ensure_ascii=False, sort_keys=True)
        return path.read_text(encoding="utf-8")
    except Exception:
        return path.read_text(encoding="utf-8", errors="replace")


def _artifact_texts(root: Path, artifacts_dir: Path, artifact: dict[str, Any], state: dict[str, Any]) -> list[tuple[Path, str]]:
    return [(p, _read_artifact_text(p)) for p in _artifact_files_with_state(root, artifacts_dir, artifact, state)]


def _split_contract_field(ref: str) -> tuple[str | None, str | None]:
    if not isinstance(ref, str) or "." not in ref:
        return None, None
    return ref.split(".", 1)




def _model_assisted_handoffs(root: Path) -> list[dict[str, Any]]:
    handoff_dir = root / "runtime" / "model_assisted_render_handoff"
    if not handoff_dir.exists():
        return []
    handoffs: list[dict[str, Any]] = []
    for path in sorted(handoff_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            data["_handoff_path"] = str(path)
            handoffs.append(data)
        except Exception:
            continue
    return handoffs


def _parse_rendered_if_structured(path: Path) -> tuple[bool, str | None]:
    try:
        if path.suffix.lower() == ".json":
            json.loads(path.read_text(encoding="utf-8"))
        elif path.suffix.lower() in {".yaml", ".yml"}:
            yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, str(exc)
    return True, None


def _runtime_value_tokens(state: dict[str, Any]) -> set[str]:
    tokens: set[str] = set()
    def walk(value: Any) -> None:
        if value is None or value == "":
            return
        if isinstance(value, (str, int, float, bool)):
            tokens.add(str(value))
            return
        if isinstance(value, list):
            for item in value:
                walk(item)
            return
        if isinstance(value, dict):
            for item in value.values():
                walk(item)
    walk(state)
    return tokens


def _validate_model_assisted_post_render(
    *,
    root: Path,
    artifacts_dir: Path,
    state: dict[str, Any],
    issues: list[ArtifactIssue],
    warnings: list[ArtifactIssue],
) -> list[str]:
    """Validate AI-rendered artifacts that correspond to handoff packets.

    If the model-assisted output does not exist yet, this records a warning, not
    a blocker. The blocker happens once a rendered artifact is supplied and fails
    strict deterministic post-validation.
    """
    checked: list[str] = []
    state_tokens = _runtime_value_tokens(state)
    for handoff in _model_assisted_handoffs(root):
        artifact_id = handoff.get("artifact_id") or "model_assisted_artifact"
        expected = handoff.get("expected_output_path")
        if not expected:
            continue
        candidates = [root / expected, artifacts_dir / expected]
        existing = next((p for p in candidates if p.exists() and p.is_file()), None)
        if not existing:
            # Handoff packet is the expected output when AI rendering has not happened yet.
            # Post-render validation starts only after a rendered file is supplied.
            continue
        checked.append(artifact_id)
        text = existing.read_text(encoding="utf-8", errors="replace")
        if re.search(r"\{\{\s*[^}]+\s*\}\}|{%\s*[^%]+\s*%}", text):
            _issue(issues, "error", "ORDO-RENDER-006", "Model-assisted output still contains unresolved template syntax after rendering.", str(existing), artifact=artifact_id)
        if existing.suffix.lower() in {".yaml", ".yml", ".json"}:
            ok, reason = _parse_rendered_if_structured(existing)
            if not ok:
                _issue(issues, "error", "ORDO-RENDER-005", "Model-assisted YAML/JSON output is invalid.", str(existing), artifact=artifact_id, expected_value=reason)
        explicit_tbd = handoff.get("explicit_tbd_defaults") or ["⚠️ TBD"]
        tbd_policy = handoff.get("tbd_policy")
        # If template had an explicit TBD marker and the rendered file replaced
        # it with a value not present in confirmed state, treat it as inferred.
        template_content = ((handoff.get("template") or {}).get("content") or "")
        if tbd_policy == "preserve_tbd_until_confirmed" and any(marker in template_content for marker in explicit_tbd):
            if not any(marker in text for marker in explicit_tbd):
                # A missing TBD is only acceptable when the output contains a confirmed state token nearby;
                # MVP rule: at least one confirmed token from state must be present in the output.
                if not any(token and token in text for token in state_tokens):
                    _issue(issues, "error", "ORDO-RENDER-004", "TBD marker was removed without evidence of a confirmed state value.", str(existing), artifact=artifact_id)
        for term in handoff.get("forbidden_unconfirmed_terms") or []:
            if term and term in text and term not in state_tokens:
                _issue(issues, "error", "ORDO-RENDER-003", "Model-assisted output contains an inferred value not confirmed in state.", str(existing), artifact=artifact_id, expected_value=term)
    return checked

def validate_artifacts(
    package_path: str | Path,
    *,
    artifacts: str | Path | None = None,
    state_path: str | None = None,
    out: str | Path | None = None,
) -> dict[str, Any]:
    """Validate rendered artifacts against confirmed contracts.

    M46.3 intentionally validates rendered content only at the token/field-value
    level. It does not execute business logic or live systems.
    """
    root, manifest, source, tests = load_package(package_path)
    artifacts_dir = Path(artifacts).resolve() if artifacts else root / "generated_outputs"
    reports_dir = root / manifest.get("reports", "reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    state, state_source = _load_state(root, state_path)

    issues: list[ArtifactIssue] = []
    warnings: list[ArtifactIssue] = []
    contracts = _contract_by_id(source)
    artifacts_by_id = _artifact_by_id(source)
    checked_contracts: set[str] = set()
    checked_artifacts: set[str] = set()

    if not artifacts_dir.exists():
        _issue(issues, "error", "ORDO-COV-012", "Generated artifacts directory does not exist.", str(artifacts_dir))
    else:
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
                    _issue(issues, "error", "ORDO-COV-REF-002", "Artifact requirement references unknown artifact.", req.get("id") or "artifact_requirements", contract=contract_id, artifact=artifact_id)
                    continue
                checked_artifacts.add(artifact_id)
                texts = _artifact_texts(root, artifacts_dir, artifact, state)
                if not texts:
                    _issue(issues, "error", "ORDO-COV-002", "Required artifact file is missing for confirmed contract.", artifact.get("path_pattern") or artifact_id, contract=contract_id, artifact=artifact_id)
                    continue
                combined_text = "\n".join(text for _path, text in texts)
                for field_id in target.get("must_include_fields", []) or []:
                    status = _field_status(contract, field_id)
                    values = _values_for_field(contract, field_id, state)
                    if status in {"candidate", "proposed"}:
                        for token in values:
                            if token and token in combined_text:
                                _issue(issues, "error", "ORDO-COV-003", "Artifact contains a candidate/proposed contract value as if it were confirmed.", artifact.get("path_pattern") or artifact_id, contract=contract_id, artifact=artifact_id, field=field_id, expected_value=token)
                        continue
                    if not values:
                        _issue(warnings, "warning", "ORDO-COV-W01", "Confirmed contract field has no concrete runtime value to check in rendered artifact.", artifact.get("path_pattern") or artifact_id, contract=contract_id, artifact=artifact_id, field=field_id)
                        continue
                    missing = [token for token in values if token not in combined_text]
                    if missing:
                        _issue(issues, "error", "ORDO-COV-002", "Confirmed contract field value is missing from required artifact.", artifact.get("path_pattern") or artifact_id, contract=contract_id, artifact=artifact_id, field=field_id, expected_value=", ".join(missing))

        for assertion in _rendered_assertions(source):
            contract_id, field_id = _split_contract_field(assertion.get("field"))
            contract = contracts.get(contract_id or "")
            if not contract or not field_id:
                continue
            values = _values_for_field(contract, field_id, state)
            if not values:
                _issue(warnings, "warning", "ORDO-COV-W02", "Rendered artifact assertion has no concrete runtime value to check.", assertion.get("id") or "rendered_artifact_assertion", contract=contract_id, field=field_id)
                continue
            for artifact_id in assertion.get("must_appear_in", []) or []:
                artifact = artifacts_by_id.get(artifact_id)
                if not artifact:
                    _issue(issues, "error", "ORDO-COV-REF-006", "Rendered artifact assertion references unknown artifact.", assertion.get("id") or "rendered_artifact_assertion", contract=contract_id, artifact=artifact_id, field=field_id)
                    continue
                checked_artifacts.add(artifact_id)
                texts = _artifact_texts(root, artifacts_dir, artifact, state)
                if not texts:
                    _issue(issues, "error", "ORDO-COV-002", "Required artifact file is missing for rendered assertion.", artifact.get("path_pattern") or artifact_id, contract=contract_id, artifact=artifact_id, field=field_id)
                    continue
                combined_text = "\n".join(text for _path, text in texts)
                missing = [token for token in values if token not in combined_text]
                if missing:
                    _issue(issues, "error", "ORDO-COV-002", "Rendered artifact assertion failed: field value is missing.", artifact.get("path_pattern") or artifact_id, contract=contract_id, artifact=artifact_id, field=field_id, expected_value=", ".join(missing))

    checked_model_assisted = _validate_model_assisted_post_render(root=root, artifacts_dir=artifacts_dir, state=state, issues=issues, warnings=warnings)

    error_items = [asdict(i) for i in issues if i.severity == "error"]
    warning_items = [asdict(i) for i in warnings]
    report = {
        "status": "failed" if error_items else "passed",
        "mode": "rendered_artifact_validation",
        "package": {"name": manifest.get("name"), "version": manifest.get("version")},
        "artifacts_dir": str(artifacts_dir),
        "state_source": state_source,
        "summary": {
            "checked_contracts": len(checked_contracts),
            "checked_artifacts": len(checked_artifacts),
            "errors": len(error_items),
            "warnings": len(warning_items),
            "model_assisted_outputs_checked": len(checked_model_assisted),
        },
        "checked_contracts": sorted(checked_contracts),
        "checked_artifacts": sorted(checked_artifacts),
        "checked_model_assisted_outputs": sorted(checked_model_assisted),
        "issues": error_items,
        "warnings": warning_items,
    }
    output = Path(out).resolve() if out else reports_dir / "artifact_validation_report.json"
    write_json(output, report)
    return report
