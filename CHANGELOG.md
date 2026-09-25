# Changelog

## 0.2.0-alpha.20.0.223-dev — 2026-09-25

- Fixed the Tree Editor Docker healthcheck contract and container host binding.

This is the repository-level release history for user-facing Ordo deliverables.
Entries are reconstructed only from published GitHub Releases, signed repository
tags, release manifests, and merged release work. Historical gaps are not
filled with inferred changes.

The current source of release truth is the matching GitHub Release and its
checksum asset. The legacy ARF line is preserved on the
[`archive/legacy`](https://github.com/solo-vey/Ordo/tree/archive/legacy) branch.

## [Unreleased]

### Changed

- GitHub Issues are the canonical work tracker. Historical file-based backlog
  records are preserved on `archive/legacy`.

## [Ordo Tree Editor 0.2.0-alpha.20.0.222-dev] - 2026-09-25

### Changed

- Retired the separate Show Path workspace mode, including its navigation,
  graph-focus UI, context-menu actions, capability metadata, and regressions.
- Kept Replay Real Chat and Execute Playbook path highlighting available.
- Ensured schema-preserving response normalization is also committed through
  the runtime StatePatch path.

## [Ordo Tree Editor 0.2.0-alpha.20.0.218-dev] - 2026-09-19

### Fixed

- Added portable host binding, a health endpoint, and corrected Docker startup
  behavior. Published the matching versioned GHCR container image.

## [Vibe ARF 0.1.3] - 2026-09-19

### Changed

- Refreshed the EDIT, CLI_RUN, and MODEL_RUN package family from the current
  Ordo CLI/runtime; all profiles passed the package-native distribution gate.

## [Ordo Tree Editor 0.2.0-alpha.20.0.217-dev] - 2026-08-29

### Changed

- Added canonical graph-transition support and removed the retired standalone
  SVG graph generator from active delivery.

## [Vibe ARF 0.1.2-maintenance.1] - 2026-08-29

### Changed

- Kept the base kit lightweight and reproducible across EDIT, CLI_RUN, and
  MODEL_RUN profiles after retiring the SVG graph generator.

## [Vibe ARF 0.1.2] - 2026-08-22

### Added

- First repository-native Vibe ARF release with reproducible EDIT, CLI_RUN,
  and MODEL_RUN profiles and SHA-256 checksums.

## [Ordo Tree Editor 0.2.0-alpha.20.0.195-dev] - 2026-08-22

### Added

- Read-only visual editor with canonical graph projection, gate and terminal
  visualization, bundled language-verification resources, and legacy adapters.

## [ARF Playbook Kit 0.4.10] - 2026-08-02

### Deprecated

- Final published legacy ARF Playbook Kit line before Vibe ARF became the
  recommended authoring layer.

## [Legacy ARF Playbook Kit 0.1.0–0.4.9] - 2026-07-23 to 2026-07-31

### Deprecated

- Historical low-level authoring releases are superseded by Vibe ARF and kept
  only for compatibility and provenance.

## [ordo-2026.07.17-rc.10] - 2026-07-17

### Added

- Prompt-only compilation and runtime routing (BL-ORDO-048).
- ARF delivery-target gate (BL-ORDO-049).
- External independence verification and EDA-001 updates (BL-ORDO-051, 053, 054).
- Blind Automation Layer (BL-ORDO-055).
- TC03/EX02 current-accepted-runs-only evidence (BL-ORDO-056).

### Versions

- Language: `0.14.0-rc.1`.
- Framework: `0.6.0-rc.1`.

## Historical normalized notes

## BL-ORDO-055

- Added first-class blind automation profiles: `step_bound` and `semantic_adaptive`.
- Added fail-closed Driver, disclosure, fact lifecycle, artifact versioning, correction/invalidation, approval, terminal-state, evaluation, and causal-review contracts.
- Added APF blind-automation design module.
- Added runtime validation/reference state implementation and regression tests.
- Added English and Ukrainian book chapter 84.
- Preserved the original Ukrainian source document with SHA-256 provenance.
- Did not create or label a canonical release.
## Publication candidate integration — Benchmark Creation Playbook

- Added `ordo.benchmark_creation_playbook@1.0.0-alpha.30` as an independently versioned system playbook.
- Preserved source package SHA-256 `cfb80dfa00974dfd44036b2e261860d7a451ef2a9ccbdc87c385814dd8440a7e`.
- Compatibility with Ordo `0.14.0-rc.1` / framework `0.6.0-rc.1` recorded as `COMPATIBLE_WITH_LIMITATIONS`.
- No canonical release was created.

## BL-ORDO-059 — Evidence Storage and Git History Strategy

- Added a complete current evidence binary inventory.
- Established Git, review, and external-asset thresholds.
- Added fail-closed evidence storage validation.
- Defined growth triggers, migration procedure, and rollback.
- Confirmed that Git LFS and Git-history rewriting are not required for the current snapshot.

## Backlog Reconciliation: BL-ORDO-001, BL-ORDO-005, BL-ORDO-008, BL-ORDO-023

- Reconciled BL-ORDO-001 against the final persisted cross-model rebuild and production-readiness gate.
- Closed BL-ORDO-005 using the completed 3-target × 2-run benchmark evidence.
- Closed BL-ORDO-008 following owner approval and successful 4-case replay validation.
- Integrated the checksum-bound BL-ORDO-023 99/100 closure bundle.
- Synchronized machine-readable and Markdown backlog records.

## BL-ORDO-014 — APF Post-Generation Defect Review

- Added a machine-readable claim-level provenance and review schema.
- Added a blocking confirmation gate with nine normative sub-gates.
- Added adversarial defect taxonomy, review profiles, selective invalidation, and cross-artifact reconciliation.
- Added independent post-correction validation and trace/resume/rollback semantics.
- Reviewed five representative critical/high-impact APF contracts.
- Added negative regression fixtures for unsupported executable claims and open critical defects.
- Closed BL-ORDO-014 with zero unresolved critical/high defects.

## Changelog maintenance

Every user-facing GitHub Release must add an entry under `Unreleased` in the
same pull request. At release time, move that entry to a versioned heading,
record the date and exact tag, and retain only verified changes. Use `Added`,
`Changed`, `Fixed`, `Deprecated`, `Removed`, and `Security` when applicable.
Internal refactors without a user-visible impact do not require a release entry.
