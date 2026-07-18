# 008. Package Variant Registry

**Playbook version:** 0.4.0  
**Status:** canonical working-draft contract  
**Backlog:** BL-BENCH-008

## Purpose

This registry defines the four benchmark package variants as separate controlled representations of the same approved test-case contract. A variant is not merely a filename or presentation style: it has a declared source lineage, transformation boundary, execution interface and contamination policy.

## Canonical variants

| ID | Name | Canonical source | Transformation objective | Default driver family |
|---|---|---|---|---|
| `PV-YAML` | YAML Playbook | approved canonical Ordo/YAML playbook | preserve executable graph, states, gates and node contracts | step-bound |
| `PV-STRUCTURED` | Structured Instructions from YAML | immutable `PV-YAML` release | compile graph semantics into ordered human-readable instructions without exposing internal Ordo syntax | step-bound |
| `PV-HISTORICAL` | Historically Accumulated All-in-One | immutable `PV-YAML` release plus approved historical style profile | express the same semantics in a historically accumulated instruction corpus while preserving required behavior | semantic-adaptive |
| `PV-DIRECT` | Direct Domain-Adapted Original All-in-One | explicitly selected original domain corpus | adapt terminology and domain bindings only; do not import YAML-derived improvements | semantic-adaptive |

## Identity and comparability

A benchmark result is comparable only when the following tuple is recorded:

`test_case_id × run_id × variant_id × variant_version × source_revision × compiler_profile_version`.

Two packages with different source revisions or compiler profiles are not the same variant release even if their visible title is identical.

## Mandatory metadata

Every variant package must contain or expose:

- variant ID and semantic version;
- canonical source identifier and SHA-256;
- compiler/adaptation profile and version;
- generated-at timestamp;
- supported RUN set;
- selected Driver family or `pending-driver-selection`;
- declared deviations and unresolved blockers;
- package manifest and checksums;
- contamination declaration.

## Cross-variant invariants

All four variants must preserve:

1. canonical task class and RUN semantics;
2. allowed/forbidden outputs;
3. correction, invalidation and terminal rules;
4. hidden/evaluator-only isolation;
5. artifact-set expectations;
6. no-invention policy;
7. traceability to the same source test-case contract.

Presentation, internal structure and prompting style may differ. Contract behavior may not drift silently.

## Contamination policy

- `PV-STRUCTURED` and `PV-HISTORICAL` may derive only from the declared YAML source and their declared compiler profile.
- `PV-DIRECT` must not consume YAML, YAML-derived structured instructions, YAML-specific validators, or improvements learned from them unless a later explicit benchmark design decision changes the experiment.
- Shared domain facts may be used only when they come from the common benchmark source package, not from another variant output.

## Readiness gate

A variant release is `variant-ready` only if:

- source lineage is complete;
- transformation profile is versioned;
- required outputs are present;
- forbidden contamination is absent;
- structural validation passes;
- semantic parity review passes or any deviation is explicitly accepted;
- checksums are generated.

This Epic defines authoring contracts, not yet runnable production compilers. Therefore current readiness is `compiler-contract-defined / implementation pending`.
