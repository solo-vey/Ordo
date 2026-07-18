# 051. Playbook Representation Compilation Governance

**Backlog:** `BL-BENCH-051`  
**Status:** OPEN  
**Priority:** High  
**Source:** `backlog_attachments/BL-BENCH-051/SOURCE_PLAYBOOK_REPRESENTATION_COMPILATION_RULES.md`

## Problem

The process creates and compares several representations of one canonical process, but the rules that determine how each representation is formed are not yet governed by one enforceable decision-tree contract. This permits semantic drift, accidental disclosure of hidden provenance, use of the wrong compiler strategy, and validation of one representation by criteria intended for another.

## Goal

Introduce explicit, versioned and machine-verifiable rules for forming every supported Playbook representation while preserving the same canonical business semantics and maintaining representation-specific isolation, compilation and validation behavior.

## Scope

The process must govern at least:

1. canonical YAML Playbook;
2. Structured Instructions;
3. Mixed Accumulated Instructions;
4. Domain-Adapted All-in-One.

## Required process changes

Add a representation-selection and compilation-governance segment to the decision tree before package construction:

1. identify the requested representation and authoritative source;
2. select the permitted compiler/adaptation strategy;
3. apply representation-specific inclusion and exclusion rules;
4. generate a lineage and transformation receipt;
5. validate semantic parity with the canonical process;
6. validate representation-specific isolation and disclosure constraints;
7. reject compilation performed by an unauthorized strategy;
8. bind the resulting package to compiler version, source hash and representation profile.

## Mandatory governance rules

### Common invariants

Every representation must preserve:

- intent and business outcome;
- required inputs and outputs;
- state mutations;
- gates and terminal semantics;
- correction ownership and correction-loop reachability;
- evidence obligations;
- failure and hard-stop behavior.

### YAML Playbook

- YAML remains the formal executable source when the variant is YAML-based.
- Node identifiers, transitions, gates, terminals and contracts must be machine-addressable.
- No prose transformation may silently replace formal semantics.

### Structured Instructions

- Must be compiled deliberately from the canonical process.
- Must preserve explicit step order, branching, gates, state and correction routes.
- Must not introduce new business rules absent from the source.
- Structural and semantic parity must be verified against the immutable source.

### Mixed Accumulated Instructions

- Must represent a controlled historically accumulated corpus rather than a visible YAML transcription.
- External model-visible content must not disclose YAML, compiler rules, synthetic provenance, benchmark metadata, node mappings or hidden expected routes.
- The hidden lineage must remain available to governance validators but excluded from the external package.

### Domain-Adapted All-in-One

- Must be produced from the actual all-in-one domain corpus and an explicit domain adaptation contract.
- It must not be reconstructed from YAML and mislabeled as domain-originated documentation.
- Adaptation may change domain vocabulary and model while preserving governed process semantics.

## Required machine-readable artifacts

- `REPRESENTATION_REGISTRY.json`;
- one versioned profile per representation;
- source/target lineage manifest;
- transformation receipt;
- semantic parity report;
- disclosure/isolation report;
- compiler or adaptation strategy declaration.

## Gates

A representation package may proceed only if:

- the requested representation is registered;
- the source type is permitted for that representation;
- the correct compiler/adaptation strategy was used;
- common semantic invariants pass;
- representation-specific rules pass;
- forbidden disclosures are absent;
- lineage and checksums are complete.

Failure disposition:

`NO_CHANGE / REPRESENTATION_COMPILATION_GOVERNANCE_FAILURE`

## Acceptance criteria

1. All four representation profiles are explicit and versioned.
2. The decision tree selects a compiler/adaptation strategy before generation.
3. A Structured Instructions candidate with semantic drift is rejected.
4. A Mixed Accumulated candidate exposing YAML provenance is rejected.
5. A Domain-Adapted candidate reconstructed from YAML without declared domain source is rejected.
6. Equivalent business semantics across variants are verified by a shared invariant set.
7. Every released representation has checksum-bound lineage and validation evidence.
8. Positive and negative regression fixtures exist for each representation.

## Deliverables

- rules integrated into the relevant decision-tree nodes and gates;
- machine-readable representation registry and schemas;
- validators and regression fixtures;
- migration guidance for existing representation packages;
- documentation and acceptance report.

## Non-goals

- Do not force all representations into an identical visible structure.
- Do not expose hidden benchmark provenance to external executors.
- Do not treat a successful file conversion as proof of semantic equivalence.
