# DD-ORDO-M34-001 — External Review Package

Status: accepted  
Milestone: M34  
Date: 2026-07-06

## Decision

M34 packages Ordo v0.12 as an **external review package** instead of declaring it a final open-source release.

The workspace remains a source-available preview candidate under `LICENSE.md`. The external review package is meant for product, architecture, methodology, documentation and license review before a public release decision.

## Reason

M33 intentionally left the license decision open. Publishing Ordo as a true open-source release before choosing licenses for the language specification, CLI, book, examples and assets would be premature.

External review allows the project owner and reviewers to evaluate the public MVP story without changing the legal release status.

## Impact

- `docs/external_review/` becomes the entry point for reviewers.
- Publication manifests explicitly state `external-review`, not `open-source-release`.
- README and CHANGELOG point to M34 status.
- Final open-source publication remains blocked until license selection.
