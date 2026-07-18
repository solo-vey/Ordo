from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
import zipfile

from .loader import load_package, load_yaml
from .linter import lint_source
from .compiler import compile_source
from .coverage import build_coverage
from .contract_coverage import validate_contract_artifact_references
from .tester import run_tests
from .runner import run_package
from .intake import guided_intake, submit_intake_node
from .release import validate_release
from .output_generator import generate_output
from .dependency_lock import write_lock, validate_lock
from .dependency_conflicts import check_conflicts
from .output_validator import validate_output
from .artifact_validator import validate_artifacts
from .consistency import consistency as build_consistency_report
from .go_no_go import go_no_go
from .rendering_policy import validate_rendering_policy
from .provenance import build_release_provenance, validate_release_provenance
from .release_diff import diff_release_provenance
from .release_notes import generate_release_notes
from .helpers import validate_state, check_gate, next_step, diff_state, explain_validation
from .reporter import write_json
from .registry_checks import find_repo_root, validate_ir_opcodes, validate_capability_registry
from .repo_checks import run_repo_checks
from .clean_check import run_clean_check
from .runtime import runtime_status, runtime_entry_protocol, validate_cli_truthfulness, validate_runtime_start_files_standard
from .session_chain import verify_session, PROTOCOL_LINE
from .runtime_restore import restore_session
from .targets import emit_compiled_targets, render_runtime_view, verify_targets, normalize_runtime_view
from .package_profiles import build_package_profile
from . import __version__

TEMPLATE_DIR = Path(__file__).parent / "templates" / "package_template"


def cmd_init(args: argparse.Namespace) -> int:
    target = Path(args.name).resolve()
    if target.exists() and any(target.iterdir()):
        print(f"ERROR: target exists and is not empty: {target}", file=sys.stderr)
        return 2
    shutil.copytree(TEMPLATE_DIR, target, dirs_exist_ok=True)
    package_name = args.package or target.name.replace("-", "_")
    for path in target.rglob("*"):
        if path.is_file() and path.suffix in {".yaml", ".yml", ".md"}:
            text = path.read_text(encoding="utf-8")
            text = text.replace("example.first_package", package_name)
            text = text.replace("First Ordo Package", package_name)
            path.write_text(text, encoding="utf-8")
    print(f"Created Ordo package template: {target}")
    return 0


def cmd_lint(args: argparse.Namespace) -> int:
    root, manifest, source, tests = load_package(args.package)
    repo_root = find_repo_root(root)
    report = lint_source(source, tests, repo_root=str(repo_root) if repo_root else None)
    rendering_report = validate_rendering_policy(root, manifest)
    runtime_start_report = validate_runtime_start_files_standard(root)

    def merge_subreport(key: str, subreport: dict) -> None:
        issues = subreport.get("issues", []) or []
        warnings = subreport.get("warnings", []) or []
        if issues or warnings:
            report.setdefault("issues", []).extend(issues + warnings)
            summary = report.setdefault("summary", {})
            summary["errors"] = int(summary.get("errors", 0)) + len([i for i in issues if i.get("severity", "error") == "error"])
            summary["warnings"] = int(summary.get("warnings", 0)) + len(warnings) + len([i for i in issues if i.get("severity") == "warning"])
            report["status"] = "failed" if int(summary.get("errors", 0)) else report.get("status", "passed")
        report[key] = subreport

    merge_subreport("rendering_policy_check", rendering_report)
    merge_subreport("runtime_start_files_check", runtime_start_report)
    out = root / "reports" / "lint_report.json"
    write_json(out, report)
    print(f"lint: {report['status']} ({out})")
    return 0 if report["status"] == "passed" else 1


def cmd_compile(args: argparse.Namespace) -> int:
    root, manifest, source, tests = load_package(args.package)
    repo_root = find_repo_root(root)
    lint_report = lint_source(source, tests, repo_root=str(repo_root) if repo_root else None)
    write_json(root / "reports" / "lint_report.json", lint_report)
    if lint_report["status"] != "passed" and not args.force:
        print("compile: failed because lint failed. Use --force to compile anyway.", file=sys.stderr)
        return 1
    contract_artifact_report = validate_contract_artifact_references(source)
    ir = compile_source(source)
    out = root / manifest.get("compiled", "compiled/program.ir.json")
    write_json(out, ir)
    targets_manifest = emit_compiled_targets(
        root,
        ir_path=out,
        source_path=root / manifest.get("source", "source/program.ordo.yaml"),
        runtime_view="ordo-code",
    )
    opcode_registry_report = validate_ir_opcodes(ir, repo_root)
    capability_registry_report = validate_capability_registry(repo_root)
    compile_status = "passed" if lint_report["status"] == "passed" else "passed_with_lint_errors_forced"
    if contract_artifact_report["status"] == "failed":
        compile_status = "failed_contract_artifact_references"
    if opcode_registry_report["status"] == "failed":
        compile_status = "failed_opcode_registry_mismatch"
    if capability_registry_report["status"] == "failed":
        compile_status = "failed_capability_registry_mismatch"
    compile_report = {
        "status": compile_status,
        "source": manifest.get("source", "source/program.ordo.yaml"),
        "output": str(out.relative_to(root)),
        "targets_manifest": "compiled/targets.manifest.json",
        "targets": sorted((targets_manifest.get("targets") or {}).keys()),
        "ops_count": len(ir.get("ops", [])),
        "lint_status": lint_report["status"],
        "contract_artifact_reference_check": contract_artifact_report,
        "opcode_registry_check": opcode_registry_report,
        "capability_registry_check": capability_registry_report,
    }
    write_json(root / "reports" / "compile_report.json", compile_report)
    print(f"compile: {compile_report['status']} ({out})")
    if contract_artifact_report["status"] == "failed":
        print("compile: contract/artifact reference check failed", file=sys.stderr)
        return 1
    if opcode_registry_report["status"] == "failed":
        print(f"compile: opcode registry mismatch missing_ops={opcode_registry_report['missing_ops']}", file=sys.stderr)
        return 1
    if capability_registry_report["status"] == "failed":
        print("compile: capability registry mismatch", file=sys.stderr)
        return 1
    return 0


