# M60.6.3 — Model Benchmark Protocol Design

Status: `passed-design-only`  
Date: 2026-07-08  
Scope: protocol/reporting/docs only  
Base: M60.6.2 calibration refinement

## Purpose

M60.6.3 defines the protocol required before running a real PathWalk model/API benchmark or a transcript-replay benchmark.

The previous M60.6.2 milestone confirmed that dry-run data is valid infrastructure readiness evidence but cannot calibrate `path_quality_score` weights because all 60 cases had saturated metrics. M60.6.3 therefore adds the missing benchmark contract rather than changing weights.

## Added protocol artifact

Primary protocol document:

```text
ordo_pathwalk/MODEL_BENCHMARK_PROTOCOL.md
```

The protocol defines:

- allowed benchmark modes: `api-driven` and `transcript-replay`;
- required artifact contract;
- minimum `MODEL_BENCHMARK_PLAN.json` fields;
- transcript schema minimum fields;
- minimum `RAW_MODEL_METRICS.csv` columns;
- failure bucket taxonomy;
- calibration eligibility gates;
- security/privacy rules;
- weight-change policy.

## Key decision

```text
M60.6.3 does not permit weight calibration by itself.
It only defines the protocol that future model benchmark evidence must satisfy.
```

Weights remain locked unless a future benchmark passes calibration eligibility gates.

## Required future benchmark artifacts

```text
MODEL_BENCHMARK_PLAN.json
jobs/<job_id>.json
transcripts/<job_id>_transcript.json
scores/<job_id>_score.json
RAW_MODEL_METRICS.csv
SUMMARY.json
SUMMARY.md
MODEL_RUN_MANIFEST.json
CALIBRATION_DECISION.md
CALIBRATION_DECISION.json
```

## Calibration gates added

| Gate | Meaning |
|---|---|
| `same_scenario_matrix` | compare runtime views/models only on the same scenario IDs |
| `sufficient_cases` | pilot: at least 30 cases per runtime view per model |
| `nonzero_variance` | at least one primary metric must vary |
| `non_saturated_scores` | not all `path_quality_score` values may be `1.0` |
| `failure_buckets_present` | non-perfect cases must be classified |
| `protocol_vs_quality_separated` | protocol violations separated from path mistakes |
| `metadata_hashes_captured` | IR/target/session/transcript/weights hashes present |
| `repeatability_checked` | repeated seeds/runs checked before comparing |
| `confidence_summary_present` | distributions or confidence intervals reported |
| `manual_failure_review_done` | failed transcripts sampled manually |
| `calibration_decision_recorded` | `CALIBRATION_DECISION.*` written |

Failing any gate means weights stay unchanged.

## Changes made

Documentation/reporting only:

- added `ordo_pathwalk/MODEL_BENCHMARK_PROTOCOL.md`;
- added report-level CSV summaries under `reports/m60_6_3_model_benchmark_protocol/`;
- added root and `docs/reports` M60.6.3 reports;
- updated workspace, developer bundle, and PathWalk README/changelog notes;
- updated book markdown source with a new chapter 60;
- updated book manifest and structure audit;
- did not regenerate compiled book/PDF.

## Validation summary

| Check | Result |
|---|---|
| Workspace `py_compile` | passed |
| Workspace PathWalk pytest | passed: 22/22 |
| PathWalk RC + developer bundle pytest | passed: 22/22 |
| Protocol document present | passed |
| Required artifact contract defined | passed |
| Transcript schema minimum defined | passed |
| Raw model metrics minimum columns defined | passed |
| Calibration gates defined | passed |
| Weights unchanged | passed |
| Runtime-core semantics unchanged | passed |
| Real model/API benchmark avoided | passed |
| PDF/book generation avoided | passed |

## Next recommended milestone

Recommended next step:

```text
M60.6.4 — Transcript Replay / Model Benchmark Pilot
```

The safest first pilot is transcript replay: score at least a small set of captured model-behavior transcripts against the M60.6.3 protocol before spending API budget on a larger live benchmark.

## Очікуваний рівень змін

Expected change level: `L0 — protocol/documentation/reporting only`  
Code locality: no runtime/scorer code changes  
Shared/base classes impact: none  
Configuration impact: none  
Database/migration impact: none  
Public/API contract impact: none  
Testing impact: existing PathWalk regression validation only  
Recommended delivery mode: safe protocol milestone before model benchmark execution
