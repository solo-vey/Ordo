from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools" / "validate_cross_artifact_contract_consistency.py"
FIXTURES = Path(__file__).parent / "fixtures" / "cross_artifact_contract_consistency"


def run_fixture(name: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL), "--root", str(FIXTURES / name)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_failing_fixture_is_blocked() -> None:
    result = run_fixture("failing")
    assert result.returncode != 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    ids = {issue["id"] for issue in report["packages"][0]["issues"]}
    assert {"CAC-004", "CAC-005"} <= ids


def test_passing_fixture_is_accepted() -> None:
    result = run_fixture("passing")
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["status"] == "PASS"
    assert report["packages"][0]["summary"]["errors"] == 0


def test_repository_discovery_skips_packages_without_contract_surfaces() -> None:
    result = subprocess.run(
        [sys.executable, str(TOOL), "--repo-root", str(ROOT)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["status"] == "PASS"
    assert report["summary"]["skipped"] >= 1
