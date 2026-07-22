"""M60 PathWalk benchmark-readiness matrix smoke.

This module performs a cheap, no-API compatibility run across the supported
M60 runtime_view modes. It is intentionally not a model-quality benchmark: it
uses a deterministic driver that submits the scenario ground truth through the
embedded runtime CLI, then scores the resulting runtime artifacts. Its purpose
is to prove that PathWalk can build packages, execute the current M60 protocol,
and produce score/SUMMARY artifacts before expensive model/API runs.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import asdict
from pathlib import Path
from typing import Any

from ..generator.maze_gen import generate_tree
from ..generator.emit_ordo_package import emit_package
from ..generator.noise_gen import generate_script, PathWalkScript
from .harness import _prepare_m60_runtime_sandbox
from .scorer import score_test_case
from .aggregate import aggregate, render_markdown

SUPPORTED_RUNTIME_VIEWS = ("json", "ordo-code", "json,ordo-code")


def _run_embedded(sandbox: Path, *args: str, timeout: int = 45) -> subprocess.CompletedProcess[str]:
    exe = sandbox / "cli_embedded" / "ordo"
    if not exe.exists():
        raise RuntimeError(f"embedded CLI missing: {exe}")
    if not args:
        raise ValueError("embedded command is required")
    command = [str(exe), args[0], str(sandbox), *args[1:]]
    # M60.5.4: enforce a hard process boundary for embedded CLI calls used by
    # benchmark workers. subprocess.run(timeout=...) only kills the direct
    # process; if the embedded launcher leaves child state behind, parent dry-run
    # jobs can appear to hang. A dedicated process group lets us terminate the
    # whole command tree deterministically.
    proc = subprocess.Popen(
        command,
        cwd=sandbox,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        return subprocess.CompletedProcess(command, proc.returncode, stdout, stderr)
    except subprocess.TimeoutExpired:
        import os, signal
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        stdout, stderr = proc.communicate()
        return subprocess.CompletedProcess(
            command,
            124,
            stdout or "",
            (stderr or "") + f"\n[ordo-pathwalk] embedded command timed out after {timeout}s\n",
        )


def _write_answer_file(sandbox: Path, step_index: int, answer: str) -> Path:
    answers_dir = sandbox / "runtime" / "pathwalk_answers"
    answers_dir.mkdir(parents=True, exist_ok=True)
    path = answers_dir / f"step_{step_index:03d}_answer.txt"
    path.write_text(str(answer), encoding="utf-8")
    return path


def _drive_ground_truth(sandbox: Path, script: PathWalkScript) -> dict[str, Any]:
    """Submit the final scenario ground truth through the embedded CLI.

    This smoke driver deliberately ignores conversational noise and does not try
    to impersonate a model. No transcript is emitted, because the goal is not to
    measure turn-level recovery. The resulting runtime artifacts are still real
    M60 artifacts and are scored by the normal scorer.
    """
    calls: list[dict[str, Any]] = []

    for idx, (node_id, answer) in enumerate(script.ground_truth):
        next_result = _run_embedded(sandbox, "next-step", "--format", "auto")
        calls.append({
            "step": idx,
            "command": "next-step --format auto",
            "returncode": next_result.returncode,
            "stdout_head": (next_result.stdout or "").splitlines()[:8],
        })
        if next_result.returncode != 0:
            raise RuntimeError("next-step failed:\n" + next_result.stdout + next_result.stderr)

        answer_file = _write_answer_file(sandbox, idx, answer)
        submit_result = _run_embedded(
            sandbox,
            "intake",
            "--submit",
            node_id,
            "--answer-file",
            str(answer_file),
        )
        calls.append({
            "step": idx,
            "command": f"intake --submit {node_id} --answer-file {answer_file.name}",
            "returncode": submit_result.returncode,
            "stdout_head": (submit_result.stdout or "").splitlines()[:12],
        })
        if submit_result.returncode != 0:
            raise RuntimeError("intake --submit failed:\n" + submit_result.stdout + submit_result.stderr)

    verify_targets = _run_embedded(sandbox, "verify-targets")
    calls.append({
        "command": "verify-targets",
        "returncode": verify_targets.returncode,
        "stdout_head": (verify_targets.stdout or "").splitlines()[:8],
    })
    if verify_targets.returncode != 0:
        raise RuntimeError("verify-targets failed:\n" + verify_targets.stdout + verify_targets.stderr)

    verify_session = _run_embedded(sandbox, "verify-session")
    calls.append({
        "command": "verify-session",
        "returncode": verify_session.returncode,
        "stdout_head": (verify_session.stdout or "").splitlines()[:8],
    })
    if verify_session.returncode != 0:
        raise RuntimeError("verify-session failed:\n" + verify_session.stdout + verify_session.stderr)

    return {"driver": "matrix-smoke-ground-truth", "calls": calls}


def run_matrix_smoke(
    out_dir: Path,
    *,
    depth: int = 3,
    branching: tuple[int, int] = (2, 3),
    tree_seed: int = 42,
    script_seed: int = 100,
    runtime_views: tuple[str, ...] = SUPPORTED_RUNTIME_VIEWS,
    force: bool = False,
) -> dict[str, Any]:
    out_dir = Path(out_dir)
    if out_dir.exists():
        if not force:
            raise FileExistsError(f"output directory exists: {out_dir}; pass force=True to replace it")
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    tree = generate_tree(seed=tree_seed, depth=depth, branching_range=branching)
    tree_dir = emit_package(tree, out_dir / "tree_source", "pathwalk.matrix_smoke", force=True)
    script = generate_script(tree, script_seed=script_seed, num_confusion_episodes=(1, 2))
    scenarios_dir = out_dir / "scenarios"
    scenarios_dir.mkdir(parents=True, exist_ok=True)
    scenario_path = scenarios_dir / "scenario_000.json"
    scenario_path.write_text(json.dumps(script.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    scores_dir = out_dir / "scores"
    scores_dir.mkdir(parents=True, exist_ok=True)
    transcripts_dir = out_dir / "transcripts"
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    sandboxes_dir = out_dir / "sandboxes"
    sandboxes_dir.mkdir(parents=True, exist_ok=True)

    matrix_rows: list[dict[str, Any]] = []
    for runtime_view in runtime_views:
        safe_view = runtime_view.replace(",", "_")
        sandbox = sandboxes_dir / f"scenario_000_{safe_view}"
        _prepare_m60_runtime_sandbox(tree_dir, sandbox, runtime_view)
        transcript = _drive_ground_truth(sandbox, script)
        transcript.update({
            "scenario_id": "scenario_000",
            "cli_mode": "enforced",
            "runtime_view": runtime_view,
            "turns": [],
        })
        transcript_path = transcripts_dir / f"scenario_000_{safe_view}_transcript.json"
        transcript_path.write_text(json.dumps(transcript, ensure_ascii=False, indent=2), encoding="utf-8")

        score = score_test_case(sandbox, script, transcript=[], rerun_verification=False)
        score.update({
            "scenario_id": "scenario_000",
            "driver": "matrix-smoke-ground-truth",
            "cli_mode": "enforced",
            "runtime_view": runtime_view,
        })
        score_path = scores_dir / f"scenario_000_{safe_view}_score.json"
        score_path.write_text(json.dumps(score, ensure_ascii=False, indent=2), encoding="utf-8")
        matrix_rows.append({
            "runtime_view": runtime_view,
            "sandbox": str(sandbox.relative_to(out_dir)),
            "score_file": str(score_path.relative_to(out_dir)),
            "gate_passed": score.get("gate_passed"),
            "path_quality_score": score.get("path_quality_score"),
            "protocol_compliance_rate": score.get("protocol_compliance_rate"),
            "runtime_metadata": score.get("runtime_metadata"),
        })

    summary = aggregate(scores_dir)
    summary["matrix_smoke"] = {
        "status": "passed" if all(r.get("gate_passed") for r in matrix_rows) else "failed",
        "runtime_views": list(runtime_views),
        "tree_seed": tree_seed,
        "script_seed": script_seed,
        "depth": depth,
        "branching": list(branching),
        "rows": matrix_rows,
    }
    (scores_dir / "SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (scores_dir / "SUMMARY.md").write_text(render_markdown(summary), encoding="utf-8")
    return summary
