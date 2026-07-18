# M60.5 PathWalk Benchmark Readiness Report

Milestone: M60.5 — PathWalk Benchmark Readiness

Type: companion utility readiness / test harness stabilization

## Result

Passed.

M60.5 adds a no-API PathWalk matrix smoke that validates the current M60 runtime protocol across all supported runtime views before expensive model/API benchmark runs.

## Verified runtime views

- `json`
- `ordo-code`
- `json,ordo-code`

## Acceptance checks

- PathWalk pytest passed: 18/18.
- Matrix smoke generated scores for all three runtime views.
- Matrix smoke generated aggregate `SUMMARY.json` and `SUMMARY.md`.
- Scores include runtime metadata and target/session hashes.
- Enforced mode remains based on `./cli_embedded/ordo`, not legacy `ordo_run.py`.

## Non-goals

- No score-weight calibration.
- No real API/model benchmark run.
- No Python/Java targets.
- No MCP/sandbox trust-level changes.

## Notes

This milestone makes PathWalk ready for controlled benchmark runs, but it does not decide final `path_quality_score` weights. Calibration requires real run data and an explicit product decision about whether PathWalk is used primarily for model comparison, Ordo release QA, or research benchmarking.
