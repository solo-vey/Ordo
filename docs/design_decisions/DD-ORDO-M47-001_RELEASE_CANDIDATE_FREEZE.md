# DD-ORDO-M47-001 — Release Candidate Freeze

## Decision

Freeze the current Ordo v0.12 preview workspace as a release candidate after M46.9 external audit self-run.

## Rationale

M46 added the missing deterministic layer for generated analytical package quality: contract coverage, rendered artifact validation, consistency reporting, and go/no-go decisioning. M46.9 confirmed the package against the external audit checklist. M47 should not add new behavior; it should preserve a stable review target.

## Consequences

- Further changes should be treated as release-candidate patches.
- New features should move after this candidate unless they fix a blocker.
- The candidate remains source-available preview only until a publication/license decision is made.