def cmd_test(args: argparse.Namespace) -> int:
    root, manifest, source, tests = load_package(args.package)
    report = run_tests(source, tests)
    out = root / "reports" / "test_report.json"
    write_json(out, report)
    summary = report.get("summary", {})
    static_marker = report.get("mode", "static_behavior_validation")
    assertion_note = ""
    if "assertions_behaviorally_evaluated" in summary:
        assertion_note = f"; assertions {summary.get('assertions_behaviorally_evaluated')}/{summary.get('assertions_total')} behaviorally evaluated"
    print(f"test: {report['status']} [static mode: {static_marker}{assertion_note}] ({out})")
    return 0 if report["status"] == "passed" else 1


def cmd_coverage(args: argparse.Namespace) -> int:
    root, manifest, source, tests = load_package(args.package)
    report = build_coverage(source, tests)
    out = root / "reports" / "coverage_report.json"
    write_json(out, report)
    print(f"coverage: {report['status']} ({out})")
    return 0 if report["status"] in {"generated", "passed"} else 1


def cmd_run(args: argparse.Namespace) -> int:
    report = run_package(args.package, answers_path=args.answers, state_path=args.state, csg_events_path=args.csg_events)
    status = "passed"
    if report.get("violations") or report.get("blocked_outputs"):
        status = "completed_with_blocks"
    print(f"run: {status} ({args.package}/reports/run_report.json)")
    return 0 if not report.get("violations") else 1


def _digest_value(report: dict) -> str:
    digest = report.get("report_digest") or report.get("evidence_digest") or {}
    return str(digest.get("value") or "") if isinstance(digest, dict) else ""


def _effective_next_step_format(package: str, requested: str | None) -> str:
    requested_norm = str(requested or "auto").strip().lower()
    if requested_norm not in {"", "auto"}:
        return "ordo-code" if requested_norm in {"ordo-code", "ordo-code-view"} else "json"
    try:
        from .runtime import resolve_runtime_paths
        resolved = resolve_runtime_paths(package)
        manifest = resolved.get("manifest") if isinstance(resolved, dict) else {}
        runtime_manifest = (manifest or {}).get("runtime_manifest") if isinstance(manifest, dict) else None
        runtime_view = normalize_runtime_view((runtime_manifest or {}).get("runtime_view") if isinstance(runtime_manifest, dict) else "json")
        return "ordo-code" if runtime_view in {"ordo-code", "json,ordo-code"} else "json"
    except Exception:
        return "json"


def _read_submit_answer(args: argparse.Namespace):
    if getattr(args, "answer", None) is not None and getattr(args, "answer_file", None):
        print("intake --submit accepts either --answer or --answer-file, not both", file=sys.stderr)
        return False, None
    if getattr(args, "answer_file", None):
        path = Path(args.answer_file)
        try:
            loaded = load_yaml(path)
            if isinstance(loaded, dict) and "answer" in loaded:
                return True, loaded.get("answer")
            if loaded not in ({}, None):
                return True, loaded
        except Exception:
            pass
        return True, path.read_text(encoding="utf-8").strip()
    return True, getattr(args, "answer", None)


def cmd_intake(args: argparse.Namespace) -> int:
    if getattr(args, "submit", None):
        ok, answer = _read_submit_answer(args)
        if not ok:
            return 2
        if answer is None:
            print("intake --submit requires --answer or --answer-file", file=sys.stderr)
            return 2
        report = submit_intake_node(args.package, node_id=args.submit, answer=answer, state_path=args.state, out=args.out)
        status = report.get("status", "blocked")
        out = Path(args.out).resolve() if args.out else Path(args.package).resolve() / "reports" / "intake_submit_report.json"
        evidence = report.get("evidence_report")
        evidence_digest = ((report.get("evidence_digest") or {}).get("value") if isinstance(report.get("evidence_digest"), dict) else "")
        print(f"intake-submit: {status} node={args.submit} next_node={report.get('next_node')} ({out})")
        if evidence:
            print(f"evidence: {evidence} sha256={evidence_digest}")
        trace = report.get("session_trace") if isinstance(report.get("session_trace"), dict) else {}
        if trace.get("path"):
            print(f"session-trace: {trace.get('path')} sha256={trace.get('trace_digest', '')}")
        print(PROTOCOL_LINE)
        return 0 if status == "passed" else 1
    report = guided_intake(args.package, answers_path=args.answers, start_node=args.start_node, non_interactive=args.non_interactive)
    status = report.get("status", "completed")
    if report.get("blocked_outputs") and status not in {"failed", "blocked"}:
        status = "completed_with_blocks"
    digest = _digest_value(report)
    reason = report.get("reason")
    print(f"intake: {status} ({args.package}/reports/intake_report.json)" + (f" reason={reason}" if reason else "") + (f" sha256={digest}" if digest else ""))
    return 0 if status not in {"failed", "blocked"} and not report.get("violations") else 1


