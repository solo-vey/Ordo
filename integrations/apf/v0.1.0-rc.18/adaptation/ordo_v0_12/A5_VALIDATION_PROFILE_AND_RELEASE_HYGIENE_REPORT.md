# A5 — Validation Profile and Release Hygiene Alignment Report

## Result

A5 aligned the APF working baseline with the Ordo v0.12 validation, derived-artifact freshness and clean-package conventions.

## Added artifacts

- `docs/APF_VALIDATION_PROFILE_ORDO_V0_12.yaml`
- `docs/APF_RELEASE_HYGIENE_AND_DERIVED_ARTIFACT_SYNC.yaml`
- `docs/APF_A5_VALIDATION_AND_RELEASE_HYGIENE_POLICY.md`

## Validation classification

| Layer | A5 status |
|---|---|
| Parent-compatible Ordo CLI chain | declared required |
| `clean-check` | CLI-supported and release-blocking |
| `repo-check --clean` | CLI-supported, policy-gated and release-blocking when applicable |
| APF-local alignment checks | package-local and release-blocking |
| Prompt application trace writer | evidence-only; no core writer claim |
| Replay/snapshot/diff/restore | deferred to A6 |

## Release-hygiene decisions

- clean source, runtime/development and evidence packages are distinct classes;
- stale compiled/runtime/generated artifacts cannot silently remain in clean source;
- clean checks are read-only and do not regenerate artifacts;
- derived artifacts require provenance, freshness policy and stale action;
- whole-package checksum regeneration is deferred until A7 final assembly;
- no new confirmed APF release is claimed by A5.

## Scope protection

A5 did not change APF authoring-flow semantics, Ordo core/CLI implementation, confirmed rc.12 decisions, or deferred backlog status.
