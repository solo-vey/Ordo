# M76.4 — PathWalk Purpose and Calibration Closure

Status: `passed`

## Decision

PathWalk primary purpose is **Ordo release QA**. Benchmark-pinned model comparison is secondary; compatibility-current runs are regression evidence; research use is exploratory only.

## Calibration result

The default weights remain unchanged and are provisionally locked. This is a deliberate calibration decision, not an omission: existing dry-run evidence is saturated and the synthetic three-case pilot is too small for statistical re-estimation.

A machine-readable eligibility gate now prevents weight changes until an adequate real-model dataset exists.

## Production interpretation

Hard release gates dominate `path_quality_score`. A weighted score cannot compensate for runtime completion failure, protocol noncompliance, direct compiled access, incomplete category coverage, or invalid evidence.

## Added artifacts

- `ordo_pathwalk/BENCHMARK_PURPOSE_AND_CALIBRATION.md`
- `ordo_pathwalk/calibration_profile.json`
- `ordo_pathwalk/runner/calibration.py`
- `ordo_pathwalk/tests/test_calibration_policy.py`

## Verdict

BL-ORDO-006 is closed for purpose definition and calibration governance. Statistical re-estimation of weights remains intentionally locked until the eligibility gate is satisfied.
