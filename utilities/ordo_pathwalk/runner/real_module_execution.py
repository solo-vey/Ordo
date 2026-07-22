"""Hardened isolated execution for generated real-module testcases.

M82.1 safety boundary:
- planner and collector are artifact-only;
- each testcase runs in one short-lived child process group;
- plan paths are validated against approved roots before execution;
- stdin and environment are controlled;
- stdout/stderr are drained through bounded collectors;
- watchdog terminates the whole process group;
- result evidence is persisted atomically;
- sandbox retention/cleanup is explicit and reported.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO

import yaml

SCHEMA_PLAN = "ordo.pathwalk.real_module_execution_plan.v2"
SCHEMA_RESULT = "ordo.pathwalk.real_module_execution_result.v3"
SCHEMA_EVIDENCE = "ordo.pathwalk.execution_evidence.v1"
SCHEMA_SUMMARY = "ordo.pathwalk.real_module_execution_summary.v3"
SUPPORTED_PLAN_SCHEMAS = {SCHEMA_PLAN, "ordo.pathwalk.real_module_execution_plan.v1"}
MIN_TIMEOUT_SECONDS = 1
MAX_TIMEOUT_SECONDS = 3600
MIN_OUTPUT_BYTES = 1024
MAX_OUTPUT_BYTES = 10_000_000
DEFAULT_MAX_OUTPUT_BYTES = 1_000_000
DEFAULT_CLEANUP_POLICY = "retain_failures"
SUPPORTED_CLEANUP_POLICIES = {"retain_all", "retain_failures", "cleanup_all"}

EXECUTION_STATUSES = {
    "passed",
    "testcase_failed",
    "process_failed",
    "timed_out",
    "invalid_output",
    "input_rejected",
    "infrastructure_error",
}
FAILURE_CATEGORIES = {
    None,
    "assertion_failed",
    "nonzero_exit",
    "terminated_by_signal",
    "watchdog_timeout",
    "missing_runtime_report",
    "malformed_runtime_report",
    "runtime_report_contract_mismatch",
    "input_validation",
    "result_exists",
    "spawn_failed",
    "stream_capture_failed",
    "cleanup_failed",
    "runner_failure",
}
STATUS_CLASS = {
    "passed": "success",
    "testcase_failed": "testcase",
    "process_failed": "process",
    "timed_out": "watchdog",
    "invalid_output": "evidence",
    "input_rejected": "input",
    "infrastructure_error": "infrastructure",
}

ENV_ALLOWLIST = {
    "PATH",
    "PYTHONPATH",
    "LANG",
    "LC_ALL",
    "LC_CTYPE",
    "TZ",
    "SYSTEMROOT",  # Windows process creation
    "WINDIR",
    "PATHEXT",
}


class InputRejected(ValueError):
    """Raised when the immutable plan/job boundary is invalid before spawn."""


@dataclass
class _BoundedCapture:
    limit: int
    data: bytearray
    truncated: bool = False

    def consume(self, stream: BinaryIO) -> None:
        while True:
            chunk = stream.read(65536)
            if not chunk:
                break
            remaining = self.limit - len(self.data)
            if remaining > 0:
                self.data.extend(chunk[:remaining])
            if len(chunk) > remaining:
                self.truncated = True

    def text(self) -> str:
        return bytes(self.data).decode("utf-8", errors="replace")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise InputRejected(f"JSON root must be an object: {path}")
    return value


def _atomic_write_json(path: Path, value: Any, *, overwrite: bool = False) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        raise FileExistsError(f"result already exists: {path}")
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        if path.exists() and not overwrite:
            raise FileExistsError(f"result already exists: {path}")
        os.replace(tmp_path, path)
    finally:
        tmp_path.unlink(missing_ok=True)


def _write_json(path: Path, value: Any) -> None:
    """Compatibility helper for non-result artifacts."""
    _atomic_write_json(path, value, overwrite=True)


def _resolved(path: Path) -> Path:
    return Path(path).expanduser().resolve(strict=False)


def _is_within(path: Path, root: Path) -> bool:
    path = _resolved(path)
    root = _resolved(root)
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _require_within(path: Path, root: Path, label: str) -> Path:
    resolved = _resolved(path)
    resolved_root = _resolved(root)
    if not _is_within(resolved, resolved_root):
        raise InputRejected(f"{label} escapes approved root: {resolved} not under {resolved_root}")
    return resolved


def _require_regular_file(path: Path, label: str) -> Path:
    path = _resolved(path)
    if not path.exists() or not path.is_file() or path.is_symlink():
        raise InputRejected(f"{label} must be an existing non-symlink regular file: {path}")
    return path


def _validate_limit(name: str, value: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise InputRejected(f"{name} must be an integer") from exc
    if not minimum <= parsed <= maximum:
        raise InputRejected(f"{name} must be between {minimum} and {maximum}: {parsed}")
    return parsed


def _plan_fingerprint(plan: dict[str, Any]) -> str:
    stable = dict(plan)
    stable.pop("plan_fingerprint", None)
    payload = json.dumps(stable, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _classify_failure(*, status: str, return_code: int | None, report_status: str) -> str | None:
    if status == "passed":
        return None
    if status == "timed_out":
        return "watchdog_timeout"
    if status == "input_rejected":
        return "input_validation"
    if status == "invalid_output":
        if report_status == "missing":
            return "missing_runtime_report"
        if report_status.startswith("invalid:"):
            return "malformed_runtime_report"
        return "runtime_report_contract_mismatch"
    if status == "process_failed":
        if isinstance(return_code, int) and return_code < 0:
            return "terminated_by_signal"
        return "nonzero_exit"
    if status == "testcase_failed":
        return "assertion_failed"
    return "runner_failure"


def _evidence_contract(result: dict[str, Any]) -> dict[str, Any]:
    status = result["status"]
    category = result.get("failure_category")
    return {
        "schema_version": SCHEMA_EVIDENCE,
        "evidence_id": f"{result.get('plan_fingerprint') or 'unbound'}:{result['job_id']}",
        "linkage": {
            "plan_fingerprint": result.get("plan_fingerprint"),
            "job_id": result["job_id"],
            "case_id": result.get("case_id"),
            "source_sha256": result.get("source_sha256"),
            "case_sha256": result.get("case_sha256"),
        },
        "outcome": {
            "status": status,
            "status_class": STATUS_CLASS[status],
            "failure_category": category,
            "retryable": status in {"infrastructure_error"},
            "testcase_decision": "pass" if status == "passed" else ("fail" if status == "testcase_failed" else "not_evaluated"),
        },
        "process": {
            "return_code": result.get("return_code"),
            "terminating_signal": result.get("terminating_signal"),
            "timed_out": result.get("timed_out", False),
            "started_at": result.get("started_at"),
            "finished_at": result.get("finished_at"),
            "duration_seconds": result.get("duration_seconds"),
            "command": result.get("command") or [],
        },
        "diagnostics": {
            "validation_error": result.get("validation_error"),
            "infrastructure_error": result.get("infrastructure_error"),
            "runtime_report_parse_status": result.get("runtime_report_parse_status"),
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "stdout_truncated": result.get("stdout_truncated", False),
            "stderr_truncated": result.get("stderr_truncated", False),
        },
        "controls": {
            "watchdog": result.get("watchdog") or {},
            "resource_limits": result.get("resource_limits") or {},
            "isolation": result.get("isolation") or {},
        },
        "artifacts": {
            "runtime_report_path": result.get("runtime_report_path"),
            "runtime_report_available": result.get("raw_evidence_ready", False),
        },
        "claims": {
            "raw_evidence_only": True,
            "scoring_performed": result.get("scoring_performed", False),
            "calibration_performed": result.get("calibration_performed", False),
        },
    }


def validate_execution_evidence(evidence: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if evidence.get("schema_version") != SCHEMA_EVIDENCE:
        errors.append("unsupported evidence schema_version")
    outcome = evidence.get("outcome")
    if not isinstance(outcome, dict):
        errors.append("outcome must be an object")
        return errors
    status = outcome.get("status")
    category = outcome.get("failure_category")
    if status not in EXECUTION_STATUSES:
        errors.append(f"unsupported outcome status: {status}")
    elif outcome.get("status_class") != STATUS_CLASS[status]:
        errors.append("status_class does not match status")
    if category not in FAILURE_CATEGORIES:
        errors.append(f"unsupported failure_category: {category}")
    if status == "passed" and category is not None:
        errors.append("passed evidence must not have failure_category")
    if status != "passed" and category is None:
        errors.append("non-passed evidence requires failure_category")
    linkage = evidence.get("linkage")
    if not isinstance(linkage, dict) or not linkage.get("job_id"):
        errors.append("linkage.job_id is required")
    process = evidence.get("process")
    if not isinstance(process, dict):
        errors.append("process must be an object")
    diagnostics = evidence.get("diagnostics")
    if not isinstance(diagnostics, dict):
        errors.append("diagnostics must be an object")
    claims = evidence.get("claims")
    if not isinstance(claims, dict) or claims.get("raw_evidence_only") is not True:
        errors.append("claims.raw_evidence_only must be true")
    return errors


def create_real_module_execution_plan(
    *,
    summary_path: Path,
    source_path: Path,
    out_dir: Path,
    timeout_seconds: int = 30,
    force: bool = False,
    max_output_bytes: int = DEFAULT_MAX_OUTPUT_BYTES,
    cleanup_policy: str = DEFAULT_CLEANUP_POLICY,
) -> dict[str, Any]:
    summary_path = _require_regular_file(Path(summary_path), "summary_path")
    source_path = _require_regular_file(Path(source_path), "source_path")
    out_dir = _resolved(Path(out_dir))
    timeout_seconds = _validate_limit("timeout_seconds", timeout_seconds, MIN_TIMEOUT_SECONDS, MAX_TIMEOUT_SECONDS)
    max_output_bytes = _validate_limit("max_output_bytes", max_output_bytes, MIN_OUTPUT_BYTES, MAX_OUTPUT_BYTES)
    if cleanup_policy not in SUPPORTED_CLEANUP_POLICIES:
        raise InputRejected(f"unsupported cleanup_policy: {cleanup_policy}")
    if out_dir.exists() and any(out_dir.iterdir()) and not force:
        raise FileExistsError(f"output directory is not empty: {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = _load_json(summary_path)
    cases = summary.get("cases") or []
    if not isinstance(cases, list) or not cases:
        raise InputRejected("summary must contain a non-empty cases list")
    case_root = _resolved(summary_path.parent / "cases")
    jobs: list[dict[str, Any]] = []
    seen_job_ids: set[str] = set()
    seen_case_ids: set[str] = set()
    for item in cases:
        if not isinstance(item, dict) or not isinstance(item.get("case_id"), str) or not item["case_id"].strip():
            raise InputRejected("every summary case must contain a non-empty string case_id")
        case_id = item["case_id"]
        if case_id in seen_case_ids:
            raise InputRejected(f"duplicate case_id: {case_id}")
        seen_case_ids.add(case_id)
        case_path = _require_within(case_root / f"{case_id}.json", case_root, "case_path")
        _require_regular_file(case_path, "case_path")
        job_id = f"EXEC_{case_id}"
        if job_id in seen_job_ids:
            raise InputRejected(f"duplicate job_id: {job_id}")
        seen_job_ids.add(job_id)
        jobs.append(
            {
                "job_id": job_id,
                "case_id": case_id,
                "case_path": str(case_path),
                "timeout_seconds": timeout_seconds,
                "result_path": str(_resolved(out_dir / "results" / f"{job_id}.json")),
                "sandbox_path": str(_resolved(out_dir / "sandboxes" / job_id)),
            }
        )

    plan: dict[str, Any] = {
        "schema_version": SCHEMA_PLAN,
        "milestone": "M82.1",
        "execution_contract": "one-job-one-child-process-collect-only-parent",
        "safety_contract": "validated-plan-one-job-one-child-process-collect-only-parent",
        "source_path": str(source_path),
        "summary_path": str(summary_path),
        "out_dir": str(out_dir),
        "approved_roots": {
            "source_root": str(source_path.parent.resolve()),
            "case_root": str(case_root),
            "execution_root": str(out_dir),
        },
        "limits": {
            "timeout_seconds": timeout_seconds,
            "max_output_bytes": max_output_bytes,
        },
        "environment_policy": {
            "mode": "allowlist",
            "allowed_keys": sorted(ENV_ALLOWLIST),
            "stdin": "closed",
        },
        "cleanup_policy": cleanup_policy,
        "jobs": jobs,
        "readiness": {
            "runtime_execution_ready": True,
            "scoring_ready": False,
            "calibration_ready": False,
        },
    }
    plan["plan_fingerprint"] = _plan_fingerprint(plan)
    plan_path = out_dir / "REAL_MODULE_EXECUTION_PLAN.json"
    _write_json(plan_path, plan)

    scripts = out_dir / "job_scripts"
    scripts.mkdir(exist_ok=True)
    for job in jobs:
        script = scripts / f"{job['job_id']}.sh"
        script.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env bash",
                    "set -euo pipefail",
                    'ROOT="${ORDO_PATHWALK_ROOT:-$(pwd)}"',
                    'export PYTHONPATH="${ORDO_CLI_ROOT:-${ROOT}/cli}:${ROOT}${PYTHONPATH:+:${PYTHONPATH}}"',
                    f'exec python3 -m utilities.ordo_pathwalk.cli real-module-exec-job --plan "{plan_path}" --job-id "{job["job_id"]}" < /dev/null',
                    "",
                ]
            ),
            encoding="utf-8",
        )
        script.chmod(0o755)
    return plan


def _prepare_sandbox(source_path: Path, sandbox: Path, case: dict[str, Any]) -> tuple[Path, Path]:
    if sandbox.exists():
        shutil.rmtree(sandbox)
    (sandbox / "source").mkdir(parents=True)
    (sandbox / "tests").mkdir()
    shutil.copy2(source_path, sandbox / "source" / "program.ordo.yaml")
    copied_source = sandbox / "source" / "program.ordo.yaml"
    copied_source.chmod(0o444)
    (sandbox / "ordo.yml").write_text("source: source/program.ordo.yaml\ntests: tests/test_cases.yaml\n", encoding="utf-8")
    (sandbox / "tests" / "test_cases.yaml").write_text("cases: []\n", encoding="utf-8")
    answer_steps = case.get("answer_steps") or case.get("clean_answer_steps") or []
    if not isinstance(answer_steps, list):
        raise InputRejected("testcase answer_steps must be a list")
    answers = {
        step["node"]: step.get("answer")
        for step in answer_steps
        if isinstance(step, dict) and isinstance(step.get("node"), str) and step.get("node")
    }
    answers_path = sandbox / "answers.yaml"
    answers_path.write_text(yaml.safe_dump(answers, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return sandbox, answers_path


def _resource_limit_capabilities(timeout_seconds: int) -> tuple[Any, dict[str, Any]]:
    capabilities: dict[str, Any] = {
        "platform": os.name,
        "process_group": os.name == "posix",
        "rlimit_cpu": False,
        "rlimit_fsize": False,
        "rlimit_nofile": False,
    }
    if os.name != "posix":
        return None, capabilities
    try:
        import resource
    except Exception:
        return None, capabilities

    cpu_limit = max(1, min(timeout_seconds + 2, MAX_TIMEOUT_SECONDS))

    def apply_limits() -> None:
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))
        resource.setrlimit(resource.RLIMIT_FSIZE, (10_000_000, 10_000_000))
        resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))

    capabilities.update({"rlimit_cpu": True, "rlimit_fsize": True, "rlimit_nofile": True})
    return apply_limits, capabilities


def _minimal_environment(sandbox: Path) -> dict[str, str]:
    env = {key: value for key, value in os.environ.items() if key in ENV_ALLOWLIST and value}
    workspace_root = Path(__file__).resolve().parents[3]
    required_pythonpath = [str(workspace_root / "cli"), str(workspace_root)]
    inherited_pythonpath = env.get("PYTHONPATH")
    if inherited_pythonpath:
        required_pythonpath.append(inherited_pythonpath)
    env["PYTHONPATH"] = os.pathsep.join(required_pythonpath)
    env["HOME"] = str(sandbox / "home")
    env["TMPDIR"] = str(sandbox / "tmp")
    env["PYTHONUNBUFFERED"] = "1"
    (sandbox / "home").mkdir(exist_ok=True)
    (sandbox / "tmp").mkdir(exist_ok=True)
    return env


def _terminate_process_tree(proc: subprocess.Popen[bytes], grace_seconds: float = 0.5) -> dict[str, Any]:
    action = {
        "requested": True,
        "strategy": "process_group" if os.name == "posix" else "single_process",
        "term_sent": False,
        "kill_sent": False,
    }
    if proc.poll() is not None:
        return action
    try:
        if os.name == "posix":
            os.killpg(proc.pid, signal.SIGTERM)
        else:
            proc.terminate()
        action["term_sent"] = True
        proc.wait(timeout=grace_seconds)
        return action
    except subprocess.TimeoutExpired:
        pass
    except ProcessLookupError:
        return action
    try:
        if os.name == "posix":
            os.killpg(proc.pid, signal.SIGKILL)
        else:
            proc.kill()
        action["kill_sent"] = True
    except ProcessLookupError:
        pass
    return action


def _validate_plan_job(plan_path: Path, plan: dict[str, Any], job_id: str) -> tuple[dict[str, Any], dict[str, Path], int, int, str]:
    if plan.get("schema_version") not in SUPPORTED_PLAN_SCHEMAS:
        raise InputRejected(f"unsupported plan schema: {plan.get('schema_version')}")
    if plan.get("plan_fingerprint") and plan["plan_fingerprint"] != _plan_fingerprint(plan):
        raise InputRejected("plan fingerprint mismatch")
    jobs = plan.get("jobs")
    if not isinstance(jobs, list):
        raise InputRejected("plan jobs must be a list")
    matches = [job for job in jobs if isinstance(job, dict) and job.get("job_id") == job_id]
    if len(matches) != 1:
        raise InputRejected(f"job_id must occur exactly once in plan: {job_id}")
    job = matches[0]
    if not isinstance(job.get("case_id"), str) or not job["case_id"]:
        raise InputRejected("job case_id is missing")

    approved = plan.get("approved_roots") or {}
    execution_root = _resolved(approved.get("execution_root") or plan.get("out_dir"))
    source_root = _resolved(approved.get("source_root") or Path(plan["source_path"]).parent)
    case_root = _resolved(approved.get("case_root") or Path(plan["summary_path"]).parent / "cases")
    plan_path = _require_within(plan_path, execution_root, "plan_path")
    source_path = _require_within(Path(plan["source_path"]), source_root, "source_path")
    case_path = _require_within(Path(job["case_path"]), case_root, "case_path")
    result_path = _require_within(Path(job["result_path"]), execution_root / "results", "result_path")
    sandbox_path = _require_within(Path(job["sandbox_path"]), execution_root / "sandboxes", "sandbox_path")
    source_path = _require_regular_file(source_path, "source_path")
    case_path = _require_regular_file(case_path, "case_path")
    if result_path in {source_path, case_path}:
        raise InputRejected("result_path aliases an input artifact")
    if sandbox_path.exists() and sandbox_path.is_symlink():
        raise InputRejected("sandbox_path must not be a symlink")
    timeout = _validate_limit("timeout_seconds", job.get("timeout_seconds", (plan.get("limits") or {}).get("timeout_seconds", 30)), MIN_TIMEOUT_SECONDS, MAX_TIMEOUT_SECONDS)
    max_output = _validate_limit("max_output_bytes", (plan.get("limits") or {}).get("max_output_bytes", DEFAULT_MAX_OUTPUT_BYTES), MIN_OUTPUT_BYTES, MAX_OUTPUT_BYTES)
    cleanup_policy = plan.get("cleanup_policy", "retain_all" if plan.get("schema_version", "").endswith("v1") else DEFAULT_CLEANUP_POLICY)
    if cleanup_policy not in SUPPORTED_CLEANUP_POLICIES:
        raise InputRejected(f"unsupported cleanup_policy: {cleanup_policy}")
    return job, {
        "plan": plan_path,
        "execution_root": execution_root,
        "source": source_path,
        "case": case_path,
        "result": result_path,
        "sandbox": sandbox_path,
    }, timeout, max_output, cleanup_policy


def _cleanup_sandbox(sandbox: Path, policy: str, status: str) -> dict[str, Any]:
    should_remove = policy == "cleanup_all" or (policy == "retain_failures" and status == "passed")
    outcome = {
        "policy": policy,
        "requested": should_remove,
        "retained": not should_remove,
        "succeeded": True,
        "error": None,
    }
    if should_remove:
        try:
            shutil.rmtree(sandbox)
            outcome["retained"] = False
        except Exception as exc:  # evidence must survive cleanup failure
            outcome["succeeded"] = False
            outcome["retained"] = sandbox.exists()
            outcome["error"] = f"{type(exc).__name__}: {exc}"
    return outcome


def run_real_module_execution_job(plan_path: Path, job_id: str) -> dict[str, Any]:
    plan_path = _resolved(Path(plan_path))
    started_at = _utc_now()
    started_monotonic = time.monotonic()
    proc: subprocess.Popen[bytes] | None = None
    stdout_capture = _BoundedCapture(DEFAULT_MAX_OUTPUT_BYTES, bytearray())
    stderr_capture = _BoundedCapture(DEFAULT_MAX_OUTPUT_BYTES, bytearray())
    watchdog_action = {"requested": False, "strategy": None, "term_sent": False, "kill_sent": False}
    status = "infrastructure_error"
    failure_category: str | None = None
    runtime_report: dict[str, Any] | None = None
    runtime_report_parse_status = "not_checked"
    paths: dict[str, Path] = {}
    job: dict[str, Any] = {"job_id": job_id, "case_id": None}
    plan: dict[str, Any] = {}
    timeout = 0
    cleanup_policy = DEFAULT_CLEANUP_POLICY
    capabilities: dict[str, Any] = {"platform": os.name, "process_group": os.name == "posix"}
    command: list[str] = []
    spawn_error: str | None = None
    validation_error: str | None = None

    try:
        plan = _load_json(plan_path)
        job, paths, timeout, max_output, cleanup_policy = _validate_plan_job(plan_path, plan, job_id)
        stdout_capture.limit = max_output
        stderr_capture.limit = max_output
        if paths["result"].exists():
            raise FileExistsError(f"result already exists: {paths['result']}")
        case = _load_json(paths["case"])
        sandbox, answers_path = _prepare_sandbox(paths["source"], paths["sandbox"], case)
        command = [sys.executable, "-m", "ordo.cli", "run", str(sandbox), "--answers", str(answers_path)]
        preexec_fn, capabilities = _resource_limit_capabilities(timeout)
        env = _minimal_environment(sandbox)
        proc = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(sandbox),
            env=env,
            start_new_session=os.name == "posix",
            preexec_fn=preexec_fn,
        )
        assert proc.stdout is not None and proc.stderr is not None
        stdout_thread = threading.Thread(target=stdout_capture.consume, args=(proc.stdout,), daemon=True)
        stderr_thread = threading.Thread(target=stderr_capture.consume, args=(proc.stderr,), daemon=True)
        stdout_thread.start()
        stderr_thread.start()
        timed_out = False
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            watchdog_action = _terminate_process_tree(proc)
            proc.wait(timeout=5)
        stdout_thread.join(timeout=5)
        stderr_thread.join(timeout=5)

        report_path = sandbox / "reports" / "run_report.json"
        if report_path.exists():
            try:
                runtime_report = _load_json(report_path)
                runtime_report_parse_status = "valid_json_object"
            except Exception as exc:
                runtime_report_parse_status = f"invalid:{type(exc).__name__}"
        else:
            runtime_report_parse_status = "missing"

        if timed_out:
            status = "timed_out"
            failure_category = _classify_failure(status=status, return_code=proc.returncode, report_status=runtime_report_parse_status)
        elif proc.returncode == 0 and runtime_report_parse_status == "valid_json_object":
            status = "passed"
        elif proc.returncode == 0:
            status = "invalid_output"
            failure_category = _classify_failure(status=status, return_code=proc.returncode, report_status=runtime_report_parse_status)
        else:
            status = "process_failed"
            failure_category = _classify_failure(status=status, return_code=proc.returncode, report_status=runtime_report_parse_status)
    except InputRejected as exc:
        status = "input_rejected"
        failure_category = "input_validation"
        validation_error = str(exc)
    except FileExistsError as exc:
        status = "input_rejected"
        failure_category = "result_exists"
        validation_error = str(exc)
    except Exception as exc:
        status = "infrastructure_error"
        failure_category = "runner_failure"
        spawn_error = f"{type(exc).__name__}: {exc}"
        if proc is not None and proc.poll() is None:
            watchdog_action = _terminate_process_tree(proc)
            try:
                proc.wait(timeout=5)
            except Exception:
                pass

    duration = round(time.monotonic() - started_monotonic, 6)
    sandbox = paths.get("sandbox")
    cleanup = {
        "policy": cleanup_policy,
        "requested": False,
        "retained": sandbox.exists() if sandbox else False,
        "succeeded": True,
        "error": None,
    }
    if sandbox and sandbox.exists():
        cleanup = _cleanup_sandbox(sandbox, cleanup_policy, status)

    return_code = proc.returncode if proc is not None else None
    terminating_signal = -return_code if isinstance(return_code, int) and return_code < 0 else None
    report_path = sandbox / "reports" / "run_report.json" if sandbox else None
    result = {
        "schema_version": SCHEMA_RESULT,
        "milestone": "M82.2",
        "plan_fingerprint": plan.get("plan_fingerprint") or (_plan_fingerprint(plan) if plan else None),
        "job_id": job_id,
        "case_id": job.get("case_id"),
        "status": status,
        "failure_category": failure_category,
        "validation_error": validation_error,
        "infrastructure_error": spawn_error,
        "source_sha256": _sha256(paths["source"]) if paths.get("source") and paths["source"].exists() else None,
        "case_sha256": _sha256(paths["case"]) if paths.get("case") and paths["case"].exists() else None,
        "return_code": return_code,
        "terminating_signal": terminating_signal,
        "timed_out": status == "timed_out",
        "started_at": started_at,
        "finished_at": _utc_now(),
        "duration_seconds": duration,
        "watchdog": {
            "timeout_seconds": timeout or None,
            **watchdog_action,
        },
        "resource_limits": capabilities,
        "isolation": {
            "sandbox_path": str(sandbox) if sandbox else None,
            "source_copied": bool(sandbox and (sandbox / "source" / "program.ordo.yaml").exists()) if cleanup.get("retained") else status != "input_rejected",
            "stdin_closed": True,
            "environment_mode": "allowlist",
            "cleanup": cleanup,
        },
        "command": command,
        "stdout": stdout_capture.text(),
        "stderr": stderr_capture.text(),
        "stdout_truncated": stdout_capture.truncated,
        "stderr_truncated": stderr_capture.truncated,
        "runtime_report_path": str(report_path) if report_path and report_path.exists() else None,
        "runtime_report_parse_status": runtime_report_parse_status,
        "raw_evidence_ready": runtime_report is not None and runtime_report_parse_status == "valid_json_object",
        "scoring_performed": False,
        "calibration_performed": False,
    }
    result["evidence"] = _evidence_contract(result)
    evidence_errors = validate_execution_evidence(result["evidence"])
    if evidence_errors:
        raise RuntimeError("execution evidence validation failed: " + "; ".join(evidence_errors))

    result_path = paths.get("result")
    if result_path is None and plan:
        execution_root = _resolved((plan.get("approved_roots") or {}).get("execution_root") or plan.get("out_dir") or plan_path.parent)
        fallback = execution_root / "results" / f"{job_id}.json"
        if _is_within(fallback, execution_root / "results"):
            result_path = fallback
    if result_path is None:
        raise RuntimeError(f"cannot persist result safely for job {job_id}: {validation_error or spawn_error}")
    _atomic_write_json(result_path, result, overwrite=False)
    return result


def collect_real_module_execution_results(plan_path: Path) -> dict[str, Any]:
    plan_path = _resolved(Path(plan_path))
    plan = _load_json(plan_path)
    if plan.get("schema_version") not in SUPPORTED_PLAN_SCHEMAS:
        raise InputRejected(f"unsupported plan schema: {plan.get('schema_version')}")
    results: list[dict[str, Any]] = []
    missing: list[str] = []
    invalid: list[dict[str, str]] = []
    execution_root = _resolved((plan.get("approved_roots") or {}).get("execution_root") or plan.get("out_dir"))
    for job in plan.get("jobs", []):
        job_id = job.get("job_id")
        try:
            result_path = _require_within(Path(job["result_path"]), execution_root / "results", "result_path")
        except Exception as exc:
            invalid.append({"job_id": str(job_id), "reason": str(exc)})
            continue
        if not result_path.exists():
            missing.append(str(job_id))
            continue
        try:
            result = _load_json(result_path)
            if result.get("job_id") != job_id or result.get("case_id") != job.get("case_id"):
                raise InputRejected("result linkage mismatch")
            if result.get("schema_version") not in {SCHEMA_RESULT, "ordo.pathwalk.real_module_execution_result.v2", "ordo.pathwalk.real_module_execution_result.v1"}:
                raise InputRejected(f"unsupported result schema: {result.get('schema_version')}")
            if result.get("schema_version") == SCHEMA_RESULT:
                evidence_errors = validate_execution_evidence(result.get("evidence") or {})
                if evidence_errors:
                    raise InputRejected("invalid execution evidence: " + "; ".join(evidence_errors))
            results.append(result)
        except Exception as exc:
            invalid.append({"job_id": str(job_id), "reason": f"{type(exc).__name__}: {exc}"})

    statuses = [str(result.get("status")) for result in results]
    counts: dict[str, int] = {
        "planned": len(plan.get("jobs", [])),
        "collected": len(results),
        "passed": statuses.count("passed"),
        "testcase_failed": statuses.count("testcase_failed"),
        "process_failed": statuses.count("process_failed") + statuses.count("failed"),
        "timed_out": statuses.count("timed_out"),
        "invalid_output": statuses.count("invalid_output"),
        "input_rejected": statuses.count("input_rejected"),
        "infrastructure_error": statuses.count("infrastructure_error"),
        "missing": len(missing),
        "invalid_results": len(invalid),
    }
    status = "passed" if counts["planned"] > 0 and counts["passed"] == counts["planned"] and not missing and not invalid else "incomplete_or_failed"
    summary = {
        "schema_version": SCHEMA_SUMMARY,
        "milestone": "M82.2",
        "status": status,
        "counts": counts,
        "missing_jobs": missing,
        "invalid_results": invalid,
        "results": results,
        "claims": {
            "raw_execution_evidence_stable": status == "passed",
            "collector_executed_jobs": False,
            "scoring_ready": False,
            "calibration_ready": False,
        },
    }
    _write_json(execution_root / "REAL_MODULE_EXECUTION_SUMMARY.json", summary)
    return summary
