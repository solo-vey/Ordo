# APF rc.10 — Handoff readiness policy

## Purpose

APF rc.10 adds a handoff readiness layer so the next consumer can safely start from the package without losing baseline, scope, confirmation, deferred, or next-step context.

## Gate

```text
N_SHARED_TAIL_HANDOFF_READINESS_GATE → HANDOFF_READINESS_GATE
```

## Required checks

HANDOFF_READINESS_GATE verifies:

- `CURRENT_STATE.md` present
- `README.md` present
- `VALIDATION_REPORT.json` present
- `START_NEXT_MODEL.md` present
- latest accepted/confirmed baseline marker present
- handoff/closure document present
- source baseline archive declared
- `current_version` and `source_version` declared
- confirmed decisions listed
- deferred items declared, even when empty
- blocking issues declared, even when zero
- APF scope boundary declared
- next recommended step declared
- no ambiguous continuation state

## Blocking rule

If HANDOFF_READINESS_GATE fails, the package cannot receive:

```text
accepted-baseline / ready-for-next-apf-patch
```

## Placement

```text
REAL_MODULE_TESTCASE_UTILITY_PACKAGING_GATE
→ EXTERNAL_CHECK_EVIDENCE_GATE
→ HANDOFF_READINESS_GATE
→ PACKAGE_COMPOSITION_GATE
→ FINAL_ARCHIVE_ASSEMBLY
```
