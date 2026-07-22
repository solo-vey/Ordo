# Manifests

This directory contains machine-readable current-state, release, policy, and
backlog manifests consumed by validation and delivery tooling.

- [`releases/README.md`](releases/README.md) — release-specific manifest grouping.
- [`external_archives/README.md`](external_archives/README.md) — locators for immutable
  payloads stored outside the active tree.
- `RELEASE_IDENTITY.json` and `VERSION_STATE.json` — current release identity and version state.
- `CONSOLIDATED_BACKLOG.json` — machine-readable counterpart of the current backlog.

Human-readable planning belongs in [`../backlog/README.md`](../backlog/README.md).
