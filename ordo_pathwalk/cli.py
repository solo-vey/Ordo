"""ordo-pathwalk: standalone benchmark CLI, deliberately NOT a subcommand of `ordo`.

Usage:
    python3 -m ordo_pathwalk.cli init-tree --depth 6 --branching 2 6 --seed 42 --out DIR
    python3 -m ordo_pathwalk.cli gen-scenarios --tree DIR --count 10 --seed 100 --out DIR
    python3 -m ordo_pathwalk.cli run --tree DIR --scenario SCRIPT.json --driver anthropic:claude-sonnet-5 --cli-mode enforced --runtime-view ordo-code --out DIR
    python3 -m ordo_pathwalk.cli score --tree DIR --scenario SCRIPT.json --sandbox SANDBOX_DIR --transcript TRANSCRIPT.json
    python3 -m ordo_pathwalk.cli self-feed-next --session DIR
    python3 -m ordo_pathwalk.cli self-submit --session DIR --turn-index N --response-file PATH [--asked-node ID]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .generator.maze_gen import generate_tree
from .generator.emit_ordo_package import emit_package
from .generator.noise_gen import generate_script, PathWalkScript
from .runner.harness import run_scenario
from .runner.scorer import score_test_case
from .runner import self_session
from .runner import aggregate as aggregate_mod
from .runner.model_benchmark import create_transcript_replay_pilot, collect_model_benchmark_results
from .runner.csg_benchmark import (
    build_dataset as build_csg_dataset,
    write_score as write_csg_score,
    write_cross_model_report as write_csg_cross_model_report,
)
from .runner.matrix_smoke import run_matrix_smoke
from .generator.real_module import write_real_module_graph_summary, write_real_module_terminal_paths, write_real_module_clean_path_cases, write_real_module_noise_cases, write_real_module_review_cards
from .runner.real_module_execution import create_real_module_execution_plan, run_real_module_execution_job, collect_real_module_execution_results
from .runner.real_module_pipeline import run_real_module_pipeline
from .runner.dry_run import (
    run_benchmark_dry_run,
    run_dry_run_case,
    create_dry_run_plan,
    run_dry_run_job,
    collect_dry_run_results,
)


def cmd_init_tree(args: argparse.Namespace) -> int:
    tree = generate_tree(seed=args.seed, depth=args.depth, branching_range=tuple(args.branching))
    out_dir = emit_package(tree, args.out, args.package_id, force=args.force)
    print(f"init-tree: created {out_dir} (depth={tree.depth}, seed={tree.seed}, start={tree.start})")
    return 0


def cmd_gen_scenarios(args: argparse.Namespace) -> int:
    tree_meta = json.loads((Path(args.tree) / "tree_meta.json").read_text(encoding="utf-8"))
    from .generator.maze_gen import MazeTree

    tree = MazeTree.from_dict(tree_meta)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    for i in range(args.count):
        script_seed = args.seed + i
        script = generate_script(tree, script_seed=script_seed, num_confusion_episodes=tuple(args.noise_density))
        path = out_dir / f"scenario_{i:03d}.json"
        path.write_text(json.dumps(script.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"gen-scenarios: wrote {path} ({len(script.turns)} turns, script_seed={script_seed})")
    return 0


def _load_script(path: Path) -> PathWalkScript:
    data = json.loads(path.read_text(encoding="utf-8"))
    from .generator.noise_gen import ScriptTurn

    turns = [ScriptTurn(**t) for t in data["turns"]]
    ground_truth = [(g["node_id"], g["value"]) for g in data["ground_truth"]]
    return PathWalkScript(tree_seed=data["tree_seed"], script_seed=data["script_seed"], turns=turns, ground_truth=ground_truth)


def cmd_run(args: argparse.Namespace) -> int:
    script = _load_script(Path(args.scenario))
    api_key_env = "ANTHROPIC_API_KEY" if args.driver.startswith("anthropic:") else "OPENAI_API_KEY"
    api_key = os.environ.get(api_key_env, "")
    if not api_key:
        print(f"run: missing {api_key_env} in environment; not calling any API.", file=sys.stderr)
        return 1
    sandbox_dir = run_scenario(
        tree_package_dir=Path(args.tree),
        script=script,
        driver_spec=args.driver,
        api_key=api_key,
        cli_mode=args.cli_mode,
        runtime_view=args.runtime_view,
        out_dir=Path(args.out),
        scenario_id=Path(args.scenario).stem,
        max_retries=args.max_retries,
    )
    print(f"run: completed, sandbox at {sandbox_dir}")
    return 0


def cmd_score(args: argparse.Namespace) -> int:
    script = _load_script(Path(args.scenario))
    transcript = None
    driver_tag = args.driver_tag
    cli_mode_tag = args.cli_mode_tag
    if args.transcript:
        data = json.loads(Path(args.transcript).read_text(encoding="utf-8"))
        transcript = data.get("turns")
        driver_tag = driver_tag or data.get("driver")
        cli_mode_tag = cli_mode_tag or data.get("cli_mode")
    weights = None
    if args.weights:
        weights = json.loads(Path(args.weights).read_text(encoding="utf-8"))
    result = score_test_case(Path(args.sandbox), script, transcript=transcript, weights=weights)
    if driver_tag:
        result["driver"] = driver_tag
    if cli_mode_tag:
        result["cli_mode"] = cli_mode_tag
    runtime_view_tag = args.runtime_view_tag
    if transcript and not runtime_view_tag:
        runtime_view_tag = data.get("runtime_view")
    if runtime_view_tag:
        result["runtime_view"] = runtime_view_tag
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.out:
        Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if result.get("gate_passed") else 1


def cmd_aggregate(args: argparse.Namespace) -> int:
    summary = aggregate_mod.aggregate(Path(args.scores_dir))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.out:
        out_path = Path(args.out)
        out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        if args.markdown:
            Path(args.markdown).write_text(aggregate_mod.render_markdown(summary), encoding="utf-8")
    return 0 if summary.get("status") == "ok" else 1





def cmd_real_module_pipeline(args: argparse.Namespace) -> int:
    result = run_real_module_pipeline(
        source_path=Path(args.source),
        out_dir=Path(args.out),
        mode=args.mode,
        case_set=args.case_set,
        noise_patterns=args.pattern,
        timeout_seconds=args.timeout,
        cleanup_policy=args.cleanup_policy,
        max_output_bytes=args.max_output_bytes,
        force=args.force,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") in {"generated", "passed"} else 1

def cmd_real_module_exec_plan(args: argparse.Namespace) -> int:
    plan = create_real_module_execution_plan(summary_path=Path(args.summary), source_path=Path(args.source), out_dir=Path(args.out), timeout_seconds=args.timeout, force=args.force)
    print(json.dumps({"status":"planned","jobs":len(plan.get("jobs",[])),"plan":str(Path(args.out)/"REAL_MODULE_EXECUTION_PLAN.json")}, ensure_ascii=False, indent=2))
    return 0

def cmd_real_module_exec_job(args: argparse.Namespace) -> int:
    result = run_real_module_execution_job(Path(args.plan), args.job_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "passed" else 1

def cmd_real_module_exec_collect(args: argparse.Namespace) -> int:
    result = collect_real_module_execution_results(Path(args.plan))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "passed" else 1

def cmd_matrix_smoke(args: argparse.Namespace) -> int:
    summary = run_matrix_smoke(
        Path(args.out),
        depth=args.depth,
        branching=tuple(args.branching),
        tree_seed=args.tree_seed,
        script_seed=args.script_seed,
        runtime_views=tuple(args.runtime_view or ["json", "ordo-code", "json,ordo-code"]),
        force=args.force,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if (summary.get("matrix_smoke") or {}).get("status") == "passed" else 1



def cmd_dry_run_plan(args: argparse.Namespace) -> int:
    plan = create_dry_run_plan(
        Path(args.out),
        scenario_count=args.scenario_count,
        depth=args.depth,
        branching=tuple(args.branching),
        tree_seed=args.tree_seed,
        script_seed=args.script_seed,
        runtime_views=tuple(args.runtime_view or ["json", "ordo-code", "json,ordo-code"]),
        force=args.force,
    )
    print(json.dumps({
        "status": "planned",
        "plan": str(Path(args.out) / "DRY_RUN_PLAN.json"),
        "expected_cases": plan.get("expected_cases"),
        "jobs": [job["job_id"] for job in plan.get("jobs", [])],
    }, ensure_ascii=False, indent=2))
    return 0


def cmd_dry_run_job(args: argparse.Namespace) -> int:
    result = run_dry_run_job(Path(args.plan), job_id=args.job_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.stdout.flush()
    sys.stderr.flush()
    # M60.5.4 hard boundary: dry-run jobs are artifact-only workers.
    # Once the score artifact and JSON result exist, do not wait for Python
    # interpreter shutdown hooks or lingering subprocess state. This command is
    # intentionally terminal for the worker process.
    os._exit(0 if result.get("status") == "passed" else 1)


def cmd_dry_run_collect(args: argparse.Namespace) -> int:
    summary = collect_dry_run_results(Path(args.plan))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if (summary.get("benchmark_dry_run") or {}).get("status") == "passed" else 1

def cmd_model_benchmark_pilot(args: argparse.Namespace) -> int:
    summary = create_transcript_replay_pilot(
        Path(args.out),
        scenario_count=args.scenario_count,
        depth=args.depth,
        branching=tuple(args.branching),
        tree_seed=args.tree_seed,
        script_seed=args.script_seed,
        runtime_views=tuple(args.runtime_view or ["json", "ordo-code", "json,ordo-code"]),
        force=args.force,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary.get("status") == "passed-pilot" else 1


def cmd_model_benchmark_collect(args: argparse.Namespace) -> int:
    summary = collect_model_benchmark_results(Path(args.plan))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary.get("status") == "passed-pilot" else 1




def cmd_csg_benchmark_build(args: argparse.Namespace) -> int:
    result = build_csg_dataset(Path(args.out))
    print(json.dumps({
        "status": "built",
        "dataset": str(args.out),
        "dataset_version": result.get("dataset_version"),
        "case_count": len(result.get("cases") or []),
        "dataset_sha256": result.get("dataset_sha256"),
    }, ensure_ascii=False, indent=2))
    return 0


def cmd_csg_benchmark_score(args: argparse.Namespace) -> int:
    result = write_csg_score(Path(args.dataset), Path(args.evidence), Path(args.out))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "passed" else 1


def cmd_csg_benchmark_aggregate(args: argparse.Namespace) -> int:
    result = write_csg_cross_model_report(Path(args.scores_dir), Path(args.out))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "passed" else 1


def cmd_real_module_graph(args: argparse.Namespace) -> int:
    result = write_real_module_graph_summary(Path(args.source), Path(args.out), force=args.force)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "passed" else 1


def cmd_real_module_paths(args: argparse.Namespace) -> int:
    result = write_real_module_terminal_paths(Path(args.summary), Path(args.out), force=args.force)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "passed" else 1

def cmd_real_module_clean_cases(args: argparse.Namespace) -> int:
    result = write_real_module_clean_path_cases(Path(args.paths), Path(args.out), force=args.force)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "passed" else 1



def cmd_real_module_noise_cases(args: argparse.Namespace) -> int:
    result = write_real_module_noise_cases(Path(args.paths), Path(args.out), patterns=args.pattern, force=args.force)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "passed" else 1


def cmd_real_module_review_cards(args: argparse.Namespace) -> int:
    result = write_real_module_review_cards([Path(path) for path in args.summary], Path(args.out), force=args.force)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "passed" else 1

def cmd_benchmark_dry_run(args: argparse.Namespace) -> int:
    summary = run_benchmark_dry_run(
        Path(args.out),
        scenario_count=args.scenario_count,
        depth=args.depth,
        branching=tuple(args.branching),
        tree_seed=args.tree_seed,
        script_seed=args.script_seed,
        runtime_views=tuple(args.runtime_view or ["json", "ordo-code", "json,ordo-code"]),
        force=args.force,
        case_timeout=args.case_timeout,
        stop_on_failure=args.stop_on_failure,
        worker_mode=args.worker_mode,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if (summary.get("benchmark_dry_run") or {}).get("status") == "passed" else 1


def cmd_dry_run_case(args: argparse.Namespace) -> int:
    result = run_dry_run_case(
        tree_dir=Path(args.tree),
        scenario_path=Path(args.scenario),
        runtime_view=args.runtime_view,
        out_dir=Path(args.out),
        scenario_id=args.scenario_id,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.stdout.flush()
    sys.stderr.flush()
    # Internal worker command: same hard-boundary behavior as dry-run-job.
    os._exit(0 if result.get("status") == "passed" else 1)

def cmd_self_feed_next(args: argparse.Namespace) -> int:
    result = self_session.feed_next_turn(Path(args.session))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") in ("ok", "no_more_turns") else 1


def cmd_self_submit(args: argparse.Namespace) -> int:
    response_text = Path(args.response_file).read_text(encoding="utf-8") if args.response_file else (args.response_text or "")
    result = self_session.submit_turn_response(Path(args.session), args.turn_index, response_text, args.asked_node)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "accepted" else 1


def cmd_self_init(args: argparse.Namespace) -> int:
    script = _load_script(Path(args.scenario))
    self_session.init_self_session(Path(args.session), script)
    print(f"self-init: session ready at {args.session}, {len(script.turns)} turns queued")
    return 0


def cmd_self_export_transcript(args: argparse.Namespace) -> int:
    merged = self_session.build_scoreable_transcript(Path(args.session))
    out = {"driver": "self", "cli_mode": args.cli_mode_tag, "turns": merged}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"self-export-transcript: wrote {args.out} ({len(merged)} turns)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ordo-pathwalk")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init-tree")
    p.add_argument("--depth", type=int, required=True)
    p.add_argument("--branching", type=int, nargs=2, default=[2, 6])
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--package-id", default="pathwalk.generated")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_init_tree)

    p = sub.add_parser("gen-scenarios")
    p.add_argument("--tree", required=True)
    p.add_argument("--count", type=int, required=True)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--noise-density", type=int, nargs=2, default=[1, 4])
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_gen_scenarios)

    p = sub.add_parser("run")
    p.add_argument("--tree", required=True)
    p.add_argument("--scenario", required=True)
    p.add_argument("--driver", required=True, help="e.g. anthropic:claude-sonnet-5 or openai:gpt-4.1")
    p.add_argument("--cli-mode", choices=["enforced", "ir_readable", "fully_freeform"], default="enforced")
    p.add_argument("--runtime-view", choices=["json", "ordo-code", "json,ordo-code"], default="ordo-code", help="M60 runtime_view for enforced mode")
    p.add_argument("--max-retries", type=int, default=4, help="API retry attempts for rate limits/timeouts")
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("score")
    p.add_argument("--scenario", required=True)
    p.add_argument("--sandbox", required=True)
    p.add_argument("--transcript")
    p.add_argument("--out")
    p.add_argument("--driver-tag", help="Override/record which driver produced this run (for aggregate breakdown)")
    p.add_argument("--cli-mode-tag", help="Override/record which cli_mode produced this run (for aggregate breakdown)")
    p.add_argument("--runtime-view-tag", help="Override/record which runtime_view produced this run")
    p.add_argument("--weights", help="JSON file overriding path_quality_score weights")
    p.set_defaults(func=cmd_score)

    p = sub.add_parser("aggregate")
    p.add_argument("--scores-dir", required=True, help="Directory containing *_score.json files")
    p.add_argument("--out", help="Write JSON summary to this path")
    p.add_argument("--markdown", help="Also write a human-readable Markdown summary to this path")
    p.set_defaults(func=cmd_aggregate)


    p = sub.add_parser("matrix-smoke")
    p.add_argument("--out", required=True, help="Output directory for generated tree, sandboxes, scores, and SUMMARY.json")
    p.add_argument("--depth", type=int, default=3)
    p.add_argument("--branching", type=int, nargs=2, default=[2, 3])
    p.add_argument("--tree-seed", type=int, default=42)
    p.add_argument("--script-seed", type=int, default=100)
    p.add_argument("--runtime-view", action="append", choices=["json", "ordo-code", "json,ordo-code"], default=None,
                   help="Runtime view to test; pass multiple times. Default tests all M60 views.")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_matrix_smoke)

    p = sub.add_parser("dry-run-plan", help="Create DRY_RUN_PLAN.json without executing jobs")
    p.add_argument("--out", required=True, help="Output directory for plan artifacts")
    p.add_argument("--scenario-count", type=int, default=20)
    p.add_argument("--depth", type=int, default=3)
    p.add_argument("--branching", type=int, nargs=2, default=[2, 3])
    p.add_argument("--tree-seed", type=int, default=42)
    p.add_argument("--script-seed", type=int, default=100)
    p.add_argument("--runtime-view", action="append", choices=["json", "ordo-code", "json,ordo-code"], help="May be passed multiple times; defaults to all M60 views")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_dry_run_plan)

    p = sub.add_parser("dry-run-job", help="Execute exactly one job from DRY_RUN_PLAN.json")
    p.add_argument("--plan", required=True)
    p.add_argument("--job-id", required=True)
    p.set_defaults(func=cmd_dry_run_job)

    p = sub.add_parser("dry-run-collect", help="Collect completed dry-run jobs into RAW_METRICS/SUMMARY")
    p.add_argument("--plan", required=True)
    p.set_defaults(func=cmd_dry_run_collect)


    p = sub.add_parser("model-benchmark-pilot", help="Create a no-API transcript-replay model benchmark pilot")
    p.add_argument("--out", required=True, help="Output directory for model benchmark pilot artifacts")
    p.add_argument("--scenario-count", type=int, default=3)
    p.add_argument("--depth", type=int, default=3)
    p.add_argument("--branching", type=int, nargs=2, default=[2, 3])
    p.add_argument("--tree-seed", type=int, default=6064)
    p.add_argument("--script-seed", type=int, default=606400)
    p.add_argument("--runtime-view", action="append", choices=["json", "ordo-code", "json,ordo-code"], help="May be passed multiple times; defaults to all M60 views")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_model_benchmark_pilot)

    p = sub.add_parser("model-benchmark-collect", help="Collect existing model benchmark pilot artifacts")
    p.add_argument("--plan", required=True)
    p.set_defaults(func=cmd_model_benchmark_collect)

    p = sub.add_parser("csg-benchmark-build", help="Build the canonical CSG model benchmark dataset")
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_csg_benchmark_build)

    p = sub.add_parser("csg-benchmark-score", help="Score CSG model evidence; synthetic evidence cannot pass")
    p.add_argument("--dataset", required=True)
    p.add_argument("--evidence", required=True)
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_csg_benchmark_score)

    p = sub.add_parser("csg-benchmark-aggregate", help="Aggregate repeated cross-model CSG benchmark score files")
    p.add_argument("--scores-dir", required=True)
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_csg_benchmark_aggregate)


    p = sub.add_parser("real-module-graph", help="M60.7.1/M60.7.2: load source/program.ordo.yaml and write REAL_MODULE_GRAPH_SUMMARY artifacts")
    p.add_argument("--source", required=True, help="Path to a real Ordo source/program.ordo.yaml")
    p.add_argument("--out", required=True, help="Output directory for REAL_MODULE_GRAPH_SUMMARY artifacts")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_real_module_graph)

    p = sub.add_parser("real-module-paths", help="M60.7.2: enumerate terminal paths from REAL_MODULE_GRAPH_SUMMARY.json")
    p.add_argument("--summary", required=True, help="Path to REAL_MODULE_GRAPH_SUMMARY.json")
    p.add_argument("--out", required=True, help="Output directory for REAL_MODULE_TERMINAL_PATHS artifacts")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_real_module_paths)

    p = sub.add_parser("real-module-clean-cases", help="M60.7.3: generate clean-path testcase artifacts from REAL_MODULE_TERMINAL_PATHS.json")
    p.add_argument("--paths", required=True, help="Path to REAL_MODULE_TERMINAL_PATHS.json")
    p.add_argument("--out", required=True, help="Output directory for clean-path testcase artifacts")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_real_module_clean_cases)


    p = sub.add_parser("real-module-noise-cases", help="M60.7.5: generate bounded noise testcase artifacts from REAL_MODULE_TERMINAL_PATHS.json")
    p.add_argument("--paths", required=True, help="Path to REAL_MODULE_TERMINAL_PATHS.json")
    p.add_argument("--out", required=True, help="Output directory for noise testcase artifacts")
    p.add_argument("--pattern", action="append", choices=["distraction", "invalid_branch", "clarification_without_submit", "skip_ahead"], help="Noise pattern to generate; pass multiple times. Defaults to distraction, invalid_branch, clarification_without_submit, and skip_ahead.")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_real_module_noise_cases)

    p = sub.add_parser("real-module-review-cards", help="M61.0: generate human review scenario cards from clean/noise testcase SUMMARY.json artifacts")
    p.add_argument("--summary", action="append", required=True, help="Path to a clean or noise testcase SUMMARY.json. Pass multiple times to combine packages.")
    p.add_argument("--out", required=True, help="Output directory for human review scenario card artifacts")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_real_module_review_cards)

    p = sub.add_parser("benchmark-dry-run")
    p.add_argument("--out", required=True, help="Output directory for dry-run artifacts")
    p.add_argument("--scenario-count", type=int, default=20)
    p.add_argument("--depth", type=int, default=3)
    p.add_argument("--branching", type=int, nargs=2, default=[2, 3])
    p.add_argument("--tree-seed", type=int, default=42)
    p.add_argument("--script-seed", type=int, default=100)
    p.add_argument("--runtime-view", action="append", choices=["json", "ordo-code", "json,ordo-code"], help="May be passed multiple times; defaults to all M60 views")
    p.add_argument("--case-timeout", type=int, default=180, help="Timeout per scenario/runtime_view subprocess")
    p.add_argument("--stop-on-failure", action="store_true")
    p.add_argument("--worker-mode", choices=["in-process", "subprocess"], default="subprocess")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_benchmark_dry_run)

    p = sub.add_parser("dry-run-case", help="Internal worker: run one scenario/runtime_view dry-run case")
    p.add_argument("--tree", required=True)
    p.add_argument("--scenario", required=True)
    p.add_argument("--runtime-view", choices=["json", "ordo-code", "json,ordo-code"], required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--scenario-id")
    p.set_defaults(func=cmd_dry_run_case)


    p = sub.add_parser("real-module-pipeline", help="M82.3: generate real-module testcases and optionally execute them through the hardened runner")
    p.add_argument("--source", required=True, help="Path to source/program.ordo.yaml")
    p.add_argument("--out", required=True, help="Output directory for generation and execution artifacts")
    p.add_argument("--mode", choices=["generate-only", "generate-and-run"], default="generate-only")
    p.add_argument("--case-set", choices=["clean", "noise", "both"], default="clean")
    p.add_argument("--pattern", action="append", choices=["distraction", "invalid_branch", "clarification_without_submit", "skip_ahead"], help="Noise pattern; may be repeated")
    p.add_argument("--timeout", type=int, default=30)
    p.add_argument("--cleanup-policy", choices=["retain_all", "retain_failures", "cleanup_all"], default="retain_failures")
    p.add_argument("--max-output-bytes", type=int, default=1000000)
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_real_module_pipeline)

    p = sub.add_parser("real-module-exec-plan", help="M82.1: create hardened isolated execution jobs for generated real-module cases")
    p.add_argument("--summary", required=True)
    p.add_argument("--source", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--timeout", type=int, default=30)
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_real_module_exec_plan)

    p = sub.add_parser("real-module-exec-job", help="M82.1 worker: execute exactly one generated real-module case")
    p.add_argument("--plan", required=True)
    p.add_argument("--job-id", required=True)
    p.set_defaults(func=cmd_real_module_exec_job)

    p = sub.add_parser("real-module-exec-collect", help="M82.1: collect raw execution evidence only")
    p.add_argument("--plan", required=True)
    p.set_defaults(func=cmd_real_module_exec_collect)

    p = sub.add_parser("self-init")
    p.add_argument("--scenario", required=True)
    p.add_argument("--session", required=True)
    p.set_defaults(func=cmd_self_init)

    p = sub.add_parser("self-export-transcript")
    p.add_argument("--session", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--cli-mode-tag", default="enforced")
    p.set_defaults(func=cmd_self_export_transcript)

    p = sub.add_parser("self-feed-next")
    p.add_argument("--session", required=True)
    p.set_defaults(func=cmd_self_feed_next)

    p = sub.add_parser("self-submit")
    p.add_argument("--session", required=True)
    p.add_argument("--turn-index", type=int, required=True)
    p.add_argument("--response-file")
    p.add_argument("--response-text")
    p.add_argument("--asked-node")
    p.set_defaults(func=cmd_self_submit)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
