# M60.6.3 — Model Benchmark Protocol Design

Status: `protocol-ready / no-model-run`  
Date: 2026-07-08  
Scope: PathWalk companion utility protocol, reporting, and documentation only

## Purpose

M60.6.3 defines the benchmark protocol that must exist before running real model/API or transcript-based PathWalk benchmarks for calibration.

M60.6 and M60.6.2 proved that the artifact-only dry-run path is stable, but they also proved that dry-run data cannot calibrate `path_quality_score` weights: all cases passed and all component metrics were saturated at `1.0`.

This protocol answers the next question:

```text
What must a real model benchmark capture before weights may be discussed?
```

## Non-goals

M60.6.3 does not:

- run a real model/API benchmark;
- change default scorer weights;
- change Ordo runtime semantics;
- introduce MCP or sandbox dependency into runtime;
- start M60.7/M61 real-module testcase generation;
- require PDF/book regeneration.

## Benchmark modes

M60.6.3 defines two allowed benchmark input modes.

### 1. API-driven benchmark mode

A model is run against generated PathWalk scenarios through the PathWalk harness.

Required properties:

- each job is independent;
- enforced runtime mode uses only `./cli_embedded/ordo`;
- direct `compiled/*` reading remains a protocol violation;
- every model turn and tool call is captured as transcript evidence;
- API credentials are never written to artifacts;
- runtime views are compared on the same scenario IDs.

### 2. Transcript-replay benchmark mode

A previously captured model interaction is scored without calling a live API.

Required properties:

- transcript schema version is explicit;
- scenario/runtime_view/model identity is preserved;
- tool calls are recorded with command, exit status, truncated output, and digest;
- scoring reads persisted runtime artifacts and transcript evidence, not narrative self-report;
- transcript replay can be used for deterministic regression of known model behavior.

Transcript replay is the safer first pilot after M60.6.3 because it avoids API instability while still introducing non-perfect model behavior if transcripts contain real mistakes.

## Required artifact contract

A valid model benchmark run must produce this artifact set:

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

Optional artifacts:

```text
job_scripts/<job_id>.sh          # for shell/CI matrix execution
reports/runtime_view_matrix.csv
reports/model_comparison.csv
reports/failure_bucket_summary.csv
reports/protocol_violation_summary.csv
```

The dry-run artifacts from M60.6 remain valid readiness evidence, but they are not a substitute for `RAW_MODEL_METRICS.csv`.

## MODEL_BENCHMARK_PLAN.json minimum fields

```json
{
  "benchmark_protocol_version": "M60.6.3",
  "benchmark_mode": "api-driven | transcript-replay",
  "scenario_set_id": "<stable-id>",
  "scenario_count": 30,
  "runtime_views": ["json", "ordo-code", "json,ordo-code"],
  "cli_mode": "enforced",
  "models": [
    {
      "provider": "<provider>",
      "model": "<model-name-or-alias>",
      "driver": "<driver-id>",
      "temperature": 0
    }
  ],
  "seed_policy": "fixed-and-recorded",
  "artifact_only_execution": true,
  "weights_locked": true
}
```

## Transcript schema minimum fields

Each transcript must expose at least:

```json
{
  "schema_version": "pathwalk.model_transcript.v1",
  "benchmark_protocol_version": "M60.6.3",
  "job_id": "scenario_000_json_model_a",
  "scenario_id": "scenario_000",
  "runtime_view": "json",
  "cli_mode": "enforced",
  "model": {
    "provider": "<provider>",
    "name": "<model>",
    "driver": "<driver-id>"
  },
  "started_at": "<iso8601>",
  "completed_at": "<iso8601>",
  "result_status": "completed | failed | timeout | protocol_violation",
  "turns": [
    {
      "turn_index": 1,
      "user_prompt": "<prompt shown to model>",
      "model_response": "<model text>",
      "tool_calls": [
        {
          "command": "./cli_embedded/ordo next-step . --format auto",
          "exit_code": 0,
          "stdout_sha256": "<digest>",
          "stderr_sha256": "<digest-or-empty>",
          "output_truncated": true
        }
      ]
    }
  ],
  "redaction": {
    "api_keys_removed": true,
    "secrets_removed": true
  }
}
```

## RAW_MODEL_METRICS.csv minimum columns

Required columns:

```text
job_id
scenario_id
runtime_view
cli_mode
benchmark_mode
provider
model
driver
seed
status
path_quality_score
cell_match_rate
protocol_compliance_rate
distraction_recovery_rate
backtrack_accuracy
turn_accuracy_rate
invalid_branch_rejection_rate
skip_ahead_resistance_rate
clarification_handling_rate
correction_recovery_rate
restore_session_usage_rate
direct_compiled_access_violations
tool_call_count
turn_count
completion_latency_ms
error_type
failure_bucket
score_schema_version
weights_hash
canonical_ir_hash
targets_manifest_hash
session_trace_hash
transcript_sha256
```

