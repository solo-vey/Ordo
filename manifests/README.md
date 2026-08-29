# Manifests

This directory contains machine-readable current-state, release, policy, and
backlog manifests consumed by validation and delivery tooling.

- [`releases/README.md`](releases/README.md) — release-specific manifest grouping.
- [`external_archives/README.md`](external_archives/README.md) — locators for immutable
  payloads stored outside the active tree.
- `RELEASE_IDENTITY.json` and `VERSION_STATE.json` — current release identity and version state.
- `ARF_PLAYBOOK_KIT_CURRENT.json` — legacy lower-level ARF Playbook Kit pointer, retained for compatibility.
- `VIBE_ARF_CURRENT.json` — current recommended Vibe ARF release and profile assets.
- The recommended downloadable authoring packages are the Vibe ARF profiles in the
  [`vibe-arf-v0.1.2` GitHub Release](https://github.com/solo-vey/Ordo/releases/tag/vibe-arf-v0.1.2).
- `CONSOLIDATED_BACKLOG.json` — machine-readable counterpart of the current backlog.

Human-readable planning belongs in [`../backlog/README.md`](../backlog/README.md).
