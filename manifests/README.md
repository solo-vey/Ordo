# Manifests

This directory contains machine-readable current-state, release, and policy
manifests consumed by validation and delivery tooling.

- [`releases/README.md`](releases/README.md) — release-specific manifest grouping.
- [`external_archives/README.md`](external_archives/README.md) — locators for immutable
  payloads stored outside the active tree.
- `RELEASE_IDENTITY.json` and `VERSION_STATE.json` — current release identity and version state.
- `VIBE_ARF_CURRENT.json` — current recommended Vibe ARF release and profile assets.
- The recommended downloadable authoring packages are the Vibe ARF profiles in the
  [`vibe-arf-v0.1.2-maintenance.1` GitHub Release](https://github.com/solo-vey/Ordo/releases/tag/vibe-arf-v0.1.2-maintenance.1).
- `ISSUE_TRACKING.json` — compact, checked-in binding to the current GitHub Issues.

Current planning belongs in [GitHub Issues](https://github.com/solo-vey/Ordo/issues).
Historical planning snapshots are preserved on the `archive/legacy` branch.
