# M57 Runtime Checkpoint Discipline Report

## Summary

M57 adds deterministic checkpoint discipline to Runtime Mode.

## Added

- `language/RUNTIME_CHECKPOINTS.md`
- checkpoint table in helper reports
- `earliest_incomplete_node`
- `forward_allowed`
- `open_required_fields`
- `ORDO-CHECKPOINT-001 ... ORDO-CHECKPOINT-006`
- one-question assistant response standard

## Updated helpers

- `validate-state`
- `check-gate`
- `next-step`
- `generate-output`

## Validation target

Runtime cannot move forward while an earlier mandatory node has open required fields.
