# M60.6.4.1 — Transcript Replay Process Boundary Hardening Blocker Report

Status: `blocked-no-release`

Base used: `M60.6.4 — Transcript Replay / Model Benchmark Pilot`

## Intended scope

Harden the M60.6.4 transcript-replay path so that benchmark execution follows the proven M60.5.4 artifact-only boundary:

```text
model-benchmark-plan → independent model-benchmark-job invocations → model-benchmark-collect
```

The scope explicitly excluded scorer weight changes, runtime-core semantic changes, and live API/model calls.

## What was implemented as WIP patch

The attempted patch added:

- `model-benchmark-plan` CLI command.
- `model-benchmark-job` CLI command.
- `model-benchmark-collect` collection from score artifacts.
- Portable `job_scripts/*.sh` for one replay job per script.
- Plan artifact contract in `MODEL_BENCHMARK_PLAN.json`.
- Job descriptors in `jobs/*.json`.
- Boundary-safe plan-only behavior for legacy `model-benchmark-pilot` CLI.

## Validation that passed

- `py_compile` for `ordo_pathwalk/*.py`: passed.
- Targeted regression tests: `6 passed`.
- Single-runtime direct CLI smoke:
  - runtime view: `json`;
  - completed: `3/3`;
  - status: `passed-pilot`;
  - failure buckets: `none=1`, `distraction_followed=1`, `protocol_violation=1`.

## Blocker found

When the same approach was expanded toward multi-runtime acceptance, the run did not complete reliably.

Observed state from the blocked acceptance attempt:

- matrix target: `3 scenarios × 3 runtime views = 9 jobs`;
- completed score artifacts before stop: `3/9`;
- hang observed in embedded runtime verification path, specifically a `verify-session` call inside a transcript replay job;
- the issue appears below the new benchmark plan/job boundary, inside the per-job embedded runtime interaction.

This means the M60.6.4.1 boundary patch is directionally correct but not sufficient as a release: independent replay jobs exist, but a single job can still stall while producing or verifying runtime evidence.

## Release decision

`M60.6.4.1` is **not released**.

Stable base remains:

```text
M60.6.4 — Transcript Replay / Model Benchmark Pilot
```

The WIP patch is included only as blocker evidence and must not be used as a stable base.

## Weights / runtime impact

- Scoring weights changed: `false`.
- Ordo runtime-core semantics changed: `false`.
- Live model/API benchmark run: `false`.
- Book/PDF generation: `false`.

## Recommended next step

Do not widen the transcript replay matrix yet. The next safe step is:

```text
M60.6.4.2 — Per-job Embedded Runtime Watchdog Hardening
```

Goal:

- keep the plan/job/collect boundary;
- add a hard per-job watchdog around embedded runtime commands;
- treat `score_file`/`transcript_file` as the job completion artifacts;
- terminate lingering embedded process groups deterministically;
- then retry a small `3 × 3` transcript replay acceptance matrix.
