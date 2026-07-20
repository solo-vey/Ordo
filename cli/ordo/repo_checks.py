from __future__ import annotations

import ast
import json
import re
import subprocess
from pathlib import Path
from typing import Any

import yaml

from .clean_check import run_clean_check

PACKAGE_PATH_PATTERN = re.compile(r"packages/[A-Za-z0-9_./-]+")


def validate_workflow_paths(repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    workflow_dir = root / ".github" / "workflows"
    issues: list[dict[str, str]] = []
    checked: list[str] = []
    if workflow_dir.exists():
        for workflow in sorted(workflow_dir.glob("*.yml")) + sorted(workflow_dir.glob("*.yaml")):
            text = workflow.read_text(encoding="utf-8")
            for match in sorted(set(PACKAGE_PATH_PATTERN.findall(text))):
                checked.append(match)
                if not (root / match).exists():
                    issues.append({
                        "code": "WORKFLOW_PATH_NOT_FOUND",
                        "path": match,
                        "workflow": str(workflow.relative_to(root)),
                        "message": f"Workflow references missing path: {match}",
                    })
    return {
        "status": "passed" if not issues else "failed",
        "checked_paths": sorted(set(checked)),
        "issues": issues,
    }


DEFAULT_FORBIDDEN_PATH_POLICY = {
    "directory_names": ["__pycache__", ".pytest_cache", ".venv", "venv", "env", "htmlcov", "__MACOSX", ".ordo-generated", ".ordo-release-candidate"],
    "directory_suffixes": [".egg-info"],
    "file_names": [".DS_Store", ".coverage"],
    "file_prefixes": ["._"],
    "file_suffixes": [".pyc", ".pyo", ".swp", ".swo", ".tmp", ".temp"],
    "path_globs": [".coverage.*", "reports/ci/**", "reports/release/**", "packages/*/reports/ci_release_evidence.json"],
}
FORBIDDEN_METADATA_DIR_NAMES = {"__pycache__"}
FORBIDDEN_METADATA_SUFFIXES = {".pyc"}
FORBIDDEN_METADATA_DIR_SUFFIXES = {".egg-info"}
HYGIENE_SCOPES = {"development", "release"}


def _is_forbidden_generated_metadata(path: Path) -> bool:
    return (
        path.name in FORBIDDEN_METADATA_DIR_NAMES
        or any(path.name.endswith(suffix) for suffix in FORBIDDEN_METADATA_DIR_SUFFIXES)
        or path.suffix in FORBIDDEN_METADATA_SUFFIXES
        or any(part in FORBIDDEN_METADATA_DIR_NAMES for part in path.parts)
        or any(any(part.endswith(suffix) for suffix in FORBIDDEN_METADATA_DIR_SUFFIXES) for part in path.parts)
    )


def _scan_generated_metadata(root: Path) -> list[str]:
    forbidden: list[str] = []
    for path in root.rglob("*"):
        if _is_forbidden_generated_metadata(path):
            forbidden.append(str(path.relative_to(root)))
    return sorted(set(forbidden))


def _git_tracked_generated_metadata(root: Path) -> tuple[list[str], str]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            text=False,
            capture_output=True,
            check=False,
        )
    except OSError:
        return [], "git_unavailable"
    if proc.returncode != 0:
        return [], "git_metadata_unavailable"
    tracked: list[str] = []
    for raw in proc.stdout.split(b"\0"):
        if not raw:
            continue
        rel = raw.decode("utf-8", errors="surrogateescape")
        if _is_forbidden_generated_metadata(Path(rel)):
            tracked.append(rel)
    return sorted(set(tracked)), "git_tracked_files"