def cmd_validate_state(args: argparse.Namespace) -> int:
    report = validate_state(args.package, state_path=args.state, answers_path=args.answers, out=args.out)
    out = Path(args.out).resolve() if args.out else Path(args.package).resolve() / "reports" / "state_validation_report.json"
    digest = _digest_value(report)
    print(f"validate-state: {report['status']} ({out})" + (f" sha256={digest}" if digest else ""))
    print("helper role: deterministic helper; AI must interpret before user-facing response")
    return 0 if report["status"] == "passed" else 1


def cmd_check_gate(args: argparse.Namespace) -> int:
    report = check_gate(args.package, args.gate_id, state_path=args.state, answers_path=args.answers, out=args.out)
    out = Path(args.out).resolve() if args.out else Path(args.package).resolve() / "reports" / f"gate_{args.gate_id}_check_report.json"
    gate_status = (report.get("gate") or {}).get("status")
    digest = _digest_value(report)
    print(f"check-gate: {report['status']} gate_status={gate_status} ({out})" + (f" sha256={digest}" if digest else ""))
    print("helper role: deterministic helper; AI must interpret before user-facing response")
    return 0 if report["status"] == "passed" else 1


def cmd_next_step(args: argparse.Namespace) -> int:
    effective_format = _effective_next_step_format(args.package, getattr(args, "format", "auto"))
    report = next_step(args.package, state_path=args.state, answers_path=args.answers, out=args.out)
    out = Path(args.out).resolve() if args.out else Path(args.package).resolve() / "reports" / "next_step_report.json"
    if effective_format == "ordo-code" and report.get("suggested_next_node"):
        view_report = render_runtime_view(args.package, format="ordo-code", node_id=str(report.get("suggested_next_node")), out=Path(args.package).resolve() / "reports" / "runtime_view_report.json")
        if view_report.get("status") != "generated":
            report["status"] = "blocked"
            report["runtime_view"] = {
                "format": "ordo-code",
                "status": view_report.get("status"),
                "issues": view_report.get("issues", []),
            }
        else:
            report["runtime_view"] = {
                "format": "ordo-code",
                "status": "generated",
                "view_report": "reports/runtime_view_report.json",
                "view_digest": (view_report.get("report_digest") or {}).get("value") if isinstance(view_report.get("report_digest"), dict) else "",
                "current_contract": view_report.get("view", ""),
            }
        report["effective_format"] = effective_format
        report = {**report}
        from .runtime_evidence import attach_report_digest
        report = attach_report_digest(report)
        write_json(out, report)
    else:
        report["effective_format"] = effective_format
        from .runtime_evidence import attach_report_digest
        report = attach_report_digest(report)
        write_json(out, report)
    digest = _digest_value(report)
    print(f"next-step: {report['suggested_next_action']} node={report.get('suggested_next_node')} format={effective_format} ({out})" + (f" sha256={digest}" if digest else ""))
    if effective_format == "ordo-code":
        rv = report.get("runtime_view") or {}
        if rv.get("current_contract"):
            print("current_contract:")
            print(str(rv.get("current_contract")).rstrip())
            if rv.get("view_digest"):
                print(f"runtime-view-report: reports/runtime_view_report.json sha256={rv.get('view_digest')}")
        elif rv.get("issues"):
            print("runtime-view: blocked", file=sys.stderr)
    print(PROTOCOL_LINE)
    print("helper role: deterministic helper; AI may adapt the human-facing wording")
    return 0 if report.get("status") != "blocked" else 1


def cmd_render_runtime_view(args: argparse.Namespace) -> int:
    report = render_runtime_view(args.package, format=args.format, node_id=args.node, out=args.out)
    out = Path(args.out).resolve() if args.out else Path(args.package).resolve() / "reports" / "runtime_view_report.json"
    digest = _digest_value(report)
    print(f"render-runtime-view: {report.get('status')} format={args.format} node={args.node or ''} ({out})" + (f" sha256={digest}" if digest else ""))
    if report.get("view"):
        print(str(report.get("view")).rstrip())
    print(PROTOCOL_LINE)
    return 0 if report.get("status") == "generated" else 1


def cmd_verify_targets(args: argparse.Namespace) -> int:
    report = verify_targets(args.package, out=args.out)
    out = Path(args.out).resolve() if args.out else Path(args.package).resolve() / "reports" / "target_verification_report.json"
    print(report.get("terminal_line", "target-set: inconsistent"))
    print(f"verify-targets: {report.get('status')} ({out})")
    return 0 if report.get("status") == "passed" else 1


