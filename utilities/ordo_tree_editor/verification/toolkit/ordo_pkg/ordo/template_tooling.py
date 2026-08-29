from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

RENDER_MODES = {"deterministic", "model_rendered", "hybrid"}
REVIEW_MODES = {"none", "standard", "strict", "custom"}
REQUIRED_FIELDS = {
    "template_id",
    "version",
    "render_mode",
    "input_schema",
    "output_contract",
    "review_profile",
    "compatibility",
}


def _load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    return yaml.safe_load(text)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_template_contract(path: str | Path) -> dict[str, Any]:
    contract_path = Path(path).resolve()
    issues: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    if not contract_path.is_file():
        return {
            "status": "failed",
            "contract": str(contract_path),
            "issues": [{"code": "TEMPLATE_CONTRACT_NOT_FOUND", "message": "Template contract file does not exist."}],
            "warnings": [],
        }

    try:
        data = _load(contract_path)
    except Exception as exc:
        return {
            "status": "failed",
            "contract": str(contract_path),
            "issues": [{"code": "TEMPLATE_CONTRACT_PARSE_ERROR", "message": str(exc)}],
            "warnings": [],
        }

    if not isinstance(data, dict):
        issues.append({"code": "TEMPLATE_CONTRACT_NOT_MAPPING", "message": "Template contract must be a mapping."})
        data = {}

    missing = sorted(REQUIRED_FIELDS - set(data))
    for field in missing:
        issues.append({"code": "TEMPLATE_REQUIRED_FIELD_MISSING", "message": f"Missing required field: {field}"})

    template_id = data.get("template_id")
    if template_id is not None and (not isinstance(template_id, str) or "." not in template_id):
        issues.append({"code": "TEMPLATE_ID_INVALID", "message": "template_id must be a dotted stable identifier."})

    version = data.get("version")
    if version is not None and (not isinstance(version, str) or version.count(".") != 2):
        issues.append({"code": "TEMPLATE_VERSION_INVALID", "message": "version must use semantic version form MAJOR.MINOR.PATCH."})

    render_mode = data.get("render_mode")
    if render_mode is not None and render_mode not in RENDER_MODES:
        issues.append({"code": "TEMPLATE_RENDER_MODE_INVALID", "message": f"render_mode must be one of {sorted(RENDER_MODES)}."})

    input_schema = data.get("input_schema")
    if input_schema is not None and not isinstance(input_schema, dict):
        issues.append({"code": "TEMPLATE_INPUT_SCHEMA_INVALID", "message": "input_schema must be a mapping."})

    output_contract = data.get("output_contract")
    if output_contract is not None and not isinstance(output_contract, dict):
        issues.append({"code": "TEMPLATE_OUTPUT_CONTRACT_INVALID", "message": "output_contract must be a mapping."})

    review_profile = data.get("review_profile")
    if isinstance(review_profile, str):
        review_mode = review_profile
    elif isinstance(review_profile, dict):
        review_mode = review_profile.get("mode")
    else:
        review_mode = None
    if review_profile is not None and review_mode not in REVIEW_MODES:
        issues.append({"code": "TEMPLATE_REVIEW_PROFILE_INVALID", "message": f"review profile mode must be one of {sorted(REVIEW_MODES)}."})

    compatibility = data.get("compatibility")
    if compatibility is not None and not isinstance(compatibility, dict):
        issues.append({"code": "TEMPLATE_COMPATIBILITY_INVALID", "message": "compatibility must be a mapping."})

    if render_mode in {"model_rendered", "hybrid"}:
        model_contract = data.get("model_contract")
        if not isinstance(model_contract, dict):
            issues.append({"code": "TEMPLATE_MODEL_CONTRACT_REQUIRED", "message": "model_contract is required for model_rendered and hybrid templates."})
        else:
            for field in ("prompt_ref", "provenance_required"):
                if field not in model_contract:
                    issues.append({"code": "TEMPLATE_MODEL_CONTRACT_INCOMPLETE", "message": f"model_contract missing: {field}"})

    if render_mode == "deterministic" and data.get("model_contract"):
        warnings.append({"code": "TEMPLATE_UNUSED_MODEL_CONTRACT", "message": "deterministic template declares model_contract; it will not be used."})

    return {
        "status": "passed" if not issues else "failed",
        "contract": str(contract_path),
        "template_id": data.get("template_id"),
        "version": data.get("version"),
        "render_mode": data.get("render_mode"),
        "sha256": _digest(contract_path),
        "issues": issues,
        "warnings": warnings,
    }

