## v9.8.0 / M61.0 — Human Review Scenario Cards

- Added `real-module-review-cards` CLI command.
- Added `generate_review_cards_from_case_summaries` and `write_real_module_review_cards`.
- Added human-review artifact contract: `cards/*.json`, `cards/*.md`, `REVIEW_CARDS.json/.md`, `RAW_REVIEW_CARD_MATRIX.csv`, and `VALIDATION_REPORT.json`.
- Review cards are generated from existing clean/noise testcase `SUMMARY.json` artifacts.
- Keeps runtime execution, scoring, calibration, model/API benchmark orchestration, and watchdog/process-boundary hardening explicitly out of scope.
- Does not change Ordo runtime-core semantics or scoring weights.

## v9.7.7 — M60.8 Stable Handoff Consolidation

- Documentation/package consolidation only.
- Clarifies the stable artifact-only real-module testcase generation flow.
- Records future backlog for human review scenario cards and runtime execution of generated testcases.
- No PathWalk runtime behavior or scoring weights changed.

## v9.7.x — M60.7 Line Closure

- Closed the current Real Module Testcase Generation artifact-only line at M60.7.5.
- Documented stop condition for noise expansion.
- Deferred `backtrack`, `correction_backtrack`, runtime execution, scoring, and benchmark orchestration as future improvements.

## v9.7.5 / M60.7.5 — Bounded Noise Testcase Artifacts

- Extended `real-module-noise-cases` to support `clarification_without_submit` and `skip_ahead` in addition to `distraction` and `invalid_branch`.
- Default generation now emits four bounded noise patterns per terminal path.
- Added testcase artifact expectations for clarification-without-submit and skip-ahead recovery behavior.
- Marked the remaining complex noise patterns (`backtrack`, `correction_backtrack`) as future improvements to avoid endless low-value expansion.
- Keeps runtime execution, scoring, calibration, and benchmark orchestration explicitly out of scope.
- Does not change Ordo runtime-core semantics or scoring weights.

## v9.7.4 / M60.7.4 — Noise Testcase Artifacts

- Added `real-module-noise-cases` CLI command.
- Added artifact-only noise testcase generation for the first two controlled patterns: `distraction` and `invalid_branch`.
- Added `RAW_NOISE_TESTCASE_MATRIX.csv`, `SUMMARY.json/.md`, per-case `cases/*.json/.md`, and `VALIDATION_REPORT.json`.
- Generates one noise case per terminal path per selected pattern.
- Keeps runtime execution, scoring, calibration, and benchmark orchestration explicitly out of scope.
- Does not change Ordo runtime-core semantics or scoring weights.

## v9.7.3 / M60.7.3 — Clean Path Testcase Artifacts

- Added `real-module-clean-cases` CLI command.
- Added `generate_clean_path_cases_from_terminal_paths` and `write_real_module_clean_path_cases`.
- Added clean-path testcase artifact contract: `cases/*.json`, `cases/*.md`, `RAW_TESTCASE_MATRIX.csv`, `SUMMARY.json/.md`, and `VALIDATION_REPORT.json`.
- Generates one clean-path case per enumerated terminal path.
- Keeps runtime execution and noise-pattern generation explicitly out of scope.
- Does not change Ordo runtime-core semantics or scoring weights.

## v9.7.2 / M60.7.2 — Terminal Path Enumeration

- Added `real-module-paths` CLI command.
- Added `enumerate_terminal_paths_from_summary` and `write_real_module_terminal_paths`.
- Added `REAL_MODULE_TERMINAL_PATHS.json/.md` artifact contract.
- Added pytest coverage for terminal path enumeration, writer, and CLI.
- Keeps testcase/noise generation explicitly out of scope.
- Does not change Ordo runtime-core semantics or scoring weights.

## v9.7.1 / M60.7.1 — Source YAML Loader and Real Module Graph Summary

- Added `real-module-graph` CLI command.
- Added `utilities/ordo_pathwalk/generator/real_module.py` for authoring-time `source/program.ordo.yaml` loading and graph summary extraction.
- Added `REAL_MODULE_GRAPH_SUMMARY.json/.md` and validation report artifact contract.
- Added neutral sample graph summary under `examples/m60_7_1_real_module_graph_summary/`.
- Added pytest coverage for the loader, artifact writer, and CLI.
- Does not implement terminal-path enumeration or testcase generation yet.
- Does not change Ordo runtime-core semantics or scoring weights.

