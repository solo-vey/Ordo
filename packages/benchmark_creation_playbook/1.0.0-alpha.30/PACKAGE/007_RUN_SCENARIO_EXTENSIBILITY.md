# RUN Scenario Extensibility

**Document version:** `0.3.0`  
**Backlog task:** `BL-BENCH-007`  
**Status:** canonical working contract

## 1. Purpose

This document defines how new scenarios `RUN_06+` may be added without silently changing the meaning of the canonical baseline `RUN_01–RUN_05`.

## 2. Extension principle

A new RUN is justified only when it tests a materially distinct interaction or lifecycle behavior that cannot be represented as:

- a new test case;
- a package variant;
- an evaluator rule;
- a parameter value inside an existing RUN;
- a regression instance of an existing RUN.

New scenarios must not be created merely because the domain facts are different.

## 3. Required proposal record

Every new scenario proposal must define:

- `proposed_run_id`;
- `scenario_name`;
- unique behavioral purpose;
- distinction from every existing RUN;
- fact-status model;
- disclosure model;
- correction model;
- expected terminal;
- allowed and forbidden outputs;
- Driver capability requirements;
- evaluator invariants;
- affected package variants;
- compatibility and migration impact;
- owner decision.

## 4. Identity and numbering

- RUN IDs are monotonic and never reused.
- A rejected proposal does not reserve an ID unless published externally.
- Published RUN semantics are immutable within a scenario major version.
- Editorial fixes use patch version.
- Additional non-breaking evaluator detail uses minor version.
- Changed terminal, disclosure, or correction semantics require a major scenario version or a new RUN ID.

Recommended identity:

```text
RUN_06@1.0.0
```

## 5. Admission gates

A proposed RUN may be admitted only if all gates pass:

1. **Distinctness gate** — behavior is not covered by RUN_01–RUN_05.
2. **Orthogonality gate** — it is not actually a package-variant or document-rubric concern.
3. **Determinism gate** — facts, transitions and expected terminal can be stated unambiguously.
4. **Driver capability gate** — required interactions can be implemented without making Driver generative or leaky.
5. **Blindness gate** — hidden/evaluator-only data remains physically separable.
6. **Comparability gate** — result identity and evaluator versioning are preserved.
7. **Regression gate** — canonical baseline RUNs remain unchanged or an explicit migration is approved.
8. **Owner approval gate** — benchmark owner accepts the scenario.

## 6. Scenario change control

After publication, edits must include:

- affected-field allowlist;
- before/after semantic diff;
- compatibility classification;
- regression selection;
- changelog entry;
- updated hashes;
- explicit statement that unrelated RUNs were not rebuilt.

This rule anticipates `BL-BENCH-041`; full automated scoped-patch verification remains open until that task is implemented.

## 7. Template and schema requirements

A new RUN must use `templates/RUN_CONTRACT.template.yaml` and validate against `schemas/run_contract.schema.json`.

Required machine-readable fields include:

```text
run_id
scenario_version
name
purpose
fact_statuses
disclosure_policy
correction_policy
expected_terminal
required_behaviors
forbidden_behaviors
allowed_outputs
forbidden_outputs
evaluator_invariants
```

## 8. Registry update

Admission of a new RUN requires synchronized updates to:

- `RUN_SCENARIO_REGISTRY.yaml`;
- this playbook’s vocabulary and conceptual model when new semantics are introduced;
- Ordo Process Rail;
- backlog and changelog;
- validation report;
- all-in-one;
- result registry compatibility rules when implemented.

## 9. Rejection conditions

Reject a proposal when:

- it duplicates an existing scenario;
- its expected terminal is ambiguous;
- it depends on evaluator leakage;
- Driver would need to invent facts;
- its distinction is only domain content;
- it combines multiple independent behaviors that should be separate scenarios;
- it changes baseline RUN semantics without migration.

## 10. Definition of Done

`BL-BENCH-007` is complete when the proposal, admission, versioning, registry, migration and rejection rules are explicit and machine-readable extension templates exist.
