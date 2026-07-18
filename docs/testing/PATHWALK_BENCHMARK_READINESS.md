# M60.5 PathWalk Benchmark Readiness

Status: companion testing layer, not Ordo runtime core.

M60.5 defines the minimum readiness bar before using `ordo_pathwalk` for real model/API benchmark runs against current Ordo M60 runtime packages.

## Scope

M60.5 does not change the Ordo runtime contract. It verifies that PathWalk can consume the current runtime package format and produce comparable benchmark artifacts.

Required runtime features consumed by PathWalk:

- embedded CLI launcher: `./cli_embedded/ordo`
- runtime views: `json`, `ordo-code`, `json,ordo-code`
- `verify-targets`
- `next-step --format auto`
- `intake --submit --answer-file`
- append-only `restore-session`
- `verify-session`
- `runtime/session.ordo.trace`
- `runtime/evidence/*_evidence.json`
- `compiled/targets.manifest.json`

## Readiness gates

A PathWalk release is benchmark-ready when:

1. It refuses legacy `python3 cli_embedded/ordo_run.py` as an enforced runtime launcher.
2. It can build or consume an M60.4+ runtime package through the current Ordo CLI.
3. It can execute a no-API matrix smoke across:
   - enforced + `json`
   - enforced + `ordo-code`
   - enforced + `json,ordo-code`
4. It can generate individual `*_score.json` files for each runtime view.
5. It can generate an aggregate `SUMMARY.json` and `SUMMARY.md`.
6. Each score includes runtime metadata:
   - `ordo_cli_version`
   - `runtime_protocol_version`
   - `runtime_view`
   - `canonical_ir_hash`
   - `targets_manifest_hash`
   - `session_trace_hash`
7. Direct `compiled/*` access in enforced mode is scored as a hard protocol violation.
8. `verify-targets` and `verify-session` must pass for `protocol_compliance_rate=1.0`.

## Matrix smoke command

Use this before expensive API/model runs:

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli matrix-smoke \
  --out /tmp/pathwalk_matrix_smoke \
  --depth 2 \
  --branching 2 2 \
  --force
```

The command creates:

```text
/tmp/pathwalk_matrix_smoke/
  tree_source/
  scenarios/scenario_000.json
  sandboxes/
  transcripts/
  scores/
    scenario_000_json_score.json
    scenario_000_ordo-code_score.json
    scenario_000_json_ordo-code_score.json
    SUMMARY.json
    SUMMARY.md
```

This smoke is not a model-quality benchmark. It uses a deterministic ground-truth driver to prove that package building, embedded runtime execution, scoring, and aggregation are wired correctly.

## What this does not prove

M60.5 matrix smoke does not measure:

- actual model reasoning quality
- prompt robustness against noisy human text
- API driver reliability under real provider rate limits
- calibrated scoring weights

Those require a later benchmark run with model drivers and documented weight policy.

## Recommended next gate for external utilities

External scenario-testing utilities must treat M60.5 as the compatibility baseline. A utility that still requires `ordo_run.py`, ignores `runtime_view`, skips `verify-targets`, or does not read `session.ordo.trace` is not M60-compatible.

## M60.5.1 benchmark dry-run blocker fix

M60.5 introduced `matrix-smoke`, which proves that one generated scenario can be executed across the runtime-view matrix. M60.5.1 adds the next readiness layer: a no-API `benchmark-dry-run` that can execute multiple generated scenarios and collect raw component metrics before any expensive model/API benchmark.

Command:

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli benchmark-dry-run \
  --out /tmp/pathwalk_dry_run \
  --scenario-count 20 \
  --runtime-view json \
  --runtime-view ordo-code \
  --runtime-view json,ordo-code \
  --depth 3 \
  --branching 2 3 \
  --force
```

The command writes:

```text
pathwalk_dry_run/
  tree_source/
  runtime_templates/
  scenarios/
  sandboxes/
  transcripts/
  scores/
  case_logs/
  RAW_METRICS.csv
  SUMMARY.json
  SUMMARY.md
```

M60.5.1 deliberately does **not** calibrate `path_quality_score` weights. It only collects raw metrics:

- `cell_match_rate`
- `protocol_compliance_rate`
- `distraction_recovery_rate`
- `backtrack_accuracy`
- `turn_accuracy_rate`
- runtime metadata and hashes

The blocker fixed in M60.5.1 was multi-scenario dry-run instability. The fix has three parts:

1. build one clean runtime template per `runtime_view`;
2. copy that template into a fresh sandbox for every scenario/case;
3. score from the verification reports produced by the runtime pass instead of re-running embedded verification commands during scoring.

For constrained environments, `benchmark-dry-run` supports `--worker-mode subprocess` and `--worker-mode in-process`. The default is subprocess mode with score-file completion detection; tests also cover in-process orchestration. External CI may choose either mode, but each case must still use a fresh sandbox.


## M60.5.2b external-job dry-run contract

M60.5.2b replaces the recommended multi-case dry-run orchestration with an explicit external-job contract:

1. `dry-run-plan` creates `DRY_RUN_PLAN.json`, generated scenarios, and runtime templates.
2. `dry-run-job --job-id <id>` executes exactly one scenario/runtime_view case.
3. `dry-run-collect` aggregates completed jobs into `RAW_METRICS.csv`, `SUMMARY.json`, and `SUMMARY.md`.

This contract is preferred for CI and long benchmark runs because each job can run in its own shell/process/container. A failed or timed-out job does not hold a long-lived benchmark parent process hostage.

`benchmark-dry-run` remains a convenience command, but acceptance evidence for benchmark readiness should use the plan/job/collect flow.

## M60.5.4 artifact-only dry-run executor

M60.5.4 tightens the external-job contract into an artifact-only executor model.
The benchmark plan is now the primary coordination artifact, not a long-lived
Python parent loop.

`dry-run-plan` writes:

```text
DRY_RUN_PLAN.json
JOB_EXECUTION.md
jobs/<job_id>.json
job_scripts/<job_id>.sh
```

Recommended execution:

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli dry-run-plan \
  --out runs/pathwalk_dry_run \
  --scenario-count 20 \
  --runtime-view json \
  --runtime-view ordo-code \
  --runtime-view json,ordo-code \
  --force

# Run each job independently, for example as a CI matrix job:
bash runs/pathwalk_dry_run/job_scripts/scenario_000_json.sh
bash runs/pathwalk_dry_run/job_scripts/scenario_000_ordo-code.sh
bash runs/pathwalk_dry_run/job_scripts/scenario_000_json_ordo-code.sh

PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli dry-run-collect \
  --plan runs/pathwalk_dry_run/DRY_RUN_PLAN.json
```

Important execution rule: do not treat a monolithic Python loop as the acceptance
path for many-job dry-runs. The stable contract is:

```text
plan artifacts → independent job invocation(s) → collect from score artifacts
```

Each generated job script runs one `dry-run-job` and redirects stdin from
`/dev/null`, so benchmark execution cannot accidentally consume a job-list file
or enter an interactive CLI path.

The convenience `benchmark-dry-run` command may still be useful for local quick
checks, but release/acceptance evidence should prefer the artifact-only flow.
