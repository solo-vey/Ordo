from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable
import hashlib
import json

import yaml


ALLOWED_PROFILES = {"light", "standard", "strict"}
PASSING_STATUSES = {"passed", "passed_with_warnings"}
CLEAN_CHECK_SCHEMA_VERSION = "ordo.clean_check.report.v1"
DEFAULT_PROFILE = "standard"


@dataclass
class Finding:
    check_id: str
    severity: str
    message: str
    target: str | None = None

    def as_dict(self) -> dict[str, Any]:
        data = {
            "check_id": self.check_id,
            "severity": self.severity,
            "message": self.message,
        }
        if self.target:
            data["target"] = self.target
        return data


def _load_yaml_checked(path: Path) -> tuple[bool, Any, str | None]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return True, yaml.safe_load(f) or {}, None
    except Exception as exc:  # pragma: no cover - message is still deterministic enough for CLI evidence
        return False, None, f"{type(exc).__name__}: {exc}"


def _load_json_checked(path: Path) -> tuple[bool, Any, str | None]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return True, json.load(f), None
    except Exception as exc:  # pragma: no cover
        return False, None, f"{type(exc).__name__}: {exc}"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _is_required(value: Any) -> bool:
    if value is True:
        return True
    return str(value).strip().lower() in {"true", "required", "yes", "1"}


