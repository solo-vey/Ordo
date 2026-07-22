# Consolidated Backlog Delta

## BL-ORDO-055 — Closed in change bundle

Implemented the Blind Automation Layer, both execution profiles, Driver and disclosure contracts, correction/invalidation and version-scoped approval semantics, terminal states, independent evaluation separation, causal diagnostic review, APF integration, runtime validation, examples, tests, and bilingual book chapters.

Canonical integration remains pending; no canonical release was created.

### BL-ORDO-001 — CSG production recommendation closure

Status: `closed`

### BL-ORDO-002 — APF graph cycles and dead-end paths

Status: `closed`

### BL-ORDO-003 — Safe runtime execution of generated real-module testcases

Status: `closed`

### BL-ORDO-004 — Backlog and maturity-state synchronization

Status: `closed`

### BL-ORDO-005 — Cross-model and repeated-run CSG benchmark

Status: `closed`

### BL-ORDO-006 — PathWalk score calibration and benchmark purpose

Status: `closed`

### BL-ORDO-007 — First-class flow reuse semantics

Status: `closed`

### BL-ORDO-008 — APF real-case replay and analyst-experience validation

Status: `closed`

### BL-ORDO-009 — APF internal mini-prompt applicability review

Status: `merged_superseded`

### BL-ORDO-010 — Translation completion and synchronization

Status: `closed`

### BL-ORDO-011 — Prompt and Mini-Prompt Governance Reconciliation

Status: `closed`

### BL-ORDO-012 — Startup/package profile and derived-artifact hardening reconciliation

Status: `closed`

### BL-ORDO-013 — Generic template and review tooling

Status: `merged_superseded`

### BL-ORDO-014 — APF post-generation defect review for critical artifacts

Status: `closed`

### BL-ORDO-015 — Release and CI Closure

Status: `merged_superseded`

### BL-ORDO-016 — Current-tree packaging self-check

Status: `closed-M85.5`

### BL-ORDO-017 — Benchmark Evidence Hardening

Status: `closed-M86.5`

### BL-ORDO-018 — CLOSED at M87.6

Status: `closed-qualified`

### BL-ORDO-020 — CLOSED at M88.5

Status: `closed`

### BL-ORDO-021 — CLOSED at M89.5

Status: `closed`

### BL-ORDO-022 — GitHub CI Closure for BL-ORDO-015

Status: `merged_superseded`

### BL-ORDO-023 — Strict-Zero A/B Benchmark Revalidation

Status: `closed`

### BL-ORDO-024 — Process Pattern, Template and Review Engineering

Status: `closed`

### BL-ORDO-025 — APF Linter Memory and Performance Hardening

Status: `closed`

### BL-ORDO-026 — Independent Full Delivery-Gate CI Verification

Status: `ready_for_external_ci`

### BL-ORDO-027 — ARF Deterministic Process Control Model

Status: `closed_recovered_baseline`

### BL-ORDO-028 — Node-Local Deterministic Execution and Self-Contained Context Model

Status: `merged_superseded`

### BL-ORDO-029 — Deterministic Node Execution and Transition Provenance

Status: `closed`

### BL-ORDO-032 — Hermetic and Non-Destructive Delivery Gate

Status: `closed`

### BL-ORDO-033 — Versioning, changelog and upgrade impact governance

Status: `closed`

### BL-ORDO-034 — Playbook Versioning and Runtime Upgrade Handoff

Status: `closed`

### BL-ORDO-035 — Test Fixture Mutation and Parallel Execution Safety

Status: `closed`

### BL-ORDO-036 — Canonical Archive Identity and Evidence Freshness

Status: `closed`

### BL-ORDO-037 — Contractual Manual Run Journey Capture and Validation

Status: `closed`

### BL-ORDO-038 — Journey Replay, Cross-Version Migration and Automated Comparison

Status: `closed`

### BL-ORDO-039 — Playbook Version Rollback Checkpoint Governance

Status: `closed`

### BL-ORDO-040 — Empirical Evidence Subsystem Foundation

Status: `closed`

### BL-ORDO-041 — Empirical Evidence Base v1.3 Canonical Migration

Status: `closed`

### BL-ORDO-042 — Empirical Evidence and Existing Evaluation Interoperability

Status: `open`

### BL-ORDO-043 — Multi-Task-Class Evidence Expansion and Scoring Calibration

Status: `open`

### BL-ORDO-046 — Publication-Safe External Developer Adoption Evidence Preparation

Status: `closed`

### BL-ORDO-047 — Canonical Integration of EDA-001 External Developer Adoption Evidence

Status: `closed`

### BL-ORDO-048 — Prompt-Only Compilation Target and Evidence-Based Runtime Routing

Status: `closed`

### BL-ORDO-049 — ARF Delivery Target Decision Gate

