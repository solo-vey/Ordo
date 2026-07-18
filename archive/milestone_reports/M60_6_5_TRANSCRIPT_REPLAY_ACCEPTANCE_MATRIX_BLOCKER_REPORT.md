# M60.6.5 Transcript Replay Acceptance Matrix — Blocker Report

Status: `blocked-no-release`

## Scope

Attempted next step after M60.6.4:

```text
M60.6.5 — Transcript Replay Acceptance Matrix
```

Goal: expand the M60.6.4 no-API transcript replay pilot from a tiny single-runtime pilot into a compact acceptance matrix across all supported runtime views:

```text
json
ordo-code
json,ordo-code
```

The milestone was intended to remain no-API / transcript-replay only. It was not intended to change runtime-core semantics or scorer weights.

## Result

M60.6.5 is **not released**.

The expansion attempt exposed a parent-loop execution blocker in the transcript-replay path. During `create_transcript_replay_pilot(...)`, the Python parent process can hang while waiting for embedded runtime CLI subprocess completion inside the transcript replay driver.

Observed hanging locations during attempts:

```text
ordo_pathwalk/runner/model_benchmark.py
  _drive_ground_truth_for_model_benchmark(...)
    embedded CLI intake / verify-targets boundary
```

Earlier attempt using the existing matrix-smoke driver showed the same class of issue:

```text
ordo_pathwalk/runner/matrix_smoke.py
  _drive_ground_truth(...)
    verify-targets boundary
```

The generated runtime sandbox itself is not obviously corrupt: when commands are re-run manually after the parent timeout, commands such as `verify-targets` and `verify-session` complete successfully. The blocker appears tied to parent-loop subprocess handling / process-boundary behavior in the new transcript-replay matrix expansion path, not to the M60.6.4 released baseline artifacts.

## What was tried

Non-released experimental patches were attempted and captured as diffs in the evidence bundle:

1. Expanded transcript replay to a multi-runtime matrix.
2. Balanced synthetic behavior buckets by cycling:
   - `perfect`
   - `distraction_failure`
   - `protocol_violation`
3. Added a runtime-safe direction pool to avoid using `back` as a generated single-select branch label.
4. Tried replacing inherited matrix-smoke runtime driving with a model-benchmark-specific runtime driver.
5. Tried OS-level `timeout --kill-after=1s` and file-backed stdout/stderr to avoid pipe inheritance issues.

These patches were **not accepted** and **not released**, because the parent-loop hang was still reproducible.

## Validation performed

Stable M60.6.4 base was rechecked from clean extraction for lightweight sanity:

```text
clean M60.6.4 py_compile: passed
selected PathWalk tests: 11 passed
```

This confirms the blocker belongs to the attempted M60.6.5 expansion path, not to a decision to invalidate M60.6.4.

## Release decision

```text
M60.6.5 release: blocked
Do not package M60.6.5 as stable
Do not change weights
Do not modify Ordo runtime-core semantics
Keep M60.6.4 as the latest stable transcript-replay pilot baseline
```

## Recommended next step

Before retrying M60.6.5, add a smaller technical hardening milestone:

```text
M60.6.4.1 — Transcript Replay Process Boundary Hardening
```

Recommended scope:

1. Do not expand the benchmark matrix yet.
2. Isolate transcript replay job execution into one process per job, similar to the M60.5.4 artifact-only dry-run contract.
3. Materialize transcript replay job descriptors and executable job scripts.
4. Use collect-only aggregation after independent job completion.
5. Only after that, retry M60.6.5 acceptance matrix.

Suggested contract:

```text
model-benchmark-plan → independent transcript-replay-job invocations → model-benchmark-collect
```

This mirrors the successful artifact-only dry-run pattern and avoids a long-lived parent Python loop holding all embedded runtime subprocesses.

## Calibration decision

Weights remain locked.

Reason: no accepted M60.6.5 matrix evidence exists, and M60.6.4 was explicitly only a small pilot, not a calibration run.

## Impact classification

Expected change level for this blocker report: `L0`.

Expected change level for the recommended future fix: `L1` for PathWalk companion utility process-boundary orchestration; `L0` for Ordo runtime core and scoring weights.
