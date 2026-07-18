# DD-ORDO-M36-001 — Release Candidate Freeze

## Status

Accepted

## Decision

M36 freezes the current Ordo v0.12.0-preview candidate for final review. The release candidate keeps the M26–M35 Process Rail reframing as the canonical direction and does not add new feature scope.

## Reason

After M26–M35, the project now has a coherent model:

- Process Rail is the core language model.
- AI Ordo Developer creates Ordo projects with a PM.
- AI Ordo Executor runs compiled Semantic JSON IR with deterministic helper checks.
- CLI supports validation, compilation, and helper commands without becoming the main conversational runtime.

The next risk is uncontrolled scope growth. A freeze milestone is needed before public preview publication.

## Impact

- New conceptual changes are deferred until after review.
- Validation evidence is captured for the current candidate.
- Publication mode remains source-available preview until license is finalized.
