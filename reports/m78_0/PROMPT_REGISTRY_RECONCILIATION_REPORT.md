# M78.0 Prompt Registry Follow-up Reconciliation

Status: **PASSED**

- Registry entries: 13
- Manifest entries: 13
- Active prompts: 12
- Conditional dormant prompts: 1
- Orphaned prompts: 0
- Duplicate IDs: 0
- Checksum mismatches: 0

## Decision

`hp.repair.backtracking_invalidation.v1` remains optional and is now explicitly `conditional`, activated only by an explicit runtime backtrack event. It is not auto-attached.

Versioned identifiers such as `ordo.clean_check.report.v1` are schema/report IDs, not prompt IDs, unless declared in a package `prompt_registry`.

## Closure

BL-ORDO-011 may be closed.