## M60.7 — Real Module Testcase Generation Kickoff

- Closed the M60.6 line at the stable M60.6.4 transcript-replay pilot.
- Marked M60.6.5 and M60.6.4.1 as blocked-no-release evidence only.
- Added `M60_6_LINE_CLOSURE_REPORT.md/.json`.
- Added `M60_7_REAL_MODULE_TESTCASE_GENERATION_KICKOFF.md/.json`.
- Added PathWalk design contract `utilities/ordo_pathwalk/REAL_MODULE_TESTCASE_GENERATION.md`.
- Defined the future real-module testcase artifact contract and noise taxonomy.
- No Ordo runtime-core semantics changed.
- No scoring weights changed.
- No real model/API benchmark was run.

# v9.6.4 / M60.6.4 — Transcript Replay Pilot

- Added no-API transcript-replay pilot generator and collector.
- Added `model-benchmark-pilot` and `model-benchmark-collect` CLI commands.
- Added required model benchmark artifacts: `MODEL_BENCHMARK_PLAN.json`, `RAW_MODEL_METRICS.csv`, `MODEL_RUN_MANIFEST.json`, and `CALIBRATION_DECISION.*`.
- Added failure bucket output for `distraction_followed` and `protocol_violation` pilot evidence.
- Added pytest coverage for the transcript-replay artifact contract.
- Default scoring weights remain unchanged.

# M60.6.3 — Model Benchmark Protocol Design

- Added `utilities/ordo_pathwalk/MODEL_BENCHMARK_PROTOCOL.md` for future real model/API and transcript-replay PathWalk benchmarks.
- Defined required benchmark artifacts, transcript evidence, raw model metrics columns, failure buckets, and calibration eligibility gates.
- Confirmed default `path_quality_score` weights remain locked until future non-saturated model-behavior data passes eligibility gates.
- Did not run a real model/API benchmark.
- Did not change runtime-core semantics or scorer weights.

# M60.5.2b — PathWalk External Job Dry-run Contract

- Added external-job dry-run orchestration: `dry-run-plan`, `dry-run-job`, and `dry-run-collect`.
- Decomposed benchmark dry-runs into independently executable jobs so one scenario/runtime_view cannot hang the full benchmark parent process.
- Preserved existing `benchmark-dry-run` as legacy/convenience orchestration, but the recommended acceptance path is now plan → individual jobs → collect.
- Added regression coverage for the plan/job/collect contract.
- Added sample external-job dry-run artifacts across `json`, `ordo-code`, and `json,ordo-code`.


## v9.2 / M60.5 Benchmark Readiness

- Added `matrix-smoke` command.
- Added no-API ground-truth matrix runner for `json`, `ordo-code`, and `json,ordo-code`.
- Added example `SUMMARY.json`, `SUMMARY.md`, and per-view score files.
- Added pytest coverage for matrix smoke.
- This is a readiness smoke, not calibrated model-quality scoring.

## v9.3 / M60.5.1

- Added `benchmark-dry-run` for multi-scenario no-API dry runs.
- Added `dry-run-case` worker.
- Added `RAW_METRICS.csv` output.
- Added no-rerun verification scoring mode for dry-run and matrix-smoke flows.
- Added benchmark dry-run orchestration test.

## v9.5 / M60.5.4 — Artifact-only dry-run executor

- `dry-run-plan` now emits immutable job descriptors and one-job shell wrappers.
- `dry-run-collect` is the canonical aggregation step for completed score artifacts.
- Multi-job acceptance should use external shell/CI execution rather than a long-lived Python parent loop.
- Added sample artifacts under `examples/m60_5_4_artifact_only_dry_run/`.

## M82.1 — Hardened isolated child runner and watchdog

- Added plan fingerprinting and approved-root path validation.
- Added input rejection before process spawn for unsafe or tampered plans.
- Minimized child environment and closed stdin explicitly.
- Added bounded stdout/stderr draining with truncation evidence.
- Hardened process-group watchdog termination.
- Added atomic result persistence and no-overwrite behavior.
- Added explicit sandbox cleanup/retention policies.
- Added capability reporting for POSIX process groups and resource limits.
- Preserved compatibility with the M76.2 plan/job/collect workflow.

## M82.3

- Added `real-module-pipeline` with `generate-only` and `generate-and-run` modes.
- Integrated real-module graph/path/case generation with M82.1 hardened workers and M82.2 evidence collection.
- Preserved scoring and calibration as separate claims.
