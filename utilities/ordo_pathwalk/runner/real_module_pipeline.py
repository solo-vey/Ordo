"""M82.3 end-to-end integration for real-module testcase generation and safe execution."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from ..generator.real_module import (
    write_real_module_clean_path_cases,
    write_real_module_graph_summary,
    write_real_module_noise_cases,
    write_real_module_terminal_paths,
)
from .real_module_execution import (
    create_real_module_execution_plan,
    collect_real_module_execution_results,
)

SCHEMA_PIPELINE = "ordo.pathwalk.real_module_pipeline.v1"
SUPPORTED_MODES = {"generate-only", "generate-and-run"}
SUPPORTED_CASE_SETS = {"clean", "noise", "both"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _selected_suites(case_set: str) -> tuple[str, ...]:
    if case_set == "both":
        return ("clean", "noise")
    return (case_set,)


def _worker_environment(workspace_root: Path) -> dict[str, str]:
    allowed = {key: value for key, value in os.environ.items() if key in {"PATH", "LANG", "LC_ALL", "LC_CTYPE", "TZ", "SYSTEMROOT", "WINDIR", "PATHEXT"}}
    cli_root = workspace_root / "cli"
    allowed["PYTHONPATH"] = os.pathsep.join((str(cli_root), str(workspace_root)))
    return allowed


def _execute_plan_workers(plan: dict[str, Any], plan_path: Path, workspace_root: Path) -> list[dict[str, Any]]:
    launches: list[dict[str, Any]] = []
    env = _worker_environment(workspace_root)
    for job in plan.get("jobs", []):
        command = [
            sys.executable,
            "-m",
            "utilities.ordo_pathwalk.cli",
            "real-module-exec-job",
            "--plan",
            str(plan_path),
            "--job-id",
            str(job["job_id"]),
        ]
        completed = subprocess.run(
            command,
            cwd=str(workspace_root),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        launches.append({
            "job_id": job["job_id"],
            "return_code": completed.returncode,
            "worker_stdout": completed.stdout,
            "worker_stderr": completed.stderr,
        })
    return launches


def run_real_module_pipeline(
    *,
    source_path: Path,
    out_dir: Path,
    mode: str = "generate-only",
    case_set: str = "clean",
    noise_patterns: Iterable[str] | None = None,
    timeout_seconds: int = 30,
    cleanup_policy: str = "retain_failures",
    max_output_bytes: int = 1_000_000,
    force: bool = False,
) -> dict[str, Any]:
    if mode not in SUPPORTED_MODES:
        raise ValueError(f"unsupported mode: {mode}")
    if case_set not in SUPPORTED_CASE_SETS:
        raise ValueError(f"unsupported case_set: {case_set}")

    source_input = Path(source_path).expanduser()
    if source_input.is_symlink():
        raise ValueError(f"source_path must be a regular non-symlink file: {source_input}")
    source_path = source_input.resolve()
    out_dir = Path(out_dir).expanduser().resolve()
    if not source_path.exists() or not source_path.is_file():
        raise ValueError(f"source_path must be a regular non-symlink file: {source_path}")
    if out_dir.exists() and any(out_dir.iterdir()) and not force:
        raise FileExistsError(f"output directory is not empty: {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)

    started_at = _utc_now()
    graph_dir = out_dir / "generation" / "graph"
    paths_dir = out_dir / "generation" / "paths"
    graph = write_real_module_graph_summary(source_path, graph_dir, force=force)
    paths = write_real_module_terminal_paths(graph_dir / "REAL_MODULE_GRAPH_SUMMARY.json", paths_dir, force=force)

    generation: dict[str, Any] = {"graph": graph, "paths": paths, "suites": {}}
    suite_summaries: dict[str, Path] = {}
    for suite in _selected_suites(case_set):
        suite_dir = out_dir / "generation" / f"{suite}_cases"
        if suite == "clean":
            result = write_real_module_clean_path_cases(paths_dir / "REAL_MODULE_TERMINAL_PATHS.json", suite_dir, force=force)
        else:
            result = write_real_module_noise_cases(
                paths_dir / "REAL_MODULE_TERMINAL_PATHS.json",
                suite_dir,
                patterns=list(noise_patterns) if noise_patterns else None,
                force=force,
            )
        generation["suites"][suite] = result
        suite_summaries[suite] = suite_dir / "SUMMARY.json"

    executions: dict[str, Any] = {}
    all_passed = True
    if mode == "generate-and-run":
        workspace_root = Path(__file__).resolve().parents[3]
        for suite, summary_path in suite_summaries.items():
            run_dir = out_dir / "execution" / suite
            plan = create_real_module_execution_plan(
                summary_path=summary_path,
                source_path=source_path,
                out_dir=run_dir,
                timeout_seconds=timeout_seconds,
                force=force,
                max_output_bytes=max_output_bytes,
                cleanup_policy=cleanup_policy,
            )
            plan_path = run_dir / "REAL_MODULE_EXECUTION_PLAN.json"
            launches = _execute_plan_workers(plan, plan_path, workspace_root)
            summary = collect_real_module_execution_results(plan_path)
            executions[suite] = {
                "plan_path": str(plan_path),
                "job_count": len(plan.get("jobs", [])),
                "worker_launches": launches,
                "summary_path": str(run_dir / "REAL_MODULE_EXECUTION_SUMMARY.json"),
                "summary": summary,
            }
            all_passed = all_passed and summary.get("status") == "passed"

    status = "generated" if mode == "generate-only" else ("passed" if all_passed else "failed")
    manifest = {
        "schema_version": SCHEMA_PIPELINE,
        "milestone": "M82.3",
        "mode": mode,
        "case_set": case_set,
        "status": status,
        "started_at": started_at,
        "finished_at": _utc_now(),
        "source_path": str(source_path),
        "out_dir": str(out_dir),
        "generation": generation,
        "execution": executions,
        "claims": {
            "testcases_generated": True,
            "runtime_execution_performed": mode == "generate-and-run",
            "raw_execution_evidence_collected": mode == "generate-and-run" and all_passed,
            "scoring_performed": False,
            "calibration_performed": False,
        },
    }
    _write_json(out_dir / "REAL_MODULE_PIPELINE_MANIFEST.json", manifest)
    return manifest
