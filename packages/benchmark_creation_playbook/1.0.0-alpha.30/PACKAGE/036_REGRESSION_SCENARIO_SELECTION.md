# 036 — Regression Scenario Selection

## Status

Canonical contract for `BL-BENCH-036`.

## Purpose

Select the smallest sufficient scenario set that proves the intended fix and protects adjacent behavior.

## Inputs

- confirmed diagnostic case;
- patch scope;
- changed component type;
- dependency and lineage map;
- historical failures;
- canonical RUN and package-variant registries.

## Selection layers

Every regression set contains, where applicable:

1. **Trigger scenario** — reproduces the original defect.
2. **Direct-neighbor scenarios** — exercise the same node, obligation, template, Driver branch or validator.
3. **Cross-variant scenarios** — detect leakage or inconsistent derived packages.
4. **Correction/terminal scenarios** — protect correction, blocking and terminal behavior.
5. **Sentinel scenarios** — stable unaffected cases that detect broad unintended changes.

## Deterministic rules

- Node or route patch: include all RUNs that can reach the changed node plus one unreachable sentinel.
- Prompt or template patch: include every artifact type rendered by it and at least one unaffected artifact type.
- Driver patch: include every RUN behavior class and every bound package family.
- Validator/evaluator patch: include known pass, known fail and boundary cases.
- Package compiler patch: include source/derived parity checks and direct-adaptation contamination checks.
- Scoring-contract patch: create a new evaluation cohort; do not compare raw scores across incompatible contracts.

## Exclusions

A scenario may be excluded only with an explicit reason and evidence that the changed component cannot affect it.

## Regression selection record

The record contains:

- patch ID;
- selected scenario IDs;
- selection reason per scenario;
- expected invariant;
- baseline result reference;
- exclusion list and rationale;
- required variants and repetitions;
- pass/fail threshold.

## Coverage gate

The set fails selection if it lacks:

- the original trigger;
- at least one adjacent-path case;
- at least one unaffected sentinel;
- any mandatory correction or terminal case implied by the patch;
- required cross-variant coverage.

## Completion evidence

This contract and `REGRESSION_SELECTION.template.yaml` complete `BL-BENCH-036`.
