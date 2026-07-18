# DD-ORDO-M38-001 — Review Feedback Intake

Status: accepted  
Milestone: M38  
Date: 2026-07-06

## Decision

Add a dedicated review feedback intake layer for the frozen `v0.12.0-preview` release candidate.

## Reason

After M36/M37 the package is frozen for review. Feedback must be collected and classified before it changes the release candidate. This prevents review comments from silently expanding the release scope.

## Consequences

- Feedback is handled through `docs/review_feedback/`.
- Each feedback item receives a classification and decision outcome.
- Feature requests are deferred by default.
- License/publication issues remain owner decisions.
- The M36/M37 freeze remains valid unless explicitly changed by a recorded decision.
