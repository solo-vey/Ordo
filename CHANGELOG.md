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

# Change Log

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
