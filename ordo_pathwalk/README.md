## M60.8 stable handoff note

M60.8 is a documentation/package consolidation milestone. PathWalk behavior remains at the M60.7.5 artifact-only boundary: `real-module-graph`, `real-module-paths`, `real-module-clean-cases`, and bounded `real-module-noise-cases` for `distraction`, `invalid_branch`, `clarification_without_submit`, and `skip_ahead`.

See root-level `STABLE_DEVELOPER_HANDOFF.md` and `FUTURE_BACKLOG.md` for the current stable path and deferred future work.


## M61.0 human review scenario cards

M61.0 adds a QA/developer reading layer over generated real-module testcase artifacts. It combines clean-path and bounded-noise `SUMMARY.json` files and emits human-readable scenario cards. It still does not run the runtime, score model behavior, or calibrate weights.

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-review-cards \
  --summary runs/real_module_clean_cases/SUMMARY.json \
  --summary runs/real_module_noise_cases/SUMMARY.json \
  --out runs/real_module_review_cards \
  --force
```

Generated artifacts:

- `cards/<card_id>.json`
- `cards/<card_id>.md`
- `REVIEW_CARDS.json`
- `REVIEW_CARDS.md`
- `RAW_REVIEW_CARD_MATRIX.csv`
- `VALIDATION_REPORT.json`

`runtime_execution_ready`, `scoring_ready`, and `calibration_ready` remain `false` by design.

## M60.7 kickoff — real-module testcase generation

M60.7 moves PathWalk toward testcase generation from real `source/program.ordo.yaml` modules. This package defines the target artifact contract and noise taxonomy but does not implement the generator yet. See `REAL_MODULE_TESTCASE_GENERATION.md`.

M60.6.5 and M60.6.4.1 are blocked-no-release experiments and are not stable bases.

# Ordo PathWalk — M60-native scenario benchmark

`ordo_pathwalk` is a companion utility for testing how a model navigates an
Ordo guided-intake decision tree. It is not part of the Ordo runtime core and
is not packaged inside normal runtime profiles.

This release candidate is adapted to the current Ordo M60 protocol and includes M60.6.1 dry-run job-script portability hardening:

- embedded launcher: `./cli_embedded/ordo`
- no use of legacy `python3 cli_embedded/ordo_run.py`
- runtime views: `json`, `ordo-code`, `json,ordo-code`
- target verification: `verify-targets`
- runtime proof: `runtime/session.ordo.trace`
- rollback: `restore-session` append-only events
- score metadata: CLI/runtime protocol/version/hash fields


## M60.6.1 portable artifact-only jobs

Generated `job_scripts/*.sh` no longer embed a temporary absolute workspace path from the generation machine. They resolve execution as follows:

1. Use `ORDO_PATHWALK_ROOT` when provided.
2. Otherwise, try to detect a workspace root when the dry-run output lives under a full Ordo workspace.
3. Use `${ROOT}/cli` by default for Ordo CLI.
4. Use `ORDO_CLI_ROOT` when PathWalk is run as a standalone RC beside a separate developer bundle.
5. Fail fast with an actionable error if `ordo_pathwalk/` or `cli/ordo/` cannot be found.

Standalone RC + developer bundle example:

```bash
export ORDO_PATHWALK_ROOT=<pathwalk-rc-root>
export ORDO_CLI_ROOT=<developer-bundle-root>/cli
export PYTHONPATH="${ORDO_PATHWALK_ROOT}:${ORDO_CLI_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"
```


## M60.7.1 real-module graph summary

M60.7.1 implements the first source-analysis slice for real-module testcase generation. It reads a real `source/program.ordo.yaml` in authoring/testcase-generation mode and writes a graph summary without reading `compiled/*`.

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-graph \
  --source path/to/source/program.ordo.yaml \
  --out runs/real_module_graph \
  --force
```

Generated artifacts:

- `REAL_MODULE_GRAPH_SUMMARY.json`
- `REAL_MODULE_GRAPH_SUMMARY.md`
- `VALIDATION_REPORT.json`

This is not testcase generation yet. Terminal-path enumeration and noise-case generation remain later M60.7 steps.

## M60.7.2 real-module terminal paths

M60.7.2 implements the next source-analysis slice: terminal path enumeration from an existing `REAL_MODULE_GRAPH_SUMMARY.json`. It still does not generate testcase/noise artifacts.

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-paths \
  --summary runs/real_module_graph/REAL_MODULE_GRAPH_SUMMARY.json \
  --out runs/real_module_paths \
  --force
```

Generated artifacts:

- `REAL_MODULE_TERMINAL_PATHS.json`
- `REAL_MODULE_TERMINAL_PATHS.md`
- `VALIDATION_REPORT.json`

`clean_path_case_generation_ready` may become `true` when terminal paths are structurally usable, but `testcase_generation_ready` stays `false` until a later milestone actually emits case artifacts.

## M60.7.3 real-module clean path cases

M60.7.3 implements the first testcase-artifact slice: one clean-path case per enumerated terminal path. It still does not run the runtime and does not generate noise variants.

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-clean-cases \
  --paths runs/real_module_paths/REAL_MODULE_TERMINAL_PATHS.json \
  --out runs/real_module_clean_cases \
  --force
```

Generated artifacts:

- `cases/<case_id>.json`
- `cases/<case_id>.md`
- `RAW_TESTCASE_MATRIX.csv`
- `SUMMARY.json`
- `SUMMARY.md`
- `VALIDATION_REPORT.json`

`runtime_execution_ready` and `noise_case_generation_ready` remain `false` by design.

## M60.7.5 real-module bounded noise cases

M60.7.5 implements a bounded controlled-noise testcase artifact slice. It reads `REAL_MODULE_TERMINAL_PATHS.json` and emits artifact-only noise cases for `distraction`, `invalid_branch`, `clarification_without_submit`, and `skip_ahead`. It still does not run runtime, score model behavior, or calibrate weights. Further complex noise patterns are future improvements, not current blockers.

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-noise-cases \
  --paths runs/real_module_paths/REAL_MODULE_TERMINAL_PATHS.json \
  --out runs/real_module_noise_cases \
  --pattern distraction \
  --pattern invalid_branch \
  --pattern clarification_without_submit \
  --pattern skip_ahead \
  --force
```

Generated artifacts:

- `cases/<case_id>.json`
- `cases/<case_id>.md`
- `RAW_NOISE_TESTCASE_MATRIX.csv`
- `SUMMARY.json`
- `SUMMARY.md`
- `VALIDATION_REPORT.json`

`runtime_execution_ready`, `scoring_ready`, and `calibration_ready` remain `false` by design.

## Basic workflow

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli init-tree \
  --depth 5 --branching 2 4 --seed 42 --out /tmp/pathwalk_tree --force

PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli gen-scenarios \
  --tree /tmp/pathwalk_tree --count 10 --seed 100 --out /tmp/pathwalk_scenarios

PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli run \
  --tree /tmp/pathwalk_tree \
  --scenario /tmp/pathwalk_scenarios/scenario_000.json \
  --driver anthropic:claude-sonnet-5 \
  --cli-mode enforced \
  --runtime-view ordo-code \
  --out /tmp/pathwalk_runs

PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli score \
  --scenario /tmp/pathwalk_scenarios/scenario_000.json \
  --sandbox /tmp/pathwalk_runs/scenario_000_sandbox \
  --transcript /tmp/pathwalk_runs/scenario_000_transcript.json \
  --out /tmp/pathwalk_scores/scenario_000_score.json

PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli aggregate \
  --scores-dir /tmp/pathwalk_scores \
  --out /tmp/pathwalk_scores/SUMMARY.json \
  --markdown /tmp/pathwalk_scores/SUMMARY.md
```

## Modes

`cli_mode` controls how much runtime discipline the model sees:

| mode | meaning |
|---|---|
| `enforced` | build/use an M60.4 runtime package and interact only through `./cli_embedded/ordo` |
| `ir_readable` | baseline: remove CLI and allow direct compiled IR reading |
| `fully_freeform` | baseline: remove CLI and compiled IR |

`runtime_view` controls the M60 AI-facing projection used by enforced runs:

| runtime_view | meaning |
|---|---|
| `json` | canonical JSON reports only |
| `ordo-code` | `next-step --format auto` emits the current Ordo-code contract fragment |
| `json,ordo-code` | mixed package containing both JSON reports and Ordo-code view |

JSON IR decides. Ordo-code explains. Session-trace proves.

## Enforced-mode command contract

In enforced mode the model prompt must use only:

```bash
./cli_embedded/ordo runtime-status .
./cli_embedded/ordo verify-targets .
./cli_embedded/ordo next-step . --format auto
./cli_embedded/ordo intake . --submit <NODE_ID> --answer-file <file>
./cli_embedded/ordo restore-session . --to-seq <N> --reason "..."
./cli_embedded/ordo verify-session .
```

Direct `compiled/*` access is a protocol violation and the scorer can mark it.

## What the scorer reads

The scorer reads persisted runtime artifacts, not model self-reports:

- `runtime/live_session_state.json`
- `runtime/state_snapshots/*.json`
- `runtime/evidence/*_evidence.json`
- `runtime/session.ordo.trace`
- `compiled/targets.manifest.json`
- `reports/target_verification_report.json`
- `reports/session_verification_report.json`

Each score records runtime metadata such as `runtime_view`, `canonical_ir_hash`,
`targets_manifest_hash`, and `session_trace_hash`.

## Tests

```bash
PYTHONPATH=cli:. pytest ordo_pathwalk/tests -q
```

The current minimal suite covers maze generation, noise generation, M60 runtime
sandbox preparation, scoring, aggregation, and retry/backoff helpers.

## M60.5 matrix smoke

Before running API/model benchmarks, verify that PathWalk is compatible with the current Ordo runtime protocol:

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli matrix-smoke \
  --out /tmp/pathwalk_matrix_smoke \
  --depth 2 \
  --branching 2 2 \
  --force
```

This creates a generated test tree, one scenario, three M60 runtime sandboxes, per-view score files, and aggregate `SUMMARY.json`/`SUMMARY.md`.

The matrix smoke is not a model-quality benchmark. It uses a deterministic ground-truth driver to validate package building, embedded CLI execution, scoring, metadata capture, and aggregation across:

- `enforced + json`
- `enforced + ordo-code`
- `enforced + json,ordo-code`

Sample output is kept in `ordo_pathwalk/examples/m60_5_matrix_smoke/`.

## M60.5.1 benchmark dry-run

Before calibrating score weights, collect raw metrics without API calls:

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli benchmark-dry-run \
  --out /tmp/pathwalk_dry_run \
  --scenario-count 20 \
  --runtime-view json \
  --runtime-view ordo-code \
  --runtime-view json,ordo-code \
  --force
```

This writes `RAW_METRICS.csv`, `SUMMARY.json`, `SUMMARY.md`, and individual `scores/*_score.json` files. It is not a model-quality benchmark; it is calibration preparation.


## M60.5.2b external-job dry-run contract

For multi-scenario dry-runs, prefer the external-job contract instead of a single long-lived parent runner:

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli dry-run-plan \
  --out runs/dry_run \
  --scenario-count 20 \
  --runtime-view json \
  --runtime-view ordo-code \
  --runtime-view json,ordo-code \
  --force

# Execute each job independently, for example from shell/CI:
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli dry-run-job \
  --plan runs/dry_run/DRY_RUN_PLAN.json \
  --job-id scenario_000_json

PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli dry-run-collect \
  --plan runs/dry_run/DRY_RUN_PLAN.json
```

This creates `DRY_RUN_PLAN.json`, one score per job, `RAW_METRICS.csv`, `SUMMARY.json`, and `SUMMARY.md`. The old `benchmark-dry-run` command remains available as a convenience layer, but the plan/job/collect contract is the recommended path for stable CI and larger benchmark runs.

## M60.5.4 artifact-only dry-run flow

For stable multi-case dry-runs, prefer the artifact-only flow:

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli dry-run-plan \
  --out runs/dry_run \
  --scenario-count 20 \
  --runtime-view json \
  --runtime-view ordo-code \
  --runtime-view json,ordo-code \
  --force

# Run each generated job independently, for example in a CI matrix:
bash runs/dry_run/job_scripts/scenario_000_json.sh

PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli dry-run-collect \
  --plan runs/dry_run/DRY_RUN_PLAN.json
```

`benchmark-dry-run` remains a local convenience command, but release evidence should use plan/job/collect artifacts.

## M60.6 calibration-preparation baseline

M60.6 uses the M60.5.4 artifact-only flow to collect raw dry-run metrics before any score calibration:

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli dry-run-plan   --out runs/m60_6_calibration_prep   --scenario-count 20   --runtime-view json   --runtime-view ordo-code   --runtime-view json,ordo-code   --force

# Execute generated jobs independently, for example:
bash runs/m60_6_calibration_prep/job_scripts/scenario_000_json.sh

PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli dry-run-collect   --plan runs/m60_6_calibration_prep/DRY_RUN_PLAN.json
```

Acceptance evidence for this milestone is stored in `examples/m60_6_calibration_prep_baseline/`:

- 20 generated scenarios;
- 3 runtime views: `json`, `ordo-code`, `json,ordo-code`;
- 60 score artifacts;
- `RAW_METRICS.csv`;
- `SUMMARY.json` and `SUMMARY.md`.

This is still not a real model/API benchmark and it does not change default scoring weights.

Standalone PathWalk RC archives do not contain the full Ordo CLI package. Tests that build runtime packages should be run from the Ordo workspace or with the workspace/developer-bundle `cli` directory on `PYTHONPATH`.


## M60.6.3 model benchmark protocol

M60.6.3 adds a protocol document for future real model/API or transcript-replay benchmarks:

```text
ordo_pathwalk/MODEL_BENCHMARK_PROTOCOL.md
```

The protocol defines required artifacts (`MODEL_BENCHMARK_PLAN.json`, transcripts, scores, `RAW_MODEL_METRICS.csv`, `MODEL_RUN_MANIFEST.json`, and `CALIBRATION_DECISION.*`), minimum transcript fields, minimum raw model metrics columns, failure buckets, calibration eligibility gates, and security rules.

This is a design/protocol milestone only. It does not run a real model benchmark and does not change default `path_quality_score` weights.

## M60.6.4 transcript-replay model benchmark pilot

M60.6.4 adds a small no-API pilot for the M60.6.3 model benchmark protocol. The pilot creates synthetic transcript evidence to prove that the artifact contract, raw model metrics, failure buckets, and calibration decision files can be generated without calling a live model provider.

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli model-benchmark-pilot \
  --out runs/m60_6_4_transcript_replay_pilot \
  --scenario-count 3 \
  --runtime-view json \
  --force

PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli model-benchmark-collect \
  --plan runs/m60_6_4_transcript_replay_pilot/MODEL_BENCHMARK_PLAN.json
```

The acceptance pilot intentionally uses a small `json` runtime-view subset in constrained environments. It creates one perfect transcript, one distraction/model-quality non-perfect transcript, and one protocol-violation transcript. This yields nonzero variance and non-saturated scores, but it is not sufficient for calibration. Weights remain locked until a larger real model/API or reviewed transcript benchmark satisfies the M60.6.3 calibration gates.

## M60.7 line closure

The current artifact-only Real Module Testcase Generation line is closed at M60.7.5. PathWalk supports graph summary, terminal path enumeration, clean-path testcase artifacts, and bounded noise testcase artifacts for `distraction`, `invalid_branch`, `clarification_without_submit`, and `skip_ahead`.

Do not keep extending noise variants inside this line by default. More complex recovery patterns such as `backtrack` and `correction_backtrack`, plus runtime execution/scoring, are future milestones.

