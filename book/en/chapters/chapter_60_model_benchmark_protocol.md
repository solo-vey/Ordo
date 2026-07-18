# Chapter 60. Model Benchmark Protocol

## Why this chapter exists

After M60.6, Ordo has a stable no-API PathWalk dry-run baseline. But a dry-run baseline is not a real model benchmark: the ground-truth driver traverses the tree ideally, so component metrics can all equal `1.0`.

M60.6.3 defines the next layer: the real model benchmark protocol.

The main rule is:

```text
Dry-run proves wiring.
Model benchmark measures behavior.
Calibration requires variance.
```

## Why weights cannot be changed immediately

M60.6.2 confirmed a perfect dry-run baseline:

```text
60/60 cases passed
all component metrics = 1.0
metric variance = 0
```

This proves infrastructure readiness. It does not show which `path_quality_score` weights are better.

Therefore:

```text
weights remain locked until real model or transcript evidence passes calibration gates
```

## Two allowed benchmark modes

### API-driven benchmark

A model actually traverses scenarios through the PathWalk harness.

In enforced mode, it must interact only through the runtime CLI:

```bash
./cli_embedded/ordo next-step . --format auto
./cli_embedded/ordo intake . --submit <NODE_ID> --answer-file <file>
./cli_embedded/ordo restore-session . --to-seq <N> --reason "..."
./cli_embedded/ordo verify-session .
```

Direct reading of `compiled/*` is forbidden.

### Transcript-replay benchmark

Instead of a live API, the benchmark consumes a previously recorded transcript of model behavior.

This is a safer first pilot because scoring and failure buckets can be validated without external-provider cost and nondeterminism.

## Required artifacts

A minimum model benchmark produces:

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

The benchmark must retain transcript evidence, not only a final score.

## Failure categories matter

A model can reach the correct terminal node while violating the runtime protocol. Therefore benchmark analysis must separate:

```text
path-quality mistakes
protocol violations
runtime-integrity failures
compiled-read violations
noise-recovery failures
```

An aggregate score must not hide these categories.

## Calibration gate

Calibration requires real variation. Evidence should include failed and non-perfect cases, multiple noise types, and repeated runs where nondeterminism matters.

Until those conditions are met:

```text
calibration = blocked
weights = unchanged
```

## Protocol boundary

The benchmark harness measures model behavior. It does not replace the embedded runtime CLI, create runtime evidence on behalf of the CLI, or silently repair model mistakes.

The benchmark must observe the process as it actually happened.

## Summary

```text
Dry-run proves the experiment can run.
Transcript replay proves scoring can interpret behavior.
Live model runs measure actual behavior.
Calibration changes weights only after sufficient variance exists.
```
