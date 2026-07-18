from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools/build_release_archive.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("build_release_archive", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_help_exposes_configurable_timeouts():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "--test-timeout-seconds" in proc.stdout
    assert "--lint-timeout-seconds" in proc.stdout
    assert "Use 0 to disable" in proc.stdout


def test_zero_timeout_maps_to_no_internal_timeout(monkeypatch):
    module = _load_module()
    seen = []

    class Result:
        returncode = 0
        stdout = "1 passed"
        stderr = ""

    def fake_run(*args, **kwargs):
        seen.append(kwargs.get("timeout"))
        return Result()

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module, "ROOT", ROOT)

    # Limit to one synthetic batch by monkeypatching glob behavior is unnecessary;
    # the fake runner makes the real file list cheap.
    result = module.run_partitioned_tests(skip_heavy=True, workers=1, timeout_seconds=0)
    assert seen
    assert all(value is None for value in seen)
    assert result["timeout_disabled"] is True


def test_negative_timeout_is_rejected():
    proc = subprocess.run(
        [
            sys.executable, str(SCRIPT), "--check-only",
            "--test-timeout-seconds", "-1",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0
    assert "timeout values must be 0 or positive integers" in proc.stderr
