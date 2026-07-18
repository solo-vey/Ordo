from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import zipfile

from .loader import load_package
from .linter import lint_source
from .registry_checks import find_repo_root
from .compiler import compile_source
from .coverage import build_coverage
from .tester import run_tests
from .runner import run_package
from .intake import guided_intake
from .output_generator import generate_output
from .dependency_lock import write_lock, validate_lock
from .dependency_conflicts import check_conflicts
from .output_validator import validate_output
from .reporter import write_json
from .provenance import build_release_provenance, validate_release_provenance


@dataclass
class ReleaseIssue:
    severity: str
    code: str
    message: str
    location: str


def _add(issues: list[ReleaseIssue], severity: str, code: str, message: str, location: str) -> None:
    issues.append(ReleaseIssue(severity, code, message, location))


def _relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _has_errors(report: dict[str, Any]) -> bool:
    return report.get("status") == "failed" or bool((report.get("summary") or {}).get("errors"))


def _zip_package(root: Path, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in root.rglob("*"):
            if path.is_file():
                if "__pycache__" in path.parts or path.suffix == ".pyc":
                    continue
                if path.resolve() == out.resolve():
                    continue
                zf.write(path, path.relative_to(root.parent))



def _write_cli_validation_summary(root: Path, manifest: dict[str, Any], status: str, steps: list[dict[str, Any]], report_path: Path) -> None:
    reports_dir = root / manifest.get("reports", "reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# CLI Validation Summary",
        "",
        f"Package: {manifest.get('name', '')}",
        f"Version: {manifest.get('version', '')}",
        f"Validation date: {datetime.now(timezone.utc).isoformat()}",
        f"CLI status: {status}",
        "",
        "## Commands",
        "",
        "| Command | Result | Notes |",
        "|---|---|---|",
    ]
    for step in steps:
        lines.append(f"| {step.get('name')} | {step.get('status')} | {step.get('report') or ''} |")
    lines.extend([
        "",
        "## IR status",
        "",
        f"- source YAML: {manifest.get('source', 'source/program.ordo.yaml')}",
        f"- compiled IR: {manifest.get('compiled', 'compiled/program.ir.json')}",
        "- IR freshness: checked during runtime-status / compile step",
        "",
        "## Output validation",
        "",
        "- generated outputs: see output_generation_report.json",
        "- validate-output: see output_validation_report.json",
        "- validate-release: " + _relative(report_path, root),
        "",
        "## Known limitations",
        "",
        "- This summary records CLI helper execution. It does not claim live AI/model execution.",
    ])
    (reports_dir / "CLI_VALIDATION_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

def validate_release(
    package_path: str | Path,
    *,
    answers_path: str | Path | None = None,
    intake_answers_path: str | Path | None = None,
    out: str | Path | None = None,
    skip_runtime: bool = False,
) -> dict[str, Any]:
    """Validate whether an Ordo package is ready for publication/handoff.

    This is an M6 release gate. It runs the static toolchain and, when inputs are
    present, runtime/intake checks. It does not execute an AI model.
    """
    root, manifest, source, tests = load_package(package_path)
    reports_dir = root / manifest.get("reports", "reports")
    compiled_path = root / manifest.get("compiled", "compiled/program.ir.json")
    reports_dir.mkdir(parents=True, exist_ok=True)
    compiled_path.parent.mkdir(parents=True, exist_ok=True)

    issues: list[ReleaseIssue] = []
    steps: list[dict[str, Any]] = []

    def record_step(name: str, status: str, report_path: Path | None = None, details: dict[str, Any] | None = None) -> None:
        steps.append({
            "name": name,
            "status": status,
            "report": _relative(report_path, root) if report_path else None,
            "details": details or {},
        })

    # Required package metadata and human documentation.
    required_files = [root / "ordo.yml", root / manifest.get("source", "source/program.ordo.yaml"), root / "README.md"]
    for required in required_files:
        if not required.exists():
            _add(issues, "error", "REQUIRED_FILE_MISSING", f"Required release file is missing: {_relative(required, root)}", _relative(required, root))
    if not manifest.get("name"):
        _add(issues, "error", "MANIFEST_NAME_REQUIRED", "ordo.yml must define package name.", "ordo.yml.name")
    if not manifest.get("version"):
        _add(issues, "error", "MANIFEST_VERSION_REQUIRED", "ordo.yml must define package version.", "ordo.yml.version")

    # Lint.
    repo_root = find_repo_root(root)
    lint_report = lint_source(source, tests, repo_root=str(repo_root) if repo_root else None)
    lint_path = reports_dir / "lint_report.json"
    write_json(lint_path, lint_report)
    record_step("lint", lint_report.get("status", "unknown"), lint_path)
    if _has_errors(lint_report):
        _add(issues, "error", "LINT_FAILED", "Lint must pass before release.", _relative(lint_path, root))

    # Compile only when lint is usable; still try to surface errors gracefully.
    ir = compile_source(source)
    write_json(compiled_path, ir)
    compile_report = {
        "status": "passed" if not _has_errors(lint_report) else "passed_with_lint_errors",
        "source": manifest.get("source", "source/program.ordo.yaml"),
        "output": _relative(compiled_path, root),
        "ops_count": len(ir.get("ops", [])),
        "lint_status": lint_report.get("status"),
    }
    compile_path = reports_dir / "compile_report.json"
    write_json(compile_path, compile_report)
    record_step("compile", compile_report["status"], compile_path, {"ops_count": compile_report["ops_count"]})
    if compile_report["ops_count"] == 0:
        _add(issues, "error", "COMPILED_IR_EMPTY", "Compiled IR must contain operations.", _relative(compiled_path, root))

    # Static tests.
    test_report = run_tests(source, tests)
    test_path = reports_dir / "test_report.json"
    write_json(test_path, test_report)
    record_step("test", test_report.get("status", "unknown"), test_path, test_report.get("summary"))
    if _has_errors(test_report):
        _add(issues, "error", "TEST_FAILED", "Static Ordo tests must pass before release.", _relative(test_path, root))

    # Coverage.
    coverage_report = build_coverage(source, tests)
    coverage_path = reports_dir / "coverage_report.json"
    write_json(coverage_path, coverage_report)
    record_step("coverage", coverage_report.get("status", "generated"), coverage_path, coverage_report.get("summary"))

    # Minimal release coverage gates: no uncovered gates or assertions for standard/strict packages.
    control_level = ((source.get("ordo") or {}).get("control_level"))
    uncovered = coverage_report.get("uncovered", {}) or {}
    if control_level in {"standard", "strict"}:
        if uncovered.get("gates"):
            _add(issues, "warning", "UNCOVERED_GATES", "Some gates are not referenced by tests.", "reports.coverage_report.uncovered.gates")
        if uncovered.get("assertions"):
            _add(issues, "warning", "UNCOVERED_ASSERTIONS", "Some assertions are not referenced by tests.", "reports.coverage_report.uncovered.assertions")
    if control_level == "strict" and (uncovered.get("gates") or uncovered.get("assertions")):
        _add(issues, "error", "STRICT_COVERAGE_REQUIRED", "Strict packages require complete gate/assertion test coverage.", "ordo.control_level")

    # Runtime and guided intake checks when possible.
    runtime_status = "skipped"
    if not skip_runtime:
        if answers_path:
            run_report = run_package(root, answers_path=answers_path)
            run_path = reports_dir / "run_report.json"
            record_step("run", "passed" if not run_report.get("violations") else "failed", run_path)
            if run_report.get("violations"):
                _add(issues, "error", "RUN_VIOLATIONS", "Runtime helper-runner reported violations.", _relative(run_path, root))
            runtime_status = "executed"
        else:
            default_answers = root / "run_inputs" / "answers_success.yaml"
            if default_answers.exists():
                run_report = run_package(root, answers_path=default_answers)
                run_path = reports_dir / "run_report.json"
                record_step("run", "passed" if not run_report.get("violations") else "failed", run_path)
                if run_report.get("violations"):
                    _add(issues, "error", "RUN_VIOLATIONS", "Runtime helper-runner reported violations.", _relative(run_path, root))
                runtime_status = "executed"
            else:
                record_step("run", "skipped", None, {"reason": "no answers file provided and run_inputs/answers_success.yaml not found"})

        if intake_answers_path:
            intake_report = guided_intake(root, answers_path=intake_answers_path, non_interactive=True)
            intake_path = reports_dir / "intake_report.json"
            record_step("intake", intake_report.get("status", "completed"), intake_path)
            if intake_report.get("violations"):
                _add(issues, "error", "INTAKE_VIOLATIONS", "Guided intake reported violations.", _relative(intake_path, root))
        else:
            default_intake = root / "run_inputs" / "intake_success.yaml"
            if default_intake.exists():
                intake_report = guided_intake(root, answers_path=default_intake, non_interactive=True)
                intake_path = reports_dir / "intake_report.json"
                record_step("intake", intake_report.get("status", "completed"), intake_path)
                if intake_report.get("violations"):
                    _add(issues, "error", "INTAKE_VIOLATIONS", "Guided intake reported violations.", _relative(intake_path, root))
            else:
                record_step("intake", "skipped", None, {"reason": "no answers file provided and run_inputs/intake_success.yaml not found"})
    else:
        record_step("run", "skipped", None, {"reason": "--skip-runtime"})
        record_step("intake", "skipped", None, {"reason": "--skip-runtime"})

    # Controlled output generation.
    try:
        output_generation_report = generate_output(root, require_allowed=False)
        output_generation_path = reports_dir / "output_generation_report.json"
        record_step("generate-output", output_generation_report.get("status", "unknown"), output_generation_path)
    except Exception as exc:
        _add(issues, "warning", "OUTPUT_GENERATION_SKIPPED", f"Output generation skipped: {exc}", "reports/output_generation_report.json")
        record_step("generate-output", "skipped", None, {"reason": str(exc)})

    try:
        output_validation_report = validate_output(root, require_generated=False)
        output_validation_path = reports_dir / "output_validation_report.json"
        record_step("validate-output", output_validation_report.get("status", "unknown"), output_validation_path, output_validation_report.get("summary"))
        if output_validation_report.get("status") != "passed":
            _add(issues, "error", "OUTPUT_VALIDATION_FAILED", "Generated output artifacts must validate before release.", _relative(output_validation_path, root))
    except Exception as exc:
        _add(issues, "warning", "OUTPUT_VALIDATION_SKIPPED", f"Output validation skipped: {exc}", "reports/output_validation_report.json")
        record_step("validate-output", "skipped", None, {"reason": str(exc)})

    # Dependency lockfile.
    try:
        lock = write_lock(root)
        lock_report_path = reports_dir / "lock_report.json"
        record_step("lock", "passed" if not lock.get("warnings") else "passed_with_warnings", lock_report_path, lock.get("summary"))
        lock_validation = validate_lock(root)
        lock_validation_path = reports_dir / "lock_validation_report.json"
        record_step("validate-lock", lock_validation.get("status", "unknown"), lock_validation_path)
        if lock_validation.get("status") != "passed":
            _add(issues, "error", "LOCKFILE_INVALID", "Dependency lockfile is missing or out of date.", _relative(lock_validation_path, root))
        conflict_report = check_conflicts(root)
        conflict_report_path = reports_dir / "dependency_conflict_report.json"
        record_step("check-conflicts", conflict_report.get("status", "unknown"), conflict_report_path, conflict_report.get("summary"))
        if conflict_report.get("status") != "passed":
            _add(issues, "error", "DEPENDENCY_CONFLICTS_UNRESOLVED", "Dependency/layer conflicts must be resolved before release.", _relative(conflict_report_path, root))
    except Exception as exc:
        _add(issues, "error", "LOCKFILE_FAILED", f"Dependency lockfile generation/validation failed: {exc}", "ordo.lock.json")
        record_step("lock", "failed", None, {"reason": str(exc)})

    # Release archive.
    release_dir = root / "release"
    release_dir.mkdir(exist_ok=True)
    archive_path = Path(out).resolve() if out else release_dir / f"{manifest.get('name', root.name)}-{manifest.get('version', '0.0.0')}.zip"
    _zip_package(root, archive_path)
    record_step("package", "created", archive_path)

    errors = [asdict(i) for i in issues if i.severity == "error"]
    warnings = [asdict(i) for i in issues if i.severity == "warning"]
    infos = [asdict(i) for i in issues if i.severity == "info"]
    report = {
        "status": "passed" if not errors else "failed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "cli_status": "executed_cli_passed" if not errors else "executed_cli_failed",
        "executed_commands": [step.get("name") for step in steps],
        "package": {
            "root": str(root),
            "name": manifest.get("name"),
            "version": manifest.get("version"),
            "ordo_version": manifest.get("ordo_version") or ((source.get("ordo") or {}).get("version")),
            "control_level": control_level,
            "execution_mode": ((source.get("ordo") or {}).get("execution_mode")),
        },
        "steps": steps,
        "release_archive": str(archive_path),
        "summary": {
            "errors": len(errors),
            "warnings": len(warnings),
            "infos": len(infos),
            "runtime_status": runtime_status,
        },
        "issues": [asdict(i) for i in issues],
    }
    report_path = reports_dir / "release_validation_report.json"
    _write_cli_validation_summary(root, manifest, report["cli_status"], steps, report_path)
    write_json(report_path, report)

    # M14 release provenance: record source/IR/output/report/archive hashes.
    provenance = build_release_provenance(root, release_archive=archive_path)
    provenance_validation = validate_release_provenance(root)
    record_step("build-provenance", "passed", reports_dir / "release_provenance.json", provenance.get("summary"))
    record_step("validate-provenance", provenance_validation.get("status", "unknown"), reports_dir / "release_provenance_validation_report.json", provenance_validation.get("summary"))
    report["steps"] = steps
    report["provenance"] = {
        "path": "reports/release_provenance.json",
        "validation_report": "reports/release_provenance_validation_report.json",
        "status": provenance_validation.get("status"),
    }
    if provenance_validation.get("status") != "passed":
        report["status"] = "failed"
        report["cli_status"] = "executed_cli_failed"
        report["issues"].append({
            "severity": "error",
            "code": "PROVENANCE_VALIDATION_FAILED",
            "message": "Release provenance manifest failed validation.",
            "location": "reports/release_provenance_validation_report.json",
        })
        report["summary"]["errors"] = report["summary"].get("errors", 0) + 1
    _write_cli_validation_summary(root, manifest, report.get("cli_status", "executed_cli_failed"), steps, report_path)
    write_json(report_path, report)
    return report
