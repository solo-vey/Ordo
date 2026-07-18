# M60.7.5 — Bounded Noise Testcase Artifacts

Status: **passed-implementation-slice**

## Scope

M60.7.5 extends the artifact-only real-module noise testcase generator with two additional bounded patterns:

- `clarification_without_submit`
- `skip_ahead`

Together with M60.7.4, the supported artifact-only patterns are now:

```text
distraction
invalid_branch
clarification_without_submit
skip_ahead
```

## Boundary decision

This milestone intentionally closes the current noise-expansion line. Remaining complex conversational patterns such as `backtrack` and `correction_backtrack` are recorded as future improvements and are not blockers.

The reason is scope control: continuing to add one small noise variant per milestone would turn M60.7 into an endless low-value patch chain.

## Implemented artifacts

`real-module-noise-cases` emits:

```text
cases/<case_id>.json
cases/<case_id>.md
RAW_NOISE_TESTCASE_MATRIX.csv
SUMMARY.json
SUMMARY.md
VALIDATION_REPORT.json
```

## Sample result

On `sample.support_triage`:

```text
terminal_paths_input: 3
patterns: 4
noise_cases: 12
ready_cases: 12
runtime_execution_ready: false
scoring_ready: false
calibration_ready: false
```

## Validation

Passed:

- workspace `py_compile`
- selected non-runtime PathWalk pytest: `20 passed`
- workspace graph → paths → noise-cases smoke
- default pattern smoke
- PathWalk RC `py_compile`
- PathWalk RC graph → paths → noise-cases CLI smoke
- book source manifest sanity
- clean zip extraction check

Not used as gate:

- runtime-harness / transcript-replay matrix tests, because that branch is already known blocked from M60.6.5 / M60.6.4.1 and is not relevant to artifact-only source-level testcase generation.
- PathWalk RC pytest as a final gate; RC CLI smoke passed, and workspace selected tests passed.

## Unchanged

- Ordo runtime-core semantics were not changed.
- Scoring weights were not changed.
- Real model/API benchmark was not run.
