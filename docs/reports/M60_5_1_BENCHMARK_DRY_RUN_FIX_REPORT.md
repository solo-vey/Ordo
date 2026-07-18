# M60.5.1 Benchmark Dry-run Blocker Fix Report

Status: passed.

## Scope

M60.5.1 fixes the blocker found while preparing M60.6: `benchmark-dry-run` must run more than one generated scenario without hanging before raw metric collection can be trusted.

This is a PathWalk benchmark-readiness patch, not a runtime-core semantic change.

## Changes

- Added `ordo_pathwalk/runner/dry_run.py`.
- Added CLI commands:
  - `benchmark-dry-run`
  - `dry-run-case` internal worker.
- Added `RAW_METRICS.csv` generation.
- Added no-rerun scoring mode so dry-run scoring reads already produced `verify-targets` / `verify-session` reports instead of launching embedded verification again.
- Updated `matrix-smoke` to use no-rerun scoring after it has already executed verification commands.
- Added a benchmark-dry-run orchestration test.
- Added sample dry-run artifacts under `ordo_pathwalk/examples/m60_5_1_benchmark_dry_run/`.

## Acceptance checks

- `benchmark-dry-run --scenario-count 2 --runtime-view json` completed.
- `RAW_METRICS.csv` was produced.
- PathWalk pytest passed: 19/19.
- `py_compile` passed for `cli/` and `ordo_pathwalk/`.
- `repo-check` passed after generated metadata cleanup.

## Not included

- Final score-weight calibration.
- Real API/model benchmark run.
- MCP or sandbox changes.
- New Python/Java compilation targets.
