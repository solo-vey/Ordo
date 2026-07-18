# M60.6.4 — Transcript Replay / Model Benchmark Pilot Report

Status: `passed-pilot / calibration-locked`

## Scope

M60.6.4 validates the M60.6.3 model benchmark protocol with a small no-API transcript-replay pilot. It adds an executable PathWalk companion utility path for generating and collecting model-benchmark artifacts without calling a live API provider.

## What changed

- Added `ordo_pathwalk/runner/model_benchmark.py`.
- Added CLI commands:
  - `model-benchmark-pilot`
  - `model-benchmark-collect`
- Added regression test: `ordo_pathwalk/tests/test_model_benchmark_pilot.py`.
- Added pilot artifacts under `reports/m60_6_4_transcript_replay_pilot/`.
- Added compact sample artifacts under `ordo_pathwalk/examples/m60_6_4_transcript_replay_pilot/`.
- Updated PathWalk protocol/docs/book source notes.

## Pilot execution

Acceptance subset:

```text
benchmark_mode: transcript-replay
provider/model: offline / synthetic-transcript-pilot
runtime_view: json
scenario_count: 3
completed_cases: 3/3
```

Evidence classes:

| Case | Intended behavior | Expected bucket |
|---|---|---|
| scenario_000_json_transcript-replay | perfect transcript evidence | `none` |
| scenario_001_json_transcript-replay | distraction/model-quality miss | `distraction_followed` |
| scenario_002_json_transcript-replay | direct `compiled/*` access in enforced mode | `protocol_violation` |

## Metrics summary

| job_id | score | protocol | distraction | bucket |
|---|---:|---:|---:|---|
| `scenario_000_json_transcript-replay` | 1.0 | 1.0 | 1.0 | `none` |
| `scenario_001_json_transcript-replay` | 0.85 | 1.0 | 0.0 | `distraction_followed` |
| `scenario_002_json_transcript-replay` | 0.75 | 0.0 | 1.0 | `protocol_violation` |


Failure buckets:

```json
{
  "none": 1,
  "distraction_followed": 1,
  "protocol_violation": 1
}
```

Calibration eligibility: `False`.

## Calibration decision

`path_quality_score` weights remain locked.

Reason: M60.6.4 proves the transcript-replay artifact contract, nonzero variance, and failure bucket plumbing, but it is not a statistically sufficient calibration run. It intentionally fails calibration gates for sufficient case count, repeatability, confidence summary, and manual review of real model failures.

## Validation

- `py_compile` for `cli/` and `ordo_pathwalk/`: passed.
- PathWalk class/file-split pytest: passed for existing and new tests.
- New transcript-replay pilot test: passed.
- CLI pilot run: passed for 3/3 `json` transcript-replay cases.
- `model-benchmark-collect` repeatability: passed.
- Final zip extraction check: passed.
- PathWalk RC v9.6.4 + developer bundle pytest for `test_model_benchmark_pilot.py`: passed.
- PathWalk RC v9.6.4 + developer bundle CLI pilot smoke: passed, 3/3 cases.

## Not done

- No live model/API benchmark was run.
- No scorer weights were changed.
- No Ordo runtime-core semantics were changed.
- Full 3-runtime-view transcript pilot was not used as acceptance in this sandbox; previous M60.6/M60.6.2 evidence already covers runtime-view dry-run comparison, while M60.6.4 validates the transcript-replay protocol path.

## Expected change level

`L1` for PathWalk companion utility CLI/reporting.

`L0` for Ordo runtime core and scorer weights.
