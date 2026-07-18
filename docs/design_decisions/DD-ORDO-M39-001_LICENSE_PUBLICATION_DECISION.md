# DD-ORDO-M39-001 — License / Publication Decision

## Status

Accepted for `v0.12.0-preview`.

## Decision

Ordo `v0.12.0-preview` will remain a **source-available preview candidate**.

The package may be prepared for GitHub preview publication and external review, but it must not be described as an open-source release until a final open-source license is explicitly selected.

## Reason

The workspace contains several different artifact classes: language/spec, book, Python CLI, reference packages, generated site/publication artifacts and possible visual assets. Selecting a real open-source license should be a deliberate owner/legal decision, not an implicit default.

## Impact

- `LICENSE.md` is the active license notice.
- `LICENSE-TODO.md` is not used.
- README/release docs must say `source-available preview candidate`.
- GitHub preview publication is allowed under this notice.
- True open-source publication remains deferred.

## Follow-up

A later milestone may replace this preview notice with one or more explicit licenses, for example separate licenses for code, documentation and assets.
