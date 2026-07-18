# DD-ORDO-M57-001 — Runtime Checkpoint Discipline

Status: accepted

## Context

Guided intake can accidentally compress several runtime nodes into one conversation turn. That makes it unclear which contract is closed and which required fields are still unresolved.

## Decision

Ordo Runtime Mode now has a checkpoint discipline layer:

- one node at a time;
- one contract at a time;
- one decision at a time;
- earliest incomplete node wins;
- generated output is blocked while checkpoint gaps remain.

The deterministic helper layer exposes checkpoint state in `validate-state`, `check-gate`, and `next-step` reports.

## Consequences

Runtime assistants must use the checkpoint table instead of free-form conversation memory when deciding whether to move forward. Batch fixture files remain usable for regression tests, but live assistant turns must not merge nodes unless `allow_batch_confirmation: true` is declared.
