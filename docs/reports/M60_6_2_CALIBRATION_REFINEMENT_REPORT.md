# M60.6.2 — Calibration Report Refinement

Status: `passed-with-calibration-blocker`  
Date: 2026-07-08  
Scope: analysis/documentation only  

## Purpose

M60.6.2 refines the calibration-preparation report after the M60.6 dry-run baseline and the M60.6.1 clean-room release-integrity hardening.

This milestone does **not** change Ordo runtime semantics, PathWalk scorer weights, runtime packaging modes, or the default `path_quality_score` formula.

## Input evidence

The refinement uses the existing artifact-only dry-run evidence:

```text
DRY_RUN_PLAN.json
jobs/*.json
job_scripts/*.sh
scores/*_score.json
RAW_METRICS.csv
SUMMARY.json
SUMMARY.md
```

Baseline shape:

```text
20 scenarios × 3 runtime views = 60 dry-run cases
runtime views: json, ordo-code, json,ordo-code
driver: benchmark-dry-run-ground-truth
cli mode: enforced
```

## Runtime-view comparison

| runtime_view | cases | passed | gate_pass_rate | mean path_quality_score | stdev |
|---|---:|---:|---:|---:|---:|
| `json` | 20 | 20 | 1.00 | 1.00 | 0.00 |
| `ordo-code` | 20 | 20 | 1.00 | 1.00 | 0.00 |
| `json,ordo-code` | 20 | 20 | 1.00 | 1.00 | 0.00 |

All runtime views passed all 20 cases. Under the dry-run ground-truth driver, there is no observed runtime-view quality difference.

## Metric variance summary

| metric | mean | min | max | stdev | calibration signal |
|---|---:|---:|---:|---:|---|
| `path_quality_score` | 1.00 | 1.00 | 1.00 | 0.00 | `absent_zero_variance` |
| `cell_match_rate` | 1.00 | 1.00 | 1.00 | 0.00 | `absent_zero_variance` |
| `protocol_compliance_rate` | 1.00 | 1.00 | 1.00 | 0.00 | `absent_zero_variance` |
| `distraction_recovery_rate` | 1.00 | 1.00 | 1.00 | 0.00 | `absent_zero_variance` |
| `backtrack_accuracy` | 1.00 | 1.00 | 1.00 | 0.00 | `absent_zero_variance` |
| `turn_accuracy_rate` | 1.00 | 1.00 | 1.00 | 0.00 | `absent_zero_variance` |


## Weight status

Default PathWalk scoring weights were inspected from score artifacts and remain unchanged:

```json
{
  "backtrack_accuracy": 0.15,
  "cell_match_rate": 0.45,
  "distraction_recovery_rate": 0.15,
  "protocol_compliance_rate": 0.25
}
```

M60.6.2 intentionally does not alter these weights.

## Calibration decision

The M60.6 dry-run baseline is valid as readiness evidence, but it is not sufficient for weight calibration.

Reason:

```text
All cases passed and all component metrics are saturated at 1.0.
The dataset has zero metric variance.
A zero-variance ground-truth dry-run cannot show which metric weights should change.
```

Therefore the correct decision is:

```text
Do not change path_quality_score weights from M60.6 dry-run data.
Use the data as infrastructure readiness evidence only.
```

## Evidence needed before real calibration

Before changing weights, collect a dataset with real model behavior or equivalent transcripts that include variance:

- model/API-driven runs or equivalent model-behavior transcripts;
- non-perfect and failed cases;
- per-noise-type labels and metrics;
- repeated runs across seeds and/or models;
- the same scenario set across `json`, `ordo-code`, and `json,ordo-code` runtime views;
- explicit distinction between protocol violations and path-quality mistakes;
- confidence intervals or at least distribution summaries, not only means.

## Added artifacts

- `M60_6_2_CALIBRATION_REFINEMENT_REPORT.md`
- `M60_6_2_CALIBRATION_REFINEMENT_REPORT.json`
- `M60_6_2_VALIDATION_REPORT.json`
- `reports/m60_6_2_calibration_refinement/RUNTIME_VIEW_COMPARISON.csv`
- `reports/m60_6_2_calibration_refinement/METRIC_VARIANCE_SUMMARY.csv`
- `reports/m60_6_2_calibration_refinement/RUNTIME_METADATA_HASH_SUMMARY.csv`

## Validation summary

| Check | Result |
|---|---|
| `RAW_METRICS.csv` present | passed |
| Expected case count = 60 | passed |
| Score artifacts count = 60 | passed |
| Runtime views compared | passed |
| Default weights unchanged | passed |
| Runtime-core semantics unchanged | passed |
| Real model/API benchmark avoided | passed |
| PDF/book generation avoided | passed |


Additional execution checks performed for M60.6.2 packaging:

| Check | Result |
|---|---|
| Workspace `py_compile` | passed |
| Workspace PathWalk pytest | passed: 22/22 |
| PathWalk RC v9.6.2 + developer bundle pytest | passed: 22/22 |
| Raw metrics sanity | passed: 60 cases, all component metrics 1.0 |
| Book source manifest/structure sanity | passed |
| Final zip extraction key files | passed |

## Next recommended milestone

M60.6.2 closes calibration-preparation reporting. The next safe step is not weight calibration yet. Recommended next milestone:

```text
M60.6.3 — Model Benchmark Protocol Design
```

That milestone should define how to run real model/API or transcript-based benchmark jobs, what raw metrics must be captured, and how calibration decisions are allowed to be made.

M60.7/M61 real-module testcase generation should remain deferred until the model benchmark protocol is explicit.

## Очікуваний рівень змін

Expected change level: `L0 — documentation/reporting/evidence only`  
Code locality: no runtime or scorer code changes  
Shared/base classes impact: none  
Configuration impact: none  
Database/migration impact: none  
Public/API contract impact: none  
Testing impact: report-level validation only  
Recommended delivery mode: safe documentation/evidence milestone
