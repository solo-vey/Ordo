from __future__ import annotations

from pathlib import Path
from typing import Any

from .artifact_validator import validate_artifacts
from .compiler import compile_source
from .consistency import consistency as build_consistency_report
from .coverage import build_coverage
from .contract_coverage import validate_contract_artifact_references
from .helpers import validate_state
from .intake import guided_intake
from .linter import lint_source
from .loader import load_package
from .output_generator import generate_output
from .registry_checks import find_repo_root, validate_ir_opcodes, validate_capability_registry
from .reporter import write_json


_NO_GO_BY_STEP = {
    "lint": "no_go_requires_source_fix",
    "compile": "no_go_requires_runner_contract",
    "coverage": "no_go_requires_template_fix",
    "validate-state": "no_go_requires_confirmation",
    "intake": "no_go_requires_confirmation",
    "generate-output": "no_go_requires_artifact_fix",
    "validate-artifacts": "no_go_requires_artifact_fix",
    "consistency": "no_go_requires_artifact_fix",
}


def _step(name: str, status: str, *, report_path: str | None = None, summary: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "step": name,
        "status": status,
        "report": report_path,
        "summary": summary or {},
    }


def _issue(step: str, message: str, *, report_path: str | None = None, code: str = "ORDO-GNG-001") -> dict[str, Any]:
    return {
        "severity": "error",
        "code": code,
        "step": step,
        "message": message,
        "report": report_path,
    }


def _rel(root: Path, path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path)


def _compile_step(root: Path, manifest: dict[str, Any], source: dict[str, Any], tests: dict[str, Any], lint_report: dict[str, Any], *, force: bool = False) -> tuple[dict[str, Any], dict[str, Any] | None]:
    out = root / manifest.get("compiled", "compiled/program.ir.json")
    contract_artifact_report = validate_contract_artifact_references(source)
    opcode_registry_report: dict[str, Any] = {"status": "skipped", "reason": "compile skipped"}
    capability_registry_report: dict[str, Any] = {"status": "skipped", "reason": "compile skipped"}
    ir: dict[str, Any] | None = None

    if lint_report.get("status") != "passed" and not force:
        compile_status = "failed_lint"
    else:
        ir = compile_source(source)
        write_json(out, ir)
        repo_root = find_repo_root(root)
        opcode_registry_report = validate_ir_opcodes(ir, repo_root)
        capability_registry_report = validate_capability_registry(repo_root)
        compile_status = "passed" if lint_report.get("status") == "passed" else "passed_with_lint_errors_forced"

    if contract_artifact_report.get("status") == "failed":
        compile_status = "failed_contract_artifact_references"
    if opcode_registry_report.get("status") == "failed":
        compile_status = "failed_opcode_registry_mismatch"
    if capability_registry_report.get("status") == "failed":
        compile_status = "failed_capability_registry_mismatch"

    report = {
        "status": compile_status,
        "source": manifest.get("source", "source/program.ordo.yaml"),
        "output": _rel(root, out),
        "ops_count": len((ir or {}).get("ops", [])),
        "lint_status": lint_report.get("status"),
        "contract_artifact_reference_check": contract_artifact_report,
        "opcode_registry_check": opcode_registry_report,
        "capability_registry_check": capability_registry_report,
    }
    write_json(root / "reports" / "compile_report.json", report)
    return report, ir


def _blocking_status(steps: list[dict[str, Any]]) -> str:
    for item in steps:
        status = item.get("status")
        name = item.get("step")
        if status in {"passed", "generated", "go"}:
            continue
        if status == "passed_with_warnings":
            continue
        return _NO_GO_BY_STEP.get(str(name), "no_go")
    return "go"


