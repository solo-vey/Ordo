# Release Notes — 1.0.0-alpha.30

Release `1.0.0-alpha.12` registers BL-BENCH-047 as OPEN. It defines the required black-box end-to-end pre-release self-validation campaign and binds the RUN_02 incident evidence. This release does not claim that the new campaign runtime has been implemented.


## Alpha 14
Registers BL-BENCH-048: internally evaluate and score self-validation RUNs, present evidence to the user, and block external blind-test promotion until explicit acceptance.


## Alpha 15 — BL-BENCH-048
Implemented internal dry evaluation and explicit user acceptance gate before external blind testing.


## Alpha 16
BL-BENCH-049 is registered as OPEN. This release specifies evaluation methodology governance but does not yet implement the compiler, schemas, gates or migration.

## Alpha 17
BL-BENCH-049 completed; evaluation methodology is explicit, versioned, test-case-specializable and checksum-bound.


## Alpha 20
`BL-BENCH-050` is OPEN. This release registers the declared-contract archive self-application gate; implementation is not yet claimed.


## Alpha 20 / BL-BENCH-050
Implemented declared-contract archive self-application as decision-tree nodes N074–N078 and hard gate G_DECLARED_CONTRACT_ARCHIVE_RELEASE.


## Alpha 21

Registered two OPEN tasks from the governance transfer package:

- BL-BENCH-051 — Playbook Representation Compilation Governance.
- BL-BENCH-052 — Evidence Base Catalog Construction and Lifecycle Governance.

Source documents are preserved as backlog attachments. No runtime implementation is claimed.


## Alpha 22

Implemented BL-BENCH-051 as enforceable representation compilation governance with registry, profiles, validator, regression fixtures, lineage/parity/disclosure evidence and decision-tree gate.


## Alpha 23

Registered BL-BENCH-053 as OPEN: enforceable improvement plateau detection, best-confirmed-version retention and safe termination of non-improving document correction loops. No runtime implementation is claimed in this release.


## alpha.24
- BL-BENCH-052 implemented: evidence catalog construction, lifecycle, score eligibility, manifest parity and restorable transfer governance.

## Alpha 25

Registered BL-BENCH-054 for live, concise, evidence-bound playbook progress output. The task remains OPEN; this release adds backlog and normative design artifacts only.


## Alpha 26 — BL-BENCH-053
Implemented improvement plateau governance, measurable delta comparison, protected regression prevention, best confirmed version retention, and terminal loop exit.


## alpha.29 — BL-BENCH-054
Execution progress status output governance implemented: nodes N098–N103, status registry, policy, schema, renderer, suppression behavior and acceptance tests.

- BL-BENCH-055 amended: current-state snapshot now covers all retained test cases independently, with mandatory TEST_CASE_COVERAGE_MATRIX reconciliation.


## Alpha 30 — package identity synchronization

- Synchronized `README.md`, `000_PLAYBOOK_CONTRACT.md`, `SUMMARY.json`, `BACKLOG.md`, `ALPHA_RELEASE_NOTES.md`, `FILE_MANIFEST_SHA256.json`, and `SHA256SUMS.txt`.
- Authoritative package identity is `ordo.benchmark_creation_playbook@1.0.0-alpha.30`.
- Lifecycle state is `Near Production`; terminal state is `T_PLAYBOOK_RELEASED`.
- Backlog is `55 DONE / 0 OPEN`.
- This release resolves the fail-closed ambiguity detected during external playbook activation.