def cmd_diff_state(args: argparse.Namespace) -> int:
    report = diff_state(args.package, before=args.before, after=args.after, out=args.out)
    out = Path(args.out).resolve() if args.out else Path(args.package).resolve() / "reports" / "state_diff_report.json"
    print(f"diff-state: changed_fields={len(report.get('changed_fields', []))} ({out})")
    return 0


def cmd_explain_validation(args: argparse.Namespace) -> int:
    report = explain_validation(args.package, report_path=args.report, out=args.out)
    out = Path(args.out).resolve() if args.out else Path(args.package).resolve() / "reports" / "validation_explanation_report.json"
    print(f"explain-validation: {report['status']} ({out})")
    for line in report.get("ai_facing_summary", []):
        print(f"- {line}")
    return 0



def cmd_validate_artifacts(args: argparse.Namespace) -> int:
    report = validate_artifacts(args.package, artifacts=args.artifacts, state_path=args.state, out=args.out)
    out = Path(args.out).resolve() if args.out else Path(args.package).resolve() / "reports" / "artifact_validation_report.json"
    print(f"validate-artifacts: {report['status']} ({out})")
    return 0 if report["status"] == "passed" else 1


def cmd_consistency(args: argparse.Namespace) -> int:
    report = build_consistency_report(args.package, artifacts=args.artifacts, state_path=args.state, out=args.out)
    out = Path(args.out).resolve() if args.out else Path(args.package).resolve() / "reports" / "CONSISTENCY_CHECK_REPORT.json"
    print(f"consistency: {report['status']} go_no_go={report.get('go_no_go')} ({out})")
    return 0 if report["status"] in {"passed", "passed_with_warnings"} else 1


def cmd_go_no_go(args: argparse.Namespace) -> int:
    report = go_no_go(
        args.package,
        answers_path=args.answers,
        state_path=args.state,
        artifacts=args.artifacts,
        run_intake=args.run_intake,
        generate_outputs=args.generate_output,
        allow_blocked_output=args.allow_blocked_output,
        force_compile=args.force_compile,
        out=args.out,
    )
    out = Path(args.out).resolve() if args.out else Path(args.package).resolve() / "reports" / "GO_NO_GO_REPORT.json"
    print(f"go-no-go: {report['status']} ({out})")
    if report.get("blocking_issues"):
        print(f"blocking issues: {len(report.get('blocking_issues') or [])}")
    return 0 if report["status"] == "go" else 1


def cmd_validate_release(args: argparse.Namespace) -> int:
    report = validate_release(args.package, answers_path=args.answers, intake_answers_path=args.intake_answers, out=args.out, skip_runtime=args.skip_runtime)
    out = Path(args.package).resolve() / "reports" / "release_validation_report.json"
    print(f"validate-release: {report['status']} ({out})")
    if report.get("release_archive"):
        print(f"release archive: {report['release_archive']}")
    return 0 if report["status"] == "passed" else 1


def _latest_report_data(package: str, report_name: str) -> dict:
    path = Path(package).resolve() / "reports" / report_name
    if not path.exists():
        return {}
    try:
        import json
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _latest_report_passed(package: str, report_name: str) -> bool:
    data = _latest_report_data(package, report_name)
    return data.get("status") in {"passed", "go"}


def cmd_generate_output(args: argparse.Namespace) -> int:
    state_report = _latest_report_data(args.package, "state_validation_report.json")
    if not args.allow_blocked and state_report.get("status") not in {"passed", "go"}:
        out = Path(args.package).resolve() / "reports" / "output_generation_report.json"
        issue = {
            "severity": "error",
            "code": "ORDO-COV-005",
            "message": "output generated before validate-state passed",
            "location": "reports/state_validation_report.json",
        }
        # If validate-state did run and exposed checkpoint gaps, use the more
        # precise M57 checkpoint error as the blocking reason.
        if state_report and state_report.get("checkpoint") and not (state_report.get("checkpoint") or {}).get("forward_allowed", False):
            issue = {
                "severity": "error",
                "code": "ORDO-CHECKPOINT-006",
                "message": "generated output requested while checkpoint gaps remain",
                "location": "reports/state_validation_report.json",
            }
        write_json(out, {"status": "failed", "issues": [issue]})
        print(f"generate-output: failed ({out})")
        print(f"{issue['code']} {issue['message']}", file=sys.stderr)
        return 1
    report = generate_output(args.package, out=args.out, require_allowed=not args.allow_blocked)
    out = Path(args.package).resolve() / "reports" / "output_generation_report.json"
    print(f"generate-output: {report['status']} ({out})")
    for path in report.get("generated_files", []):
        print(f"generated: {path}")
    return 0 if report["status"] == "passed" else 1


def cmd_validate_output(args: argparse.Namespace) -> int:
    report = validate_output(args.package, require_generated=not args.allow_missing)
    print(f"validate-output: {report['status']} ({args.package}/reports/output_validation_report.json)")
    return 0 if report["status"] == "passed" else 1


def cmd_lock(args: argparse.Namespace) -> int:
    lock = write_lock(args.package, out=args.out)
    print(f"lock: generated ({args.package}/ordo.lock.json)")
    print(f"dependencies: {lock.get('summary', {}).get('dependencies_total', 0)}")
    return 0