def go_no_go(
    package_path: str | Path,
    *,
    answers_path: str | Path | None = None,
    state_path: str | Path | None = None,
    artifacts: str | Path | None = None,
    run_intake: bool = False,
    generate_outputs: bool = False,
    allow_blocked_output: bool = False,
    force_compile: bool = False,
    out: str | Path | None = None,
) -> dict[str, Any]:
    """Run the M46.5 deterministic go/no-go validation pipeline.

    This helper composes existing Ordo checks. It does not execute an AI model,
    external systems, databases, REST APIs, or project business code.
    """
    root, manifest, source, tests = load_package(package_path)
    reports_dir = root / manifest.get("reports", "reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    steps: list[dict[str, Any]] = []
    blocking_issues: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    repo_root = find_repo_root(root)
    lint_report = lint_source(source, tests, repo_root=str(repo_root) if repo_root else None)
    lint_path = reports_dir / "lint_report.json"
    write_json(lint_path, lint_report)
    steps.append(_step("lint", lint_report.get("status", "failed"), report_path=_rel(root, lint_path), summary=lint_report.get("summary", {})))
    if lint_report.get("status") != "passed":
        blocking_issues.append(_issue("lint", "lint failed", report_path=_rel(root, lint_path)))

    compile_report, _ir = _compile_step(root, manifest, source, tests, lint_report, force=force_compile)
    compile_path = reports_dir / "compile_report.json"
    steps.append(_step("compile", compile_report.get("status", "failed"), report_path=_rel(root, compile_path), summary={
        "ops_count": compile_report.get("ops_count"),
        "contract_artifact_reference_check": (compile_report.get("contract_artifact_reference_check") or {}).get("status"),
        "opcode_registry_check": (compile_report.get("opcode_registry_check") or {}).get("status"),
    }))
    if compile_report.get("status") not in {"passed", "passed_with_lint_errors_forced"}:
        blocking_issues.append(_issue("compile", "compile failed", report_path=_rel(root, compile_path)))

    coverage_report = build_coverage(source, tests)
    coverage_path = reports_dir / "coverage_report.json"
    write_json(coverage_path, coverage_report)
    steps.append(_step("coverage", coverage_report.get("status", "failed"), report_path=_rel(root, coverage_path), summary=coverage_report.get("summary", {})))
    if coverage_report.get("status") not in {"passed", "generated"}:
        blocking_issues.append(_issue("coverage", "coverage failed", report_path=_rel(root, coverage_path)))

    if run_intake:
        intake_report = guided_intake(root, answers_path=answers_path, non_interactive=True)
        intake_path = reports_dir / "intake_report.json"
        steps.append(_step("intake", intake_report.get("status", "completed"), report_path=_rel(root, intake_path), summary={
            "violations": len(intake_report.get("violations", []) or []),
            "blocked_outputs": len(intake_report.get("blocked_outputs", []) or []),
        }))
        if intake_report.get("violations") or intake_report.get("blocked_outputs"):
            blocking_issues.append(_issue("intake", "guided intake has violations or blocked outputs", report_path=_rel(root, intake_path)))

    inferred_state_path = state_path
    if inferred_state_path is None and answers_path is None:
        intake_report_path = reports_dir / "intake_report.json"
        if intake_report_path.exists():
            inferred_state_path = intake_report_path

    state_report = validate_state(root, state_path=inferred_state_path, answers_path=answers_path, out=reports_dir / "state_validation_report.json")
    state_report_path = reports_dir / "state_validation_report.json"
    steps.append(_step("validate-state", state_report.get("status", "blocked"), report_path=_rel(root, state_report_path), summary={
        "missing_required_fields": len(state_report.get("missing_required_fields", []) or []),
        "blocked_gates": len(state_report.get("blocked_gates", []) or []),
        "violations": len(state_report.get("violations", []) or []),
    }))
    if state_report.get("status") != "passed":
        blocking_issues.append(_issue("validate-state", "state validation failed", report_path=_rel(root, state_report_path)))

    if generate_outputs:
        output_report = generate_output(root, out=artifacts, require_allowed=not allow_blocked_output)
        output_path = reports_dir / "output_generation_report.json"
        steps.append(_step("generate-output", output_report.get("status", "failed"), report_path=_rel(root, output_path), summary={
            "generated_files": len(output_report.get("generated_files", []) or []),
            "artifacts_total": output_report.get("artifacts_total"),
        }))
        if output_report.get("status") != "passed":
            blocking_issues.append(_issue("generate-output", "output generation failed or is blocked", report_path=_rel(root, output_path)))

    artifact_report = validate_artifacts(root, artifacts=artifacts, state_path=state_path, out=reports_dir / "artifact_validation_report.json")
    artifact_path = reports_dir / "artifact_validation_report.json"
    steps.append(_step("validate-artifacts", artifact_report.get("status", "failed"), report_path=_rel(root, artifact_path), summary=artifact_report.get("summary", {})))
    if artifact_report.get("status") != "passed":
        blocking_issues.append(_issue("validate-artifacts", "rendered artifact validation failed", report_path=_rel(root, artifact_path)))
        blocking_issues.extend(artifact_report.get("issues", []) or [])
    warnings.extend(artifact_report.get("warnings", []) or [])

    consistency_report = build_consistency_report(root, artifacts=artifacts, state_path=state_path, out=reports_dir / "CONSISTENCY_CHECK_REPORT.json")
    consistency_path = reports_dir / "CONSISTENCY_CHECK_REPORT.json"
    steps.append(_step("consistency", consistency_report.get("status", "failed"), report_path=_rel(root, consistency_path), summary=consistency_report.get("summary", {})))
    if consistency_report.get("status") not in {"passed", "passed_with_warnings"}:
        blocking_issues.append(_issue("consistency", "cross-artifact consistency failed", report_path=_rel(root, consistency_path)))
        blocking_issues.extend(consistency_report.get("blocking_issues", []) or [])
    warnings.extend(consistency_report.get("warnings", []) or [])

    status = _blocking_status(steps)
    if blocking_issues and status == "go":
        status = "no_go"

    report = {
        "status": status,
        "kind": "go_no_go",
        "mode": "deterministic_helper_pipeline",
        "cli_status": "executed_cli_passed" if status == "go" else "executed_cli_failed",
        "executed_commands": [step["step"] for step in steps],
        "package": {"name": manifest.get("name"), "version": manifest.get("version")},
        "pipeline": [step["step"] for step in steps],
        "steps": steps,
        "blocking_issues": blocking_issues,
        "warnings": warnings,
        "summary": {
            "steps_total": len(steps),
            "blocking_issues": len(blocking_issues),
            "warnings": len(warnings),
            "artifacts_dir": str(Path(artifacts).resolve()) if artifacts else str(root / "generated_outputs"),
        },
        "known_limitations": [
            "go-no-go composes deterministic helper checks; it does not execute an AI model.",
            "rendered artifact checks are based on declared contract values and artifact mappings.",
            "business/runtime system behavior still requires project-specific tests outside this helper.",
        ],
    }
    output = Path(out).resolve() if out else reports_dir / "GO_NO_GO_REPORT.json"
    write_json(output, report)
    return report
