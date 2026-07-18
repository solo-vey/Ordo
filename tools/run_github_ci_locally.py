from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = (
    "history_event_guided_intake",
    "ordo_applied_project_factory",
    "ordo_hybrid_executor",
    "ordo_project_builder",
)


def run(cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None, timeout: int = 5400) -> dict:
    merged = os.environ.copy()
    merged.update({"PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": str(cwd / "cli")})
    if env:
        merged.update(env)
    proc = subprocess.run(cmd, cwd=cwd, env=merged, text=True, capture_output=True, timeout=timeout)
    return {
        "command": cmd,
        "returncode": proc.returncode,
        "stdout_tail": "\n".join(proc.stdout.splitlines()[-20:]),
        "stderr_tail": "\n".join(proc.stderr.splitlines()[-20:]),
        "status": "passed" if proc.returncode == 0 else "failed",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the BL-ORDO-026 GitHub delivery workflow locally.")
    parser.add_argument("--out", type=Path, default=ROOT / "reports/local_ci")
    parser.add_argument("--skip-full-suite", action="store_true")
    args = parser.parse_args(argv)

    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []

    with tempfile.TemporaryDirectory(prefix="ordo_bl026_ci_") as td:
        checkout = Path(td) / "checkout"
        shutil.copytree(ROOT, checkout, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", "reports/local_ci"))
        subprocess.run(["git", "init", "-q"], cwd=checkout, check=True)
        subprocess.run(["git", "config", "user.email", "local-ci@ordo.invalid"], cwd=checkout, check=True)
        subprocess.run(["git", "config", "user.name", "Ordo Local CI"], cwd=checkout, check=True)
        subprocess.run(["git", "add", "-A"], cwd=checkout, check=True)
        subprocess.run(["git", "commit", "-qm", "local CI snapshot"], cwd=checkout, check=True)
        revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=checkout, text=True).strip()

        results.append(run([
            sys.executable, "-m", "pytest",
            "cli/tests/test_ci_clean_gate_workflow.py",
            "cli/tests/test_release_clean_gate_workflow.py",
            "cli/tests/test_release_clean_gate_provenance_linkage.py",
            "cli/tests/test_bl_ordo_026_delivery_workflow.py",
            "-q", "-p", "no:cacheprovider",
        ], cwd=checkout))

        for package in PACKAGES:
            with tempfile.TemporaryDirectory(prefix=f"lint_{package}_") as lint_td:
                tmp_pkg = Path(lint_td) / package
                shutil.copytree(checkout / "packages" / package, tmp_pkg)
                results.append(run([
                    sys.executable, "-m", "ordo.cli", "lint", str(tmp_pkg)
                ], cwd=checkout))

        candidate = Path(td) / "release_candidate"
        candidate.mkdir()
        archive_proc = subprocess.run(
            ["bash", "-lc", f"git archive --format=tar HEAD | tar -xf - -C {candidate!s}"],
            cwd=checkout, text=True, capture_output=True, check=False,
        )
        results.append({
            "command": ["git archive", "HEAD"],
            "returncode": archive_proc.returncode,
            "stdout_tail": archive_proc.stdout[-1000:],
            "stderr_tail": archive_proc.stderr[-1000:],
            "status": "passed" if archive_proc.returncode == 0 else "failed",
        })
        strict_report = out / "strict_repo_clean_check.json"
        results.append(run([
            sys.executable, "-m", "ordo.cli", "repo-check", str(candidate),
            "--clean", "--profile", "strict", "--hygiene-scope", "release",
            "--fail-on-warning", "--json", "--out", str(strict_report),
        ], cwd=checkout))

        if not args.skip_full_suite:
            results.append(run([
                sys.executable, "tools/build_release_archive.py", "--check-only",
                "--workers", "4", "--test-timeout-seconds", "3600",
                "--lint-timeout-seconds", "900",
            ], cwd=checkout, timeout=7200))

        archive = out / "ordo-release-candidate.zip"
        results.append(run([
            sys.executable, "tools/build_release_archive.py", "--out", str(archive),
            "--workers", "4", "--test-timeout-seconds", "3600",
            "--lint-timeout-seconds", "900",
        ], cwd=checkout, timeout=7200))

    archive_sha = hashlib.sha256(archive.read_bytes()).hexdigest() if archive.is_file() else None
    passed = all(item["status"] == "passed" for item in results)
    evidence = {
        "schema_version": "ordo.local_github_ci_simulation.v1",
        "status": "passed" if passed else "failed",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "revision": revision,
        "clean_temporary_git_checkout": True,
        "steps": results,
        "archive": archive.name if archive.is_file() else None,
        "archive_sha256": archive_sha,
        "external_ci_required_for_closure": True,
    }
    (out / "BL_ORDO_026_LOCAL_CI_EVIDENCE.json").write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if archive_sha:
        (out / f"{archive.name}.sha256").write_text(f"{archive_sha}  {archive.name}\n", encoding="utf-8")
    print(json.dumps({"status": evidence["status"], "steps": len(results), "archive_sha256": archive_sha}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