def _walk_dicts(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_dicts(child)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_dicts(item)


def _prompt_registry_ids(source: dict[str, Any]) -> set[str]:
    registry = source.get("prompt_registry") if isinstance(source, dict) else None
    prompts = (registry or {}).get("prompts") if isinstance(registry, dict) else []
    ids: set[str] = set()
    if isinstance(prompts, list):
        for entry in prompts:
            if isinstance(entry, dict) and entry.get("prompt_id"):
                ids.add(str(entry["prompt_id"]))
    return ids


def _prompt_ref_ids(source: dict[str, Any]) -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    for idx, item in enumerate(_walk_dicts(source)):
        prompt_refs = item.get("prompt_refs")
        if isinstance(prompt_refs, list):
            owner = str(item.get("id") or item.get("artifact_id") or item.get("gate_id") or f"object_{idx}")
            for ref in prompt_refs:
                if isinstance(ref, dict) and ref.get("prompt_id"):
                    refs.append((owner, str(ref["prompt_id"])))
    return refs


def _delta_backlog_items(source: dict[str, Any]) -> list[dict[str, Any]]:
    backlog = source.get("delta_backlog") if isinstance(source, dict) else None
    if not isinstance(backlog, dict):
        return []
    for key in ("items", "entries", "deltas", "backlog"):
        value = backlog.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def _is_backlogged(path: str, backlog_items: list[dict[str, Any]]) -> bool:
    for item in backlog_items:
        haystack = " ".join(str(item.get(key, "")) for key in ("id", "target", "path", "artifact", "description", "reason"))
        if path in haystack:
            return True
    return False


def _entry_files_from_startup_profile(source: dict[str, Any]) -> tuple[bool, list[tuple[str, str, bool]], list[str]]:
    profile = source.get("startup_package_profile") if isinstance(source, dict) else None
    if not isinstance(profile, dict):
        return False, [], []
    files: list[tuple[str, str, bool]] = []
    prompt_ids: list[str] = []
    for entry in profile.get("entry_files", []) or []:
        if isinstance(entry, dict) and entry.get("path"):
            files.append((str(entry["path"]), str(entry.get("role") or "entry_file"), _is_required(entry.get("required", True))))
    for mode in profile.get("startup_modes", []) or []:
        if isinstance(mode, dict):
            if mode.get("entry_file"):
                files.append((str(mode["entry_file"]), f"startup_mode:{mode.get('mode', 'unknown')}", _is_required(mode.get("required", True))))
            if mode.get("prompt_id"):
                prompt_ids.append(str(mode["prompt_id"]))
    return True, files, prompt_ids


def _derived_artifact_paths(source: dict[str, Any]) -> tuple[bool, list[tuple[str, str]]]:
    sync = source.get("artifact_sync") if isinstance(source, dict) else None
    if not isinstance(sync, dict):
        return False, []
    candidates: list[Any] = []
    for key in ("artifacts", "derived_artifacts", "items", "entries"):
        if isinstance(sync.get(key), list):
            candidates.extend(sync[key])
    paths: list[tuple[str, str]] = []
    for item in candidates:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role") or item.get("artifact_role") or item.get("id") or "derived_artifact")
        for key in ("path", "artifact_path", "target", "output", "derived_path"):
            if item.get(key):
                paths.append((str(item[key]), role))
                break
    return True, paths


def run_clean_check(package: str | Path, profile: str = "standard", fail_on_warning: bool = False) -> dict[str, Any]:
    requested_profile = str(profile or DEFAULT_PROFILE).strip().lower()
    profile = requested_profile if requested_profile in ALLOWED_PROFILES else DEFAULT_PROFILE
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []

    if requested_profile not in ALLOWED_PROFILES:
        warnings.append(Finding(
            "profile_requested_valid",
            "warning",
            f"unsupported profile {requested_profile!r}; using {DEFAULT_PROFILE!r}",
            "profile",
        ).as_dict())

    def add_check(check_id: str, status: str, message: str, severity: str = "info", target: str | None = None) -> None:
        item = {"check_id": check_id, "status": status, "message": message}
        if target:
            item["target"] = target
        checks.append(item)
        if status == "failed":
            finding = Finding(check_id, severity, message, target).as_dict()
            if severity == "error":
                errors.append(finding)
            else:
                warnings.append(finding)

    root = Path(package).resolve()
    if root.is_file():
        root = root.parent
    if not root.exists() or not root.is_dir():
        add_check("package_root_exists", "failed", f"package root does not exist: {root}", "error", str(root))
        return _finalize(root, requested_profile, profile, checks, warnings, errors, fail_on_warning)
    add_check("package_root_exists", "passed", "package root exists", target=str(root))

    manifest_path = root / "ordo.yml"
    if not manifest_path.exists():
        add_check("package_manifest_present", "failed", "ordo.yml is missing", "error", "ordo.yml")
        return _finalize(root, requested_profile, profile, checks, warnings, errors, fail_on_warning)
    add_check("package_manifest_present", "passed", "ordo.yml exists", target="ordo.yml")

    ok, manifest, err = _load_yaml_checked(manifest_path)
    if not ok or not isinstance(manifest, dict):
        add_check("package_manifest_parse", "failed", f"ordo.yml parse failed: {err}", "error", "ordo.yml")
        return _finalize(root, requested_profile, profile, checks, warnings, errors, fail_on_warning)
    add_check("package_manifest_parse", "passed", "ordo.yml parses as YAML", target="ordo.yml")

    source_rel = manifest.get("source")
    if not source_rel:
        add_check("source_yaml_declared", "failed", "manifest does not declare source", "error", "ordo.yml:source")
        return _finalize(root, requested_profile, profile, checks, warnings, errors, fail_on_warning)
    add_check("source_yaml_declared", "passed", "manifest declares source YAML", target="ordo.yml:source")

    source_path = root / str(source_rel)
    if not source_path.exists():
        add_check("source_yaml_exists", "failed", f"declared source YAML is missing: {source_rel}", "error", str(source_rel))
        return _finalize(root, requested_profile, profile, checks, warnings, errors, fail_on_warning)
    add_check("source_yaml_exists", "passed", "declared source YAML exists", target=str(source_rel))

    ok, source, err = _load_yaml_checked(source_path)
    if not ok or not isinstance(source, dict):
        add_check("source_yaml_parse", "failed", f"source YAML parse failed: {err}", "error", str(source_rel))
        return _finalize(root, requested_profile, profile, checks, warnings, errors, fail_on_warning)
    add_check("source_yaml_parse", "passed", "source YAML parses", target=str(source_rel))

    # Manifest-declared paths: source is handled above; tests are required only if declared and missing is a warning in light, error otherwise.
    for key in ("tests",):
        rel = manifest.get(key)
        if not rel:
            continue
        target = root / str(rel)
        if target.exists():
            add_check("declared_manifest_paths_exist", "passed", f"manifest path exists: {key}", target=str(rel))
        else:
            severity = "warning" if profile == "light" else "error"
            add_check("declared_manifest_paths_exist", "failed", f"manifest path is missing: {key}={rel}", severity, str(rel))

    # Optional compiled output is a derived artifact; missing compiled files should not block unless artifact_sync later declares them strictly.
    compiled_rel = manifest.get("compiled")
    if compiled_rel:
        if (root / str(compiled_rel)).exists():
            add_check("declared_manifest_paths_exist", "passed", "compiled artifact path exists", target=str(compiled_rel))
        else:
            add_check("declared_manifest_paths_exist", "passed", "compiled artifact path is declared but not required by clean-check v1 without artifact_sync", target=str(compiled_rel))

    manifest_checksum_checked = False
    prompt_manifest = root / "PROMPT_MANIFEST.json"
    if prompt_manifest.exists():
        ok, prompt_data, err = _load_json_checked(prompt_manifest)
        if not ok or not isinstance(prompt_data, dict):
            add_check("declared_manifest_checksums_match", "failed", f"PROMPT_MANIFEST.json parse failed: {err}", "error", "PROMPT_MANIFEST.json")
        else:
            for entry in prompt_data.get("prompts", []) or []:
                if not isinstance(entry, dict) or not entry.get("path"):
                    continue
                rel = str(entry["path"])
                current = root / rel
                manifest_checksum_checked = True
                if not current.exists():
                    add_check("declared_manifest_paths_exist", "failed", f"prompt manifest path is missing: {rel}", "error", rel)
                    continue
                expected = entry.get("sha256")
                if expected:
                    actual = _sha256(current)
                    if actual == str(expected):
                        add_check("declared_manifest_checksums_match", "passed", f"checksum matches: {rel}", target=rel)
                    else:
                        severity = "warning" if profile == "light" else "error"
                        add_check("declared_manifest_checksums_match", "failed", f"checksum mismatch: {rel}", severity, rel)
    if not manifest_checksum_checked:
        add_check("declared_manifest_checksums_match", "not_applicable", "no prompt/file checksum manifest found")

    registry_ids = _prompt_registry_ids(source)
    refs = _prompt_ref_ids(source)
    if registry_ids or refs:
        missing_refs = [(owner, prompt_id) for owner, prompt_id in refs if prompt_id not in registry_ids]
        if missing_refs:
            for owner, prompt_id in missing_refs:
                add_check("prompt_registry_refs_resolve_when_present", "failed", f"prompt_ref does not resolve: {prompt_id}", "error", owner)
        else:
            add_check("prompt_registry_refs_resolve_when_present", "passed", f"all prompt_refs resolve ({len(refs)})")
    else:
        add_check("prompt_registry_refs_resolve_when_present", "not_applicable", "no prompt_registry or prompt_refs present")

    has_startup, startup_files, startup_prompt_ids = _entry_files_from_startup_profile(source)
    if has_startup:
        for rel, role, required in startup_files:
            if (root / rel).exists():
                add_check("startup_profile_entries_exist_when_present", "passed", f"startup entry exists: {role}", target=rel)
            else:
                severity = "error" if required or profile in {"standard", "strict"} else "warning"
                add_check("startup_profile_entries_exist_when_present", "failed", f"startup entry is missing: {role} -> {rel}", severity, rel)
        if startup_prompt_ids and registry_ids:
            for prompt_id in startup_prompt_ids:
                if prompt_id in registry_ids:
                    add_check("startup_profile_entries_exist_when_present", "passed", f"startup prompt id resolves: {prompt_id}", target=prompt_id)
                else:
                    add_check("startup_profile_entries_exist_when_present", "failed", f"startup prompt id does not resolve: {prompt_id}", "error", prompt_id)
    else:
        add_check("startup_profile_entries_exist_when_present", "not_applicable", "no startup_package_profile present")

    has_artifact_sync, derived_paths = _derived_artifact_paths(source)
    backlog_items = _delta_backlog_items(source)
    if has_artifact_sync:
        if not derived_paths:
            add_check("derived_artifacts_current_or_backlogged_when_declared", "passed", "artifact_sync present without concrete derived artifact paths")
        for rel, role in derived_paths:
            if (root / rel).exists():
                add_check("derived_artifacts_current_or_backlogged_when_declared", "passed", f"derived artifact exists: {role}", target=rel)
            elif _is_backlogged(rel, backlog_items):
                add_check("derived_artifacts_current_or_backlogged_when_declared", "passed", f"missing derived artifact is covered by delta_backlog: {role}", target=rel)
            else:
                severity = "warning" if profile == "light" else "error"
                add_check("derived_artifacts_current_or_backlogged_when_declared", "failed", f"derived artifact missing and not backlogged: {role} -> {rel}", severity, rel)
    else:
        add_check("derived_artifacts_current_or_backlogged_when_declared", "not_applicable", "no artifact_sync present")

    if backlog_items:
        today = date.today().isoformat()
        for item in backlog_items:
            status = str(item.get("status") or item.get("delta_status") or "open").lower()
            due = str(item.get("due") or item.get("expires_on") or item.get("expiry") or "").strip()
            owner = str(item.get("owner") or "").strip()
            blocker = status in {"blocker", "blocked", "open_blocker"} or str(item.get("severity", "")).lower() in {"blocker", "error"}
            if blocker and profile in {"standard", "strict"}:
                if due and due < today:
                    sev = "error" if profile == "strict" else "warning"
                    add_check("delta_backlog_blockers_not_expired_when_declared", "failed", f"delta backlog blocker is expired: {item.get('id', '<unknown>')}", sev, str(item.get("id", "delta_backlog")))
                elif not owner and profile == "strict":
                    add_check("delta_backlog_blockers_not_expired_when_declared", "failed", f"delta backlog blocker has no owner: {item.get('id', '<unknown>')}", "error", str(item.get("id", "delta_backlog")))
        if not any(c["check_id"] == "delta_backlog_blockers_not_expired_when_declared" and c["status"] == "failed" for c in checks):
            add_check("delta_backlog_blockers_not_expired_when_declared", "passed", "delta_backlog blockers are acceptable for selected profile")
    else:
        add_check("delta_backlog_blockers_not_expired_when_declared", "not_applicable", "no delta_backlog entries present")

    return _finalize(root, requested_profile, profile, checks, warnings, errors, fail_on_warning)


def _finalize(root: Path, profile_requested: str, profile: str, checks: list[dict[str, Any]], warnings: list[dict[str, Any]], errors: list[dict[str, Any]], fail_on_warning: bool) -> dict[str, Any]:
    if errors:
        status = "blocked"
    elif warnings:
        status = "passed_with_warnings"
    else:
        status = "passed"
    exit_code = 1 if errors or (fail_on_warning and warnings) else 0
    status_counts = {
        "passed": sum(1 for check in checks if check.get("status") == "passed"),
        "failed": sum(1 for check in checks if check.get("status") == "failed"),
        "not_applicable": sum(1 for check in checks if check.get("status") == "not_applicable"),
    }
    summary = {
        "error_count": len(errors),
        "warning_count": len(warnings),
        "check_count": len(checks),
        "passed_count": status_counts["passed"],
        "failed_count": status_counts["failed"],
        "not_applicable_count": status_counts["not_applicable"],
    }
    return {
        "schema_version": CLEAN_CHECK_SCHEMA_VERSION,
        "mode": "clean_package_check",
        "status": status,
        "profile_requested": profile_requested,
        "profile": profile,
        "fail_on_warning": bool(fail_on_warning),
        "exit_code": exit_code,
        "package_root": str(root),
        "summary": summary,
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
        "exit_policy": {
            "passed": 0,
            "passed_with_warnings": 1 if fail_on_warning else 0,
            "blocked": 1,
        },
    }
