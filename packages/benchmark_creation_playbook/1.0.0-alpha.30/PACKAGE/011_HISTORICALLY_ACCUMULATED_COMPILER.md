# 011. Historically Accumulated All-in-One Compiler Contract

**Backlog:** BL-BENCH-011  
**Output variant:** `PV-HISTORICAL`

## Goal

Generate a single historically styled instruction corpus that preserves YAML-derived behavior but presents it as an accumulated domain manual rather than a visible step graph.

## Controlled transformation

The compiler may:

- regroup instructions by domain topic;
- express transitions as semantic conditions rather than numbered next-node references;
- combine closely related explanatory material;
- retain historical vocabulary and narrative style defined by a versioned style profile.

The compiler must not:

- remove mandatory decisions or terminal rules;
- hide blocking conditions inside prose;
- convert exact gates into recommendations;
- introduce behavior from the direct-domain corpus;
- use previous run outputs or evaluation findings as source material;
- collapse correction and approval-version semantics.

## Mandatory semantic anchors

The resulting corpus must explicitly preserve:

- intake and evidence requirements;
- fact lifecycle and correction rules;
- current-version approval semantics;
- package output contract;
- RUN-specific terminal behavior;
- no-invention and no-premature-finish rules;
- Driver interaction expectations;
- separation of executor-visible and hidden data.

## Provenance

Every major section must map to source YAML node IDs or canonical contracts in a machine-readable companion map. The visible all-in-one need not show every node ID, but provenance must remain auditable.

## Required outputs

- historical all-in-one instruction file;
- provenance map;
- style-profile declaration;
- semantic parity report;
- source hash and checksums.

## Validation

Validation must combine:

- mandatory concept coverage;
- semantic path sampling for RUN_01–RUN_05;
- terminal outcome parity;
- correction/backtrack parity;
- absence of foreign-variant contamination;
- explicit detection of prose-only weak gates.

## Current implementation status

The controlled compiler contract is defined. No executable compiler is yet claimed.
