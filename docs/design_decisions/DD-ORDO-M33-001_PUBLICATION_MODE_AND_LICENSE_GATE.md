# DD-ORDO-M33-001 — Publication mode and license gate

## Status

Accepted for M33 package state.

## Decision

Ordo v0.12 Public MVP is treated as a **source-available preview candidate**, not as a finalized open-source release.

A repository-level `LICENSE.md` records that the license is pending and that no broad reuse rights are granted until the project owner selects an explicit license.

## Reason

The project is ready for external review, but choosing an open-source license is a project-owner decision. Publishing without a clear notice would create ambiguity for readers and contributors.

## Impact

- `LICENSE-TODO.md` is replaced by `LICENSE.md`.
- Public wording must avoid calling Ordo open-source until the license is selected.
- M33 can be used for GitHub publication as a review candidate.
- A future milestone should finalize license selection before a true open-source release.
