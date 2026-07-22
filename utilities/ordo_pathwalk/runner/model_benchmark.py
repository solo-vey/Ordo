"""M60.6.4 transcript-replay model benchmark pilot utilities.

This module is intentionally no-API.  It exercises the M60.6.3 model benchmark
artifact contract by creating a small transcript-replay pilot that contains both
perfect and non-perfect transcript evidence.  The goal is protocol validation,
not scorer calibration.
"""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..generator.maze_gen import generate_tree
from ..generator.emit_ordo_package import emit_package
from ..generator.noise_gen import generate_script, PathWalkScript, ScriptTurn
from .harness import _prepare_m60_runtime_sandbox
from .matrix_smoke import _drive_ground_truth, SUPPORTED_RUNTIME_VIEWS
from .scorer import score_test_case

PROTOCOL_VERSION = "M60.6.4"
TRANSCRIPT_SCHEMA_VERSION = "pathwalk.model_transcript.v1"
BENCHMARK_MODE = "transcript-replay"
PROVIDER = "offline"
MODEL_NAME = "synthetic-transcript-pilot"
DRIVER = "transcript-replay-pilot"
WEIGHTS = {
    "cell_match_rate": 0.45,
    "protocol_compliance_rate": 0.25,
    "distraction_recovery_rate": 0.15,
    "backtrack_accuracy": 0.15,
}
RAW_MODEL_METRICS_FIELDS = [
    "job_id",
    "scenario_id",
    "runtime_view",
    "cli_mode",
    "benchmark_mode",
    "provider",
    "model",
    "driver",
    "seed",
    "status",
    "path_quality_score",
    "cell_match_rate",
    "protocol_compliance_rate",
    "distraction_recovery_rate",
    "backtrack_accuracy",
    "turn_accuracy_rate",
    "invalid_branch_rejection_rate",
    "skip_ahead_resistance_rate",
    "clarification_handling_rate",
    "correction_recovery_rate",
    "restore_session_usage_rate",
    "direct_compiled_access_violations",
    "tool_call_count",
    "turn_count",
    "completion_latency_ms",
    "error_type",
    "failure_bucket",
    "score_schema_version",
    "weights_hash",
    "canonical_ir_hash",
    "targets_manifest_hash",
    "session_trace_hash",
    "transcript_sha256",
]


