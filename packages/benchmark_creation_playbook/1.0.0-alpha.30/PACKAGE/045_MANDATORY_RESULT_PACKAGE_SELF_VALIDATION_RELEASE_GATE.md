# BL-BENCH-045 — Mandatory Result Package Self-Validation and Release Gate

## Status

**DONE**

## Problem

A package can pass integrity, preflight and several file-level validators while still being unsuitable for testing. The RUN_02 analysis demonstrates this failure mode: Passport and Manual QA failed mandatory validators; Jira and Automation passed only formally while containing facts from another run; approvals were absent; and the Driver correctly returned `not_ready`.

The current process must therefore prohibit delivery of a generated result package until the package itself has passed a complete, package-level self-check.

## Required behavior

Before any package is returned for benchmark testing, the creating model/runtime must execute a mandatory fail-closed release gate that verifies at least:

1. ZIP and internal checksum integrity.
2. Presence of all required result artifacts, evidence, logs and manifests.
3. PASS receipts for every mandatory artifact validator.
4. Cross-artifact consistency against the authoritative selected-run input.
5. Absence of foreign/stale literals originating from another run or template.
6. Consistency of document IDs, record keys, old/new values, operation, timestamps, event types, collection names, rule IDs and dedup keys.
7. References point only to current, non-invalidated artifact versions.
8. Manual QA contains the full required executable step sequence, exact assertions, rollback command and post-rollback assertion.
9. Automation uses the authoritative payload and proves exact cardinality, idempotency and zero forbidden side effects.
10. Driver presentation and approvals are bound to the exact validated version IDs.
11. Terminal state is actually releasable; `not_ready`, missing approvals or any unresolved FAIL block delivery.
12. No unsupported claim of live execution, repository symbols or unavailable bindings.

## Correction loop

On any failed check, the package must not be handed off. The runtime must:

1. identify the failing artifact/version and root evidence;
2. invalidate that version;
3. regenerate or correct it as a new version;
4. rerun artifact validators;
5. rerun cross-artifact selected-run consistency;
6. rerun the complete package-level gate;
7. release only after an explicit PASS report.

## Required outputs

- machine-readable package self-check report;
- human-readable summary;
- validated artifact/version inventory;
- validator receipt inventory;
- cross-artifact consistency report;
- approval/version-binding report;
- final release disposition: `PASS_RELEASE`, `BLOCKED_REGENERATE`, or `NO_GO`;
- checksums for the released package and reports.

## Acceptance criteria

- A package with one failed mandatory validator is blocked.
- A package whose individual files pass but contain facts from another run is blocked.
- A package with missing approvals or approvals for stale versions is blocked.
- A package with incomplete Manual QA/Automation evidence is blocked.
- The gate produces deterministic evidence explaining every block.
- After correction, only the newly validated versions can be released.
- Positive and negative acceptance fixtures prove fail-closed behavior.
- The gate is integrated into the execution step that returns the package, not left as an optional post-processing check.

## Source evidence

`backlog_attachments/BL-BENCH-045/RUN_02_DETAILED_ANALYSIS_FOR_MODEL.docx`


## Implementation closure

Implemented in `1.0.0-alpha.9` with:

- `tools/validate_result_package_release.py`;
- `RESULT_PACKAGE_RELEASE_GATE_POLICY.yaml`;
- `schemas/result_package_release_gate_report.schema.json`;
- `templates/RESULT_PACKAGE_RELEASE_GATE_REPORT.template.json`;
- positive and negative fixtures under `fixtures/result_package_release_gate/`;
- `reports/RESULT_PACKAGE_RELEASE_GATE_ACCEPTANCE_TESTS.json`.

The package-return step is fail-closed. A result may be returned for benchmark testing only when the generated report has `release_disposition=PASS_RELEASE` and `releasable=true`. Any validator failure, selected-run mismatch, foreign literal, stale reference or approval, incomplete Manual QA/Automation evidence, unsupported claim, or non-releasable Driver state blocks handoff.
