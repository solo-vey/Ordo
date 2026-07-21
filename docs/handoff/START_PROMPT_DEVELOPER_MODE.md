# Start Prompt — M60.7 transition note

Use **M60.6.4** as the last stable benchmark-preparation base. Treat M60.6.5 and M60.6.4.1 as blocked-no-release evidence only.

For M60.7 work, focus on PathWalk real-module testcase generation from `source/program.ordo.yaml`. Do not change runtime-core semantics, do not change scoring weights, and do not revive the blocked transcript replay matrix path unless a separate watchdog/process-boundary milestone is explicitly opened.

# START PROMPT — AI Ordo Developer Bundle Mode

You are AI Ordo Developer working with an Ordo Developer Bundle.

Use `language/` as the language/spec source, `cli/` as deterministic helper layer, and `packages/ordo_project_builder/` as the canonical Developer example.

For any subject package runtime session, do not paste large runtime rules into the chat. Use the package's `START_PROMPT_RUNTIME_MODE.md`, then read `START_HERE_RUNTIME_MODE.md` and follow it strictly.

Do not claim CLI passed unless CLI actually ran. Report explicit CLI status.

## M56 package build profiles

Ordo subject packages now distinguish three build profiles:

```bash
ordo package <package> --profile dev --out <zip>
ordo package <package> --profile runtime --out <zip>
ordo package <package> --profile evidence --out <zip>
```

- `dev` is the full editable package with source YAML, tests, run inputs, templates, reports, and development material.
- `runtime` is the clean guided-execution package. It uses `compiled/program.ir.json` as the primary runtime source and excludes `source/`, `tests/`, `run_inputs/`, `domain/`, generated outputs, state snapshots, and release zips.
- `evidence` contains validation/provenance/hash reports only.

Runtime packaging creates `ordo.runtime.json`, `reports/BUILD_MANIFEST.json`, and `reports/SHA256SUMS.txt`. The runtime package records the source YAML hash even though editable YAML is not included.

## M57 Runtime Checkpoint Discipline

Runtime Mode now enforces a checkpoint layer: one node, one contract, and one decision at a time. Helper reports expose `checkpoint_table`, `earliest_incomplete_node`, `open_required_fields`, and `forward_allowed`. `next-step` prioritizes the earliest incomplete node, and `generate-output` is blocked while checkpoint gaps remain. Detailed rules live in `language/RUNTIME_CHECKPOINTS.md` and package `START_HERE_RUNTIME_MODE.md`; minimal runtime prompts stay minimal.



M59.1 note: runtime packages should include `cli_embedded/ordo`; do not treat a runtime session as enforced if the embedded CLI cannot execute.

## M60.3.2 runtime CLI safety note

This bundle includes the M60.3.2 safety patch: bare `intake <package>` fails fast in non-TTY automation unless `--submit`, `--answers`, or `--non-interactive` is provided. Scenario-testing utilities should use explicit `intake --submit ... --answer-file ...` or `intake --answers ... --non-interactive`.

## M60.6.2 calibration note

M60.6.2 is a report/evidence refinement milestone. Do not change PathWalk scoring weights from the M60.6 dry-run baseline alone: all 60 dry-run cases passed with all component metrics at 1.0, so the dataset has no calibration variance.


## Current benchmark protocol status

Latest stable protocol milestone: `M60.6.3 — Model Benchmark Protocol Design`.

Before any real PathWalk model/API benchmark or transcript-replay benchmark, follow `ordo_pathwalk/MODEL_BENCHMARK_PROTOCOL.md`. Do not change `path_quality_score` weights from dry-run-only data.

## M60.6.4 transcript replay pilot

This bundle includes PathWalk v9.6.4 transcript-replay pilot support. Use `model-benchmark-pilot` for a no-API protocol pilot and `model-benchmark-collect` to regenerate `SUMMARY.*` and `CALIBRATION_DECISION.*` from `MODEL_BENCHMARK_PLAN.json`. This does not change runtime-core semantics or scoring weights.


## M60.7 Line Closure

M60.7 is closed at stable M60.7.5 as an artifact-only Real Module Testcase Generation line. Do not continue adding noise variants by default. Supported artifact-only noise patterns are `distraction`, `invalid_branch`, `clarification_without_submit`, and `skip_ahead`. Treat `backtrack`, `correction_backtrack`, runtime execution, scoring, and benchmark orchestration as future improvements unless explicitly reopened.

## M60.7.1 Source YAML Loader and Graph Summary

M60.7.1 adds the first implemented slice of Real Module Testcase Generation: PathWalk can now read a real `source/program.ordo.yaml` in authoring/testcase-generation mode and emit `REAL_MODULE_GRAPH_SUMMARY.json/.md` plus `VALIDATION_REPORT.json`. This does not read `compiled/*`, does not generate testcases yet, and does not change runtime-core semantics or scoring weights.

Command:

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-graph --source path/to/source/program.ordo.yaml --out runs/real_module_graph --force
```

## M60.7.2 Terminal Path Enumeration

M60.7.2 extends the Real Module Testcase Generation line with terminal path enumeration from `REAL_MODULE_GRAPH_SUMMARY.json`. PathWalk now writes `REAL_MODULE_TERMINAL_PATHS.json/.md` plus a validation report. This is still source-analysis/testcase-preparation work: it does not emit testcase/noise artifacts, does not read `compiled/*`, and does not change Ordo runtime-core semantics or scoring weights.

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-paths \
  --summary runs/real_module_graph/REAL_MODULE_GRAPH_SUMMARY.json \
  --out runs/real_module_paths \
  --force
```



## M60.7.5 — Bounded Noise Testcase Artifacts

M60.7.5 extends `real-module-noise-cases` to four artifact-only patterns: `distraction`, `invalid_branch`, `clarification_without_submit`, and `skip_ahead`. This closes the current noise-expansion line; remaining complex patterns are future improvements unless explicitly reopened. Runtime execution, scoring, calibration, and benchmark orchestration remain out of scope.

## M60.7.4 — Noise Testcase Artifacts

Stable M60.7.4 adds `real-module-noise-cases`, which turns `REAL_MODULE_TERMINAL_PATHS.json` into artifact-only noise testcase artifacts for `distraction` and `invalid_branch`: `cases/*.json`, `cases/*.md`, `RAW_NOISE_TESTCASE_MATRIX.csv`, `SUMMARY.json/.md`, and `VALIDATION_REPORT.json`. Runtime execution, scoring, calibration, and benchmark orchestration remain future milestones.

## M60.7.3 — Clean Path Testcase Artifacts

Stable M60.7.3 adds `real-module-clean-cases`, which turns `REAL_MODULE_TERMINAL_PATHS.json` into clean-path testcase artifacts: `cases/*.json`, `cases/*.md`, `RAW_TESTCASE_MATRIX.csv`, `SUMMARY.json/.md`, and `VALIDATION_REPORT.json`. Runtime execution and noise generation remain future milestones.
