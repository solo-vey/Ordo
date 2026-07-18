# 038 — Stable Benchmark Evolution

## Status

Canonical contract for `BL-BENCH-038`.

## Purpose

Allow the benchmark system to evolve without destroying historical comparability or mixing unrelated changes.

## Change classes

Every release classifies each mutation as one of:

- playbook/runtime behavior;
- RUN scenario contract;
- package compiler or variant lineage;
- Driver contract;
- process evaluation contract;
- document evaluation contract;
- test-case evidence;
- registry/matrix policy;
- tooling or packaging only.

## Controlled evolution rules

1. One release must declare a primary change class.
2. Secondary changes require explicit dependency justification.
3. Scenario, scoring and Driver changes must not be bundled silently.
4. Contract changes create new versioned cohorts.
5. Historical records remain readable under their original contracts.
6. Migration is explicit; reinterpretation in place is forbidden.
7. Benchmark owner approval is required for changes affecting comparability.
8. Release notes must state which comparisons remain valid, become conditional or are invalidated.

## Stability gates

A release is stable only when:

- checksums and lineage are complete;
- changed contracts are version-bumped;
- regression and sentinel scenarios pass;
- no unexplained out-of-scope changes exist;
- comparison-cohort impact is declared;
- rollback package exists;
- prior versions remain accessible;
- result registry migration, if any, is append-only.

## Compatibility dispositions

- `FULLY_COMPARABLE`;
- `COMPARABLE_WITH_FILTERS`;
- `NEW_COHORT_REQUIRED`;
- `HISTORICAL_ONLY`;
- `INVALID_RELEASE`.

## Release evidence

- change classification;
- affected contracts and versions;
- migration note;
- cohort impact report;
- regression evidence;
- rollback reference;
- updated changelog and checksums.

## Relationship to BL-BENCH-041

This contract requires scoped changes and out-of-scope diff evidence but does not yet implement the dedicated enforceable YAML patch verifier. `BL-BENCH-041` remains open.

## Completion evidence

This contract and evolution policy registry complete `BL-BENCH-038`.
