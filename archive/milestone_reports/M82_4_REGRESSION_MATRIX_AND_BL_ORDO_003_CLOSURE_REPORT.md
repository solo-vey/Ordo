# M82.4 — Regression Matrix and BL-ORDO-003 Closure

Status: passed
Date: 2026-07-12
Backlog item: BL-ORDO-003

## Closure decision

BL-ORDO-003 is closed. Generated real-module testcases can now be generated and executed through a hardened child-process boundary with watchdog termination, isolated sandboxes, bounded diagnostics, versioned raw evidence, deterministic failure taxonomy, and collect-only parent behavior.

## Regression matrix

| Area | Coverage | Result |
|---|---|---|
| Plan boundary | fingerprint, approved roots, duplicate IDs, limits, cleanup policy | passed |
| Path safety | traversal, symlink source, symlink sandbox | passed |
| Process isolation | one job per child process, closed stdin, environment allowlist | passed |
| Watchdog | timeout and process-group termination | passed |
| Evidence | schema v1, linkage, bounded stdout/stderr, invalid/tampered evidence rejection | passed |
| Failure taxonomy | nonzero exit, signal, timeout, missing/malformed/mismatched report, input/infrastructure failures | passed |
| Cleanup | retain-all, retain-failures, cleanup-all, atomic persistence | passed |
| Pipeline | generate-only, generate-and-run, clean/noise/both, overwrite guard | passed |
| Claims | raw evidence only; no implicit scoring or calibration | passed |
| Broader PathWalk regression | partitioned execution | passed |

## Test evidence

- M82 closure matrix and M76/M82 compatibility: 29 passed.
- Core PathWalk regression group: 45 passed.
- CSG protocol/production/model-benchmark group: 9 passed.
- Total unique relevant tests: 83 passed.
- Monolithic suite execution exceeded the environment time limit; the same relevant coverage was executed in deterministic partitions.
- `test_model_drivers_retry.py` is outside BL-ORDO-003 scope and is not part of the closure claim.

## Defect found and fixed during closure

The pipeline resolved a source symlink before checking `is_symlink()`, allowing a symlink source to pass validation. M82.4 moved the symlink check before path resolution and added a regression test.

## Bounded claims

- Safe generated-testcase execution: ready.
- Raw execution evidence: ready.
- Automatic scoring from this evidence: not enabled by this closure.
- Calibration claims: not enabled by this closure.

## Closure gate

All required BL-ORDO-003 scenarios are covered: normal completion, timeout/watchdog, crash/process failure taxonomy, malformed output, cleanup, path safety, and integration regression. No blocker remains.
