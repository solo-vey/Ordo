# M60.7.4 — Noise Testcase Artifacts Report

Status: `passed-implementation-slice`

## Scope

M60.7.4 adds first artifact-only noise testcase generation for real-module terminal paths.

Implemented patterns:

- `distraction`
- `invalid_branch`

Explicitly out of scope:

- runtime execution
- scoring
- calibration
- benchmark/watchdog orchestration
- remaining noise patterns: `backtrack`, `skip_ahead`, `clarification_without_submit`, `correction_backtrack`

## Implemented artifacts

The new CLI command is:

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-noise-cases   --paths runs/real_module_paths/REAL_MODULE_TERMINAL_PATHS.json   --out runs/real_module_noise_cases   --pattern distraction   --pattern invalid_branch   --force
```

Generated files:

```text
cases/<case_id>.json
cases/<case_id>.md
RAW_NOISE_TESTCASE_MATRIX.csv
SUMMARY.json
SUMMARY.md
VALIDATION_REPORT.json
```

## Sample smoke result

Package: `sample.support_triage`

```text
terminal_paths_input: 3
patterns: 2
noise_cases: 6
ready_cases: 6
```

Pattern counts:

```json
{
  "distraction": 3,
  "invalid_branch": 3
}
```

## Validation

Passed:

- workspace `py_compile`
- selected non-runtime PathWalk pytest: `18 passed`
- workspace graph → paths → noise-cases CLI smoke
- generated `RAW_NOISE_TESTCASE_MATRIX.csv`
- generated per-case JSON/Markdown artifacts
- clean zip extraction check
- PathWalk RC + developer bundle `py_compile`: passed
- PathWalk RC + developer bundle graph → paths → noise-cases smoke: passed

Not used as gate:

- runtime-harness / transcript-replay matrix tests, because that branch is a known blocked-no-release branch from M60.6.5 / M60.6.4.1.

## Readiness

```text
noise_cases_ready: true
runtime_execution_ready: false
scoring_ready: false
calibration_ready: false
```

## Change impact

Expected change level:

- `L1` for PathWalk companion utility artifact generation
- `L0` for Ordo runtime core and scoring weights

No runtime-core semantics changed. No scoring weights changed. No real model/API benchmark was run. PDF/book was not generated.
