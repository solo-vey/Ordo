"""M60.6 dry-run orchestration for PathWalk benchmark calibration prep.

The dry-run is intentionally no-API and no-model: it drives the scenario
`ground_truth` through real M60 runtime packages, then scores the produced
runtime artifacts. Unlike the single-scenario matrix smoke, this module is
meant to run many scenarios and collect raw component metrics.

Important design rule: each scenario/runtime_view case is executed in its own
short-lived Python subprocess. This avoids reusing one long-lived process across
many embedded runtime sandboxes, which previously made multi-scenario dry-runs
fragile and prone to hangs in automated environments.
"""

from __future__ import annotations

import csv
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from ..generator.maze_gen import generate_tree
from ..generator.emit_ordo_package import emit_package
from ..generator.noise_gen import generate_script, PathWalkScript, ScriptTurn
from .aggregate import aggregate, render_markdown
from .harness import _workspace_root, _local_ordo_env, _prepare_m60_runtime_sandbox
from .matrix_smoke import _drive_ground_truth, SUPPORTED_RUNTIME_VIEWS
from .scorer import score_test_case


def _safe_runtime_view(runtime_view: str) -> str:
    return runtime_view.replace(",", "_").replace("/", "_")


def _load_script(path: Path) -> PathWalkScript:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    turns = [ScriptTurn(**turn) for turn in data["turns"]]
    ground_truth = [(item["node_id"], item["value"]) for item in data["ground_truth"]]
    return PathWalkScript(
        tree_seed=data["tree_seed"],
        script_seed=data["script_seed"],
        turns=turns,
        ground_truth=ground_truth,
    )