def cmd_validate_lock(args: argparse.Namespace) -> int:
    report = validate_lock(args.package)
    print(f"validate-lock: {report['status']} ({args.package}/reports/lock_validation_report.json)")
    return 0 if report["status"] == "passed" else 1


def cmd_check_conflicts(args: argparse.Namespace) -> int:
    report = check_conflicts(args.package)
    print(f"check-conflicts: {report['status']} ({args.package}/reports/dependency_conflict_report.json)")
    return 0 if report["status"] == "passed" else 1


def cmd_build_provenance(args: argparse.Namespace) -> int:
    report = build_release_provenance(args.package, release_archive=args.release_archive)
    print(f"build-provenance: {report['status']} ({args.package}/reports/release_provenance.json)")
    return 0 if report["status"] == "passed" else 1


def cmd_validate_provenance(args: argparse.Namespace) -> int:
    report = validate_release_provenance(args.package)
    print(f"validate-provenance: {report['status']} ({args.package}/reports/release_provenance_validation_report.json)")
    return 0 if report["status"] == "passed" else 1


def cmd_diff_release(args: argparse.Namespace) -> int:
    report = diff_release_provenance(args.package, base=args.base, head=args.head, out=args.out)
    print(f"diff-release: {report['status']} ({args.package}/reports/release_diff_report.json)")
    return 0 if report["status"] in {"passed", "changed"} else 1


def cmd_generate_release_notes(args: argparse.Namespace) -> int:
    report = generate_release_notes(args.package, diff=args.diff, out=args.out)
    print(f"generate-release-notes: {report['status']} ({report['output']})")
    print(f"diff status: {report.get('summary', {}).get('diff_status')}")
    return 0


def cmd_runtime_entry(args: argparse.Namespace) -> int:
    report = runtime_entry_protocol(args.package, state_path=args.state, out=args.out)
    out = Path(args.out).resolve() if args.out else Path(args.package).resolve() / "reports" / "runtime_entry_report.json"
    next_node = (report.get("next_step") or {}).get("node_id")
    print(f"runtime-entry: {report['status']} next_node={next_node} ({out})")
    return 0 if report.get("status") == "ready" else 1


def cmd_runtime_status(args: argparse.Namespace) -> int:
    report = runtime_status(args.package, require_ir=not args.allow_missing_ir, out=args.out)
    out = Path(args.out).resolve() if args.out else Path(args.package).resolve() / "reports" / "runtime_status_report.json"
    print(f"runtime-status: {report['status']} ({out})")
    return 0 if report.get("status") == "ready" or (args.allow_missing_ir and report.get("status") != "missing_manifest") else 1


def cmd_restore_session(args: argparse.Namespace) -> int:
    report = restore_session(args.package, to_seq=int(args.to_seq), out=args.out, reason=args.reason)
    out = Path(args.out).resolve() if args.out else Path(args.package).resolve() / "reports" / "restore_session_report.json"
    status = report.get("status", "blocked")
    restore = report.get("restore") if isinstance(report.get("restore"), dict) else {}
    print(f"restore-session: {status} to_seq={restore.get('to_seq')} next_node={report.get('next_node')} ({out})")
    evidence = report.get("evidence_report")
    evidence_digest = ((report.get("evidence_digest") or {}).get("value") if isinstance(report.get("evidence_digest"), dict) else "")
    if evidence:
        print(f"evidence: {evidence} sha256={evidence_digest}")
    trace = report.get("session_trace") if isinstance(report.get("session_trace"), dict) else {}
    if trace.get("path"):
        print(f"session-trace: {trace.get('path')} sha256={trace.get('trace_digest', '')}")
    print(PROTOCOL_LINE)
    return 0 if status == "passed" else 1


def cmd_verify_session(args: argparse.Namespace) -> int:
    report = verify_session(args.package, out=args.out)
    out = Path(args.out).resolve() if args.out else Path(args.package).resolve() / "reports" / "session_verification_report.json"
    print(report.get("terminal_line", "session-chain: broken at seq unknown"))
    print(f"verify-session: {report['status']} ({out})")
    return 0 if report.get("status") == "passed" else 1


def cmd_validate_cli_status(args: argparse.Namespace) -> int:
    import json
    path = Path(args.report).resolve()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        data = {"cli_status": "invalid", "error": str(exc)}
    report = validate_cli_truthfulness(data)
    out = Path(args.out).resolve() if args.out else path.with_name(path.stem + "_cli_truthfulness_report.json")
    write_json(out, report)
    print(f"validate-cli-status: {report['status']} ({out})")
    return 0 if report.get("status") in {"passed", "passed_with_warnings"} else 1


def cmd_repo_check(args: argparse.Namespace) -> int:
    report = run_repo_checks(
        args.repo,
        clean=getattr(args, "clean", False),
        clean_profile=getattr(args, "profile", "standard"),
        clean_fail_on_warning=getattr(args, "fail_on_warning", False),
        hygiene_scope=getattr(args, "hygiene_scope", "development"),
    )
    out = Path(args.out).resolve() if args.out else Path(args.repo).resolve() / "reports" / "repo_check_report.json"
    write_json(out, report)
    if getattr(args, "json", False):
        import json as _json
        print(_json.dumps(report, ensure_ascii=False, indent=2))
    else:
        suffix = " + clean" if getattr(args, "clean", False) else ""
        print(f"repo-check{suffix}: {report['status']} ({out})")
    return int(report.get("exit_code", 1))


