from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import subprocess
import hashlib

from .execution_trace import replay_plan, state_fingerprint, validate_execution_trace
from .loader import load_package
from .runtime_evidence import file_sha256, write_report_with_digest


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _git_clean(checkout: Path) -> tuple[bool, str | None]:
    if not (checkout / ".git").exists():
        return False, "CHECKOUT_NOT_A_GIT_WORKTREE"
    result = subprocess.run(
        ["git", "-C", str(checkout), "status", "--porcelain"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        return False, "CHECKOUT_STATUS_UNAVAILABLE"
    return not bool(result.stdout.strip()), None if not result.stdout.strip() else "CHECKOUT_DIRTY"


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Ordo deterministic replay report",
        "",
        f"- Status: `{report['status']}`",
        f"- Replay mode: `{report['replay_mode']}`",
        f"- Trace: `{report['trace']}`",
        f"- Checkout: `{report['checkout']}`",
        f"- Replayed records: `{report['summary']['replayed_records']}`",
        "",
        "## Findings",
        "",
    ]
    findings = report.get("findings") or []
    if not findings:
        lines.append("No mismatches or unsupported conditions.")
    else:
        for item in findings:
            lines.append(f"- `{item['code']}` — {item['message']}")
    return "\n".join(lines) + "\n"


def replay_recorded_run(
    *,
    checkout: str | Path,
    package: str | Path,
    trace_path: str | Path,
    out: str | Path | None = None,
) -> dict[str, Any]:
    """Replay recorded evidence without model calls or external side effects.

    This is deliberately a deterministic *evidence replay*.  A trace that needs an
    unrecorded external dependency is blocked rather than guessed or executed.
    """
    checkout_path = Path(checkout).resolve()
    package_path = Path(package).resolve()
    trace_file = Path(trace_path).resolve()
    findings: list[dict[str, str]] = []
    clean, clean_issue = _git_clean(checkout_path)
    if clean_issue:
        findings.append({"code": clean_issue, "message": "replay requires a clean Git checkout"})
    if not _inside(package_path, checkout_path):
        findings.append({"code": "PACKAGE_OUTSIDE_CHECKOUT", "message": "package must be located inside the supplied checkout"})
    if not trace_file.is_file():
        findings.append({"code": "TRACE_NOT_FOUND", "message": "execution trace file does not exist"})
        trace: dict[str, Any] = {}
    else:
        try:
            trace = json.loads(trace_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            trace = {}
            findings.append({"code": "TRACE_INVALID_JSON", "message": "execution trace is not valid JSON"})

    validation = validate_execution_trace(trace) if trace else {"valid": False, "issues": []}
    for issue in validation.get("issues", []):
        findings.append({"code": str(issue.get("code")), "message": str(issue.get("message"))})

    replay = trace.get("replay") if isinstance(trace.get("replay"), dict) else {}
    dependencies = replay.get("external_dependencies") if isinstance(replay.get("external_dependencies"), dict) else {}
    strategy = dependencies.get("strategy", "recorded")
    if strategy not in {"recorded", "mocked"}:
        findings.append({"code": "EXTERNAL_DEPENDENCY_UNSUPPORTED", "message": f"external dependency strategy '{strategy}' is not executable deterministically"})

    contract = trace.get("replay_contract") if isinstance(trace.get("replay_contract"), dict) else {}
    identity = contract.get("playbook") if isinstance(contract.get("playbook"), dict) else {}
    try:
        root, manifest, _, _ = load_package(package_path)
        source_rel = str(manifest.get("source", "source/program.ordo.yaml"))
        source_file = root / source_rel
        actual_digest = "sha256:" + file_sha256(source_file)
        expected_digest = identity.get("sha256")
        if expected_digest and expected_digest != actual_digest:
            findings.append({"code": "PLAYBOOK_DIGEST_MISMATCH", "message": "checkout playbook differs from the trace source"})
    except Exception as exc:
        findings.append({"code": "PACKAGE_UNAVAILABLE", "message": f"cannot load package from checkout: {exc}"})

    plan = replay_plan(trace, mode="deterministic") if validation.get("valid") else {"ready": False, "steps": []}
    if not plan.get("ready") and not findings:
        findings.append({"code": "REPLAY_PLAN_UNAVAILABLE", "message": "trace cannot produce a deterministic replay plan"})

    classes = {"accepted_decision": 0, "blocker": 0, "discrepancy": 0, "runtime_only": 0}
    for event in trace.get("events", []) if isinstance(trace.get("events"), list) else []:
        record = event.get("replay_record") if isinstance(event.get("replay_record"), dict) else {}
        kind = record.get("evidence_class")
        if kind in classes:
            classes[kind] += 1

    status = "passed" if not findings else ("blocked" if any(item["code"].startswith(("CHECKOUT_", "EXTERNAL_", "PACKAGE_", "REPLAY_")) for item in findings) else "failed")
    report = {
        "format": "ordo-deterministic-replay-report.v1",
        "status": status,
        "generated_at": _utc_now(),
        "checkout": str(checkout_path),
        "checkout_clean": clean,
        "package": str(package_path),
        "trace": str(trace_file),
        "trace_checksum": state_fingerprint(trace).get("checksum"),
        "replay_mode": "deterministic",
        "summary": {"replayed_records": len(plan.get("steps", [])), "evidence_classes": classes},
        "findings": findings,
    }
    target = Path(out).resolve() if out else package_path / "reports" / "deterministic_replay_report.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    report = write_report_with_digest(target, report)
    target.with_suffix(".md").write_text(_markdown(report), encoding="utf-8")
    return report


def export_replay_evidence(
    *,
    trace_path: str | Path,
    state_path: str | Path,
    out: str | Path,
) -> dict[str, Any]:
    """Create a read-only evidence export and prove supplied state was not changed."""
    trace_file, state_file, target = Path(trace_path).resolve(), Path(state_path).resolve(), Path(out).resolve()
    before_bytes = state_file.read_bytes()
    trace = json.loads(trace_file.read_text(encoding="utf-8"))
    validation = validate_execution_trace(trace)
    target.mkdir(parents=True, exist_ok=True)
    exported_trace = target / "execution_trace.json"
    exported_trace.write_text(json.dumps(trace, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    after_bytes = state_file.read_bytes()
    report = {
        "format": "ordo-replay-evidence-export.v1",
        "status": "passed" if validation["valid"] and before_bytes == after_bytes else "failed",
        "trace": {"source": str(trace_file), "sha256": file_sha256(trace_file), "validation": validation},
        "state_non_mutation": {
            "path": str(state_file),
            "before_sha256": hashlib.sha256(before_bytes).hexdigest(),
            "after_sha256": hashlib.sha256(after_bytes).hexdigest(),
            "unchanged": before_bytes == after_bytes,
        },
        "exported_files": [{"path": exported_trace.name, "sha256": file_sha256(exported_trace)}],
    }
    report = write_report_with_digest(target / "replay_evidence_export_report.json", report)
    (target / "replay_evidence_export_report.md").write_text(_markdown({
        "status": report["status"], "replay_mode": "audit_only", "trace": str(trace_file), "checkout": "not applicable",
        "summary": {"replayed_records": len(trace.get("events", []))},
        "findings": [] if report["status"] == "passed" else [{"code": "EXPORT_MUTATION_OR_TRACE_INVALID", "message": "state changed or trace validation failed"}],
    }), encoding="utf-8")
    return report
