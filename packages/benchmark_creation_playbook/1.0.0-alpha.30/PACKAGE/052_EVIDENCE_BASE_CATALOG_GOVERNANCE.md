# 052. Evidence Base Catalog Construction and Lifecycle Governance

**Backlog:** `BL-BENCH-052`  
**Status:** OPEN  
**Priority:** High  
**Source:** `backlog_attachments/BL-BENCH-052/SOURCE_EVIDENCE_BASE_CATALOG_GOVERNANCE.md`

## Problem

The benchmark process produces source packages, fixtures, Playbook variants, launch prompts, internal self-validation, dry evaluations, external blind runs, audits, scorecards and removal history. Without one enforceable catalog-governance layer, these artifacts can be stored inconsistently, lose version binding, mix blind and non-blind evidence, overwrite history or enter canonical comparisons without explicit acceptance.

## Goal

Create an executable governance layer for building, maintaining, validating and transferring the full evidence-base catalog throughout its lifecycle.

## Canonical hierarchy

The process must govern the hierarchy:

```text
task class
  → test case
    → playbook representation
      → approved package
      → neutral launch prompt
      → internal self-validation
      → internal dry evaluation
      → user acceptance decision
      → external blind runs
      → audits and diagnostics
      → confirmed score ledger
      → comparative analysis
```

## Required catalog classes

The catalog must separate at minimum:

- governance and schemas;
- authoritative problem inputs;
- fixtures and expected scenarios;
- implementation/representation packages;
- neutral launch prompts;
- internal self-validation evidence;
- internal dry-evaluation evidence;
- external blind-run evidence;
- run audits and root-cause analyses;
- confirmed score ledger and comparative matrix;
- manifests and checksum inventories;
- rejected, invalidated, quarantined and deprecated records;
- transfer/handoff packages.

## Mandatory lifecycle rules

### Immutability

- Original externally returned ZIPs and terminal reports are immutable.
- Corrections create a new run revision or package version.
- Historic evidence is never silently rewritten.

### Evidence classification

Every evidence item must declare one class, including:

- `INTERNAL_SELF_VALIDATION_NOT_BLIND`;
- `INTERNAL_DRY_EVALUATION_NOT_BLIND`;
- `EXTERNAL_BLIND_CANDIDATE`;
- `EXTERNAL_BLIND_CONFIRMED`;
- `REJECTED`;
- `INVALIDATED`;
- `QUARANTINED`;
- `DEPRECATED`.

Internal evidence must never enter canonical blind scorecards.

### Version and checksum binding

Every canonical record must bind:

- task class and test-case IDs;
- representation ID;
- package version and SHA-256;
- launch-prompt version and SHA-256;
- methodology/profile version and effective hash;
- run/revision ID;
- audit version;
- acceptance decision;
- score record and comparison cohort.

### Acceptance

A run enters canonical evidence only after:

1. physical extraction and audit;
2. methodology-bound scoring;
3. explicit user confirmation;
4. manifest and checksum update;
5. successful catalog integrity validation.

A validator PASS alone is insufficient for canonical acceptance.

### Rejection and invalidation

- Rejected runs stay traceable but do not enter confirmed score ledgers.
- Invalidated series are removed from canonical averages and comparison tables without deleting history.
- Canonical revision selection requires an explicit decision record.

### Transfer

Every transfer package must include:

- catalog index;
- manifest and checksums;
- current status and open work;
- lineage and version bindings;
- accepted/rejected/invalidation history;
- reading order and restoration instructions.

## Required machine-readable artifacts

- catalog schema;
- evidence-item schema;
- run registry;
- package and prompt registry;
- acceptance ledger;
- invalidation/deprecation ledger;
- score ledger;
- comparative cohort manifest;
- filesystem-to-manifest validation report.

## Decision-tree integration

Add governed nodes and gates for:

1. initialize or migrate catalog;
2. register authoritative source and test case;
3. register representation package and launch prompt;
4. classify and store internal evidence;
5. receive and preserve external evidence;
6. audit and score;
7. request explicit user acceptance;
8. promote or reject run revision;
9. update score ledger and comparative matrix;
10. validate complete catalog consistency;
11. build a checksum-bound transfer package.

Failure disposition:

`NO_CHANGE / EVIDENCE_CATALOG_GOVERNANCE_FAILURE`

## Acceptance criteria

1. Catalog structure is versioned and machine-readable.
2. Internal and external evidence are physically and semantically separated.
3. Original run packages cannot be overwritten by correction.
4. No score enters a canonical comparison without a confirmed evidence record.
5. Every canonical item is traceable to package, prompt, methodology, audit and user decision.
6. Rejected and invalidated runs remain preserved but excluded from canonical averages.
7. Filesystem and manifests reconcile with zero orphaned or unregistered canonical files.
8. Existing evidence bases can be migrated without mutating the prior baseline.
9. Transfer packages are independently restorable and checksum-verifiable.
10. Positive and negative regression fixtures cover orphan files, stale bindings, mixed evidence classes, overwritten revisions and unconfirmed scores.

## Deliverables

- decision-tree rules and gates;
- canonical directory contract;
- schemas, registries and ledgers;
- catalog validator and migration tool;
- acceptance and regression fixtures;
- transfer-package builder and restoration check;
- documentation and validation report.

## Non-goals

- Do not auto-confirm generated evidence.
- Do not merge internal dry results with external blind benchmark evidence.
- Do not delete rejected or obsolete evidence merely to simplify the catalog.


## Implementation closure — alpha.24

Implemented as executable playbook governance with nodes `N085`–`N091`, hard gate `G_EVIDENCE_BASE_CATALOG_GOVERNANCE`, terminal `T_EVIDENCE_BASE_CATALOG_GOVERNANCE_FAILURE`, a versioned catalog contract, JSON schemas, filesystem-to-manifest validator, score-eligibility checks, lifecycle ledgers, and restorable transfer validation.
