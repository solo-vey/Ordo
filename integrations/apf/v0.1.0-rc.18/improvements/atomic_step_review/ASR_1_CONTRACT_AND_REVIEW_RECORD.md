# ASR-1 — Atomic Step Review contract and review record

## Completed

- Added the machine-readable Atomic Step Review contract.
- Added a reusable review record template.
- Defined required evidence, findings, severity, proposed decomposition, transition decision, and human decision fields.
- Defined progression behavior for `passed`, `recommendation`, `blocking_issue`, and `needs_human_decision`.

## Key boundary

APF may detect and recommend a minimal safe split, but may not silently change confirmed business semantics, approval authority, ownership, or state transitions.

## Validation

- Contract YAML: valid.
- Review record template YAML: valid.
- Blocking and human-decision behavior: defined.
- Ordo core changes: none.
- Internal APF runtime enforcement: not started.
