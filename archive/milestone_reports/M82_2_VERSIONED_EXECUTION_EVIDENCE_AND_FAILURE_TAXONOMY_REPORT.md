# M82.2 — Versioned Execution Evidence and Failure Taxonomy

## Status

`implemented / validated-for-M82.2`

Backlog item: `BL-ORDO-003`

## Implemented

- canonical nested evidence contract `ordo.pathwalk.execution_evidence.v1`;
- result envelope upgraded to `ordo.pathwalk.real_module_execution_result.v3`;
- summary envelope upgraded to `ordo.pathwalk.real_module_execution_summary.v3`;
- machine-readable JSON Schema for execution evidence;
- closed execution status taxonomy;
- closed failure-category taxonomy;
- explicit status classes: success, testcase, process, watchdog, evidence, input and infrastructure;
- separation of testcase decision from process outcome;
- retryability flag limited to infrastructure failures;
- evidence linkage to plan, job, testcase and source/case hashes;
- process, diagnostics, controls, artifacts and claims sections;
- raw-evidence-only claim with scoring and calibration explicitly false;
- runtime evidence validator;
- collector rejection of contradictory or tampered v3 evidence;
- compatibility reading of v1 and v2 result envelopes;
- compatibility fields retained in the v3 result envelope.

## Canonical statuses

- `passed`;
- `testcase_failed`;
- `process_failed`;
- `timed_out`;
- `invalid_output`;
- `input_rejected`;
- `infrastructure_error`.

## Canonical failure categories

- `assertion_failed`;
- `nonzero_exit`;
- `terminated_by_signal`;
- `watchdog_timeout`;
- `missing_runtime_report`;
- `malformed_runtime_report`;
- `runtime_report_contract_mismatch`;
- `input_validation`;
- `result_exists`;
- `spawn_failed`;
- `stream_capture_failed`;
- `cleanup_failed`;
- `runner_failure`.

## Validation

Passed:

- 6 dedicated M82.2 evidence/taxonomy tests;
- 9 M82.1 hardening tests;
- 4 M76.2 compatibility tests;
- Python syntax validation;
- JSON Schema syntax validation.

Total relevant tests: `19 passed`.

## Scope boundary

M82.2 does not close BL-ORDO-003. Remaining:

- M82.3 generated-testcase integration through the hardened runner;
- M82.4 full regression/failure matrix and closure.

## Change impact

`L3 — shared/runtime evidence contract`.

No Ordo language semantics were changed.
