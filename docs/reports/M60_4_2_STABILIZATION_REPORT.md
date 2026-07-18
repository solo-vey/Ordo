# M60.4.2 — Stabilization / Full Regression Pass

Status: **passed with class-split regression gate**  
Date: 2026-07-07

## Scope

M60.4.2 does not introduce a new runtime feature. It stabilizes the M60.4.1 baseline after PathWalk M60-native adaptation and the branch-aware current-node runtime fix.

## Checks performed

- Core CLI class-split regression: **82/82 passed** across 21 unittest classes.
- PathWalk pytest suite: **17/17 passed**.
- Python bytecode compile check: passed for `cli/ordo` and `ordo_pathwalk`.
- Repository hygiene check: passed after removing generated cache/report artifacts produced during test runs.
- Embedded runtime smoke: passed.

## Embedded runtime smoke coverage

The smoke run built a History Event runtime package with `runtime_view=ordo-code` and verified:

```text
runtime-status: ready
verify-targets: passed
next-step --format auto: current_contract emitted
intake --submit N_EVENT_GOAL: passed
intake --submit N_PATH_SELECT: passed
restore-session --to-seq 1: passed
verify-session: passed / session-chain intact
package command: blocked by embedded runtime allowlist
```

## Regression method note

The monolithic `unittest discover` command remains too noisy/long for this execution environment and was not used as the release acceptance gate. The reliable gate for this patch is class-split execution of all unittest classes from `cli/tests/test_cli_workflow.py`, plus the independent PathWalk pytest suite.

## Runtime feature changes

None. M60.4.2 is a stabilization and validation milestone.

## Next recommended step

M60.5 — PathWalk Benchmark Readiness:

- run PathWalk matrix smoke for `enforced+json`, `enforced+ordo-code`, and `enforced+json,ordo-code`;
- produce a sample `SUMMARY.json`;
- verify score metadata and hashes across runs;
- prepare instructions for external model/API benchmark runs.