def validate_generated_metadata_absent(
    repo_root: str | Path,
    scope: str = "development",
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    if scope not in HYGIENE_SCOPES:
        raise ValueError(f"unsupported hygiene scope: {scope}")

    observed = _scan_generated_metadata(root)
    if scope == "release":
        return {
            "status": "passed" if not observed else "failed",
            "scope": scope,
            "evidence_mode": "release_tree_filesystem",
            "forbidden_paths": observed,
            "observed_transient_paths": observed,
            "note": "Release-tree validation is strict: generated Python metadata must be absent from the candidate tree.",
        }

    tracked, evidence_mode = _git_tracked_generated_metadata(root)
    return {
        "status": "passed" if not tracked else "failed",
        "scope": scope,
        "evidence_mode": evidence_mode,
        "forbidden_paths": tracked,
        "observed_transient_paths": observed,
        "note": (
            "Development validation blocks generated metadata only when it is tracked by Git. "
            "Untracked __pycache__, .pyc, and .egg-info created by normal local installation or tests are reported but are non-blocking."
        ),
    }



def _load_unified_hygiene_policy(root: Path) -> dict[str, Any]:
    path = root / "repo_hygiene.yml"
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    policy = data.get("repo_hygiene", data)
    return policy if isinstance(policy, dict) else {}


def _forbidden_path_policy(root: Path) -> dict[str, list[str]]:
    policy = _load_unified_hygiene_policy(root).get("forbidden_paths", {})
    if not isinstance(policy, dict):
        policy = {}
    return {
        key: [str(item) for item in policy.get(key, DEFAULT_FORBIDDEN_PATH_POLICY[key]) or []]
        for key in DEFAULT_FORBIDDEN_PATH_POLICY
    }


def _matches_forbidden_path(rel: Path, policy: dict[str, list[str]]) -> bool:
    parts = rel.parts
    name = rel.name
    text = rel.as_posix()
    return (
        any(part in policy["directory_names"] for part in parts)
        or any(any(part.endswith(suffix) for suffix in policy["directory_suffixes"]) for part in parts)
        or name in policy["file_names"]
        or any(name.startswith(prefix) for prefix in policy["file_prefixes"])
        or any(name.endswith(suffix) for suffix in policy["file_suffixes"])
        or any(rel.match(pattern) or Path(text).match(pattern) for pattern in policy["path_globs"])
    )


def _scan_repository_forbidden_paths(root: Path) -> list[str]:
    policy = _forbidden_path_policy(root)
    forbidden: list[str] = []
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if _matches_forbidden_path(rel, policy):
            forbidden.append(rel.as_posix())
    return sorted(set(forbidden))


def _git_tracked_forbidden_paths(root: Path) -> tuple[list[str], str]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            text=False,
            capture_output=True,
            check=False,
        )
    except OSError:
        return [], "git_unavailable"
    if proc.returncode != 0:
        return [], "git_metadata_unavailable"
    policy = _forbidden_path_policy(root)
    tracked = []
    for raw in proc.stdout.split(b"\0"):
        if not raw:
            continue
        rel = Path(raw.decode("utf-8", errors="surrogateescape"))
        if _matches_forbidden_path(rel, policy):
            tracked.append(rel.as_posix())
    return sorted(set(tracked)), "git_tracked_files"


def validate_repository_forbidden_paths(
    repo_root: str | Path,
    scope: str = "development",
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    if scope not in HYGIENE_SCOPES:
        raise ValueError(f"unsupported hygiene scope: {scope}")
    observed = _scan_repository_forbidden_paths(root)
    if scope == "release":
        forbidden = observed
        evidence_mode = "release_tree_filesystem"
    else:
        forbidden, evidence_mode = _git_tracked_forbidden_paths(root)
    return {
        "status": "passed" if not forbidden else "failed",
        "scope": scope,
        "evidence_mode": evidence_mode,
        "forbidden_paths": forbidden,
        "observed_transient_paths": observed,
        "note": (
            "Development scope blocks only Git-tracked forbidden paths; untracked local artifacts are reported. "
            "Release scope blocks every forbidden path in the isolated candidate tree."
        ),
    }


def _git_tracked_paths(root: Path) -> tuple[list[Path], str]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            text=False,
            capture_output=True,
            check=False,
        )
    except OSError:
        return [], "git_unavailable"
    if proc.returncode != 0:
        return [], "git_metadata_unavailable"
    paths = [
        Path(raw.decode("utf-8", errors="surrogateescape"))
        for raw in proc.stdout.split(b"\0")
        if raw
    ]
    return paths, "git_tracked_files"