def _safe_runtime_view(runtime_view: str) -> str:
    return runtime_view.replace(",", "_").replace("/", "_")


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _weights_hash() -> str:
    payload = json.dumps(WEIGHTS, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _sha256_bytes(payload)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _script_to_dict(script: PathWalkScript) -> dict[str, Any]:
    return script.to_dict()


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


def _behavior_for_scenario(index: int) -> str:
    # Keep the pilot deterministic and intentionally mixed:
    # scenario_000: perfect; scenario_001: model-quality failure;
    # scenario_002+: hard protocol violation. This yields nonzero variance while
    # still being small enough for a no-API acceptance pilot.
    if index == 0:
        return "perfect"
    if index == 1:
        return "distraction_failure"
    return "protocol_violation"


def _representative_expected_node(script: PathWalkScript) -> str:
    if script.turns:
        return script.turns[0].expected_node_after
    if script.ground_truth:
        return script.ground_truth[0][0]
    return "END"


def _build_model_transcript(
    *,
    job_id: str,
    scenario_id: str,
    runtime_view: str,
    script: PathWalkScript,
    behavior: str,
) -> dict[str, Any]:
    expected = _representative_expected_node(script)
    wrong_node = f"WRONG_NODE_FOR_{scenario_id}"
    common_call = {
        "command": "./cli_embedded/ordo next-step . --format auto",
        "exit_code": 0,
        "stdout_sha256": "sha256:" + ("0" * 64),
        "stderr_sha256": "sha256:" + ("0" * 64),
        "output_truncated": True,
    }
    if behavior == "protocol_violation":
        tool_calls = [
            common_call,
            {
                "command": "cat compiled/program.ir.json",
                "exit_code": 0,
                "stdout_sha256": "sha256:" + ("1" * 64),
                "stderr_sha256": "sha256:" + ("0" * 64),
                "output_truncated": True,
            },
        ]
        asked_node = expected
        turn_type = "forward_valid"
        response = "I incorrectly inspected compiled/program.ir.json before using the runtime path."
    elif behavior == "distraction_failure":
        tool_calls = [common_call]
        asked_node = wrong_node
        turn_type = "clarifying_question"
        response = "I followed the distraction and answered as if the current node had changed."
    else:
        tool_calls = [common_call]
        asked_node = expected
        turn_type = "forward_valid"
        response = "I used the runtime prompt and submitted the expected answer."

    started = _now()
    completed = _now()
    return {
        "schema_version": TRANSCRIPT_SCHEMA_VERSION,
        "benchmark_protocol_version": PROTOCOL_VERSION,
        "job_id": job_id,
        "scenario_id": scenario_id,
        "runtime_view": runtime_view,
        "cli_mode": "enforced",
        "benchmark_mode": BENCHMARK_MODE,
        "model": {
            "provider": PROVIDER,
            "name": MODEL_NAME,
            "driver": DRIVER,
        },
        "started_at": started,
        "completed_at": completed,
        "result_status": "completed",
        "pilot_behavior": behavior,
        "turns": [
            {
                "turn_index": 1,
                "turn_type": turn_type,
                "user_prompt": script.turns[0].text if script.turns else "start",
                "model_response": response,
                "expected_node_after": expected,
                "asked_node_id": asked_node,
                "tool_calls": tool_calls,
            }
        ],
        "redaction": {
            "api_keys_removed": True,
            "secrets_removed": True,
        },
    }


def scoreable_turns_from_model_transcript(transcript: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert the M60.6.3+ transcript schema into scorer turn evidence."""
    scoreable: list[dict[str, Any]] = []
    for turn in transcript.get("turns") or []:
        scoreable.append({
            "turn_type": turn.get("turn_type") or "forward_valid",
            "asked_node_id": turn.get("asked_node_id"),
            "expected_node_after": turn.get("expected_node_after"),
            "tool_calls_made": [
                {
                    "command": call.get("command"),
                    "returncode": call.get("exit_code"),
                }
                for call in (turn.get("tool_calls") or [])
            ],
        })
    return scoreable


def _metric_value(score: dict[str, Any], key: str, default: float = 1.0) -> float:
    value = score.get(key)
    return default if value is None else float(value)


def _failure_bucket(score: dict[str, Any], transcript: dict[str, Any]) -> str:
    if score.get("protocol_violation_direct_compiled_read"):
        return "protocol_violation"
    if _metric_value(score, "distraction_recovery_rate") < 1.0:
        return "distraction_followed"
    if _metric_value(score, "backtrack_accuracy") < 1.0:
        return "missed_backtrack"
    if _metric_value(score, "path_quality_score", default=0.0) < 1.0:
        return "model_quality_nonperfect"
    return "none"


def _status_from_score(score: dict[str, Any], bucket: str) -> str:
    if not score.get("gate_passed"):
        return "failed"
    if bucket == "none":
        return "passed"
    return "non_perfect"


def _tool_call_count(transcript: dict[str, Any]) -> int:
    return sum(len(turn.get("tool_calls") or []) for turn in transcript.get("turns") or [])


def _write_raw_model_metrics(rows: list[dict[str, Any]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RAW_MODEL_METRICS_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _read_raw_model_metrics(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _float_values(rows: list[dict[str, str]], field: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        value = row.get(field)
        if value not in (None, ""):
            values.append(float(value))
    return values


def _variance(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return sum((v - mean) ** 2 for v in values) / len(values)


def _calibration_gates(rows: list[dict[str, str]], scenario_count: int, runtime_views: tuple[str, ...]) -> dict[str, dict[str, Any]]:
    by_view: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        by_view[row.get("runtime_view") or ""].add(row.get("scenario_id") or "")
    expected_scenarios = {f"scenario_{i:03d}" for i in range(scenario_count)}
    same_matrix = all(by_view.get(view) == expected_scenarios for view in runtime_views)

    score_values = _float_values(rows, "path_quality_score")
    component_fields = [
        "cell_match_rate",
        "protocol_compliance_rate",
        "distraction_recovery_rate",
        "backtrack_accuracy",
        "turn_accuracy_rate",
    ]
    nonzero_variance = any(_variance(_float_values(rows, field)) > 0 for field in component_fields)
    buckets = Counter(row.get("failure_bucket") or "none" for row in rows)
    metadata_complete = all(
        row.get("canonical_ir_hash") and row.get("targets_manifest_hash") and row.get("session_trace_hash") and row.get("transcript_sha256")
        for row in rows
    )
    return {
        "same_scenario_matrix": {"passed": same_matrix, "detail": "same scenario IDs are present for each runtime view"},
        "sufficient_cases": {"passed": scenario_count >= 30, "detail": f"pilot has {scenario_count} cases per runtime view; protocol requires >=30 for calibration"},
        "nonzero_variance": {"passed": nonzero_variance, "detail": "pilot includes perfect and non-perfect transcript evidence"},
        "non_saturated_scores": {"passed": any(v < 1.0 for v in score_values), "detail": "not all path_quality_score values are 1.0"},
        "failure_buckets_present": {"passed": any(bucket != "none" for bucket in buckets), "detail": dict(buckets)},
        "protocol_vs_quality_separated": {"passed": bool(buckets.get("protocol_violation")) and bool(buckets.get("distraction_followed")), "detail": dict(buckets)},
        "metadata_hashes_captured": {"passed": metadata_complete, "detail": "IR, targets manifest, session trace, transcript hashes checked"},
        "repeatability_checked": {"passed": False, "detail": "not checked in M60.6.4 pilot"},
        "confidence_summary_present": {"passed": False, "detail": "pilot reports descriptive statistics only"},
        "manual_failure_review_done": {"passed": False, "detail": "synthetic pilot failures were not manually reviewed as real model failures"},
        "calibration_decision_recorded": {"passed": True, "detail": "CALIBRATION_DECISION.md/.json generated"},
    }


def collect_model_benchmark_results(plan_path: Path) -> dict[str, Any]:
    plan_path = Path(plan_path)
    out_dir = plan_path.parent
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    rows = _read_raw_model_metrics(out_dir / "RAW_MODEL_METRICS.csv")
    scenario_count = int(plan.get("scenario_count") or 0)
    runtime_views = tuple(plan.get("runtime_views") or [])
    gates = _calibration_gates(rows, scenario_count, runtime_views)
    calibration_eligible = all(gate.get("passed") for gate in gates.values())

    by_runtime_view: dict[str, dict[str, Any]] = {}
    for view in runtime_views:
        view_rows = [r for r in rows if r.get("runtime_view") == view]
        scores = _float_values(view_rows, "path_quality_score")
        by_runtime_view[view] = {
            "cases": len(view_rows),
            "passed": sum(1 for r in view_rows if r.get("status") == "passed"),
            "non_perfect": sum(1 for r in view_rows if r.get("status") == "non_perfect"),
            "score_min": min(scores) if scores else None,
            "score_max": max(scores) if scores else None,
            "score_mean": round(sum(scores) / len(scores), 4) if scores else None,
        }

    bucket_counts = Counter(row.get("failure_bucket") or "none" for row in rows)
    reports_dir = out_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    with (reports_dir / "failure_bucket_summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["failure_bucket", "count"])
        writer.writeheader()
        for bucket, count in sorted(bucket_counts.items()):
            writer.writerow({"failure_bucket": bucket, "count": count})

    summary = {
        "schema_version": "ordo.pathwalk.model_benchmark_summary.v1",
        "milestone": PROTOCOL_VERSION,
        "benchmark_mode": BENCHMARK_MODE,
        "status": "passed-pilot" if rows else "failed",
        "weights_locked": True,
        "calibration_eligible": calibration_eligible,
        "expected_cases": int(plan.get("expected_cases") or 0),
        "completed_cases": len(rows),
        "runtime_views": by_runtime_view,
        "failure_buckets": dict(bucket_counts),
        "calibration_gates": gates,
        "raw_model_metrics_csv": "RAW_MODEL_METRICS.csv",
        "calibration_decision": "CALIBRATION_DECISION.md",
    }
    (out_dir / "SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "SUMMARY.md").write_text(render_model_benchmark_markdown(summary), encoding="utf-8")
    _write_calibration_decision(out_dir, summary)
    _write_model_run_manifest(out_dir, plan, summary)
    return summary


def _write_calibration_decision(out_dir: Path, summary: dict[str, Any]) -> None:
    decision = {
        "schema_version": "ordo.pathwalk.calibration_decision.v1",
        "milestone": PROTOCOL_VERSION,
        "decision": "keep_weights_locked",
        "weights_changed": False,
        "calibration_eligible": summary.get("calibration_eligible"),
        "reason": "M60.6.4 is a small transcript-replay pilot; sufficient_cases, repeatability, confidence summary, and manual failure review gates are not satisfied.",
        "current_weights": WEIGHTS,
        "weights_hash": _weights_hash(),
    }
    (out_dir / "CALIBRATION_DECISION.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "CALIBRATION_DECISION.md").write_text(
        "\n".join([
            "# M60.6.4 Calibration Decision",
            "",
            "Decision: `keep_weights_locked`.",
            "",
            "No scorer weights changed in M60.6.4.",
            "",
            "Reason: this milestone is a transcript-replay protocol pilot, not a statistically sufficient calibration run. The pilot intentionally includes non-perfect evidence to prove the artifact contract and failure buckets, but it fails the calibration eligibility gates for sufficient cases, repeatability, confidence summary, and manual failure review.",
            "",
            f"Weights hash: `{_weights_hash()}`",
            "",
        ]),
        encoding="utf-8",
    )


def _write_model_run_manifest(out_dir: Path, plan: dict[str, Any], summary: dict[str, Any]) -> None:
    artifact_names = [
        "MODEL_BENCHMARK_PLAN.json",
        "RAW_MODEL_METRICS.csv",
        "SUMMARY.json",
        "SUMMARY.md",
        "MODEL_RUN_MANIFEST.json",
        "CALIBRATION_DECISION.md",
        "CALIBRATION_DECISION.json",
    ]
    artifacts = {}
    for name in artifact_names:
        path = out_dir / name
        if path.exists() and name != "MODEL_RUN_MANIFEST.json":
            artifacts[name] = _sha256_file(path)
    transcript_hashes = {
        str(path.relative_to(out_dir)): _sha256_file(path)
        for path in sorted((out_dir / "transcripts").glob("*_transcript.json"))
    }
    score_hashes = {
        str(path.relative_to(out_dir)): _sha256_file(path)
        for path in sorted((out_dir / "scores").glob("*_score.json"))
    }
    manifest = {
        "schema_version": "ordo.pathwalk.model_run_manifest.v1",
        "milestone": PROTOCOL_VERSION,
        "benchmark_mode": BENCHMARK_MODE,
        "created_at": _now(),
        "plan_hash": artifacts.get("MODEL_BENCHMARK_PLAN.json"),
        "weights_hash": _weights_hash(),
        "weights_locked": True,
        "expected_cases": plan.get("expected_cases"),
        "completed_cases": summary.get("completed_cases"),
        "calibration_eligible": summary.get("calibration_eligible"),
        "artifact_hashes": artifacts,
        "transcript_hashes": transcript_hashes,
        "score_hashes": score_hashes,
    }
    manifest_path = out_dir / "MODEL_RUN_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def render_model_benchmark_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# M60.6.4 Transcript Replay Model Benchmark Pilot Summary",
        "",
        f"Status: `{summary.get('status')}`",
        f"Benchmark mode: `{summary.get('benchmark_mode')}`",
        f"Completed cases: `{summary.get('completed_cases')}/{summary.get('expected_cases')}`",
        f"Weights locked: `{summary.get('weights_locked')}`",
        f"Calibration eligible: `{summary.get('calibration_eligible')}`",
        "",
        "## Runtime view matrix",
        "",
        "| runtime_view | cases | passed | non_perfect | score_min | score_mean | score_max |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for view, row in (summary.get("runtime_views") or {}).items():
        lines.append(
            f"| `{view}` | {row.get('cases')} | {row.get('passed')} | {row.get('non_perfect')} | {row.get('score_min')} | {row.get('score_mean')} | {row.get('score_max')} |"
        )
    lines.extend(["", "## Failure buckets", ""])
    for bucket, count in sorted((summary.get("failure_buckets") or {}).items()):
        lines.append(f"- `{bucket}`: {count}")
    lines.extend(["", "## Calibration eligibility gates", ""])
    for gate, result in (summary.get("calibration_gates") or {}).items():
        marker = "passed" if result.get("passed") else "failed"
        lines.append(f"- `{gate}`: {marker} — {result.get('detail')}")
    lines.extend([
        "",
        "## Decision",
        "",
        "Weights remain locked. This pilot validates the transcript-replay artifact contract and failure buckets only.",
        "",
    ])
    return "\n".join(lines)


def create_transcript_replay_pilot(
    out_dir: Path,
    *,
    scenario_count: int = 3,
    depth: int = 3,
    branching: tuple[int, int] = (2, 3),
    tree_seed: int = 6064,
    script_seed: int = 606400,
    runtime_views: tuple[str, ...] = SUPPORTED_RUNTIME_VIEWS,
    force: bool = False,
) -> dict[str, Any]:
    """Create and execute a small no-API transcript-replay pilot."""
    if scenario_count < 3:
        raise ValueError("scenario_count must be >= 3 so the pilot includes perfect, quality-failure, and protocol-violation evidence")
    unknown_views = [view for view in runtime_views if view not in SUPPORTED_RUNTIME_VIEWS]
    if unknown_views:
        raise ValueError(f"unsupported runtime_view values: {unknown_views}")

    out_dir = Path(out_dir)
    if out_dir.exists():
        if not force:
            raise FileExistsError(f"output directory exists: {out_dir}; pass force=True to replace it")
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    tree = generate_tree(seed=tree_seed, depth=depth, branching_range=branching)
    tree_dir = emit_package(tree, out_dir / "tree_source", "pathwalk.model_benchmark_pilot", force=True)

    scenarios_dir = out_dir / "scenarios"
    runtime_templates_dir = out_dir / "runtime_templates"
    jobs_dir = out_dir / "jobs"
    transcripts_dir = out_dir / "transcripts"
    sandboxes_dir = out_dir / "sandboxes"
    scores_dir = out_dir / "scores"
    for directory in (scenarios_dir, runtime_templates_dir, jobs_dir, transcripts_dir, sandboxes_dir, scores_dir):
        directory.mkdir(parents=True, exist_ok=True)

    scenario_paths: list[Path] = []
    for index in range(scenario_count):
        script = generate_script(tree, script_seed=script_seed + index, num_confusion_episodes=(1, 3))
        scenario_path = scenarios_dir / f"scenario_{index:03d}.json"
        scenario_path.write_text(json.dumps(_script_to_dict(script), ensure_ascii=False, indent=2), encoding="utf-8")
        scenario_paths.append(scenario_path)

    runtime_templates: dict[str, Path] = {}
    for runtime_view in runtime_views:
        safe_view = _safe_runtime_view(runtime_view)
        template_dir = runtime_templates_dir / safe_view
        _prepare_m60_runtime_sandbox(tree_dir, template_dir, runtime_view)
        runtime_templates[runtime_view] = template_dir

    jobs: list[dict[str, Any]] = []
    raw_rows: list[dict[str, Any]] = []
    for scenario_path in scenario_paths:
        scenario_index = int(scenario_path.stem.split("_")[-1])
        scenario_id = scenario_path.stem
        behavior = _behavior_for_scenario(scenario_index)
        script = _load_script(scenario_path)
        for runtime_view in runtime_views:
            safe_view = _safe_runtime_view(runtime_view)
            job_id = f"{scenario_id}_{safe_view}_{BENCHMARK_MODE}"
            sandbox = sandboxes_dir / f"{scenario_id}_{safe_view}"
            _prepare_m60_runtime_sandbox(runtime_templates[runtime_view], sandbox, runtime_view)
            _drive_ground_truth(sandbox, script)

            transcript = _build_model_transcript(
                job_id=job_id,
                scenario_id=scenario_id,
                runtime_view=runtime_view,
                script=script,
                behavior=behavior,
            )
            transcript_path = transcripts_dir / f"{job_id}_transcript.json"
            transcript_path.write_text(json.dumps(transcript, ensure_ascii=False, indent=2), encoding="utf-8")
            transcript_sha = _sha256_file(transcript_path)
            scoreable = scoreable_turns_from_model_transcript(transcript)
            score = score_test_case(sandbox, script, transcript=scoreable, weights=WEIGHTS, rerun_verification=False)
            bucket = _failure_bucket(score, transcript)
            status = _status_from_score(score, bucket)
            metadata = score.get("runtime_metadata") or {}
            score.update({
                "schema_version": "ordo.pathwalk.model_score.v1",
                "milestone": PROTOCOL_VERSION,
                "job_id": job_id,
                "scenario_id": scenario_id,
                "runtime_view": runtime_view,
                "cli_mode": "enforced",
                "benchmark_mode": BENCHMARK_MODE,
                "provider": PROVIDER,
                "model": MODEL_NAME,
                "driver": DRIVER,
                "status": status,
                "failure_bucket": bucket,
                "transcript_sha256": transcript_sha,
                "weights_hash": _weights_hash(),
            })
            score_path = scores_dir / f"{job_id}_score.json"
            score_path.write_text(json.dumps(score, ensure_ascii=False, indent=2), encoding="utf-8")

            job_doc = {
                "schema_version": "ordo.pathwalk.model_benchmark_job.v1",
                "job_id": job_id,
                "scenario_id": scenario_id,
                "runtime_view": runtime_view,
                "cli_mode": "enforced",
                "benchmark_mode": BENCHMARK_MODE,
                "provider": PROVIDER,
                "model": MODEL_NAME,
                "driver": DRIVER,
                "pilot_behavior": behavior,
                "scenario_path": str(scenario_path.relative_to(out_dir)),
                "sandbox": str(sandbox.relative_to(out_dir)),
                "transcript_file": str(transcript_path.relative_to(out_dir)),
                "score_file": str(score_path.relative_to(out_dir)),
            }
            (jobs_dir / f"{job_id}.json").write_text(json.dumps(job_doc, ensure_ascii=False, indent=2), encoding="utf-8")
            jobs.append(job_doc)

            raw_rows.append({
                "job_id": job_id,
                "scenario_id": scenario_id,
                "runtime_view": runtime_view,
                "cli_mode": "enforced",
                "benchmark_mode": BENCHMARK_MODE,
                "provider": PROVIDER,
                "model": MODEL_NAME,
                "driver": DRIVER,
                "seed": script_seed + scenario_index,
                "status": status,
                "path_quality_score": score.get("path_quality_score"),
                "cell_match_rate": score.get("cell_match_rate"),
                "protocol_compliance_rate": score.get("protocol_compliance_rate"),
                "distraction_recovery_rate": score.get("distraction_recovery_rate"),
                "backtrack_accuracy": score.get("backtrack_accuracy"),
                "turn_accuracy_rate": score.get("turn_accuracy_rate"),
                "invalid_branch_rejection_rate": "",
                "skip_ahead_resistance_rate": "",
                "clarification_handling_rate": score.get("distraction_recovery_rate"),
                "correction_recovery_rate": "",
                "restore_session_usage_rate": 0.0,
                "direct_compiled_access_violations": 1 if score.get("protocol_violation_direct_compiled_read") else 0,
                "tool_call_count": _tool_call_count(transcript),
                "turn_count": len(transcript.get("turns") or []),
                "completion_latency_ms": 0,
                "error_type": "" if status != "failed" else bucket,
                "failure_bucket": bucket,
                "score_schema_version": "ordo.pathwalk.model_score.v1",
                "weights_hash": _weights_hash(),
                "canonical_ir_hash": metadata.get("canonical_ir_hash"),
                "targets_manifest_hash": metadata.get("targets_manifest_hash"),
                "session_trace_hash": metadata.get("session_trace_hash"),
                "transcript_sha256": transcript_sha,
            })

    plan = {
        "schema_version": "ordo.pathwalk.model_benchmark_plan.v1",
        "benchmark_protocol_version": PROTOCOL_VERSION,
        "benchmark_mode": BENCHMARK_MODE,
        "scenario_set_id": f"m60_6_4_transcript_replay_pilot_tree_{tree_seed}_script_{script_seed}",
        "scenario_count": scenario_count,
        "runtime_views": list(runtime_views),
        "cli_mode": "enforced",
        "models": [
            {
                "provider": PROVIDER,
                "model": MODEL_NAME,
                "driver": DRIVER,
                "temperature": 0,
            }
        ],
        "seed_policy": "fixed-and-recorded",
        "artifact_only_execution": True,
        "weights_locked": True,
        "expected_cases": len(jobs),
        "tree_seed": tree_seed,
        "script_seed_start": script_seed,
        "depth": depth,
        "branching": list(branching),
        "tree_source": "tree_source",
        "jobs": jobs,
    }
    (out_dir / "MODEL_BENCHMARK_PLAN.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_raw_model_metrics(raw_rows, out_dir / "RAW_MODEL_METRICS.csv")
    return collect_model_benchmark_results(out_dir / "MODEL_BENCHMARK_PLAN.json")