REGISTRY_STATUSES = {"active", "deprecated", "experimental", "disabled"}


def validate_template_registry(path: str | Path) -> dict[str, Any]:
    registry_path = Path(path).resolve()
    issues: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    entries_report: list[dict[str, Any]] = []
    if not registry_path.is_file():
        return {"status":"failed","registry":str(registry_path),"issues":[{"code":"TEMPLATE_REGISTRY_NOT_FOUND","message":"Template registry file does not exist."}],"warnings":[],"entries":[]}
    try:
        data = _load(registry_path)
    except Exception as exc:
        return {"status":"failed","registry":str(registry_path),"issues":[{"code":"TEMPLATE_REGISTRY_PARSE_ERROR","message":str(exc)}],"warnings":[],"entries":[]}
    if not isinstance(data, dict):
        issues.append({"code":"TEMPLATE_REGISTRY_NOT_MAPPING","message":"Template registry must be a mapping."})
        data = {}
    if data.get("schema_version") != "ordo.template.registry.v1":
        issues.append({"code":"TEMPLATE_REGISTRY_SCHEMA_VERSION_INVALID","message":"schema_version must be ordo.template.registry.v1."})
    entries = data.get("templates")
    if not isinstance(entries, list):
        issues.append({"code":"TEMPLATE_REGISTRY_ENTRIES_INVALID","message":"templates must be a list."})
        entries = []
    seen_keys: set[tuple[str, str]] = set()
    active_versions: dict[str, list[str]] = {}
    root = registry_path.parent
    for index, entry in enumerate(entries):
        prefix = f"templates[{index}]"
        if not isinstance(entry, dict):
            issues.append({"code":"TEMPLATE_REGISTRY_ENTRY_INVALID","message":f"{prefix} must be a mapping."})
            continue
        tid, version = entry.get("template_id"), entry.get("version")
        status = entry.get("status")
        contract_ref = entry.get("contract_ref")
        if not isinstance(tid, str) or "." not in tid:
            issues.append({"code":"TEMPLATE_REGISTRY_ID_INVALID","message":f"{prefix}.template_id is invalid."})
        if not isinstance(version, str) or version.count(".") != 2:
            issues.append({"code":"TEMPLATE_REGISTRY_VERSION_INVALID","message":f"{prefix}.version must be semantic version."})
        key = (str(tid), str(version))
        if key in seen_keys:
            issues.append({"code":"TEMPLATE_REGISTRY_DUPLICATE_ENTRY","message":f"Duplicate template/version: {tid}@{version}."})
        seen_keys.add(key)
        if status not in REGISTRY_STATUSES:
            issues.append({"code":"TEMPLATE_REGISTRY_STATUS_INVALID","message":f"{prefix}.status must be one of {sorted(REGISTRY_STATUSES)}."})
        if status == "active" and isinstance(tid, str) and isinstance(version, str):
            active_versions.setdefault(tid, []).append(version)
        if not isinstance(contract_ref, str) or not contract_ref:
            issues.append({"code":"TEMPLATE_REGISTRY_CONTRACT_REF_MISSING","message":f"{prefix}.contract_ref is required."})
            continue
        contract_path = (root / contract_ref).resolve()
        try:
            contract_path.relative_to(root.resolve())
        except ValueError:
            issues.append({"code":"TEMPLATE_REGISTRY_PATH_ESCAPE","message":f"{prefix}.contract_ref escapes the registry root."})
            continue
        contract_report = validate_template_contract(contract_path)
        entries_report.append({"template_id":tid,"version":version,"status":status,"contract":str(contract_path),"contract_status":contract_report["status"]})
        if contract_report["status"] != "passed":
            issues.append({"code":"TEMPLATE_REGISTRY_CONTRACT_INVALID","message":f"Contract failed validation: {contract_ref}."})
            continue
        if contract_report.get("template_id") != tid or contract_report.get("version") != version:
            issues.append({"code":"TEMPLATE_REGISTRY_METADATA_MISMATCH","message":f"Registry metadata differs from contract for {tid}@{version}."})
        expected_sha = entry.get("sha256")
        if expected_sha and expected_sha != contract_report.get("sha256"):
            issues.append({"code":"TEMPLATE_REGISTRY_STALE_CHECKSUM","message":f"Checksum mismatch for {tid}@{version}."})
        if entry.get("render_mode") and entry.get("render_mode") != contract_report.get("render_mode"):
            issues.append({"code":"TEMPLATE_REGISTRY_RENDER_MODE_MISMATCH","message":f"render_mode differs from contract for {tid}@{version}."})
        usages = entry.get("used_by", [])
        if usages is not None and not isinstance(usages, list):
            issues.append({"code":"TEMPLATE_REGISTRY_USAGE_INVALID","message":f"{prefix}.used_by must be a list."})
        if status == "active" and not usages:
            warnings.append({"code":"TEMPLATE_REGISTRY_ACTIVE_UNUSED","message":f"Active template {tid}@{version} has no declared usage."})
        if status == "deprecated" and not entry.get("replaced_by"):
            warnings.append({"code":"TEMPLATE_REGISTRY_DEPRECATED_NO_REPLACEMENT","message":f"Deprecated template {tid}@{version} has no replacement."})
    for tid, versions in active_versions.items():
        if len(versions) > 1:
            issues.append({"code":"TEMPLATE_REGISTRY_MULTIPLE_ACTIVE_VERSIONS","message":f"Multiple active versions for {tid}: {sorted(versions)}."})
    return {
        "status":"passed" if not issues else "failed",
        "registry":str(registry_path),
        "schema_version":data.get("schema_version"),
        "entry_count":len(entries),
        "sha256":_digest(registry_path),
        "issues":issues,
        "warnings":warnings,
        "entries":entries_report,
    }