Additional columns are allowed, but these fields are the minimum contract for calibration analysis.

## Failure bucket taxonomy

Each failed or non-perfect job must be assigned one primary bucket:

| Bucket | Meaning |
|---|---|
| `protocol_violation` | model bypassed the runtime protocol, e.g. direct compiled access |
| `wrong_branch` | model selected a wrong decision-tree branch |
| `invalid_submit` | model submitted an answer rejected by runtime |
| `missed_backtrack` | model failed to recover after correction/backtrack |
| `distraction_followed` | model followed irrelevant/distraction instruction |
| `skip_ahead` | model attempted to bypass required node order |
| `clarification_failure` | model failed to ask or use clarification correctly |
| `timeout_or_loop` | model failed to complete within turn/tool limits |
| `runtime_error` | runtime/package failure, not model quality |
| `scorer_error` | scorer/aggregation failure |

Calibration analysis must separate model-quality failures from runtime/scorer failures.

## Calibration eligibility gates

Weights must remain locked unless all gates below pass.

| Gate | Requirement |
|---|---|
| `same_scenario_matrix` | the same scenario IDs are run for each compared runtime view/model |
| `sufficient_cases` | at least 30 cases per runtime view per model for pilot analysis, larger before release calibration |
| `nonzero_variance` | at least one primary component metric has nonzero variance |
| `non_saturated_scores` | not all `path_quality_score` values are `1.0` |
| `failure_buckets_present` | non-perfect cases are bucketed and reviewed |
| `protocol_vs_quality_separated` | protocol violations are separated from path-quality mistakes |
| `metadata_hashes_captured` | IR, target manifest, session trace, transcript, and weights hashes are present |
| `repeatability_checked` | repeated seeds/runs show whether results are stable enough to compare |
| `confidence_summary_present` | distributions or confidence intervals are reported, not only means |
| `manual_failure_review_done` | a sample of failed transcripts is manually inspected before changing weights |
| `calibration_decision_recorded` | proposed weight changes are documented in `CALIBRATION_DECISION.*` |

Failing any gate means: keep weights unchanged.

## Weight-change policy

No scorer weight may be changed directly from benchmark output.

Allowed path:

```text
benchmark artifacts
  → calibration analysis
  → failure-bucket review
  → calibration decision report
  → explicit milestone approval
  → scoped scorer patch
  → regression + dry-run + model-benchmark revalidation
```

M60.6.3 therefore keeps the current default weights:

```json
{
  "cell_match_rate": 0.45,
  "protocol_compliance_rate": 0.25,
  "distraction_recovery_rate": 0.15,
  "backtrack_accuracy": 0.15
}
```

## Runtime-view comparison rule

Runtime views may be compared only when all of the following are true:

```text
same scenario IDs
same benchmark mode
same model/provider/driver configuration
same scorer version
same weight hash
same runtime protocol version
same random seed policy
same timeout/tool limits
```

Otherwise the comparison is descriptive only and must not drive calibration.

## Security and privacy rules

Benchmark artifacts must not contain:

- API keys;
- bearer tokens;
- private account identifiers;
- raw provider request headers;
- full unredacted secret-bearing environment variables.

Allowed:

- provider/model names;
- timestamped run metadata;
- hashed/truncated tool outputs;
- redacted prompts and transcripts when needed.

## Acceptance criteria for the next executable milestone

A future M60.6.4 pilot can be considered valid if it produces:

- one explicit `MODEL_BENCHMARK_PLAN.json`;
- at least one API-driven or transcript-replay job;
- transcript artifacts matching the schema contract;
- `RAW_MODEL_METRICS.csv` with the minimum columns;
- `SUMMARY.md` distinguishing readiness, model-quality signal, and calibration eligibility;
- a `CALIBRATION_DECISION.md` that either keeps weights unchanged or explains why gates allow a proposed change.

## Deferred work

M60.7/M61 real-module testcase generation remains deferred until the model benchmark protocol has at least one pilot run with real model behavior or equivalent transcripts.

## M60.6.4 pilot status

M60.6.4 implements the first executable transcript-replay pilot for this protocol.

Pilot properties:

```text
benchmark_mode: transcript-replay
provider/model: offline / synthetic-transcript-pilot
acceptance subset: 3 scenarios × json runtime_view
artifact contract: MODEL_BENCHMARK_PLAN → transcripts → scores → RAW_MODEL_METRICS → SUMMARY → CALIBRATION_DECISION
```

The pilot deliberately includes three evidence classes:

```text
perfect path → failure_bucket=none
distraction/model-quality miss → failure_bucket=distraction_followed
enforced-mode direct compiled access → failure_bucket=protocol_violation
```

This proves nonzero variance and failure-bucket plumbing, but it does not unlock calibration. The pilot is below the required case count, has no repeatability analysis, has no confidence interval summary, and does not include manual review of real model failures. Therefore `path_quality_score` weights remain locked.
