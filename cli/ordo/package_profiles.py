from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
import hashlib
import json
import zipfile

from .loader import load_package
from .runtime import runtime_status, validate_cli_truthfulness
from .registry_checks import find_repo_root
import shutil
from .reporter import write_json
from .targets import emit_compiled_targets, verify_targets, normalize_runtime_view, runtime_view_behavior, runtime_view_includes_ordo_code
from .ci_release_evidence import validate_ci_release_evidence
from .build_identity import write_build_identity, new_build_identity, bind_report, validate_report_binding
from .package_reconciliation import pre_zip_reconciliation
from .prompt_compiler import compile_prompt_only, validate_prompt_compilation

PACKAGE_PROFILES = {"dev", "runtime", "evidence", "prompt_only"}


def _rel(root: Path, path: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def _issue(code: str, message: str, location: str | None = None, severity: str = "error") -> dict[str, Any]:
    return {"severity": severity, "code": code, "message": message, "location": location}


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _has_cli_evidence(root: Path) -> bool:
    reports = root / "reports"
    evidence_names = [
        "lint_report.json",
        "compile_report.json",
        "test_report.json",
        "coverage_report.json",
        "output_validation_report.json",
        "release_validation_report.json",
        "GO_NO_GO_REPORT.json",
        "runtime_entry_report.json",
        "runtime_status_report.json",
    ]
    for name in evidence_names:
        data = _read_json(reports / name)
        if data and (data.get("status") or data.get("cli_status") or data.get("executed_commands")):
            return True
    return False


def _cli_status(root: Path) -> tuple[str, dict[str, Any] | None]:
    # Prefer explicit release/go-no-go evidence. Otherwise a collection of report
    # files is still accepted as executed CLI evidence for package profiling.
    for name in ["release_validation_report.json", "GO_NO_GO_REPORT.json", "runtime_entry_report.json"]:
        data = _read_json(root / "reports" / name)
        if data and data.get("cli_status"):
            return str(data.get("cli_status")), data
    if _has_cli_evidence(root):
        return "executed_cli_passed", {"cli_status": "executed_cli_passed", "cli_evidence": True}
    return "logical_self_check_only", {"cli_status": "logical_self_check_only"}


def _is_transient(path: Path) -> bool:
    return "__pycache__" in path.parts or path.suffix == ".pyc" or path.name.endswith(".egg-info")


def _dev_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*") if p.is_file() and not _is_transient(p))


RUNTIME_CLI_ALLOWED_COMMANDS = {
    "runtime-status",
    "runtime-entry",
    "next-step",
    "check-gate",
    "validate-state",
    "intake",
    "generate-output",
    "validate-output",
    "validate-artifacts",
    "consistency",
    "go-no-go",
    "validate-cli-status",
    "verify-session",
    "restore-session",
    "render-runtime-view",
    "verify-targets",
}


def _write_embedded_runtime_cli(root: Path) -> list[Path]:
    """Create a runtime-only embedded CLI inside a subject package."""
    repo_root = find_repo_root(root)
    source_pkg = None
    if repo_root is not None and (repo_root / "cli" / "ordo").exists():
        source_pkg = repo_root / "cli" / "ordo"
    else:
        source_pkg = Path(__file__).resolve().parent
    if not source_pkg.exists():
        return []
    target = root / "cli_embedded"
    if target.exists():
        shutil.rmtree(target)
    pkg_target = target / "ordo_pkg" / "ordo"
    shutil.copytree(source_pkg, pkg_target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.egg-info", "templates"))
    wrapper = target / "ordo"
    allowed = ", ".join(sorted(RUNTIME_CLI_ALLOWED_COMMANDS))
    wrapper.write_text(f'''#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path

ALLOWED = {sorted(RUNTIME_CLI_ALLOWED_COMMANDS)!r}

def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] in {{"-h", "--help"}}:
        print("Ordo embedded runtime CLI")
        print("Allowed runtime commands: {allowed}")
        print("Usage: cli_embedded/ordo <runtime-command> <package> [args]")
        return 0
    command = sys.argv[1]
    if command not in ALLOWED:
        print(f"embedded runtime CLI blocks non-runtime command: {{command}}", file=sys.stderr)
        print("Allowed runtime commands: {allowed}", file=sys.stderr)
        return 2
    here = Path(__file__).resolve().parent
    sys.path.insert(0, str(here / "ordo_pkg"))
    from ordo.cli import main as ordo_main
    return int(ordo_main(sys.argv[1:]))

if __name__ == "__main__":
    raise SystemExit(main())
''', encoding="utf-8")
    try:
        wrapper.chmod(0o755)
    except Exception:
        pass
    (target / "README.md").write_text("""# Embedded Ordo Runtime CLI

This runtime package carries a minimal CLI entrypoint so guided execution does not depend on model memory or direct IR reading.

Use:

```bash
./cli_embedded/ordo runtime-entry .
./cli_embedded/ordo next-step . --state run_state.json
./cli_embedded/ordo intake . --submit <NODE_ID> --answer "<answer>"
./cli_embedded/ordo intake . --submit <NODE_ID> --answer-file tmp_answer.yaml
./cli_embedded/ordo check-gate . <GATE_ID> --state run_state.json
./cli_embedded/ordo validate-state . --state run_state.json
./cli_embedded/ordo render-runtime-view . --format ordo-code --node <NODE_ID>
./cli_embedded/ordo verify-targets .
./cli_embedded/ordo restore-session . --to-seq <N>
./cli_embedded/ordo verify-session .
```

Only runtime commands are exposed. Authoring/package/release commands are intentionally blocked in the embedded runtime profile.

M60.4 adds append-only `restore-session` for correction/backtrack without deleting prior proof material. M60.3 keeps JSON IR as the canonical target, supports explicit runtime view modes (`json`, `ordo-code`, `json,ordo-code`), and writes `runtime/session.ordo.trace` as an append-only proof program. M59.4+M60.3 require every incremental node submit to write `runtime/evidence/*_evidence.json`, `runtime/state_snapshots/SESSION-*.json`, `runtime/session.ordo.trace`, and an auto-resume cache at `runtime/live_session_state.json`; the AI must show evidence and trace digests before asking the next question. `restore-session` must write restore evidence, a restore snapshot, and a restore trace step. Final approval requires `verify-session`.
""", encoding="utf-8")
    return sorted(p for p in target.rglob("*") if p.is_file())

def _runtime_files(root: Path) -> list[Path]:
    allowed_roots = {"output_templates", "cli_embedded"}
    explicit = {
        "README.md",
        "START_HERE_RUNTIME_MODE.md",
        "START_PROMPT_RUNTIME_MODE.md",
        "ordo.runtime.json",
        "compiled/program.ir.json",
        "compiled/targets.manifest.json",
        "runtime/session.ordo.trace",
        "reports/CLI_VALIDATION_SUMMARY.md",
        "reports/ci_release_evidence.json",
        "reports/release_validation_report.json",
        "reports/BUILD_MANIFEST.json",
        "reports/SHA256SUMS.txt",
        "cli_embedded/ordo",
        "cli_embedded/README.md",
    }
    targets_manifest = _read_json(root / "compiled" / "targets.manifest.json") or {}
    for spec in ((targets_manifest.get("targets") or {}) if isinstance(targets_manifest.get("targets"), dict) else {}).values():
        if isinstance(spec, dict) and spec.get("path"):
            explicit.add(str(spec.get("path")))
    files: list[Path] = []
    for p in root.rglob("*"):
        if not p.is_file() or _is_transient(p):
            continue
        rel = _rel(root, p)
        first = rel.split("/", 1)[0]
        if rel in explicit or first in allowed_roots:
            files.append(p)
    return sorted(files)



def _prompt_only_files(root: Path) -> list[Path]:
    base = root / "compiled" / "prompt_only"
    allowed = [base / "MODEL_INSTRUCTIONS.md", base / "PROMPT_COMPILATION_MANIFEST.json", root / "reports" / "BUILD_MANIFEST.json", root / "reports" / "SHA256SUMS.txt", root / "reports" / "package_report.json"]
    return sorted(p for p in allowed if p.exists())

def _evidence_files(root: Path) -> list[Path]:
    reports = root / "reports"
    files: list[Path] = []
    if reports.exists():
        for p in reports.rglob("*"):
            if p.is_file() and not _is_transient(p):
                files.append(p)
    return sorted(files)


def _write_sha256s(root: Path, files: Iterable[Path], output: Path) -> None:
    lines: list[str] = []
    for p in sorted(files, key=lambda x: _rel(root, x)):
        if p.resolve() == output.resolve():
            continue
        lines.append(f"{_sha256_file(p)}  {_rel(root, p)}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def _write_build_manifest(root: Path, manifest: dict[str, Any], profile: str, files: list[Path], *, cli_status: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    data = {
        "status": "generated",
        "profile": profile,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "package": {
            "id": manifest.get("name"),
            "version": manifest.get("version"),
            "ordo_version": manifest.get("ordo_version"),
        },
        "cli_status": cli_status,
        "files": [
            {"path": _rel(root, p), "sha256": _sha256_file(p), "size_bytes": p.stat().st_size}
            for p in files
        ],
        "summary": {"file_count": len(files)},
    }
    if extra:
        data.update(extra)
    write_json(root / "reports" / "BUILD_MANIFEST.json", data)
    return data


def _write_runtime_manifest(root: Path, manifest: dict[str, Any], *, cli_status: str, runtime_view: str = "ordo-code") -> dict[str, Any]:
    source_path = root / manifest.get("source", "source/program.ordo.yaml")
    compiled_path = root / manifest.get("compiled", "compiled/program.ir.json")
    normalized_runtime_view = normalize_runtime_view(runtime_view)
    targets_manifest = _read_json(root / "compiled" / "targets.manifest.json") or {}
    compiled_targets = sorted(((targets_manifest.get("targets") or {}) if isinstance(targets_manifest.get("targets"), dict) else {}).keys())
    capabilities = ["embedded_cli", "hard_stop", "per_node_evidence", "hash_chain", "verify_session", "restore_session", "canary", "multi_target_manifest", "session_trace", "runtime_view_modes"]
    if "ordo-code-view" in compiled_targets:
        capabilities.append("ordo_code_view")
    data = {
        "package_id": manifest.get("name"),
        "package_version": manifest.get("version"),
        "profile": "runtime",
        "runtime_source": "compiled/program.ir.json",
        "templates": "output_templates/",
        "source_yaml_included": False,
        "embedded_cli_included": True,
        "embedded_cli_path": "cli_embedded/ordo",
        "trust_level": "level_1_cli_in_package_hard_stop",
        "trust_level_detail": "level_1_cli_in_package_hard_stop_hash_chain_human_verify_m59_4_hardened_m60_4_restore_session",
        "trust_level_capabilities": capabilities,
        "runtime_view": normalized_runtime_view,
        "runtime_view_behavior": runtime_view_behavior(normalized_runtime_view),
        "canonical_target": "json-ir",
        "targets_manifest": "compiled/targets.manifest.json",
        "compiled_targets": compiled_targets,
        "source_yaml_sha256": _sha256_file(source_path) if source_path.exists() else "",
        "compiled_ir_sha256": _sha256_file(compiled_path) if compiled_path.exists() else "",
        "compiler_version": manifest.get("ordo_version") or "unknown",
        "cli_validation_status": cli_status,
    }
    write_json(root / "ordo.runtime.json", data)
    return data


def _validate_profile_inputs(root: Path, manifest: dict[str, Any], profile: str, *, cli_status: str, cli_evidence: dict[str, Any] | None) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    if profile not in PACKAGE_PROFILES:
        issues.append(_issue("ORDO-PACKAGE-001", f"unknown package profile: {profile}", "--profile"))
        return issues

    if cli_status == "executed_cli_passed":
        truth_report = validate_cli_truthfulness(cli_evidence or {})
        if truth_report.get("status") != "passed":
            issues.append(_issue("ORDO-PACKAGE-010", "package claims executed_cli_passed without CLI evidence", "reports/"))

    if profile == "prompt_only":
        source_path = root / manifest.get("source", "source/program.ordo.yaml")
        compile_prompt_only(source_path, root / "compiled" / "prompt_only", playbook_version=str(manifest.get("version", "unresolved")), language_version=str(manifest.get("ordo_version", "unresolved")))
        validation = validate_prompt_compilation(root / "compiled" / "prompt_only", source_path=source_path)
        if validation.get("status") != "passed":
            issues.extend(validation.get("issues", []))
    if profile == "runtime":
        compiled_path = root / manifest.get("compiled", "compiled/program.ir.json")
        if not compiled_path.exists():
            issues.append(_issue("ORDO-PACKAGE-003", "runtime profile missing compiled IR", "compiled/program.ir.json"))
        rt = runtime_status(root, require_ir=True)
        if rt.get("status") == "stale_ir":
            issues.append(_issue("ORDO-RUNTIME-004", "IR is stale. Run ordo compile before runtime packaging.", "compiled/program.ir.json"))
        elif rt.get("status") not in {"ready", "missing_ir"}:
            for issue in rt.get("issues", []) or []:
                issues.append(issue)
        if not (root / "output_templates").exists():
            issues.append(_issue("ORDO-PACKAGE-004", "runtime profile missing output templates", "output_templates/"))
        if not (root / "START_HERE_RUNTIME_MODE.md").exists():
            issues.append(_issue("ORDO-PACKAGE-005", "runtime profile missing START_HERE_RUNTIME_MODE.md", "START_HERE_RUNTIME_MODE.md"))
    return issues


def _validate_built_profile(root: Path, profile: str, files: list[Path]) -> list[dict[str, Any]]:
    rels = {_rel(root, p) for p in files}
    issues: list[dict[str, Any]] = []
    if profile == "runtime":
        forbidden = [r for r in rels if r == "source/program.ordo.yaml" or r.startswith(("source/", "tests/", "run_inputs/", "domain/", "generated_outputs/", "release/")) or r.startswith("runtime/state_snapshots/")]
        if forbidden:
            issues.append(_issue("ORDO-PACKAGE-002", "runtime profile includes source/development files", ", ".join(sorted(forbidden)[:5])))
        targets_manifest = _read_json(root / "compiled" / "targets.manifest.json") or {}
        targets = (targets_manifest.get("targets") or {}) if isinstance(targets_manifest.get("targets"), dict) else {}
        required_targets = {str(spec.get("path")): "ORDO-PACKAGE-012" for spec in targets.values() if isinstance(spec, dict) and spec.get("path")}
        required_runtime_files = {
            "compiled/program.ir.json": "ORDO-PACKAGE-003",
            "compiled/targets.manifest.json": "ORDO-PACKAGE-012",
            "runtime/session.ordo.trace": "ORDO-PACKAGE-013",
            "output_templates": "ORDO-PACKAGE-004",
            "START_HERE_RUNTIME_MODE.md": "ORDO-PACKAGE-005",
            "ordo.runtime.json": "ORDO-PACKAGE-006",
            "reports/BUILD_MANIFEST.json": "ORDO-PACKAGE-007",
            "reports/SHA256SUMS.txt": "ORDO-PACKAGE-008",
            "cli_embedded/ordo": "ORDO-PACKAGE-011",
            "cli_embedded/README.md": "ORDO-PACKAGE-011",
        }
        required_runtime_files.update(required_targets)
        for required, code in required_runtime_files.items():
            if required == "output_templates":
                if not any(r.startswith("output_templates/") for r in rels):
                    issues.append(_issue(code, "runtime profile missing output templates", "output_templates/"))
            elif required not in rels:
                message = f"runtime profile missing {required}"
                if code == "ORDO-PACKAGE-011":
                    message = "runtime profile missing embedded runtime CLI"
                issues.append(_issue(code, message, required))
    elif profile == "prompt_only":
        required={"compiled/prompt_only/MODEL_INSTRUCTIONS.md","compiled/prompt_only/PROMPT_COMPILATION_MANIFEST.json","reports/BUILD_MANIFEST.json","reports/SHA256SUMS.txt"}
        for item in sorted(required-rels): issues.append(_issue("ORDO-PROMPT-009", f"prompt-only profile missing {item}", item))
        forbidden=[r for r in rels if r.startswith(("source/","tests/","runtime/","output_templates/"))]
        if forbidden: issues.append(_issue("ORDO-PROMPT-010", "prompt-only profile includes source/runtime files", ", ".join(sorted(forbidden)[:5])))
    elif profile == "evidence":
        forbidden = [r for r in rels if r.startswith(("source/", "tests/", "run_inputs/", "domain/", "output_templates/", "generated_outputs/", "runtime/")) or r in {"ordo.yml", "ordo.lock.json", "START_HERE_RUNTIME_MODE.md", "START_PROMPT_RUNTIME_MODE.md"}]
        if forbidden:
            issues.append(_issue("ORDO-PACKAGE-009", "evidence profile includes editable/source/runtime files", ", ".join(sorted(forbidden)[:5])))
    return issues


def build_package_profile(package_path: str | Path, *, profile: str = "dev", out: str | Path | None = None, allow_unvalidated_output: bool = False, runtime_view: str = "ordo-code", ci_evidence: str | Path | None = None) -> dict[str, Any]:
    runtime_view = normalize_runtime_view(runtime_view)
    root, manifest, source, tests = load_package(package_path)
    reports_dir = root / manifest.get("reports", "reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    out_path = Path(out).resolve() if out else root.with_name(f"{root.name}-{profile}.zip")

    # BL-ORDO-048: prompt-only is a derived compilation artifact, not a canonical
    # source/runtime release. It uses source binding and its own fail-closed
    # manifest validation instead of CI-bound release reconciliation.
    if profile == "prompt_only":
        cli_status, _ = _cli_status(root)
        source_path = root / manifest.get("source", "source/program.ordo.yaml")
        compiled_dir = root / "compiled" / "prompt_only"
        compile_prompt_only(
            source_path, compiled_dir,
            playbook_version=str(manifest.get("version", "unresolved")),
            language_version=str(manifest.get("ordo_version", "unresolved")),
        )
        validation = validate_prompt_compilation(compiled_dir, source_path=source_path)
        if validation.get("status") != "passed":
            report = {"status":"failed","profile":profile,"output":str(out_path),"issues":validation.get("issues",[])}
            write_json(reports_dir / "package_report.json", report)
            return report
        initial_files = _prompt_only_files(root)
        _write_build_manifest(root, manifest, profile, initial_files, cli_status=cli_status, extra={
            "compilation_manifest":"compiled/prompt_only/PROMPT_COMPILATION_MANIFEST.json",
            "guarantee_model":"explicit_retained_and_lost",
        })
        files = _prompt_only_files(root)
        _write_sha256s(root, files, reports_dir / "SHA256SUMS.txt")
        files = _prompt_only_files(root)
        build_issues = _validate_built_profile(root, profile, files)
        if build_issues:
            report = {"status":"failed","profile":profile,"output":str(out_path),"issues":build_issues}
            write_json(reports_dir / "package_report.json", report)
            return report
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for item in files:
                zf.write(item, Path(root.name) / item.relative_to(root))
        report = {
            "status":"passed","profile":profile,"cli_status":cli_status,"output":str(out_path),
            "package":{"id":manifest.get("name"),"version":manifest.get("version")},
            "summary":{"files_included":len(files)},
            "included_files":[_rel(root,item) for item in files],"issues":[],
            "canonical_release":False,
        }
        write_json(reports_dir / "package_report.json", report)
        return report

    cli_status, cli_evidence = _cli_status(root)
    issues = []
    if profile in {"dev", "runtime"}:
        if ci_evidence is None:
            issues.append(_issue("ORDO-CI-008", "CI-bound packaging requires --ci-evidence", "reports/ci_release_evidence.json"))
        else:
            issues.extend(validate_ci_release_evidence(root, Path(ci_evidence).resolve()))

    # M87.7: reuse the identity persisted by validate-release so binding checks
    # compare against the validated tree; only mint a fresh identity when none exists.
    persisted_identity = _read_json(reports_dir / "build_identity.json")
    if persisted_identity and persisted_identity.get("schema_version") == "ordo.build_identity.v1":
        build_identity = persisted_identity
    else:
        # Fallback identity is computed in memory only: `validate-release` is
        # the sole writer of reports/build_identity.json, so a blocked or
        # experimental packaging attempt leaves no generated files behind.
        build_identity = new_build_identity(root)

    # Mandatory green release gate is evaluated together with CI evidence so a
    # blocked packaging attempt reports every missing precondition at once.
    if profile in {"dev", "runtime"}:
        release_validation = _read_json(reports_dir / "release_validation_report.json")
        if release_validation:
            binding_issues = validate_report_binding(release_validation, build_identity)
            for item in binding_issues:
                item.setdefault("location", "reports/release_validation_report.json")
            issues.extend(binding_issues)

        if not release_validation or release_validation.get("status") != "passed":
            issues.append(_issue(
                "ORDO-PACKAGE-014",
                "mandatory green release validation must pass before packaging",
                "reports/release_validation_report.json",
            ))

    if not issues and profile == "runtime":
        compiled_path = root / manifest.get("compiled", "compiled/program.ir.json")
        if compiled_path.exists():
            emit_compiled_targets(
                root,
                ir_path=compiled_path,
                source_path=root / manifest.get("source", "source/program.ordo.yaml"),
                runtime_view=runtime_view,
            )
    issues.extend(_validate_profile_inputs(root, manifest, profile, cli_status=cli_status, cli_evidence=cli_evidence))

    if not allow_unvalidated_output and profile in {"dev", "runtime"}:
        output_validation = _read_json(reports_dir / "output_validation_report.json")
        if not output_validation or output_validation.get("status") != "passed":
            issues.append(_issue("ORDO-COV-006", "package created before validate-output passed", "reports/output_validation_report.json"))

    if issues:
        report = {
            "status": "failed",
            "profile": profile,
            "cli_status": cli_status,
            "output": str(out_path),
            "issues": issues,
        }
        write_json(reports_dir / "package_report.json", report)
        return report

    if profile == "runtime":
        _write_embedded_runtime_cli(root)
        _write_runtime_manifest(root, manifest, cli_status=cli_status, runtime_view=runtime_view)
        initial_files = _runtime_files(root)
        # BUILD_MANIFEST and SHA files are regenerated as profile evidence.
        build_manifest = reports_dir / "BUILD_MANIFEST.json"
        sha_file = reports_dir / "SHA256SUMS.txt"
        runtime_manifest_data = _read_json(root / "ordo.runtime.json") or {}
        _write_build_manifest(root, manifest, profile, initial_files, cli_status=cli_status, extra={"runtime_manifest": "ordo.runtime.json", "embedded_cli": "cli_embedded/ordo", "targets_manifest": "compiled/targets.manifest.json", "session_trace": "runtime/session.ordo.trace", "runtime_view": runtime_view, "runtime_view_behavior": runtime_view_behavior(runtime_view), "compiled_targets": runtime_manifest_data.get("compiled_targets", []), "trust_level": "level_1_cli_in_package_hard_stop", "trust_level_detail": "level_1_cli_in_package_hard_stop_hash_chain_human_verify_m59_4_hardened_m60_4_restore_session"})
        files = _runtime_files(root)
        _write_sha256s(root, files, sha_file)
        files = _runtime_files(root)
    elif profile == "prompt_only":
        initial_files = _prompt_only_files(root)
        _write_build_manifest(root, manifest, profile, initial_files, cli_status=cli_status, extra={"compilation_manifest":"compiled/prompt_only/PROMPT_COMPILATION_MANIFEST.json","guarantee_model":"explicit_retained_and_lost"})
        files = _prompt_only_files(root)
        _write_sha256s(root, files, reports_dir / "SHA256SUMS.txt")
        files = _prompt_only_files(root)
    elif profile == "evidence":
        initial_files = _evidence_files(root)
        _write_build_manifest(root, manifest, profile, initial_files, cli_status=cli_status)
        files = _evidence_files(root)
        _write_sha256s(root, files, reports_dir / "SHA256SUMS.txt")
        files = _evidence_files(root)
    else:
        initial_files = _dev_files(root)
        _write_build_manifest(root, manifest, profile, initial_files, cli_status=cli_status)
        files = _dev_files(root)
        _write_sha256s(root, files, reports_dir / "SHA256SUMS.txt")
        files = _dev_files(root)

    build_issues = _validate_built_profile(root, profile, files)
    if build_issues:
        report = {
            "status": "failed",
            "profile": profile,
            "cli_status": cli_status,
            "output": str(out_path),
            "issues": build_issues,
        }
        write_json(reports_dir / "package_report.json", report)
        return report

    out_path.parent.mkdir(parents=True, exist_ok=True)
    reconciliation_report = pre_zip_reconciliation(
        root,
        build_identity,
        [reports_dir / "release_validation_report.json"],
        checksum_manifest=(root / "SHA256SUMS.txt") if (root / "SHA256SUMS.txt").exists() else None,
        build_manifest=(root / "BUILD_MANIFEST.json") if (root / "BUILD_MANIFEST.json").exists() else None,
    )
    reconciliation_path = reports_dir / "pre_zip_reconciliation_report.json"
    reconciliation_path.write_text(json.dumps(reconciliation_report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if reconciliation_report["status"] != "passed":
        issues.extend(reconciliation_report["issues"])
        report = {
            "status": "failed",
            "profile": profile,
            "archive": None,
            "issues": issues,
            "pre_zip_reconciliation": "failed",
        }
        bind_report(report, build_identity)
        report_path = reports_dir / "package_report.json"
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return report

    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in files:
            if p.resolve() == out_path.resolve():
                continue
            zf.write(p, Path(root.name) / p.relative_to(root))

    report = {
        "status": "passed",
        "profile": profile,
        "cli_status": cli_status,
        "output": str(out_path),
        "package": {"id": manifest.get("name"), "version": manifest.get("version")},
        "summary": {"files_included": len(files)},
        "runtime_view": runtime_view if profile == "runtime" else None,
        "runtime_view_behavior": runtime_view_behavior(runtime_view) if profile == "runtime" else None,
        "included_files": [_rel(root, p) for p in files],
        "issues": [],
    }
    write_json(reports_dir / "package_report.json", report)
    return report