def _lookup(data: dict[str, Any], dotted: str) -> Any:
    value: Any = data
    for part in dotted.split('.'):
        if not isinstance(value, dict) or part not in value:
            raise KeyError(dotted)
        value = value[part]
    return value


def _render_text(template_text: str, inputs: dict[str, Any]) -> str:
    import re
    pattern = re.compile(r"\{\{\s*([A-Za-z0-9_.-]+)\s*\}\}")
    missing: list[str] = []
    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        try:
            value = _lookup(inputs, key)
        except KeyError:
            missing.append(key)
            return match.group(0)
        if isinstance(value, (dict, list, bool)) or value is None:
            return json.dumps(value, ensure_ascii=False, indent=2)
        return str(value)
    rendered = pattern.sub(repl, template_text)
    if missing:
        raise ValueError(f"Missing template inputs: {', '.join(sorted(set(missing)))}")
    return rendered


def _validate_render_inputs(contract: dict[str, Any], inputs: Any) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if not isinstance(inputs, dict):
        return [{"code": "TEMPLATE_RENDER_INPUT_NOT_MAPPING", "message": "Render input must be a mapping."}]
    schema = contract.get("input_schema") or {}
    required = schema.get("required") or []
    for field in required:
        if field not in inputs:
            issues.append({"code": "TEMPLATE_RENDER_REQUIRED_INPUT_MISSING", "message": f"Missing required input: {field}"})
    properties = schema.get("properties") or {}
    type_map = {"string": str, "array": list, "object": dict, "boolean": bool, "integer": int, "number": (int, float)}
    for field, spec in properties.items():
        if field not in inputs or not isinstance(spec, dict) or not spec.get("type"):
            continue
        expected = type_map.get(spec["type"])
        if expected and not isinstance(inputs[field], expected):
            issues.append({"code": "TEMPLATE_RENDER_INPUT_TYPE_INVALID", "message": f"Input {field} must be {spec['type']}."})
    return issues


