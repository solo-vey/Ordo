# M60.6.4 Transcript Replay Model Benchmark Pilot Summary

Status: `passed-pilot`
Benchmark mode: `transcript-replay`
Completed cases: `3/3`
Weights locked: `True`
Calibration eligible: `False`

## Runtime view matrix

| runtime_view | cases | passed | non_perfect | score_min | score_mean | score_max |
|---|---:|---:|---:|---:|---:|---:|
| `json` | 3 | 1 | 2 | 0.75 | 0.8667 | 1.0 |

## Failure buckets

- `distraction_followed`: 1
- `none`: 1
- `protocol_violation`: 1

## Calibration eligibility gates

- `same_scenario_matrix`: passed — same scenario IDs are present for each runtime view
- `sufficient_cases`: failed — pilot has 3 cases per runtime view; protocol requires >=30 for calibration
- `nonzero_variance`: passed — pilot includes perfect and non-perfect transcript evidence
- `non_saturated_scores`: passed — not all path_quality_score values are 1.0
- `failure_buckets_present`: passed — {'none': 1, 'distraction_followed': 1, 'protocol_violation': 1}
- `protocol_vs_quality_separated`: passed — {'none': 1, 'distraction_followed': 1, 'protocol_violation': 1}
- `metadata_hashes_captured`: passed — IR, targets manifest, session trace, transcript hashes checked
- `repeatability_checked`: failed — not checked in M60.6.4 pilot
- `confidence_summary_present`: failed — pilot reports descriptive statistics only
- `manual_failure_review_done`: failed — synthetic pilot failures were not manually reviewed as real model failures
- `calibration_decision_recorded`: passed — CALIBRATION_DECISION.md/.json generated

## Decision

Weights remain locked. This pilot validates the transcript-replay artifact contract and failure buckets only.
