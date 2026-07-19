#!/usr/bin/env python3
"""Project delivery gate (M87.7).

The ONLY sanctioned way to produce the project archive. Refuses to build
while any blocking check is red, and regenerates FINAL_PACKAGE_SELF_CHECK
from the actual current tree so the shipped self-report can never be stale.

Usage:
    python3 tools/build_release_archive.py --out /path/to/ORDO_PROJECT.zip
    python3 tools/build_release_archive.py --check-only

Blocking checks (all must pass):
  1. CLI test suite, executed per test file (partitioned to bound memory).
  2. `ordo lint` on every package under packages/ (APF may be skipped with
     --skip-heavy in constrained environments; skipping is recorded honestly).
  3. Backlog/maturity manifest synchronization (md == json).
  4. Root hygiene: no stray milestone reports in the repository root.

On success writes FINAL_PACKAGE_SELF_CHECK_REPORT.{json,md} reflecting THIS
run, then zips the tree (excluding caches). On failure exits non-zero and
writes DELIVERY_GATE_REPORT.json with the blocking issues.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import zipfile
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))
from release_integrity import build_verified_archive, load_identity, source_tree_hash
from check_english_only_policy import validate as validate_english_only_policy

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_PARTS = {".git", "__pycache__", ".pytest_cache", "node_modules"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


HEAVY_TESTS: set[str] = set()


def run_partitioned_tests(
    skip_heavy: bool = False,
    workers: int = 4,
    timeout_seconds: int = 3600,
    log_dir: Path | None = None,
) -> dict:
    test_dir = ROOT / "cli" / "tests"
    files = sorted(test_dir.glob("test_*.py"))
    classification_path = ROOT / "manifests" / "TEST_EXECUTION_CLASSIFICATION.json"
    classification = json.loads(classification_path.read_text(encoding="utf-8"))
    declared_serial = set(classification.get("serial_files", {}))
    # Tests that mutate or scan the SHARED workspace (stale-artifact injection,
    # workspace-wide repo-check, shared reports/repo_check_report.json) are not
    # parallel-safe: racing batches produce nondeterministic failures that do
    # not reproduce serially. They run in one dedicated serial batch at the end.
    workspace_serial_names = declared_serial
    serial_files = [f for f in files if f.name in workspace_serial_names]
    parallel_files = [f for f in files if f.name not in workspace_serial_names]
    worker_count = max(1, min(workers, len(parallel_files) or 1))
    batches: list[list[Path]] = [[] for _ in range(worker_count)]
    for index, file in enumerate(parallel_files):
        batches[index % worker_count].append(file)

    if log_dir is not None:
        log_dir.mkdir(parents=True, exist_ok=True)

    def run_batch(batch_index: int, batch: list[Path], label: str) -> dict:
        rels = [f.relative_to(ROOT).as_posix() for f in batch]
        deselect: list[str] = []
        skipped: list[str] = []
        if skip_heavy:
            for h in HEAVY_TESTS:
                file_name, test_name = h.split("::", 1)
                for rel in rels:
                    if rel.endswith("/" + file_name) or rel == file_name:
                        nodeid_base = rel[len("cli/"):] if rel.startswith("cli/") else rel
                        deselect += ["--deselect", nodeid_base + "::" + test_name]
                        skipped.append(h)
        effective_timeout = None if timeout_seconds == 0 else timeout_seconds
        try:
            # Every deterministic group receives a fresh repository snapshot.
            # Tests intentionally mutate reports, fixtures, and generated paths;
            # sharing one workspace makes later groups observe earlier side effects.
            with tempfile.TemporaryDirectory(prefix=f"ordo-test-group-{batch_index:02d}-") as tmp:
                isolated_root = Path(tmp) / "repo"
                def ignore_isolated_snapshot(directory: str, names: list[str]) -> set[str]:
                    ignored = {
                        name for name in names
                        if name in {".git", "__pycache__", ".pytest_cache", "node_modules", "dist"}
                    }
                    # reports/ci is ephemeral workflow evidence created after the
                    # first gate. It is not canonical source input and must not
                    # contaminate the release-build validation snapshot.
                    if Path(directory).resolve() == (ROOT / "reports").resolve() and "ci" in names:
                        ignored.add("ci")
                    return ignored

                shutil.copytree(
                    ROOT,
                    isolated_root,
                    ignore=ignore_isolated_snapshot,
                )
                isolated_rels = [
                    (isolated_root / rel).relative_to(isolated_root).as_posix()
                    for rel in rels
                ]
                proc = subprocess.run(
                    [sys.executable, "-m", "pytest", *isolated_rels, "-q", "-p", "no:cacheprovider", *deselect],
                    cwd=isolated_root,
                    capture_output=True,
                    text=True,
                    timeout=effective_timeout,
                    env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin:/usr/local/bin"},
                )
            combined_output = (proc.stdout or "") + (proc.stderr or "")
            tail = combined_output.strip().splitlines()[-1] if combined_output.strip() else ""
            log_name = f"test_group_{batch_index:02d}_{label}.log"
            if log_dir is not None:
                (log_dir / log_name).write_text(combined_output, encoding="utf-8")
            m_pass = re.search(r"(\d+) passed", tail)
            m_fail = re.search(r"(\d+) failed", tail)
            m_err = re.search(r"(\d+) error", tail)
            passed = int(m_pass.group(1)) if m_pass else 0
            failed = int(m_fail.group(1)) if m_fail else 0
            errors = int(m_err.group(1)) if m_err else (
                0 if proc.returncode == 0 else (0 if passed and not failed else 1)
            )
            return {
                "batch": batch_index,
                "files": [f.name for f in batch],
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "returncode": proc.returncode,
                "tail": tail[:500],
                "log_file": log_name if log_dir is not None else None,
                "skipped": skipped,
                "timed_out": False,
                "timeout_seconds": timeout_seconds,
            }
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            stderr = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            combined_output = stdout + "\n" + stderr
            tail_source = combined_output.strip().splitlines()
            log_name = f"test_group_{batch_index:02d}_{label}.log"
            if log_dir is not None:
                (log_dir / log_name).write_text(combined_output, encoding="utf-8")
            return {
                "batch": batch_index,
                "files": [f.name for f in batch],
                "passed": 0,
                "failed": 0,
                "errors": 1,
                "returncode": 124,
                "tail": (tail_source[-1] if tail_source else "test partition timed out")[:500],
                "log_file": log_name if log_dir is not None else None,
                "skipped": skipped,
                "timed_out": True,
                "timeout_seconds": timeout_seconds,
            }

    results: list[dict] = []
    # Run deterministic groups sequentially. This avoids cross-group workspace
    # contamination and makes the failing group immediately visible in CI.
    for batch_index, batch in enumerate(batches):
        if not batch:
            continue
        print(f"test-group {batch_index + 1}/{len(batches)}: START files={len(batch)}", flush=True)
        result = run_batch(batch_index, batch, "parallel_partition")
        results.append(result)
        state = "PASS" if result["returncode"] == 0 else "FAIL"
        print(
            f"test-group {batch_index + 1}/{len(batches)}: {state} "
            f"passed={result['passed']} failed={result['failed']} errors={result['errors']} "
            f"log={result.get('log_file') or 'not-written'}",
            flush=True,
        )
        if result["returncode"] != 0:
            print(result.get("tail", ""), flush=True)

    # Workspace-mutating tests run strictly after the normal groups finish.
    if serial_files:
        serial_index = len(batches)
        print(f"test-group serial: START files={len(serial_files)}", flush=True)
        result = run_batch(serial_index, serial_files, "workspace_serial")
        results.append(result)
        state = "PASS" if result["returncode"] == 0 else "FAIL"
        print(
            f"test-group serial: {state} passed={result['passed']} "
            f"failed={result['failed']} errors={result['errors']} "
            f"log={result.get('log_file') or 'not-written'}",
            flush=True,
        )
        if result["returncode"] != 0:
            print(result.get("tail", ""), flush=True)

    failures = []
    skipped_heavy: list[str] = []
    for result in results:
        skipped_heavy.extend(result["skipped"])
        if result["returncode"] != 0:
            failures.append({
                "batch": result["batch"],
                "files": result["files"],
                "tail": result["tail"],
                "log_file": result.get("log_file"),
            })
    return {
        "test_files": len(files),
        "passed": sum(r["passed"] for r in results),
        "failed": sum(r["failed"] for r in results),
        "collection_or_run_errors": sum(r["errors"] for r in results),
        "failing_files": failures,
        "skipped_heavy_tests": sorted(set(skipped_heavy)),
        "execution_mode": f"sequential deterministic groups ({worker_count} normal + {1 if serial_files else 0} serial)",
        "group_order": [r["batch"] for r in results],
        "partition_timeout_seconds": timeout_seconds,
        "timeout_disabled": timeout_seconds == 0,
    }


def run_package_lints(skip_heavy: bool, timeout_seconds: int = 3600) -> dict:
    import shutil
    import tempfile
    results = {}
    package_roots = sorted({p.parent for p in (ROOT / "packages").rglob("ordo.yml")})
    for pkg in package_roots:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_pkg = Path(tmp) / pkg.name
            shutil.copytree(pkg, tmp_pkg, ignore=shutil.ignore_patterns("__pycache__"))
            effective_timeout = None if timeout_seconds == 0 else timeout_seconds
            try:
                proc = subprocess.run(
                    [sys.executable, "-c",
                     "import sys; sys.path.insert(0,'cli'); from ordo.cli import main; sys.exit(main(['lint', %r]))" % str(tmp_pkg)],
                    cwd=ROOT, capture_output=True, text=True, timeout=effective_timeout,
                    env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin:/usr/local/bin"},
                )
                results[pkg.relative_to(ROOT / "packages").as_posix()] = "passed" if proc.returncode == 0 else "failed"
            except subprocess.TimeoutExpired:
                results[pkg.relative_to(ROOT / "packages").as_posix()] = f"timed_out_after_{timeout_seconds}s"
    return results


def check_manifest_sync() -> list[str]:
    issues = []
    md = (ROOT / "CONSOLIDATED_BACKLOG.md").read_text(encoding="utf-8")
    md_statuses = dict(re.findall(r"### (BL-ORDO-\d+) — .*?\n\nStatus: `([^`]+)`", md, re.S))
    data = json.loads((ROOT / "manifests/CONSOLIDATED_BACKLOG.json").read_text(encoding="utf-8"))
    js = {i["id"]: i["status"] for i in data["items"]}
    if md_statuses != js:
        issues.append("CONSOLIDATED_BACKLOG.md and manifests/CONSOLIDATED_BACKLOG.json are desynchronized")
    return issues


def check_root_hygiene() -> list[str]:
    stray = [p.name for p in ROOT.iterdir() if p.is_file() and re.match(r"^M\d+_", p.name)]
    if stray:
        return [f"{len(stray)} milestone report(s) in root; move to archive/milestone_reports/: {stray[:5]}"]
    return []


def check_english_only_policy() -> dict:
    result = validate_english_only_policy(ROOT, ROOT / "policies" / "english_only_policy.yaml")
    path = ROOT / "reports" / "english_only_policy_report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result

def build_zip(out: Path, report: dict, self_check: dict, md_text: str) -> dict:
    reports = {
        "DELIVERY_GATE_REPORT.json": json.dumps(report, indent=2) + "\n",
        "FINAL_PACKAGE_SELF_CHECK_REPORT.json": json.dumps(self_check, indent=2) + "\n",
        "FINAL_PACKAGE_SELF_CHECK_REPORT.md": md_text,
    }
    return build_verified_archive(ROOT, out, reports, report["run_id"])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--check-only", action="store_true")
    ap.add_argument("--workers", type=int, default=4, help="Number of deterministic test groups; groups run sequentially.")
    ap.add_argument(
        "--test-log-dir", type=Path, default=None,
        help="Optional directory for complete per-group pytest logs.",
    )
    ap.add_argument(
        "--test-timeout-seconds", type=int, default=3600,
        help="Timeout for each test partition. Use 0 to disable the internal timeout.",
    )
    ap.add_argument(
        "--lint-timeout-seconds", type=int, default=3600,
        help="Timeout for each package lint. Use 0 to disable the internal timeout.",
    )
    ap.add_argument("--skip-heavy", action="store_true",
                    help="Deprecated compatibility flag; no tests or package lints are skipped.")
    args = ap.parse_args(argv)

    if args.test_timeout_seconds < 0 or args.lint_timeout_seconds < 0:
        ap.error("timeout values must be 0 or positive integers")
    tests = run_partitioned_tests(
        skip_heavy=args.skip_heavy,
        workers=args.workers,
        timeout_seconds=args.test_timeout_seconds,
        log_dir=args.test_log_dir,
    )
    lints = run_package_lints(
        skip_heavy=args.skip_heavy,
        timeout_seconds=args.lint_timeout_seconds,
    )
    sync_issues = check_manifest_sync()
    root_issues = check_root_hygiene()
    english_only = check_english_only_policy()

    blocking: list[str] = []
    if tests["failed"] or tests["collection_or_run_errors"] or tests["failing_files"]:
        blocking.append(f"test suite red: {tests['failed']} failed, files: {[f['files'] for f in tests['failing_files']]}")
    for name, status in lints.items():
        if status == "failed":
            blocking.append(f"package lint failed: {name}")
        elif status.startswith("timed_out_after_"):
            blocking.append(f"package lint timed out: {name} ({status})")
    blocking += sync_issues + root_issues
    if english_only["status"] != "passed":
        blocking.append(f"English-only policy failed: {english_only['new_violation_count']} new violation(s), {english_only['parse_failure_count']} parse failure(s)")

    identity = load_identity(ROOT)
    run_id = f"{identity['release_id']}:{uuid.uuid4().hex}"
    current_source_hash = source_tree_hash(ROOT)
    report = {
        "report_id": f"ORDO_DELIVERY_GATE_{_now()[:10].replace('-', '_')}",
        "run_id": run_id,
        "release_id": identity["release_id"],
        "language_version": identity["language_version"],
        "framework_version": identity["framework_version"],
        "source_tree_hash": current_source_hash,
        "generated_at": _now(),
        "generated_by": "tools/build_release_archive.py",
        "status": "passed" if not blocking else "blocked",
        "tests": tests,
        "package_lints": lints,
        "manifest_sync": "passed" if not sync_issues else "failed",
        "root_hygiene": "passed" if not root_issues else "failed",
        "english_only_policy": english_only,
        "blocking_issues": blocking,
        "timeouts": {
            "test_partition_seconds": args.test_timeout_seconds,
            "package_lint_seconds": args.lint_timeout_seconds,
            "zero_means_disabled": True,
        },
        "policy": "The project archive may only be produced by this script while status is passed.",
    }

    (ROOT / "DELIVERY_GATE_REPORT.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if blocking:
        print("delivery gate: BLOCKED")
        for b in blocking:
            print("  -", b)
        return 1

    # Regenerate the self-check from THIS run so it can never be stale.
    self_check = {
        "report_id": report["report_id"].replace("DELIVERY_GATE", "FINAL_SELF_CHECK"),
        "generated_at": report["generated_at"],
        "generated_by": report["generated_by"],
        "status": "passed",
        "run_id": report["run_id"],
        "release_id": report["release_id"],
        "source_tree_hash": report["source_tree_hash"],
        "tests": tests,
        "package_lints": lints,
        "english_only_policy": english_only,
        "note": "Generated automatically at delivery time from the current tree; never hand-written.",
    }
    (ROOT / "FINAL_PACKAGE_SELF_CHECK_REPORT.json").write_text(
        json.dumps(self_check, indent=2) + "\n",
        encoding="utf-8",
    )
    md_lines = [
        "# Final Package Self-Check",
        "",
        f"Generated: {self_check['generated_at']} by `tools/build_release_archive.py` (delivery gate).",
        "",
        f"- Test files: {tests['test_files']}",
        f"- Passed: {tests['passed']}",
        f"- Failed: {tests['failed']}",
        f"- Package lints: " + ", ".join(f"{k}={v}" for k, v in lints.items()),
        "",
        "This file is regenerated on every delivery; a stale copy indicates the archive bypassed the gate.",
    ]
    md_text = "\n".join(md_lines) + "\n"

    print(f"delivery gate: PASSED (tests {tests['passed']} passed / {tests['failed']} failed; lints: {lints})")

    if args.check_only or args.out is None:
        return 0
    result = build_zip(args.out, report, self_check, md_text)
    print(f"archive: {args.out} ({result['verified_files']} verified files; sha256={result['archive_sha256']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
