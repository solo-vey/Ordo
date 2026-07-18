# Chapter 59. PathWalk Benchmark Readiness

The previous chapter added safe backtracking through `restore-session`. This made PathWalk scenarios with backtrack and correction technically possible in the current Ordo runtime protocol.

Before expensive benchmark runs against external models, however, another question must be answered: is the testing utility itself correctly connected to the current runtime package?

That is the purpose of PathWalk Benchmark Readiness.

## Why a readiness smoke test is needed

PathWalk is not part of the runtime core. It is a companion utility for checking how a model traverses Ordo scenarios.

Before real API runs, the infrastructure itself must be checked:

- PathWalk builds an M60 runtime package;
- it uses `./cli_embedded/ordo`, not the old `ordo_run.py`;
- all supported runtime views work;
- the correct runtime artifacts are inspected;
- score files are generated;
- aggregate summaries work.

This is done with a cheap no-API smoke test.

## Matrix smoke

Example:

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli matrix-smoke \
  --out /tmp/pathwalk_matrix_smoke \
  --depth 2 \
  --branching 2 2 \
  --force
```

The matrix covers:

```text
enforced + json
enforced + ordo-code
enforced + json,ordo-code
```

This is not a real model-quality test. PathWalk follows ground truth through the embedded CLI. The purpose is to prove that protocol, scorer, and aggregator are connected correctly.

## What readiness does and does not prove

A passing smoke test proves wiring readiness. It does not prove that a model behaves well.

The distinction is essential:

```text
wiring readiness != model quality
perfect dry-run != calibrated benchmark
```

A ground-truth driver is expected to produce perfect or near-perfect metrics. That means the infrastructure can execute the experiment, not that the metric weights are correct.

## Calibration remains blocked without variance

Before real calibration, PathWalk needs evidence containing:

- non-perfect cases;
- failed cases;
- per-noise-type labels;
- repeated seeds or model runs;
- a clear distinction between protocol violations and path-quality mistakes.

If every component metric equals `1.0`, there is no useful variance for calibrating score weights.

## Practical conclusion

PathWalk Benchmark Readiness is a preflight gate:

```text
first prove the harness is wired correctly;
then run real model or transcript evidence;
only then discuss calibration.
```

This keeps benchmark claims honest and prevents infrastructure readiness from being mislabeled as model-quality evidence.