def run_dry_run_case(
    *,
    tree_dir: Path,
    scenario_path: Path,
    runtime_view: str,
    out_dir: Path,
    scenario_id: str | None = None,
) -> dict[str, Any]:
    """Run one scenario/runtime_view case in the current process.

    This function is called by the `dry-run-case` CLI subcommand. The multi-case
    orchestrator should invoke it through a subprocess, not directly, so each
    runtime sandbox has an isolated Python process lifecycle.
    """
    if runtime_view not in SUPPORTED_RUNTIME_VIEWS:
        raise ValueError(f"unsupported runtime_view: {runtime_view!r}")

    tree_dir = Path(tree_dir)
    scenario_path = Path(scenario_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    scenario_id = scenario_id or scenario_path.stem
    safe_view = _safe_runtime_view(runtime_view)

    sandboxes_dir = out_dir / "sandboxes"
    transcripts_dir = out_dir / "transcripts"
    scores_dir = out_dir / "scores"
    for d in (sandboxes_dir, transcripts_dir, scores_dir):
        d.mkdir(parents=True, exist_ok=True)

    sandbox = sandboxes_dir / f"{scenario_id}_{safe_view}"
    _prepare_m60_runtime_sandbox(tree_dir, sandbox, runtime_view)

    script = _load_script(scenario_path)
    transcript = _drive_ground_truth(sandbox, script)
    transcript.update({
        "scenario_id": scenario_id,
        "driver": "benchmark-dry-run-ground-truth",
        "cli_mode": "enforced",
        "runtime_view": runtime_view,
        "turns": [],
    })
    transcript_path = transcripts_dir / f"{scenario_id}_{safe_view}_transcript.json"
    transcript_path.write_text(json.dumps(transcript, ensure_ascii=False, indent=2), encoding="utf-8")

    score = score_test_case(sandbox, script, transcript=[], rerun_verification=False)
    score.update({
        "scenario_id": scenario_id,
        "driver": "benchmark-dry-run-ground-truth",
        "cli_mode": "enforced",
        "runtime_view": runtime_view,
    })
    score_path = scores_dir / f"{scenario_id}_{safe_view}_score.json"
    score_path.write_text(json.dumps(score, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "status": "passed" if score.get("gate_passed") else "failed",
        "scenario_id": scenario_id,
        "runtime_view": runtime_view,
        "sandbox": str(sandbox.relative_to(out_dir)),
        "transcript": str(transcript_path.relative_to(out_dir)),
        "score_file": str(score_path.relative_to(out_dir)),
        "path_quality_score": score.get("path_quality_score"),
        "protocol_compliance_rate": score.get("protocol_compliance_rate"),
    }


def _write_raw_metrics_csv(scores_dir: Path, out_path: Path) -> None:
    rows: list[dict[str, Any]] = []
    for path in sorted(Path(scores_dir).glob("*_score.json")):
        try:
            score = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        metadata = score.get("runtime_metadata") or {}
        rows.append({
            "score_file": path.name,
            "scenario_id": score.get("scenario_id"),
            "runtime_view": score.get("runtime_view") or metadata.get("runtime_view"),
            "driver": score.get("driver"),
            "cli_mode": score.get("cli_mode"),
            "gate_passed": score.get("gate_passed"),
            "path_quality_score": score.get("path_quality_score"),
            "cell_match_rate": score.get("cell_match_rate"),
            "protocol_compliance_rate": score.get("protocol_compliance_rate"),
            "distraction_recovery_rate": score.get("distraction_recovery_rate"),
            "backtrack_accuracy": score.get("backtrack_accuracy"),
            "turn_accuracy_rate": score.get("turn_accuracy_rate"),
            "runtime_protocol_version": metadata.get("runtime_protocol_version"),
            "ordo_cli_version": metadata.get("ordo_cli_version"),
            "canonical_ir_hash": metadata.get("canonical_ir_hash"),
            "targets_manifest_hash": metadata.get("targets_manifest_hash"),
            "session_trace_hash": metadata.get("session_trace_hash"),
        })

    fieldnames = [
        "score_file",
        "scenario_id",
        "runtime_view",
        "driver",
        "cli_mode",
        "gate_passed",
        "path_quality_score",
        "cell_match_rate",
        "protocol_compliance_rate",
        "distraction_recovery_rate",
        "backtrack_accuracy",
        "turn_accuracy_rate",
        "runtime_protocol_version",
        "ordo_cli_version",
        "canonical_ir_hash",
        "targets_manifest_hash",
        "session_trace_hash",
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)





def _write_job_artifacts(out_dir: Path, jobs: list[dict[str, Any]]) -> None:
    """Write artifact-only job descriptors and one-job shell wrappers.

    M60.5.4 contract: multi-case benchmark execution is represented as
    artifacts. A supervisor/CI may run each job script independently; PathWalk
    no longer requires a Python parent loop to keep control of every case.
    """
    jobs_dir = out_dir / "jobs"
    scripts_dir = out_dir / "job_scripts"
    jobs_dir.mkdir(parents=True, exist_ok=True)
    scripts_dir.mkdir(parents=True, exist_ok=True)
    root = _workspace_root()
    for job in jobs:
        job_doc = dict(job)
        job_doc["schema_version"] = "ordo.pathwalk.dry_run_job.v1"
        job_doc["plan_path"] = "DRY_RUN_PLAN.json"
        job_doc["execution_contract"] = "artifact-only-one-job"
        job_file = jobs_dir / f"{job['job_id']}.json"
        job_file.write_text(json.dumps(job_doc, ensure_ascii=False, indent=2), encoding="utf-8")
        script = scripts_dir / f"{job['job_id']}.sh"
        script.write_text(
            "\n".join([
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                "SCRIPT_DIR=\"$(cd \"$(dirname \"${BASH_SOURCE[0]}\")\" && pwd)\"",
                "PLAN=\"${SCRIPT_DIR}/../DRY_RUN_PLAN.json\"",
                "ROOT=\"${ORDO_PATHWALK_ROOT:-}\"",
                "if [[ -z \"${ROOT}\" ]]; then",
                "  CANDIDATE=\"$(cd \"${SCRIPT_DIR}/../../..\" && pwd)\"",
                "  if [[ -d \"${CANDIDATE}/ordo_pathwalk\" ]]; then ROOT=\"${CANDIDATE}\"; fi",
                "fi",
                "if [[ -z \"${ROOT}\" || ! -d \"${ROOT}/ordo_pathwalk\" ]]; then",
                "  echo \"ERROR: ORDO_PATHWALK_ROOT must point to an Ordo workspace or PathWalk RC root containing ordo_pathwalk/.\" >&2",
                "  echo \"For standalone RC + developer bundle, set ORDO_PATHWALK_ROOT=<pathwalk_rc_root> and ORDO_CLI_ROOT=<developer_bundle>/cli.\" >&2",
                "  exit 64",
                "fi",
                "CLI_ROOT=\"${ORDO_CLI_ROOT:-${ROOT}/cli}\"",
                "if [[ ! -d \"${CLI_ROOT}/ordo\" ]]; then",
                "  echo \"ERROR: Ordo CLI package not found. Set ORDO_CLI_ROOT to a cli directory containing ordo/.\" >&2",
                "  exit 65",
                "fi",
                "PY_PATH=\"${CLI_ROOT}:${ROOT}${PYTHONPATH:+:${PYTHONPATH}}\"",
                "cd \"${ROOT}\"",
                f"exec env PYTHONPATH=\"${{PY_PATH}}\" python3 -m ordo_pathwalk.cli dry-run-job --plan \"${{PLAN}}\" --job-id {job['job_id']} < /dev/null",
                "",
            ]),
            encoding="utf-8",
        )
        script.chmod(script.stat().st_mode | 0o111)
    readme = out_dir / "JOB_EXECUTION.md"
    readme.write_text(
        "\n".join([
            "# PathWalk dry-run job execution",
            "",
            "This directory uses the M60.6.1 artifact-only dry-run execution contract.",
            "",
            "Recommended execution model:",
            "",
            "1. `DRY_RUN_PLAN.json` declares the full benchmark matrix.",
            "2. `jobs/*.json` are immutable one-job descriptors.",
            "3. `job_scripts/*.sh` executes exactly one job and redirects stdin from `/dev/null`.",
            "4. Run jobs independently from a shell, CI matrix, or external supervisor.",
            "5. After jobs finish, run `python3 -m ordo_pathwalk.cli dry-run-collect --plan DRY_RUN_PLAN.json`.",
            "",
            "Do not use a long-lived Python parent process as the acceptance path for multi-job dry-runs.",
            "",
            "Portable execution note: job scripts no longer embed a generation-machine workspace path.",
            "If scripts are not inside a full Ordo workspace, set `ORDO_PATHWALK_ROOT` to a workspace or PathWalk RC root.",
            "If that root does not contain `cli/ordo`, also set `ORDO_CLI_ROOT` to the developer bundle `cli/` directory.",
            "",
        ]),
        encoding="utf-8",
    )

def create_dry_run_plan(
    out_dir: Path,
    *,
    scenario_count: int = 20,
    depth: int = 3,
    branching: tuple[int, int] = (2, 3),
    tree_seed: int = 42,
    script_seed: int = 100,
    runtime_views: tuple[str, ...] = SUPPORTED_RUNTIME_VIEWS,
    force: bool = False,
) -> dict[str, Any]:
    """Create a dry-run plan without executing any jobs.

    M60.5.2b external-job contract: a benchmark is decomposed into a plan,
    independent one-job invocations, and a collect step. This avoids keeping a
    long-lived parent process responsible for all runtime sandboxes.
    """
    if scenario_count < 1:
        raise ValueError("scenario_count must be >= 1")
    unknown_views = [v for v in runtime_views if v not in SUPPORTED_RUNTIME_VIEWS]
    if unknown_views:
        raise ValueError(f"unsupported runtime_view values: {unknown_views}")

    out_dir = Path(out_dir)
    if out_dir.exists():
        if not force:
            raise FileExistsError(f"output directory exists: {out_dir}; pass force=True to replace it")
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    tree = generate_tree(seed=tree_seed, depth=depth, branching_range=branching)
    tree_dir = emit_package(tree, out_dir / "tree_source", "pathwalk.benchmark_dry_run", force=True)

    scenarios_dir = out_dir / "scenarios"
    scenarios_dir.mkdir(parents=True, exist_ok=True)
    scenario_paths: list[Path] = []
    for i in range(scenario_count):
        script = generate_script(tree, script_seed=script_seed + i, num_confusion_episodes=(1, 3))
        scenario_path = scenarios_dir / f"scenario_{i:03d}.json"
        scenario_path.write_text(json.dumps(script.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        scenario_paths.append(scenario_path)

    runtime_templates_dir = out_dir / "runtime_templates"
    runtime_templates_dir.mkdir(parents=True, exist_ok=True)
    runtime_templates: dict[str, Path] = {}
    for runtime_view in runtime_views:
        safe_view = _safe_runtime_view(runtime_view)
        template_dir = runtime_templates_dir / safe_view
        _prepare_m60_runtime_sandbox(tree_dir, template_dir, runtime_view)
        runtime_templates[runtime_view] = template_dir

    jobs: list[dict[str, Any]] = []
    for scenario_path in scenario_paths:
        scenario_id = scenario_path.stem
        for runtime_view in runtime_views:
            safe_view = _safe_runtime_view(runtime_view)
            job_id = f"{scenario_id}_{safe_view}"
            jobs.append({
                "job_id": job_id,
                "scenario_id": scenario_id,
                "runtime_view": runtime_view,
                "scenario_path": str(scenario_path.relative_to(out_dir)),
                "runtime_template": str(runtime_templates[runtime_view].relative_to(out_dir)),
                "expected_score_file": f"scores/{job_id}_score.json",
                "expected_transcript_file": f"transcripts/{job_id}_transcript.json",
            })

    plan = {
        "schema_version": "ordo.pathwalk.dry_run_plan.v1",
        "mode": "artifact-only-external-job",
        "scenario_count": scenario_count,
        "runtime_views": list(runtime_views),
        "expected_cases": len(jobs),
        "tree_seed": tree_seed,
        "script_seed_start": script_seed,
        "depth": depth,
        "branching": list(branching),
        "tree_source": "tree_source",
        "job_artifacts": {
            "descriptors_dir": "jobs",
            "scripts_dir": "job_scripts",
            "readme": "JOB_EXECUTION.md",
            "contract": "run each job as an independent process; collect from score artifacts",
        },
        "jobs": jobs,
    }
    plan_path = out_dir / "DRY_RUN_PLAN.json"
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_job_artifacts(out_dir, jobs)
    return plan


def _load_plan(plan_path: Path) -> tuple[Path, dict[str, Any]]:
    plan_path = Path(plan_path)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if plan.get("schema_version") != "ordo.pathwalk.dry_run_plan.v1":
        raise ValueError("unsupported dry-run plan schema")
    return plan_path.parent, plan


def run_dry_run_job(plan_path: Path, *, job_id: str) -> dict[str, Any]:
    """Execute one dry-run job from a plan in the current process."""
    out_dir, plan = _load_plan(plan_path)
    jobs = {job["job_id"]: job for job in plan.get("jobs", [])}
    if job_id not in jobs:
        raise KeyError(f"job not found in plan: {job_id}")
    job = jobs[job_id]
    return run_dry_run_case(
        tree_dir=out_dir / job["runtime_template"],
        scenario_path=out_dir / job["scenario_path"],
        runtime_view=job["runtime_view"],
        out_dir=out_dir,
        scenario_id=job["scenario_id"],
    )


def collect_dry_run_results(plan_path: Path) -> dict[str, Any]:
    """Collect existing dry-run job outputs into RAW_METRICS/SUMMARY files."""
    out_dir, plan = _load_plan(plan_path)
    scores_dir = out_dir / "scores"
    raw_metrics_path = out_dir / "RAW_METRICS.csv"
    _write_raw_metrics_csv(scores_dir, raw_metrics_path)

    summary = aggregate(scores_dir)
    case_results: list[dict[str, Any]] = []
    for job in plan.get("jobs", []):
        expected_score = out_dir / job["expected_score_file"]
        status = "missing"
        score_doc: dict[str, Any] = {}
        if expected_score.exists():
            try:
                score_doc = json.loads(expected_score.read_text(encoding="utf-8"))
                status = "passed" if score_doc.get("gate_passed") else "failed"
            except Exception:
                status = "unreadable"
        case_results.append({
            "job_id": job["job_id"],
            "scenario_id": job["scenario_id"],
            "runtime_view": job["runtime_view"],
            "status": status,
            "score_file": job["expected_score_file"] if expected_score.exists() else None,
            "path_quality_score": score_doc.get("path_quality_score"),
            "protocol_compliance_rate": score_doc.get("protocol_compliance_rate"),
        })

    expected_cases = int(plan.get("expected_cases") or len(plan.get("jobs", [])))
    passed_cases = sum(1 for r in case_results if r.get("status") == "passed")
    completed_cases = sum(1 for r in case_results if r.get("status") in {"passed", "failed"})
    summary["benchmark_dry_run"] = {
        "status": "passed" if passed_cases == expected_cases and summary.get("status") == "ok" else "failed",
        "execution_contract": "artifact-only-external-job",
        "scenario_count": plan.get("scenario_count"),
        "runtime_views": plan.get("runtime_views"),
        "expected_cases": expected_cases,
        "completed_cases": completed_cases,
        "passed_cases": passed_cases,
        "tree_seed": plan.get("tree_seed"),
        "script_seed_start": plan.get("script_seed_start"),
        "depth": plan.get("depth"),
        "branching": plan.get("branching"),
        "raw_metrics_csv": str(raw_metrics_path.relative_to(out_dir)),
        "case_results": case_results,
    }
    (out_dir / "SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "SUMMARY.md").write_text(render_markdown(summary), encoding="utf-8")
    return summary

def run_benchmark_dry_run(
    out_dir: Path,
    *,
    scenario_count: int = 20,
    depth: int = 3,
    branching: tuple[int, int] = (2, 3),
    tree_seed: int = 42,
    script_seed: int = 100,
    runtime_views: tuple[str, ...] = SUPPORTED_RUNTIME_VIEWS,
    force: bool = False,
    case_timeout: int = 180,
    stop_on_failure: bool = False,
    worker_mode: str = "subprocess",
) -> dict[str, Any]:
    """Run an isolated no-API benchmark dry-run over many scenarios."""
    if scenario_count < 1:
        raise ValueError("scenario_count must be >= 1")
    if worker_mode not in {"in-process", "subprocess"}:
        raise ValueError("worker_mode must be 'in-process' or 'subprocess'")
    unknown_views = [v for v in runtime_views if v not in SUPPORTED_RUNTIME_VIEWS]
    if unknown_views:
        raise ValueError(f"unsupported runtime_view values: {unknown_views}")

    out_dir = Path(out_dir)
    if out_dir.exists():
        if not force:
            raise FileExistsError(f"output directory exists: {out_dir}; pass force=True to replace it")
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    tree = generate_tree(seed=tree_seed, depth=depth, branching_range=branching)
    tree_dir = emit_package(tree, out_dir / "tree_source", "pathwalk.benchmark_dry_run", force=True)

    scenarios_dir = out_dir / "scenarios"
    scenarios_dir.mkdir(parents=True, exist_ok=True)
    scenario_paths: list[Path] = []
    for i in range(scenario_count):
        script = generate_script(tree, script_seed=script_seed + i, num_confusion_episodes=(1, 3))
        scenario_path = scenarios_dir / f"scenario_{i:03d}.json"
        scenario_path.write_text(json.dumps(script.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        scenario_paths.append(scenario_path)

    # Build one clean runtime template per runtime_view, then let each case
    # worker copy that template into its own sandbox. Rebuilding runtime packages
    # per scenario is slow and was the main source of multi-scenario instability.
    runtime_templates_dir = out_dir / "runtime_templates"
    runtime_templates_dir.mkdir(parents=True, exist_ok=True)
    runtime_templates: dict[str, Path] = {}
    for runtime_view in runtime_views:
        safe_view = _safe_runtime_view(runtime_view)
        template_dir = runtime_templates_dir / safe_view
        _prepare_m60_runtime_sandbox(tree_dir, template_dir, runtime_view)
        runtime_templates[runtime_view] = template_dir

    logs_dir = out_dir / "case_logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    case_results: list[dict[str, Any]] = []

    env = _local_ordo_env()
    root = _workspace_root()
    for scenario_path in scenario_paths:
        scenario_id = scenario_path.stem
        for runtime_view in runtime_views:
            safe_view = _safe_runtime_view(runtime_view)
            log_base = logs_dir / f"{scenario_id}_{safe_view}"
            command = [
                sys.executable,
                "-m",
                "ordo_pathwalk.cli",
                "dry-run-case",
                "--tree",
                str(runtime_templates[runtime_view]),
                "--scenario",
                str(scenario_path),
                "--runtime-view",
                runtime_view,
                "--out",
                str(out_dir),
                "--scenario-id",
                scenario_id,
            ]
            stdout_log = log_base.with_suffix(".stdout.txt")
            stderr_log = log_base.with_suffix(".stderr.txt")
            try:
                if worker_mode == "in-process":
                    case_doc = run_dry_run_case(
                        tree_dir=runtime_templates[runtime_view],
                        scenario_path=scenario_path,
                        runtime_view=runtime_view,
                        out_dir=out_dir,
                        scenario_id=scenario_id,
                    )
                    stdout_log.write_text(json.dumps(case_doc, ensure_ascii=False, indent=2), encoding="utf-8")
                    stderr_log.write_text("", encoding="utf-8")
                    case_result = {
                        "scenario_id": scenario_id,
                        "runtime_view": runtime_view,
                        "returncode": 0 if case_doc.get("status") == "passed" else 1,
                        "status": "passed" if case_doc.get("status") == "passed" else "failed",
                        "case": case_doc,
                        "stdout_log": str(stdout_log.relative_to(out_dir)),
                        "stderr_log": str(stderr_log.relative_to(out_dir)),
                    }
                else:
                    # Worker subprocess mode watches for the score artifact instead
                    # of waiting indefinitely for interpreter shutdown. Some embedded
                    # CLI subprocess trees can leave the worker alive briefly after it
                    # has already written all benchmark artifacts. Once the score file
                    # exists, the case is complete and any lingering worker process is
                    # terminated.
                    command = [
                        sys.executable,
                        "-m",
                        "ordo_pathwalk.cli",
                        "dry-run-case",
                        "--tree",
                        str(runtime_templates[runtime_view]),
                        "--scenario",
                        str(scenario_path),
                        "--runtime-view",
                        runtime_view,
                        "--out",
                        str(out_dir),
                        "--scenario-id",
                        scenario_id,
                    ]
                    expected_score = out_dir / "scores" / f"{scenario_id}_{safe_view}_score.json"
                    with stdout_log.open("w", encoding="utf-8") as stdout_f, stderr_log.open("w", encoding="utf-8") as stderr_f:
                        proc = subprocess.Popen(
                            command,
                            cwd=root,
                            env=env,
                            stdout=stdout_f,
                            stderr=stderr_f,
                            text=True,
                            start_new_session=True,
                        )
                        deadline = time.monotonic() + case_timeout
                        while time.monotonic() < deadline:
                            if expected_score.exists():
                                # Give the worker a short chance to exit naturally,
                                # then kill any lingering process group.
                                try:
                                    proc.wait(timeout=2)
                                except subprocess.TimeoutExpired:
                                    try:
                                        os.killpg(proc.pid, signal.SIGKILL)
                                    except ProcessLookupError:
                                        pass
                                    try:
                                        proc.wait(timeout=5)
                                    except Exception:
                                        pass
                                break
                            if proc.poll() is not None:
                                break
                            time.sleep(0.2)
                        else:
                            try:
                                os.killpg(proc.pid, signal.SIGKILL)
                            except ProcessLookupError:
                                pass
                            try:
                                proc.wait(timeout=5)
                            except Exception:
                                pass
                            raise TimeoutError(f"case timed out after {case_timeout}s")
                    stdout_text = stdout_log.read_text(encoding="utf-8") if stdout_log.exists() else ""
                    try:
                        case_doc = json.loads(stdout_text)
                    except Exception:
                        case_doc = {}
                    if expected_score.exists():
                        try:
                            score_doc = json.loads(expected_score.read_text(encoding="utf-8"))
                        except Exception:
                            score_doc = {}
                        if not case_doc:
                            case_doc = {
                                "status": "passed" if score_doc.get("gate_passed") else "failed",
                                "scenario_id": scenario_id,
                                "runtime_view": runtime_view,
                                "score_file": str(expected_score.relative_to(out_dir)),
                                "path_quality_score": score_doc.get("path_quality_score"),
                                "protocol_compliance_rate": score_doc.get("protocol_compliance_rate"),
                            }
                    case_result = {
                        "scenario_id": scenario_id,
                        "runtime_view": runtime_view,
                        "returncode": proc.returncode,
                        "status": "passed" if expected_score.exists() and case_doc.get("status") == "passed" else "failed",
                        "case": case_doc,
                        "stdout_log": str(stdout_log.relative_to(out_dir)),
                        "stderr_log": str(stderr_log.relative_to(out_dir)),
                    }
            except TimeoutError:
                with stderr_log.open("a", encoding="utf-8") as stderr_f:
                    stderr_f.write(f"\nTIMEOUT after {case_timeout}s\n")
                case_result = {
                    "scenario_id": scenario_id,
                    "runtime_view": runtime_view,
                    "returncode": None,
                    "status": "timeout",
                    "case": {},
                    "stdout_log": str(stdout_log.relative_to(out_dir)),
                    "stderr_log": str(stderr_log.relative_to(out_dir)),
                }
            case_results.append(case_result)
            if stop_on_failure and case_result["status"] != "passed":
                break
        if stop_on_failure and case_results and case_results[-1]["status"] != "passed":
            break

    scores_dir = out_dir / "scores"
    raw_metrics_path = out_dir / "RAW_METRICS.csv"
    _write_raw_metrics_csv(scores_dir, raw_metrics_path)

    summary = aggregate(scores_dir)
    expected_cases = scenario_count * len(runtime_views)
    passed_cases = sum(1 for r in case_results if r.get("status") == "passed")
    summary["benchmark_dry_run"] = {
        "status": "passed" if passed_cases == expected_cases and summary.get("status") == "ok" else "failed",
        "scenario_count": scenario_count,
        "runtime_views": list(runtime_views),
        "expected_cases": expected_cases,
        "completed_cases": len(case_results),
        "passed_cases": passed_cases,
        "case_timeout_seconds": case_timeout,
        "worker_mode": worker_mode,
        "tree_seed": tree_seed,
        "script_seed_start": script_seed,
        "depth": depth,
        "branching": list(branching),
        "raw_metrics_csv": str(raw_metrics_path.relative_to(out_dir)),
        "case_results": case_results,
    }
    (out_dir / "SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "SUMMARY.md").write_text(render_markdown(summary), encoding="utf-8")
    return summary