def render_template(contract_path: str | Path, input_path: str | Path, output_dir: str | Path) -> dict[str, Any]:
    contract_file = Path(contract_path).resolve()
    input_file = Path(input_path).resolve()
    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    contract_report = validate_template_contract(contract_file)
    if contract_report["status"] != "passed":
        return {"status": "failed", "issues": contract_report["issues"], "contract": str(contract_file)}
    try:
        contract = _load(contract_file)
        inputs = _load(input_file)
    except Exception as exc:
        return {"status": "failed", "issues": [{"code": "TEMPLATE_RENDER_INPUT_PARSE_ERROR", "message": str(exc)}]}
    issues = _validate_render_inputs(contract, inputs)
    if issues:
        return {"status": "failed", "issues": issues, "contract": str(contract_file), "input": str(input_file)}

    mode = contract["render_mode"]
    output_contract = contract.get("output_contract") or {}
    extension = {"markdown": ".md", "json": ".json", "yaml": ".yaml", "text": ".txt"}.get(output_contract.get("format"), ".txt")
    artifact_name = output_contract.get("filename") or f"{contract['template_id'].replace('.', '_')}{extension}"
    artifact_path = out_dir / artifact_name
    job_path = out_dir / "model_render_job.json"
    provenance = {
        "template_id": contract["template_id"],
        "version": contract["version"],
        "render_mode": mode,
        "contract_sha256": _digest(contract_file),
        "input_sha256": _digest(input_file),
    }

    template_ref = contract.get("template_ref")
    template_text = None
    if template_ref:
        source = (contract_file.parent / template_ref).resolve()
        try:
            source.relative_to(contract_file.parent.resolve())
        except ValueError:
            return {"status":"failed","issues":[{"code":"TEMPLATE_RENDER_PATH_ESCAPE","message":"template_ref escapes contract directory."}]}
        if not source.is_file():
            return {"status":"failed","issues":[{"code":"TEMPLATE_RENDER_SOURCE_NOT_FOUND","message":f"Missing template source: {template_ref}"}]}
        template_text = source.read_text(encoding="utf-8")
        provenance["template_source_sha256"] = _digest(source)

    artifacts: list[str] = []
    if mode == "deterministic":
        if template_text is None:
            return {"status":"failed","issues":[{"code":"TEMPLATE_RENDER_SOURCE_REQUIRED","message":"deterministic templates require template_ref."}]}
        try:
            artifact_path.write_text(_render_text(template_text, inputs), encoding="utf-8")
        except ValueError as exc:
            return {"status":"failed","issues":[{"code":"TEMPLATE_RENDER_PLACEHOLDER_UNRESOLVED","message":str(exc)}]}
        artifacts.append(str(artifact_path))
    else:
        scaffold_path = None
        if mode == "hybrid":
            if template_text is None:
                return {"status":"failed","issues":[{"code":"TEMPLATE_RENDER_SOURCE_REQUIRED","message":"hybrid templates require template_ref scaffold."}]}
            scaffold_path = artifact_path
            try:
                scaffold_path.write_text(_render_text(template_text, inputs), encoding="utf-8")
            except ValueError as exc:
                return {"status":"failed","issues":[{"code":"TEMPLATE_RENDER_PLACEHOLDER_UNRESOLVED","message":str(exc)}]}
            artifacts.append(str(scaffold_path))
        job = {
            "schema_version": "ordo.template.render_job.v1",
            "job_type": "model_render" if mode == "model_rendered" else "hybrid_completion",
            "template": provenance,
            "prompt_ref": (contract.get("model_contract") or {}).get("prompt_ref"),
            "input_snapshot": inputs,
            "output_contract": output_contract,
            "review_profile": contract.get("review_profile"),
            "scaffold_path": str(scaffold_path) if scaffold_path else None,
            "provenance_required": bool((contract.get("model_contract") or {}).get("provenance_required")),
        }
        job_path.write_text(json.dumps(job, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        artifacts.append(str(job_path))

    evidence = {
        "schema_version": "ordo.template.render_evidence.v1",
        "status": "passed",
        "mode": mode,
        "provenance": provenance,
        "artifacts": artifacts,
        "issues": [],
    }
    evidence_path = out_dir / "render_evidence.json"
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    evidence["evidence_path"] = str(evidence_path)
    return evidence


REVIEW_SEVERITIES = {"info", "warning", "error"}


def _markdown_sections(text: str) -> set[str]:
    import re
    sections: set[str] = set()
    for line in text.splitlines():
        m = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if m:
            sections.add(m.group(1).strip().casefold())
    return sections


def review_template_artifact(
    contract_path: str | Path,
    artifact_path: str | Path,
    *,
    render_evidence_path: str | Path | None = None,
    reviewer: str = "ordo-template-review-engine",
) -> dict[str, Any]:
    contract_file = Path(contract_path).resolve()
    artifact_file = Path(artifact_path).resolve()
    checks: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []

    contract_report = validate_template_contract(contract_file)
    if contract_report["status"] != "passed":
        return {
            "schema_version": "ordo.template.review_evidence.v1",
            "status": "failed",
            "decision": "reject",
            "contract": str(contract_file),
            "artifact": str(artifact_file),
            "checks": [],
            "findings": contract_report.get("issues", []),
            "reviewer": reviewer,
        }
    contract = _load(contract_file)
    profile = contract.get("review_profile")
    if isinstance(profile, str):
        profile = {"mode": profile}
    profile = profile or {"mode": "standard"}
    mode = profile.get("mode", "standard")

    if not artifact_file.is_file():
        findings.append({"code": "TEMPLATE_REVIEW_ARTIFACT_NOT_FOUND", "severity": "error", "message": "Rendered artifact does not exist."})
    else:
        raw = artifact_file.read_bytes()
        text = raw.decode("utf-8", errors="replace")
        checks.append({"check_id": "artifact_exists", "status": "passed", "evidence": str(artifact_file)})
        checks.append({"check_id": "artifact_nonempty", "status": "passed" if raw else "failed", "evidence": {"size_bytes": len(raw)}})
        if not raw:
            findings.append({"code": "TEMPLATE_REVIEW_EMPTY_ARTIFACT", "severity": "error", "message": "Rendered artifact is empty."})

        output_contract = contract.get("output_contract") or {}
        expected_format = output_contract.get("format")
        suffix_map = {"markdown": {".md", ".markdown"}, "json": {".json"}, "yaml": {".yaml", ".yml"}, "text": {".txt"}}
        allowed = suffix_map.get(expected_format)
        if allowed:
            ok = artifact_file.suffix.lower() in allowed
            checks.append({"check_id": "output_format", "status": "passed" if ok else "failed", "evidence": {"expected": expected_format, "actual_suffix": artifact_file.suffix}})
            if not ok:
                findings.append({"code": "TEMPLATE_REVIEW_OUTPUT_FORMAT_MISMATCH", "severity": "error", "message": f"Expected {expected_format} artifact."})

        max_bytes = output_contract.get("max_bytes") or profile.get("max_bytes")
        if isinstance(max_bytes, int):
            ok = len(raw) <= max_bytes
            checks.append({"check_id": "max_bytes", "status": "passed" if ok else "failed", "evidence": {"size_bytes": len(raw), "max_bytes": max_bytes}})
            if not ok:
                findings.append({"code": "TEMPLATE_REVIEW_ARTIFACT_TOO_LARGE", "severity": "error", "message": f"Artifact exceeds {max_bytes} bytes."})

        required_sections = output_contract.get("required_sections") or []
        if required_sections:
            if expected_format == "markdown":
                actual = _markdown_sections(text)
                missing = [name for name in required_sections if str(name).casefold() not in actual]
            else:
                missing = []
                try:
                    parsed = json.loads(text) if expected_format == "json" else yaml.safe_load(text)
                except Exception:
                    parsed = None
                if isinstance(parsed, dict):
                    missing = [name for name in required_sections if name not in parsed]
                else:
                    missing = list(required_sections)
            checks.append({"check_id": "required_sections", "status": "passed" if not missing else "failed", "evidence": {"required": required_sections, "missing": missing}})
            for name in missing:
                findings.append({"code": "TEMPLATE_REVIEW_REQUIRED_SECTION_MISSING", "severity": "error", "location": str(name), "message": f"Missing required section: {name}"})

        forbidden = profile.get("forbidden_content") or output_contract.get("forbidden_content") or []
        for token in forbidden:
            if str(token).casefold() in text.casefold():
                findings.append({"code": "TEMPLATE_REVIEW_FORBIDDEN_CONTENT", "severity": "error", "location": str(token), "message": f"Forbidden content detected: {token}"})
        checks.append({"check_id": "forbidden_content", "status": "passed" if not any(f.get("code")=="TEMPLATE_REVIEW_FORBIDDEN_CONTENT" for f in findings) else "failed", "evidence": {"patterns": forbidden}})

        if expected_format in {"json", "yaml"}:
            try:
                json.loads(text) if expected_format == "json" else yaml.safe_load(text)
                parse_ok = True
            except Exception as exc:
                parse_ok = False
                findings.append({"code": "TEMPLATE_REVIEW_OUTPUT_PARSE_ERROR", "severity": "error", "message": str(exc)})
            checks.append({"check_id": "output_parse", "status": "passed" if parse_ok else "failed"})

    provenance: dict[str, Any] = {}
    if render_evidence_path:
        evidence_file = Path(render_evidence_path).resolve()
        if not evidence_file.is_file():
            findings.append({"code": "TEMPLATE_REVIEW_RENDER_EVIDENCE_NOT_FOUND", "severity": "error", "message": "Render evidence file does not exist."})
            checks.append({"check_id": "render_evidence", "status": "failed"})
        else:
            try:
                render_evidence = _load(evidence_file)
            except Exception as exc:
                render_evidence = None
                findings.append({"code": "TEMPLATE_REVIEW_RENDER_EVIDENCE_PARSE_ERROR", "severity": "error", "message": str(exc)})
            if isinstance(render_evidence, dict):
                provenance = render_evidence.get("provenance") or {}
                expected_contract_sha = _digest(contract_file)
                contract_ok = provenance.get("contract_sha256") == expected_contract_sha
                artifact_list = [str(Path(x).resolve()) for x in render_evidence.get("artifacts", []) if isinstance(x, str)]
                artifact_ok = str(artifact_file) in artifact_list
                checks.append({"check_id": "render_evidence_contract", "status": "passed" if contract_ok else "failed"})
                checks.append({"check_id": "render_evidence_artifact_link", "status": "passed" if artifact_ok else "failed"})
                if not contract_ok:
                    findings.append({"code": "TEMPLATE_REVIEW_CONTRACT_PROVENANCE_MISMATCH", "severity": "error", "message": "Render evidence contract checksum does not match reviewed contract."})
                if not artifact_ok:
                    findings.append({"code": "TEMPLATE_REVIEW_ARTIFACT_NOT_IN_RENDER_EVIDENCE", "severity": "error", "message": "Artifact is not declared by render evidence."})
    elif mode == "strict":
        findings.append({"code": "TEMPLATE_REVIEW_RENDER_EVIDENCE_REQUIRED", "severity": "error", "message": "Strict review requires render evidence."})
        checks.append({"check_id": "render_evidence", "status": "failed"})

    error_count = sum(1 for f in findings if f.get("severity", "error") == "error")
    warning_count = sum(1 for f in findings if f.get("severity") == "warning")
    decision = "approve" if error_count == 0 else "reject"
    status = "passed" if decision == "approve" else "failed"
    evidence = {
        "schema_version": "ordo.template.review_evidence.v1",
        "status": status,
        "decision": decision,
        "review_mode": mode,
        "template_id": contract.get("template_id"),
        "template_version": contract.get("version"),
        "contract": str(contract_file),
        "contract_sha256": _digest(contract_file),
        "artifact": str(artifact_file),
        "artifact_sha256": _digest(artifact_file) if artifact_file.is_file() else None,
        "render_evidence": str(Path(render_evidence_path).resolve()) if render_evidence_path else None,
        "provenance": provenance,
        "summary": {"checks": len(checks), "errors": error_count, "warnings": warning_count},
        "checks": checks,
        "findings": findings,
        "reviewer": reviewer,
    }
    return evidence


REVIEW_RANK = {"none": 0, "standard": 1, "custom": 2, "strict": 3}


def _review_mode(contract: dict[str, Any]) -> str:
    profile = contract.get("review_profile")
    if isinstance(profile, str):
        return profile
    if isinstance(profile, dict):
        return str(profile.get("mode", "standard"))
    return "standard"


def diff_template_versions(old_path: str | Path, new_path: str | Path) -> dict[str, Any]:
    old_file, new_file = Path(old_path).resolve(), Path(new_path).resolve()
    old_report, new_report = validate_template_contract(old_file), validate_template_contract(new_file)
    issues: list[dict[str, str]] = []
    if old_report["status"] != "passed":
        issues.append({"code": "TEMPLATE_DIFF_OLD_CONTRACT_INVALID", "message": "Old contract failed validation."})
    if new_report["status"] != "passed":
        issues.append({"code": "TEMPLATE_DIFF_NEW_CONTRACT_INVALID", "message": "New contract failed validation."})
    if issues:
        return {"schema_version":"ordo.template.version_diff.v1","status":"failed","decision":"block","issues":issues,"changes":[]}

    old, new = _load(old_file), _load(new_file)
    changes: list[dict[str, Any]] = []
    def add(path: str, kind: str, before: Any, after: Any, breaking: bool, reason: str):
        changes.append({"path":path,"kind":kind,"before":before,"after":after,"breaking":breaking,"reason":reason})

    if old.get("template_id") != new.get("template_id"):
        add("template_id","changed",old.get("template_id"),new.get("template_id"),True,"Stable template identity changed.")
    if old.get("render_mode") != new.get("render_mode"):
        add("render_mode","changed",old.get("render_mode"),new.get("render_mode"),True,"Renderer execution contract changed.")

    old_out, new_out = old.get("output_contract") or {}, new.get("output_contract") or {}
    if old_out.get("format") != new_out.get("format"):
        add("output_contract.format","changed",old_out.get("format"),new_out.get("format"),True,"Output representation changed.")
    old_sections=set(old_out.get("required_sections") or [])
    new_sections=set(new_out.get("required_sections") or [])
    for x in sorted(new_sections-old_sections):
        add(f"output_contract.required_sections.{x}","added",None,x,True,"New mandatory output section added.")
    for x in sorted(old_sections-new_sections):
        add(f"output_contract.required_sections.{x}","removed",x,None,False,"Required output section relaxed.")

    old_in, new_in = old.get("input_schema") or {}, new.get("input_schema") or {}
    old_req=set(old_in.get("required") or [])
    new_req=set(new_in.get("required") or [])
    for x in sorted(new_req-old_req):
        add(f"input_schema.required.{x}","added",None,x,True,"New mandatory input added.")
    for x in sorted(old_req-new_req):
        add(f"input_schema.required.{x}","removed",x,None,False,"Input requirement relaxed.")
    old_props, new_props=old_in.get("properties") or {}, new_in.get("properties") or {}
    for x in sorted(set(old_props)-set(new_props)):
        add(f"input_schema.properties.{x}","removed",old_props[x],None,True,"Previously accepted input property removed.")
    for x in sorted(set(new_props)-set(old_props)):
        add(f"input_schema.properties.{x}","added",None,new_props[x],x in new_req,"New input property added.")
    for x in sorted(set(old_props)&set(new_props)):
        if old_props[x] != new_props[x]:
            add(f"input_schema.properties.{x}","changed",old_props[x],new_props[x],True,"Input property contract changed.")

    old_review, new_review = _review_mode(old), _review_mode(new)
    if old_review != new_review:
        breaking = REVIEW_RANK.get(new_review, 99) > REVIEW_RANK.get(old_review, 99)
        add("review_profile.mode","changed",old_review,new_review,breaking,"Review policy strengthened." if breaking else "Review policy relaxed or changed.")

    if old.get("compatibility") != new.get("compatibility"):
        add("compatibility","changed",old.get("compatibility"),new.get("compatibility"),True,"Compatibility range changed and requires explicit review.")
    if old.get("model_contract") != new.get("model_contract"):
        add("model_contract","changed",old.get("model_contract"),new.get("model_contract"),True,"Model rendering contract changed.")
    if old.get("template_ref") != new.get("template_ref"):
        add("template_ref","changed",old.get("template_ref"),new.get("template_ref"),False,"Template source reference changed; artifact review is required.")

    breaking=[c for c in changes if c["breaking"]]
    old_major=int(str(old.get("version","0.0.0")).split('.')[0])
    new_major=int(str(new.get("version","0.0.0")).split('.')[0])
    version_policy_ok = not breaking or new_major > old_major
    migration = new.get("migration") or {}
    migration_ok = not breaking or bool(migration.get("required") and migration.get("guide_ref"))
    decision = "allow" if (not breaking or (version_policy_ok and migration_ok)) else "block"
    gate_findings=[]
    if breaking and not version_policy_ok:
        gate_findings.append({"code":"TEMPLATE_BREAKING_CHANGE_MAJOR_BUMP_REQUIRED","message":"Breaking changes require a higher MAJOR version."})
    if breaking and not migration_ok:
        gate_findings.append({"code":"TEMPLATE_BREAKING_CHANGE_MIGRATION_REQUIRED","message":"Breaking changes require migration.required=true and migration.guide_ref."})
    return {
        "schema_version":"ordo.template.version_diff.v1",
        "status":"passed" if decision=="allow" else "failed",
        "decision":decision,
        "old":{"path":str(old_file),"template_id":old.get("template_id"),"version":old.get("version"),"sha256":_digest(old_file)},
        "new":{"path":str(new_file),"template_id":new.get("template_id"),"version":new.get("version"),"sha256":_digest(new_file)},
        "summary":{"changes":len(changes),"breaking_changes":len(breaking),"migration_required":bool(breaking)},
        "changes":changes,
        "migration":{"declared":bool(migration),"guide_ref":migration.get("guide_ref"),"valid":migration_ok},
        "findings":gate_findings,
        "issues":[],
    }