def _duplicate_nesting_findings(
    paths: list[Path],
    repo_name: str,
    settings: dict[str, Any],
    exempt: tuple[str, ...],
) -> list[str]:
    forbidden: list[str] = []
    for rel in paths:
        text = rel.as_posix()
        if any(text == prefix.rstrip("/") or text.startswith(prefix) for prefix in exempt):
            continue
        parts = rel.parts[:-1] if rel.suffix else rel.parts
        if not parts:
            continue
        adjacent_index = next(
            (
                index
                for index in range(1, len(parts))
                if settings.get("adjacent_segment_repetition", True)
                and parts[index].casefold() == parts[index - 1].casefold()
            ),
            None,
        )
        repository_repeat = (
            settings.get("repository_name_repetition", True)
            and parts[0].casefold() == repo_name
        )
        if repository_repeat:
            forbidden.append(parts[0])
        elif adjacent_index is not None:
            forbidden.append("/".join(parts[: adjacent_index + 1]))
    return sorted(set(forbidden))


def validate_duplicate_repository_nesting(
    repo_root: str | Path,
    scope: str = "development",
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    if scope not in HYGIENE_SCOPES:
        raise ValueError(f"unsupported hygiene scope: {scope}")
    settings = _load_unified_hygiene_policy(root).get("duplicate_nesting", {})
    if not isinstance(settings, dict) or not settings.get("enabled", False):
        return {
            "status": "passed",
            "scope": scope,
            "forbidden_paths": [],
            "observed_transient_paths": [],
            "note": "duplicate nesting check disabled",
        }

    exempt = tuple(str(item) for item in settings.get("exempt_prefixes", []) or [])
    repo_name = root.name.casefold()
    observed_paths = [
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file()
    ]
    observed = _duplicate_nesting_findings(observed_paths, repo_name, settings, exempt)

    if scope == "release":
        forbidden = observed
        evidence_mode = "release_tree_filesystem"
    else:
        tracked_paths, evidence_mode = _git_tracked_paths(root)
        forbidden = _duplicate_nesting_findings(tracked_paths, repo_name, settings, exempt)

    return {
        "status": "passed" if not forbidden else "failed",
        "scope": scope,
        "evidence_mode": evidence_mode,
        "forbidden_paths": forbidden,
        "observed_transient_paths": observed,
        "exempt_prefixes": list(exempt),
        "note": (
            "Development scope blocks duplicate nesting only in Git-tracked paths. "
            "Release scope blocks duplicate nesting anywhere in the isolated candidate tree."
        ),
    }

PACKAGE_GENERATED_ROOTS = {"compiled", "reports", "runtime", "generated_outputs"}
PACKAGE_GENERATED_ALLOWED_REPORT_TEMPLATES = {
    "CLI_VALIDATION_SUMMARY.md",
    "PACKAGE_PROFILE_SUMMARY.md",
}


def _package_generated_artifact_findings(paths: list[Path]) -> list[str]:
    forbidden: list[str] = []
    for rel in paths:
        if len(rel.parts) < 4 or rel.parts[0] != "packages":
            continue
        generated_name = rel.parts[2]
        if generated_name not in PACKAGE_GENERATED_ROOTS:
            continue
        if rel.name == ".gitkeep":
            continue
        if generated_name == "reports" and rel.name in PACKAGE_GENERATED_ALLOWED_REPORT_TEMPLATES:
            continue
        forbidden.append(rel.as_posix())
    return sorted(set(forbidden))


def validate_package_generated_artifacts_absent(
    repo_root: str | Path,
    scope: str = "development",
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    if scope not in HYGIENE_SCOPES:
        raise ValueError(f"unsupported hygiene scope: {scope}")

    packages_dir = root / "packages"
    observed_paths = [
        path.relative_to(root)
        for path in packages_dir.rglob("*")
        if path.is_file()
    ] if packages_dir.exists() else []
    observed = _package_generated_artifact_findings(observed_paths)

    if scope == "release":
        forbidden = observed
        evidence_mode = "release_tree_filesystem"
    else:
        tracked_paths, evidence_mode = _git_tracked_paths(root)
        forbidden = _package_generated_artifact_findings(tracked_paths)

    return {
        "status": "passed" if not forbidden else "failed",
        "scope": scope,
        "evidence_mode": evidence_mode,
        "forbidden_paths": forbidden,
        "observed_transient_paths": observed,
        "note": (
            "Development scope blocks package-generated artifacts only when Git-tracked; "
            "release scope blocks them anywhere in the isolated candidate tree. "
            "Allowed exceptions remain .gitkeep placeholders and reports/CLI_VALIDATION_SUMMARY.md "
            "and reports/PACKAGE_PROFILE_SUMMARY.md templates."
        ),
    }


REPO_HYGIENE_SCHEMA_VERSION = "ordo.repo_hygiene.report.v1"


def _load_repo_hygiene_policy(root: Path) -> tuple[Path | None, dict[str, Any] | None, str | None]:
    for name in ("repo_hygiene.yml", "repo_hygiene.yaml", "ordo_repo_hygiene.yml", "ordo_repo_hygiene.yaml"):
        path = root / name
        if not path.exists():
            continue
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception as exc:  # pragma: no cover - exact parser text is environment-dependent
            return path, None, f"{type(exc).__name__}: {exc}"
        if not isinstance(data, dict):
            return path, None, "policy file must contain a YAML mapping"
        policy = data.get("repo_hygiene", data)
        if not isinstance(policy, dict):
            return path, None, "repo_hygiene policy must be a mapping"
        return path, policy, None
    return None, None, None


def _discover_delegated_package_roots(root: Path) -> list[dict[str, Any]]:
    packages_dir = root / "packages"
    if not packages_dir.exists():
        return []
    delegated: list[dict[str, Any]] = []
    for package in sorted(p for p in packages_dir.iterdir() if p.is_dir()):
        if (package / "ordo.yml").exists():
            delegated.append({
                "root_id": package.name,
                "path": str(package.relative_to(root)),
                "role": "applied_package",
                "clean_check": "delegated",
                "status": "delegated",
            })
    return delegated


def run_repo_root_contract(repo_root: str | Path, entry: dict[str, Any]) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    rel = str(entry.get("path") or "").strip()
    target = (root / rel).resolve()
    checks: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    try:
        target.relative_to(root)
    except ValueError:
        return {"status": "blocked", "checks": [], "errors": [{"check_id": "root_contract_path_within_repo", "message": "root contract path escapes repository", "target": rel}]}

    def record(check_id: str, ok: bool, subject: str, message: str = "") -> None:
        item = {"check_id": check_id, "status": "passed" if ok else "blocked", "target": subject}
        if message:
            item["message"] = message
        checks.append(item)
        if not ok:
            errors.append(item.copy())

    record("root_contract_root_exists", target.exists() and target.is_dir(), rel)
    if not target.exists() or not target.is_dir():
        return {"status": "blocked", "checks": checks, "errors": errors}

    contract = entry.get("contract") or {}
    if not isinstance(contract, dict):
        record("root_contract_mapping", False, rel, "contract must be a mapping")
        return {"status": "blocked", "checks": checks, "errors": errors}

    for required in contract.get("required_paths", []) or []:
        rp = target / str(required)
        record("root_contract_required_path", rp.exists(), f"{rel}/{required}")

    for pattern in contract.get("yaml_globs", []) or []:
        for fp in sorted(target.glob(str(pattern))):
            if fp.is_file():
                try:
                    yaml.safe_load(fp.read_text(encoding="utf-8"))
                    record("root_contract_yaml_parse", True, str(fp.relative_to(root)))
                except Exception as exc:
                    record("root_contract_yaml_parse", False, str(fp.relative_to(root)), f"{type(exc).__name__}: {exc}")

    for pattern in contract.get("json_globs", []) or []:
        for fp in sorted(target.glob(str(pattern))):
            if fp.is_file():
                try:
                    json.loads(fp.read_text(encoding="utf-8"))
                    record("root_contract_json_parse", True, str(fp.relative_to(root)))
                except Exception as exc:
                    record("root_contract_json_parse", False, str(fp.relative_to(root)), f"{type(exc).__name__}: {exc}")

    for pattern in contract.get("python_globs", []) or []:
        for fp in sorted(target.glob(str(pattern))):
            if fp.is_file():
                try:
                    ast.parse(fp.read_text(encoding="utf-8"), filename=str(fp))
                    record("root_contract_python_syntax", True, str(fp.relative_to(root)))
                except Exception as exc:
                    record("root_contract_python_syntax", False, str(fp.relative_to(root)), f"{type(exc).__name__}: {exc}")

    return {
        "status": "passed" if not errors else "blocked",
        "checks": checks,
        "errors": errors,
        "summary": {"check_count": len(checks), "blocked_count": len(errors)},
    }


def run_repo_package_hygiene(
    repo_root: str | Path,
    profile: str = "standard",
    fail_on_warning: bool = False,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    checked_roots: list[dict[str, Any]] = []
    delegated_roots: list[dict[str, Any]] = []
    not_applicable_roots: list[dict[str, Any]] = []

    policy_path, policy, policy_error = _load_repo_hygiene_policy(root)
    if policy_error:
        errors.append({
            "check_id": "repo_hygiene_policy_parse",
            "message": policy_error,
            "target": str(policy_path.relative_to(root)) if policy_path else "repo_hygiene",
        })
        policy = None

    if not policy:
        delegated_roots = _discover_delegated_package_roots(root)
        status = "blocked" if errors else "not_applicable"
        exit_code = 1 if errors else 0
        return {
            "schema_version": REPO_HYGIENE_SCHEMA_VERSION,
            "mode": "repo_package_hygiene",
            "status": status,
            "repo_root": str(root),
            "policy_path": str(policy_path.relative_to(root)) if policy_path else None,
            "profile": profile,
            "fail_on_warning": bool(fail_on_warning),
            "roots": [],
            "delegated_roots": delegated_roots,
            "warnings": warnings,
            "errors": errors,
            "summary": {
                "root_count": len(delegated_roots),
                "checked_count": 0,
                "passed_count": 0,
                "warning_count": 0,
                "blocked_count": 0,
                "delegated_count": len(delegated_roots),
                "not_applicable_count": 0,
            },
            "exit_code": exit_code,
            "note": "No repo_hygiene policy found; applied package roots are delegated by default.",
        }

    effective_profile = str(policy.get("default_profile") or profile or "standard")
    if profile:
        effective_profile = str(profile)
    effective_fail_on_warning = bool(policy.get("fail_on_warning", fail_on_warning) or fail_on_warning)

    roots = policy.get("roots", [])
    if not isinstance(roots, list):
        roots = []
        errors.append({"check_id": "repo_hygiene_roots_valid", "message": "repo_hygiene.roots must be a list", "target": str(policy_path.relative_to(root)) if policy_path else "repo_hygiene"})

    for idx, entry in enumerate(roots):
        if not isinstance(entry, dict):
            warnings.append({"check_id": "repo_hygiene_root_valid", "message": "root entry is not a mapping", "target": f"roots[{idx}]"})
            continue
        rel = str(entry.get("path") or "").strip()
        root_id = str(entry.get("root_id") or rel or f"root_{idx}")
        role = str(entry.get("role") or "unknown")
        treatment = str(entry.get("clean_check") or "delegated").strip().lower()
        release_blocking = bool(entry.get("release_blocking", treatment == "required"))
        base_item = {
            "root_id": root_id,
            "path": rel,
            "role": role,
            "clean_check": treatment,
            "release_blocking": release_blocking,
        }
        if treatment == "delegated":
            delegated_roots.append({**base_item, "status": "delegated"})
            continue
        if treatment in {"ignored", "not_applicable"}:
            not_applicable_roots.append({**base_item, "status": "not_applicable"})
            continue
        if treatment == "root_contract":
            contract_report = run_repo_root_contract(root, entry)
            contract_status = str(contract_report.get("status"))
            item = {**base_item, "status": contract_status, "exit_code": 0 if contract_status == "passed" else 1, "summary": contract_report.get("summary", {}), "contract_report": contract_report}
            checked_roots.append(item)
            if contract_status == "blocked":
                finding = {"check_id": "repo_root_contract_blocked", "message": f"root contract blocked for {root_id}", "target": rel}
                if release_blocking:
                    errors.append(finding)
                else:
                    warnings.append(finding)
            continue
        if treatment not in {"required", "optional"}:
            warnings.append({"check_id": "repo_hygiene_clean_check_treatment", "message": f"unsupported clean_check treatment {treatment!r}; treating as delegated", "target": root_id})
            delegated_roots.append({**base_item, "status": "delegated"})
            continue
        if not rel:
            errors.append({"check_id": "repo_hygiene_root_path_declared", "message": "root path is missing", "target": root_id})
            continue
        package_root = root / rel
        if treatment == "optional" and not package_root.exists():
            not_applicable_roots.append({**base_item, "status": "not_applicable", "message": "optional root does not exist"})
            continue
        clean_report = run_clean_check(package_root, profile=effective_profile, fail_on_warning=effective_fail_on_warning)
        clean_status = str(clean_report.get("status"))
        item = {
            **base_item,
            "status": clean_status,
            "exit_code": int(clean_report.get("exit_code", 1)),
            "summary": clean_report.get("summary", {}),
        }
        checked_roots.append(item)
        if clean_status == "blocked":
            finding = {"check_id": "repo_clean_required_root_blocked", "message": f"clean-check blocked for {root_id}", "target": rel}
            if release_blocking:
                errors.append(finding)
            else:
                warnings.append(finding)
        elif clean_status == "passed_with_warnings":
            finding = {"check_id": "repo_clean_root_warnings", "message": f"clean-check warnings for {root_id}", "target": rel}
            if release_blocking and effective_fail_on_warning:
                errors.append(finding)
            else:
                warnings.append(finding)

    passed_count = sum(1 for item in checked_roots if item.get("status") == "passed")
    warning_count = sum(1 for item in checked_roots if item.get("status") == "passed_with_warnings") + len(warnings)
    blocked_count = sum(1 for item in checked_roots if item.get("status") == "blocked") + len(errors)
    if errors:
        status = "blocked"
    elif warnings or any(item.get("status") == "passed_with_warnings" for item in checked_roots):
        status = "passed_with_warnings"
    elif checked_roots:
        status = "passed"
    else:
        status = "not_applicable"
    exit_code = 1 if status == "blocked" else 0
    return {
        "schema_version": REPO_HYGIENE_SCHEMA_VERSION,
        "mode": "repo_package_hygiene",
        "status": status,
        "repo_root": str(root),
        "policy_path": str(policy_path.relative_to(root)) if policy_path else None,
        "profile": effective_profile,
        "fail_on_warning": effective_fail_on_warning,
        "roots": checked_roots,
        "delegated_roots": delegated_roots,
        "warnings": warnings,
        "errors": errors,
        "summary": {
            "root_count": len(checked_roots) + len(delegated_roots) + len(not_applicable_roots),
            "checked_count": len(checked_roots),
            "passed_count": passed_count,
            "warning_count": warning_count,
            "blocked_count": blocked_count,
            "delegated_count": len(delegated_roots),
            "not_applicable_count": len(not_applicable_roots),
        },
        "exit_code": exit_code,
    }


def run_repo_checks(
    repo_root: str | Path,
    clean: bool = False,
    clean_profile: str = "standard",
    clean_fail_on_warning: bool = False,
    hygiene_scope: str = "development",
) -> dict[str, Any]:
    if hygiene_scope not in HYGIENE_SCOPES:
        raise ValueError(f"unsupported hygiene scope: {hygiene_scope}")
    workflow = validate_workflow_paths(repo_root)
    generated = validate_generated_metadata_absent(repo_root, scope=hygiene_scope)
    repository_forbidden = validate_repository_forbidden_paths(repo_root, scope=hygiene_scope)
    duplicate_nesting = validate_duplicate_repository_nesting(repo_root, scope=hygiene_scope)
    package_generated = validate_package_generated_artifacts_absent(repo_root, scope=hygiene_scope)
    reports = {
        "workflow_paths": workflow,
        "generated_metadata_absent": generated,
        "repository_forbidden_paths": repository_forbidden,
        "duplicate_repository_nesting": duplicate_nesting,
        "package_generated_artifacts_absent": package_generated,
    }
    failed = [name for name, report in reports.items() if report.get("status") != "passed"]
    if clean:
        repo_hygiene = run_repo_package_hygiene(repo_root, profile=clean_profile, fail_on_warning=clean_fail_on_warning)
        reports["repo_package_hygiene"] = repo_hygiene
        if repo_hygiene.get("status") == "blocked":
            failed.append("repo_package_hygiene")
    status = "passed" if not failed else "failed"
    return {
        "schema_version": "ordo.repo_check.report.v2",
        "status": status,
        "hygiene_scope": hygiene_scope,
        "profile": clean_profile if clean else None,
        "clean_enabled": bool(clean),
        "failed_checks": sorted(set(failed)),
        "reports": reports,
        "exit_code": 0 if status == "passed" else 1,
    }
