# M60.6 Line Closure Report

Generated: 2026-07-08T08:30:00+02:00

## Status

**Decision:** close the M60.6 benchmark-preparation line at **M60.6.4**.

**Stable base:** `M60.6.4 — Transcript Replay / Model Benchmark Pilot`.

**Blocked experimental branches:**

- `M60.6.5 — Transcript Replay Acceptance Matrix` — blocked, not released.
- `M60.6.4.1 — Transcript Replay Process Boundary Hardening` — blocked, not released.

These blocked branches are retained only as evidence and must not be used as a stable base.

## What M60.6 accomplished

M60.6 achieved its original goal: no-API benchmark-preparation evidence through the stable artifact-only dry-run contract.

Accepted stable chain:

```text
dry-run-plan → independent job_scripts/*.sh → dry-run-collect
```

Accepted evidence:

```text
20 scenarios × 3 runtime views = 60 cases
60/60 passed
RAW_METRICS.csv collected
SUMMARY.json and SUMMARY.md collected
```

M60.6.1 added clean-room release-integrity hardening and fixed generated job-script portability.  
M60.6.2 confirmed that the dry-run baseline is readiness evidence but not calibration evidence because all scores were saturated at `1.0`.  
M60.6.3 defined the model benchmark protocol.  
M60.6.4 implemented a small no-API transcript replay pilot.

## What remains explicitly out of scope

The following are **not** complete and must not be represented as complete:

- real model/API benchmark;
- calibration run;
- path_quality_score weight change;
- broad transcript replay acceptance matrix;
- subprocess/watchdog hardening for large model benchmark matrices.

## Known blocker summary

The blocked experimental path is localized to PathWalk transcript-replay orchestration, not to Ordo runtime-core semantics.

Observed issue:

```text
multi-runtime transcript replay can hang around embedded runtime child / verify-session boundary
```

This is a benchmark-runner process-boundary problem. It is not a blocker for moving to the next language/PathWalk design milestone.

## Decision for next work

Move to:

```text
M60.7 — Real Module Testcase Generation
```

M60.7 should focus on generating testcase artifacts from a real Ordo source module, not on expanding transcript/model benchmark execution.

## Guardrails carried forward

- Do not use M60.6.5 or M60.6.4.1 WIP patches as stable base.
- Do not calibrate weights from saturated dry-run metrics.
- Do not run broad model benchmark matrices until a separate watchdog/process-boundary hardening milestone exists.
- Keep PathWalk as a companion utility, not runtime core.
- Keep the M60 runtime principle unchanged:

```text
JSON IR decides.
Ordo-code explains.
Session-trace proves.
```
