# M60.6 Calibration Preparation Report

## Status

`passed` — M60.6 no-API dry-run baseline completed from the stable M60.5.4 artifact-only executor.

## Base

- Stable base: `M60.5.4 — PathWalk Artifact-only Dry-run Executor`
- Execution path: `dry-run-plan → independent job_scripts/*.sh → dry-run-collect`
- Runtime modes compared: `json`, `ordo-code`, `json,ordo-code`
- API/model calls: none
- Score weight changes: none

## Dry-run baseline

| Metric | Result |
|---|---:|
| Scenarios | 20 |
| Runtime views | json, ordo-code, json,ordo-code |
| Expected cases | 60 |
| Completed cases | 60 |
| Passed cases | 60 |
| RAW_METRICS rows | 60 |
| Score artifacts | 60 |
| Gate pass rate | 1.0 |
| Mean path quality score | 1.0 |
| Protocol compliance failures | 0 |

## Runtime-view comparison

| Runtime view | Cases | Mean path quality | Min | Max | Mean protocol compliance |
|---|---:|---:|---:|---:|---:|
| `json` | 20 | 1.0 | 1.0 | 1.0 | 1.0 |
| `json,ordo-code` | 20 | 1.0 | 1.0 | 1.0 | 1.0 |
| `ordo-code` | 20 | 1.0 | 1.0 | 1.0 | 1.0 |

## Validation checks

- `py_compile` for `cli` + `ordo_pathwalk`: passed.
- PathWalk pytest in workspace context: `22/22 passed`.
- PathWalk pytest from standalone RC with workspace CLI on `PYTHONPATH`: `22/22 passed`.
- `dry-run-plan`: passed.
- Independent generated job scripts: `60/60 passed`.
- `dry-run-collect`: passed.
- Metadata completeness: canonical IR hash, targets manifest hash and session trace hash present for all `60` raw metric rows.

## Artifact evidence

Compact evidence is stored in:

```text
reports/m60_6_calibration_prep_baseline/
├── DRY_RUN_PLAN.json
├── JOB_EXECUTION.md
├── jobs/*.json
├── job_scripts/*.sh
├── scores/*_score.json
├── RAW_METRICS.csv
├── SUMMARY.json
├── SUMMARY.md
├── scenarios/*.json
└── job_logs/*.log
```

The same compact evidence is mirrored into:

```text
ordo_pathwalk/examples/m60_6_calibration_prep_baseline/
```

Bulky runtime sandboxes were not copied into the release package. They are generated execution outputs, not the compact artifact contract required for calibration preparation.

## What this does not prove

- This is not a real model-quality benchmark.
- This does not calibrate or change scoring weights.
- This does not prove performance on a real module source YAML.
- This does not introduce M60.7 / M61.0 real-module testcase generation.

## Execution note

In this ChatGPT sandbox, long parent-loop orchestration hit tool lifecycle limits. The final acceptance therefore used the generated independent `job_scripts/*.sh` in small batches. That is the intended M60.5.4 artifact-only execution path and is the path accepted for M60.6.

## Release decision

M60.6 can be released as **Benchmark Dry Run / Calibration Preparation**. Default weights remain unchanged.