Status: `closed`

### BL-ORDO-050 — APF Legacy IR Opcode Registry Reconciliation

Status: `open`

### BL-ORDO-051 — External Developer Independence Verification Framework

Status: `closed`

### BL-ORDO-053 — Integrate Updated External Adoption Independence Submission for EDA-001

Status: `closed`

### BL-ORDO-054 — EDA-001 Level 1 Proof-Supplied Submission Integration

Status: `closed`

### BL-ORDO-055 — Blind Automation Profiles and Causal Playbook Improvement Standard

Status: `closed`

### BL-ORDO-056 — TC03/EX02 Current Accepted Runs Evidence Canonical Integration

Status: `closed`

### BL-ORDO-058 — Ukrainian Text Remediation and Localization Boundary

Status: `open`

Classify the 1,889 non-book Ukrainian-text document locations recorded in
[UKRAINIAN_TEXT_REMEDIATION_INVENTORY.md](UKRAINIAN_TEXT_REMEDIATION_INVENTORY.md),
then decide each location's canonical treatment: translate, preserve as
localized content, archive, relocate, regenerate, or remove. No remediation
may rewrite immutable evidence, archives, fixtures, or legal text before its
classification and reference/checksum impact are explicit.

### BL-ORDO-059 — Legacy Checkpoint Lifecycle and Archive Disposition

Status: `closed`

Use [CHECKPOINT_LIFECYCLE_AUDIT.md](CHECKPOINT_LIFECYCLE_AUDIT.md) to decide
the canonical treatment for the four pre-RC6 rollback archives. They were
externalized to the checksum-bound historical provenance release after clean
retrieval and restore verification.

### BL-ORDO-060 — Historical Payload Externalization and Current-State Cleanup

Status: `closed`

Historical transfer, recovery, handoff, release/status, manifest, and
checkpoint payloads that were not current runtime inputs now live in the
checksum-bound [external historical archive](../docs/EXTERNAL_ARCHIVES.md).
The active tree retains only a compact locator manifest and current
documentation. `docs/apf/legacy-root/` remains in-repository until its active
references are separately migrated.

### BL-ORDO-061 — APF Module Source Reconciliation

Status: `open`

Reconcile the modular APF source with
`packages/ordo_applied_project_factory/source/program.ordo.yaml` so that
assembly from `module_manifest.yaml` is semantically identical to the
canonical program. The M74.6 assembly test is a required passing condition;
do not weaken or remove it. Closed by PR #31, merged as
`0ba5db05ac0b3dd56ae24561656154573d202fc2`, after exact assembly and full
repository validation passed.

## Backlog Reconciliation — 2026-07-18

The following items are authoritatively closed:

- `BL-ORDO-001` — cross-model CSG production recommendation closure; superseding final rebuild and production-readiness evidence recorded.
- `BL-ORDO-005` — cross-model and repeated-run CSG benchmark; 3 model targets, 6 valid runs, 2 runs per target, all passed.
- `BL-ORDO-008` — APF real-case replay and analyst-experience validation; owner-approved closure, 4/4 replay cases passed, mean analyst experience 0.975.
- `BL-ORDO-023` — A/B benchmark revalidation under the approved 99/100 criterion; overall 99.487/100, minimum run 98.462/100.

Earlier blocked or deferred records are retained as historical reports but no longer define current backlog status.

## Repository maintenance contours

### J.6 — Repository root structure audit and cleanup

Status: `closed`

The root inventory, APF documentation and evidence relocation, delivery and release evidence relocation, governance consolidation, relocation integrity contract, and final root allowlist validation are complete. The canonical closure record is [`../manifests/J6_ROOT_CLEANUP_CLOSURE.json`](../manifests/J6_ROOT_CLEANUP_CLOSURE.json).

### L — Documentation quality and chat-first onboarding

Status: `closed`

The L.1 audit, L.2 chat-first onboarding implementation, L.3 final validation, and L.4 contour closure are complete. The canonical record is [`../manifests/L_DOCUMENTATION_CONTOUR_CLOSURE.json`](../manifests/L_DOCUMENTATION_CONTOUR_CLOSURE.json).

The earlier L.2 closure remains preserved as phase-level evidence: [`../manifests/L2_DOCUMENTATION_CONTOUR_CLOSURE.json`](../manifests/L2_DOCUMENTATION_CONTOUR_CLOSURE.json).


## BL-ORDO-014 Closure — M83.4

BL-ORDO-014 is closed. The package now contains a claim-level provenance schema, blocking confirmation gate, adversarial review taxonomy, independent post-correction validator, trace/resume/rollback contract, five representative critical/high-impact review records, and negative regression fixtures. Unresolved critical/high defects: 0.

### BL-ORDO-057 — GitHub Publication Hygiene and Repository Front Door

Status: `closed`
