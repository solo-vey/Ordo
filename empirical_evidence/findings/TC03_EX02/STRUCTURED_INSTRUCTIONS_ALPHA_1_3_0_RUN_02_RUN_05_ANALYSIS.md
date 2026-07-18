# Structured Instructions Alpha 1.3.0 — RUN_02–RUN_05 analysis

## Results

| RUN | Process | Documents | Final | Terminal result | Main observation |
|---|---:|---:|---:|---|---|
| RUN_02 | 96 | N/A | 96 | `NO_CHANGE` | Driver validators rejected the attempted artifacts; no approvals or business artifacts were included. |
| RUN_03 | 99 | 100 | 99 | `T_SCENARIO_EXHAUSTED / no_go` | Correctly ended without canonical documents after the authoritative scenario was exhausted. |
| RUN_04 | 99 | 97 | 98 | `T_COMPLETED / go` | Correction and regeneration loops were executed; final artifacts passed Driver validation, cross-artifact gate and package gate. |
| RUN_05 | 100 | 100 | 100 | `T_INPUT_BLOCKED / no_go` | Mandatory facts remained unavailable; no values, documents, approvals or caller-authored receipts were invented. |

## Observations

### RUN_02

Preflight passed. Driver-owned validators rejected Passport, Jira, Manual QA and Automation. The terminal package contains validation evidence and `NO_CHANGE.json`, but excludes failed business artifacts and approvals. This is correct fail-closed behavior. The evidence uses `EVIDENCE_SHA256SUMS.txt` rather than the common `SHA256SUMS.txt` filename; this is a minor consistency issue.

### RUN_03

The checksum manifest is valid. Driver finishes at `T_SCENARIO_EXHAUSTED` with `no_go`. No route-forbidden canonical documents were generated.

### RUN_04

The checksum manifest is valid. Driver recorded failed initial validator runs, correction ownership, regeneration and successful later versions. Final state contains four approvals, four Driver-generated validation receipts, `T_COMPLETED`, cross-artifact PASS and package PASS. A blocked omission-capable test remains explicitly represented as a structured blocker rather than runnable coverage; this is disclosed consistently.

### RUN_05

The checksum manifest is valid. The run stops at `T_INPUT_BLOCKED` because mandatory identifiers and event binding are unavailable. No business artifacts or approvals are created and the caller does not create validation receipts.

## Conclusion

Alpha 1.3.0 preserves the expected behavior across positive, correction, exhaustion and hard-stop routes. Its complete five-run average Final score is **97.6**. The only material defect across the set is the RUN_01 evidence-package checksum self-reference already recorded separately.
