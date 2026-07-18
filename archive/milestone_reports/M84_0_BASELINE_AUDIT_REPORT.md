# M84.0 — Baseline Audit

Status: completed, no source mutation.

## Reproduced baseline

- Target: `cli/tests/test_cli_workflow.py`
- Result: **23 passed / 62 failed**
- Duration: 25.97 s
- Release archive SHA-256: `23d68ec72b82d51b1c6de1e3ee9ca61d62d6c54c654c5d4d4ee59329b7d0fab7`

## Root cause

The primary blocker is not a false-positive validator. The new graph validation correctly detects real defects in reference packages and in the init template. Compile, artifact, runtime, and release tests then fail as a cascade because lint blocks compilation.

## Reference packages

- `ordo_project_builder`: 11 findings — 2 missing targets, 9 nodes without terminal path.
- `ordo_hybrid_executor`: 8 findings — 7 nodes without terminal path, 1 undeclared cycle.
- `history_event_guided_intake`: 13 findings — 2 missing targets, 10 nodes without terminal path, 1 unregistered source construct.

## Additional release defect

`FINAL_PACKAGE_SELF_CHECK_REPORT.json` is stale and describes an older tree/test count. It cannot serve as release evidence for M83.0.

## Decision

Proceed to M84.1: migrate reference packages and the init template under the existing validator. Do not weaken graph validation.
