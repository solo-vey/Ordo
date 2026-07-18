import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

from ordo_pathwalk.runner import real_module_execution as runtime

ROOT = Path(__file__).resolve().parents[2]
SUMMARY = ROOT / "ordo_pathwalk/examples/m60_7_3_clean_path_testcases/SUMMARY.json"
SOURCE = ROOT / "ordo_pathwalk/examples/m60_7_2_terminal_path_enumeration/source/program.ordo.yaml"


def _plan(tmp_path: Path, **kwargs):
    out = tmp_path / "run"
    plan = runtime.create_real_module_execution_plan(
        summary_path=SUMMARY,
        source_path=SOURCE,
        out_dir=out,
        timeout_seconds=20,
        **kwargs,
    )
    return out, plan


def test_plan_records_m82_1_boundary_controls(tmp_path):
    out, plan = _plan(tmp_path)
    assert plan["milestone"] == "M82.1"
    assert plan["schema_version"] == runtime.SCHEMA_PLAN
    assert plan["safety_contract"].startswith("validated-plan")
    assert plan["approved_roots"]["execution_root"] == str(out.resolve())
    assert plan["environment_policy"]["mode"] == "allowlist"
    assert plan["environment_policy"]["stdin"] == "closed"
    assert plan["cleanup_policy"] == "retain_failures"
    assert plan["plan_fingerprint"] == runtime._plan_fingerprint(plan)


def test_tampered_plan_is_rejected_before_spawn_and_safe_result_is_written(tmp_path):
    out, plan = _plan(tmp_path)
    plan_path = out / "REAL_MODULE_EXECUTION_PLAN.json"
    plan["jobs"][0]["sandbox_path"] = str(tmp_path / "escaped")
    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

    result = runtime.run_real_module_execution_job(plan_path, plan["jobs"][0]["job_id"])

    assert result["status"] == "input_rejected"
    assert result["failure_category"] == "input_validation"
    assert "fingerprint mismatch" in result["validation_error"]
    assert not (tmp_path / "escaped").exists()
    persisted = out / "results" / f"{plan['jobs'][0]['job_id']}.json"
    assert persisted.exists()


def test_validly_fingerprinted_traversing_sandbox_is_rejected(tmp_path):
    out, plan = _plan(tmp_path)
    plan_path = out / "REAL_MODULE_EXECUTION_PLAN.json"
    plan["jobs"][0]["sandbox_path"] = str(tmp_path / "escaped")
    plan["plan_fingerprint"] = runtime._plan_fingerprint(plan)
    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

    result = runtime.run_real_module_execution_job(plan_path, plan["jobs"][0]["job_id"])

    assert result["status"] == "input_rejected"
    assert "escapes approved root" in result["validation_error"]
    assert not (tmp_path / "escaped").exists()


def test_minimal_environment_drops_secrets_and_adds_private_home(tmp_path, monkeypatch):
    monkeypatch.setenv("ORDO_FAKE_SECRET", "do-not-inherit")
    monkeypatch.setenv("PATH", os.environ.get("PATH", ""))
    env = runtime._minimal_environment(tmp_path)
    assert "ORDO_FAKE_SECRET" not in env
    assert env["HOME"] == str(tmp_path / "home")
    assert env["TMPDIR"] == str(tmp_path / "tmp")
    assert str(ROOT / "cli") in env["PYTHONPATH"]
    assert env["PYTHONUNBUFFERED"] == "1"


def test_passed_job_is_cleaned_after_atomic_result_persistence(tmp_path):
    out, plan = _plan(tmp_path, cleanup_policy="retain_failures")
    job = plan["jobs"][0]
    result = runtime.run_real_module_execution_job(out / "REAL_MODULE_EXECUTION_PLAN.json", job["job_id"])

    assert result["status"] == "passed"
    assert result["isolation"]["cleanup"]["succeeded"] is True
    assert result["isolation"]["cleanup"]["retained"] is False
    assert not Path(job["sandbox_path"]).exists()
    result_path = Path(job["result_path"])
    assert result_path.exists()
    assert not list(result_path.parent.glob(f".{result_path.name}.*.tmp"))


def test_failed_job_retains_sandbox_for_diagnosis(tmp_path, monkeypatch):
    out, plan = _plan(tmp_path, cleanup_policy="retain_failures")
    job = plan["jobs"][0]
    original = runtime._minimal_environment

    def broken_environment(sandbox):
        env = original(sandbox)
        env["PYTHONPATH"] = ""
        return env

    monkeypatch.setattr(runtime, "_minimal_environment", broken_environment)
    result = runtime.run_real_module_execution_job(out / "REAL_MODULE_EXECUTION_PLAN.json", job["job_id"])

    assert result["status"] == "process_failed"
    assert result["isolation"]["cleanup"]["retained"] is True
    assert Path(job["sandbox_path"]).exists()


def test_existing_result_is_never_overwritten(tmp_path):
    out, plan = _plan(tmp_path, cleanup_policy="retain_all")
    job = plan["jobs"][0]
    runtime.run_real_module_execution_job(out / "REAL_MODULE_EXECUTION_PLAN.json", job["job_id"])
    original = Path(job["result_path"]).read_bytes()

    with pytest.raises(FileExistsError):
        runtime.run_real_module_execution_job(out / "REAL_MODULE_EXECUTION_PLAN.json", job["job_id"])

    assert Path(job["result_path"]).read_bytes() == original


@pytest.mark.skipif(os.name != "posix", reason="M82.1 reference watchdog behavior is POSIX process-group termination")
def test_watchdog_terminates_process_group_with_descendant(tmp_path):
    child_pid_file = tmp_path / "child.pid"
    script = (
        "import subprocess,sys,time; "
        "p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)']); "
        f"open({str(child_pid_file)!r},'w').write(str(p.pid)); "
        "time.sleep(60)"
    )
    proc = subprocess.Popen(
        [sys.executable, "-c", script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    deadline = time.time() + 5
    while not child_pid_file.exists() and time.time() < deadline:
        time.sleep(0.05)
    assert child_pid_file.exists()
    descendant_pid = int(child_pid_file.read_text())

    action = runtime._terminate_process_tree(proc, grace_seconds=0.1)
    proc.wait(timeout=5)

    assert action["strategy"] == "process_group"
    assert action["term_sent"] is True
    proc_stat = Path(f"/proc/{descendant_pid}/stat")
    if proc_stat.exists():
        # A terminated descendant can remain briefly as a zombie until reaped by init.
        assert proc_stat.read_text().split()[2] == "Z"
    else:
        with pytest.raises(ProcessLookupError):
            os.kill(descendant_pid, 0)


def test_bounded_capture_drains_but_keeps_only_limit():
    read_fd, write_fd = os.pipe()
    payload = b"x" * 8192
    os.write(write_fd, payload)
    os.close(write_fd)
    capture = runtime._BoundedCapture(1024, bytearray())
    with os.fdopen(read_fd, "rb") as stream:
        capture.consume(stream)
    assert len(capture.data) == 1024
    assert capture.truncated is True