def cmd_clean_check(args: argparse.Namespace) -> int:
    report = run_clean_check(
        args.package,
        profile=args.profile,
        fail_on_warning=getattr(args, "fail_on_warning", False),
    )
    out = Path(args.out).resolve() if args.out else Path(report.get("package_root", args.package)).resolve() / "reports" / "clean_check_report.json"
    write_json(out, report)
    if getattr(args, "json", False):
        import json as _json
        print(_json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"clean-check: {report['status']} profile={report.get('profile')} ({out})")
        if report.get("errors"):
            print(f"errors: {len(report['errors'])}", file=sys.stderr)
            for issue in report["errors"][:3]:
                print(f"{issue.get('check_id')}: {issue.get('message')}", file=sys.stderr)
        if report.get("warnings"):
            print(f"warnings: {len(report['warnings'])}", file=sys.stderr)
    return int(report.get("exit_code", 1))


def cmd_package(args: argparse.Namespace) -> int:
    report = build_package_profile(
        args.package,
        profile=args.profile,
        out=args.out,
        allow_unvalidated_output=getattr(args, "allow_unvalidated_output", False),
        runtime_view=getattr(args, "runtime_view", "ordo-code"),
    )
    out = report.get("output")
    print(f"package: {report['status']} profile={report.get('profile')} ({out})")
    if report.get("issues"):
        print(f"blocking issues: {len(report.get('issues') or [])}", file=sys.stderr)
        for issue in report.get("issues", [])[:3]:
            print(f"{issue.get('code')} {issue.get('message')}", file=sys.stderr)
    return 0 if report.get("status") == "passed" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ordo", description="Ordo v0.12 CLI v0.38.0")
    parser.add_argument("--version", action="version", version=f"ordo {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="Create a new Ordo package template")
    p.add_argument("name")
    p.add_argument("--package", help="Ordo package name, defaults to directory name")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("lint", help="Lint an Ordo package")
    p.add_argument("package")
    p.set_defaults(func=cmd_lint)

    p = sub.add_parser("compile", help="Compile Ordo Source to Semantic JSON IR")
    p.add_argument("package")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_compile)

    p = sub.add_parser("test", help="Run static Ordo test cases")
    p.add_argument("package")
    p.set_defaults(func=cmd_test)

    p = sub.add_parser("coverage", help="Generate coverage report")
    p.add_argument("package")
    p.set_defaults(func=cmd_coverage)

    p = sub.add_parser("run", help="Run helper-runner without AI model")
    p.add_argument("package")
    p.add_argument("--answers", help="YAML file with answers keyed by node id")
    p.add_argument("--state", help="YAML file with initial state overrides")
    p.add_argument("--csg-events", help="YAML/JSON list of model proposals to enforce through CSG runtime")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("intake", help="Run guided intake runtime without AI model or submit one node answer")
    p.add_argument("package")
    p.add_argument("--answers", help="YAML file with scripted answers keyed by node id")
    p.add_argument("--start-node", help="Node id to start from; defaults to first node")
    p.add_argument("--non-interactive", action="store_true", help="Do not prompt; block when an answer is missing")
    p.add_argument("--submit", metavar="NODE_ID", help="Submit exactly one node answer and write per-node evidence")
    p.add_argument("--answer", help="Answer value for --submit")
    p.add_argument("--answer-file", help="Read answer for --submit from UTF-8 text/YAML/JSON; mapping key `answer` is accepted")
    p.add_argument("--state", help="State/report JSON/YAML to continue from when using --submit")
    p.add_argument("--out", help="Optional submit report path; defaults to reports/intake_submit_report.json")
    p.set_defaults(func=cmd_intake)

    p = sub.add_parser("validate-state", help="Validate Ordo state as a deterministic helper for AI interpretation")
    p.add_argument("package")
    p.add_argument("--state", help="YAML file with state overrides")
    p.add_argument("--answers", help="YAML answers file to apply before validation")
    p.add_argument("--out", help="Optional output path; defaults to reports/state_validation_report.json")
    p.set_defaults(func=cmd_validate_state)

    p = sub.add_parser("check-gate", help="Evaluate one gate as a deterministic helper for AI interpretation")
    p.add_argument("package")
    p.add_argument("gate_id")
    p.add_argument("--state", help="YAML file with state overrides")
    p.add_argument("--answers", help="YAML answers file to apply before gate check")
    p.add_argument("--out", help="Optional output path")
    p.set_defaults(func=cmd_check_gate)

    p = sub.add_parser("next-step", help="Suggest the next Process Rail step from current state")
    p.add_argument("package")
    p.add_argument("--state", help="YAML file with state overrides")
    p.add_argument("--answers", help="YAML answers file to apply before next-step check")
    p.add_argument("--format", choices=["auto", "json", "ordo-code", "ordo-code-view"], default="auto", help="AI-facing output format; auto follows ordo.runtime.json runtime_view in runtime packages and uses json in source packages")
    p.add_argument("--out", help="Optional output path; defaults to reports/next_step_report.json")
    p.set_defaults(func=cmd_next_step)

    p = sub.add_parser("diff-state", help="Compare two state YAML files")
    p.add_argument("package")
    p.add_argument("--before", required=True, help="Previous state YAML")
    p.add_argument("--after", required=True, help="New state YAML")
    p.add_argument("--out", help="Optional output path; defaults to reports/state_diff_report.json")
    p.set_defaults(func=cmd_diff_state)

    p = sub.add_parser("explain-validation", help="Create AI-facing summary from a validation report")
    p.add_argument("package")
    p.add_argument("--report", help="Validation report path; defaults to reports/state_validation_report.json")
    p.add_argument("--out", help="Optional output path; defaults to reports/validation_explanation_report.json")
    p.set_defaults(func=cmd_explain_validation)


    p = sub.add_parser("validate-artifacts", help="Validate rendered Markdown/JSON/YAML artifacts against confirmed contract fields")
    p.add_argument("package")
    p.add_argument("--artifacts", help="Generated artifacts directory; defaults to package/generated_outputs")
    p.add_argument("--state", help="YAML/JSON state file; defaults to latest intake/run report")
    p.add_argument("--out", help="Optional output path; defaults to reports/artifact_validation_report.json")
    p.set_defaults(func=cmd_validate_artifacts)


    p = sub.add_parser("consistency", help="Generate CONSISTENCY_CHECK_REPORT.json for cross-artifact consistency")
    p.add_argument("package")
    p.add_argument("--artifacts", help="Generated artifacts directory; defaults to package/generated_outputs")
    p.add_argument("--state", help="YAML/JSON state file; defaults to latest intake/run report")
    p.add_argument("--out", help="Optional output path; defaults to reports/CONSISTENCY_CHECK_REPORT.json")
    p.set_defaults(func=cmd_consistency)


    p = sub.add_parser("go-no-go", help="Run final deterministic validation pipeline and return go/no-go")
    p.add_argument("package")
    p.add_argument("--answers", help="YAML answers file for validate-state or optional intake")
    p.add_argument("--state", help="YAML/JSON state file for validate-state/artifact checks")
    p.add_argument("--artifacts", help="Generated artifacts directory; defaults to package/generated_outputs")
    p.add_argument("--run-intake", action="store_true", help="Run guided intake first using --answers in non-interactive mode")
    p.add_argument("--generate-output", action="store_true", help="Generate output artifacts before artifact validation")
    p.add_argument("--allow-blocked-output", action="store_true", help="Allow generate-output even if output gates are blocked")
    p.add_argument("--force-compile", action="store_true", help="Compile even if lint fails, then still report no-go")
    p.add_argument("--out", help="Optional output path; defaults to reports/GO_NO_GO_REPORT.json")
    p.set_defaults(func=cmd_go_no_go)

    p = sub.add_parser("validate-release", help="Run package release validation and create release archive")
    p.add_argument("package")
    p.add_argument("--answers", help="YAML answers file for helper-runner")
    p.add_argument("--intake-answers", help="YAML answers file for guided intake")
    p.add_argument("--out", help="Release archive path")
    p.add_argument("--skip-runtime", action="store_true", help="Skip run/intake runtime checks")
    p.set_defaults(func=cmd_validate_release)

    p = sub.add_parser("generate-output", help="Generate controlled Markdown output artifacts from run/intake state")
    p.add_argument("package")
    p.add_argument("--out", help="Output directory; defaults to package/generated_outputs")
    p.add_argument("--allow-blocked", action="store_true", help="Generate even when output gates are blocked")
    p.set_defaults(func=cmd_generate_output)

    p = sub.add_parser("validate-output", help="Validate generated markdown output artifacts")
    p.add_argument("package")
    p.add_argument("--allow-missing", action="store_true", help="Do not fail when no generated output files exist")
    p.set_defaults(func=cmd_validate_output)

    p = sub.add_parser("lock", help="Resolve package dependencies and write ordo.lock.json")
    p.add_argument("package")
    p.add_argument("--out", help="Optional lockfile output path; defaults to package/ordo.lock.json")
    p.set_defaults(func=cmd_lock)

    p = sub.add_parser("validate-lock", help="Validate ordo.lock.json against currently resolved dependencies")
    p.add_argument("package")
    p.set_defaults(func=cmd_validate_lock)

    p = sub.add_parser("check-conflicts", help="Detect unresolved dependency/layer conflicts")
    p.add_argument("package")
    p.set_defaults(func=cmd_check_conflicts)

    p = sub.add_parser("build-provenance", help="Build release provenance manifest")
    p.add_argument("package")
    p.add_argument("--release-archive", help="Optional existing release archive path")
    p.set_defaults(func=cmd_build_provenance)

    p = sub.add_parser("validate-provenance", help="Validate release provenance manifest")
    p.add_argument("package")
    p.set_defaults(func=cmd_validate_provenance)

    p = sub.add_parser("diff-release", help="Compare two release provenance manifests")
    p.add_argument("package")
    p.add_argument("--base", required=True, help="Base release_provenance.json to compare from")
    p.add_argument("--head", help="Head release_provenance.json; defaults to package reports/release_provenance.json")
    p.add_argument("--out", help="Optional output path for release_diff_report.json")
    p.set_defaults(func=cmd_diff_release)

    p = sub.add_parser("generate-release-notes", help="Generate human-readable Markdown release notes from release_diff_report.json")
    p.add_argument("package")
    p.add_argument("--diff", help="Optional release_diff_report.json path; defaults to package reports/release_diff_report.json")
    p.add_argument("--out", help="Optional output Markdown path; defaults to package reports/release_notes.md")
    p.set_defaults(func=cmd_generate_release_notes)



    p = sub.add_parser("render-runtime-view", help="Render an AI-facing runtime contract view from compiled IR through CLI")
    p.add_argument("package")
    p.add_argument("--format", choices=["ordo-code", "ordo-code-view"], default="ordo-code")
    p.add_argument("--node", help="Optional node id; if omitted, render the package runtime view")
    p.add_argument("--out", help="Optional output path; defaults to reports/runtime_view_report.json")
    p.set_defaults(func=cmd_render_runtime_view)


    p = sub.add_parser("runtime-entry", help="Validate Runtime Mode entrypoint and derive first guided step from compiled IR")
    p.add_argument("package")
    p.add_argument("--state", help="Optional run_state JSON/YAML file")
    p.add_argument("--out", help="Optional output path; defaults to reports/runtime_entry_report.json")
    p.set_defaults(func=cmd_runtime_entry)

    p = sub.add_parser("runtime-status", help="Check package source-of-truth runtime readiness and stale IR")
    p.add_argument("package")
    p.add_argument("--allow-missing-ir", action="store_true", help="Report non-runtime fallback instead of failing on missing IR")
    p.add_argument("--out", help="Optional output path; defaults to reports/runtime_status_report.json")
    p.set_defaults(func=cmd_runtime_status)


    p = sub.add_parser("verify-targets", help="Verify M60 compiled target manifest and AI-facing target hashes")
    p.add_argument("package")
    p.add_argument("--out", help="Optional output path; defaults to reports/target_verification_report.json")
    p.set_defaults(func=cmd_verify_targets)


    p = sub.add_parser("restore-session", help="Append-only restore to a previous runtime snapshot sequence")
    p.add_argument("package")
    p.add_argument("--to-seq", required=True, type=int, help="Existing session snapshot sequence to restore state from")
    p.add_argument("--reason", help="Optional human-readable reason for the restore event")
    p.add_argument("--out", help="Optional output path; defaults to reports/restore_session_report.json")
    p.set_defaults(func=cmd_restore_session)


    p = sub.add_parser("verify-session", help="Verify M59.3 tamper-evident runtime session hash-chain and canary")
    p.add_argument("package")
    p.add_argument("--out", help="Optional output path; defaults to reports/session_verification_report.json")
    p.set_defaults(func=cmd_verify_session)

    p = sub.add_parser("validate-cli-status", help="Validate whether a report truthfully declares actual CLI execution status")
    p.add_argument("report")
    p.add_argument("--out", help="Optional output path")
    p.set_defaults(func=cmd_validate_cli_status)

    p = sub.add_parser("repo-check", help="Validate repository-level references and generated metadata")
    p.add_argument("repo", nargs="?", default=".")
    p.add_argument("--clean", action="store_true", help="Also aggregate repo-level package hygiene using clean-check policy")
    p.add_argument("--profile", choices=["light", "standard", "strict"], default="standard", help="Clean-check profile for --clean")
    p.add_argument("--fail-on-warning", action="store_true", help="For --clean, fail release-blocking roots with warnings")
    p.add_argument(
        "--hygiene-scope",
        choices=["development", "release"],
        default="development",
        help="development checks tracked source hygiene; release strictly scans the supplied candidate tree",
    )
    p.add_argument("--json", action="store_true", help="Print deterministic JSON report to stdout")
    p.add_argument("--out", help="Optional output path; defaults to reports/repo_check_report.json")
    p.set_defaults(func=cmd_repo_check)


    p = sub.add_parser("clean-check", help="Check whether an Ordo package is clean for handoff/release review")
    p.add_argument("package")
    p.add_argument("--profile", choices=["light", "standard", "strict"], default="standard")
    p.add_argument("--json", action="store_true", help="Print deterministic JSON report to stdout")
    p.add_argument("--fail-on-warning", action="store_true", help="Return non-zero when warnings are present")
    p.add_argument("--out", help="Optional output path; defaults to reports/clean_check_report.json")
    p.set_defaults(func=cmd_clean_check)

    p = sub.add_parser("package", help="Zip an Ordo package")
    p.add_argument("package")
    p.add_argument("--out")
    p.add_argument("--profile", choices=["dev", "runtime", "evidence"], default="dev", help="Package build profile")
    p.add_argument("--runtime-view", choices=["json", "ordo-code", "json,ordo-code", "ordo-code-view"], default="ordo-code", help="Runtime AI-facing projection mode; json-ir is always included as canonical")
    p.add_argument("--allow-unvalidated-output", action="store_true", help="Allow packaging without a passed validate-output report")
    p.set_defaults(func=cmd_package)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
