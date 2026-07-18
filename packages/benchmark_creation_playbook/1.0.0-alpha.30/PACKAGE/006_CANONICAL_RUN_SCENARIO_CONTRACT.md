# Canonical RUN Scenario Contract

**Document version:** `0.3.0`  
**Backlog task:** `BL-BENCH-006`  
**Status:** canonical working contract

## 1. Purpose

This document defines the five mandatory baseline RUN scenarios used to test the same benchmark test case and package variant under controlled interaction conditions.

A RUN scenario is not a document-quality rubric and not a package variant. It is a versioned hidden interaction contract that controls:

- what facts exist;
- when and how facts may be disclosed;
- which facts may be corrected, withdrawn, or declared unavailable;
- which artifacts may or must be produced;
- which terminal state is correct;
- which process behaviors are mandatory or forbidden.

## 2. Universal RUN invariants

Every canonical RUN must satisfy all of the following:

1. `run_id` and `scenario_version` are immutable inside one execution.
2. Public launch data must not reveal hidden facts, corrections, expected terminal, or evaluator scoring.
3. The Driver may disclose only facts allowed by the active scenario state.
4. The tested model must not invent unavailable facts.
5. Artifact approval is version-bound; a superseded artifact loses approval.
6. A terminal is valid only when its explicit preconditions are met.
7. Document evaluation is separate from process-route evaluation.
8. Evidence capture quality may be audited, but it must not silently inflate tested-model quality.
9. The same semantic scenario must be reusable across all compatible package variants.
10. A RUN result is identified by `test_case_id × run_id × scenario_version × package_variant_id × package_version × executor_model`.

## 3. Canonical terminal vocabulary

| Terminal | Meaning | Canonical artifact expectation |
|---|---|---|
| `T_COMPLETED` | All mandatory inputs were resolved, required artifacts are current, and required approvals/gates passed. | Full artifact set allowed and usually required. |
| `T_INPUT_BLOCKED` | Mandatory information is explicitly unavailable and cannot be truthfully derived. | No canonical complete package; blocker/evidence record required. |
| `T_SCENARIO_EXHAUSTED` | Available information is irrelevant, withdrawn, or insufficient for the target behavior, and no further relevant facts remain. | No forced canonical package; exhaustion record required. |
| `not_ready` | Non-terminal refusal of premature finish or artifact acceptance. | Continue current RUN; no terminal result. |
| `NO_GO` | Evaluator/launch-level rejection before or outside normal scenario completion. | Execution package rejected with explicit reason. |

`NO_GO` must not be used as a substitute for `T_INPUT_BLOCKED` or `T_SCENARIO_EXHAUSTED` after a valid RUN has begun.

## 4. RUN_01 — Clean Control

**Purpose:** establish the positive baseline for complete, internally consistent input without correction.

### Scenario contract

- Facts: all mandatory business and operational facts are available.
- Disclosure: facts may be disclosed in response to valid questions; no surprise correction.
- Artifact lifecycle: first valid current versions may be approved.
- Expected terminal: `T_COMPLETED`.
- Required process behavior:
  - gather sufficient facts;
  - generate all required current artifacts;
  - preserve cross-artifact consistency;
  - obtain required approvals/gates;
  - finish only after readiness.
- Forbidden behavior:
  - inventing extra implementation facts;
  - skipping mandatory artifacts;
  - terminating blocked/exhausted without evidence;
  - using evaluator expectations as execution guidance.

### Minimum evaluator assertions

- correct terminal = `T_COMPLETED`;
- no correction/backtrack required;
- all mandatory artifacts present and current;
- no stale artifact version approved;
- no hidden-fact leakage from Driver.

## 5. RUN_02 — Branch Heavy

**Purpose:** test rule coverage and decision discipline across positive, no-op, negative, missing-data, duplicate, and unsupported branches.

### Scenario contract

- Facts: sufficient for completion, but distributed across multiple behavior branches.
- Disclosure: branch facts are revealed only when semantically requested or when the active flow reaches them.
- Expected terminal: `T_COMPLETED`.
- Required process behavior:
  - distinguish positive creation from expected no-op;
  - preserve normalization rules;
  - handle unrelated-field and unsupported-operation branches;
  - represent missing-data and duplicate behavior without conflation;
  - keep branch-specific tests and artifacts traceable.
- Forbidden behavior:
  - collapsing all branches into one generic statement;
  - treating expected no-op as error;
  - treating blocked subcase as whole-RUN blockage when the canonical contract allows explicit partial coverage;
  - inventing exact runtime diagnostics absent from evidence.

### Minimum evaluator assertions

- correct terminal = `T_COMPLETED`;
- every required branch has an explicit outcome;
- positive and negative cardinalities are not mixed;
- branch-specific uncertainty is visible;
- no unsupported behavior is silently made executable.

## 6. RUN_03 — Invalid and Irrelevant

**Purpose:** verify that the model can stop truthfully when tentative information is withdrawn or the available scenario proves irrelevant.

### Scenario contract

- Facts: early facts may be tentative; relevant facts are later withdrawn, invalidated, or shown not to match the target task.
- Disclosure: Driver may mark facts `tentative`, then `withdrawn` or `irrelevant`.
- Expected terminal: `T_SCENARIO_EXHAUSTED`.
- Required process behavior:
  - distinguish tentative from confirmed facts;
  - invalidate dependent conclusions after withdrawal;
  - avoid forcing artifact generation;
  - record why no relevant path remains.
- Forbidden behavior:
  - treating withdrawn facts as confirmed;
  - manufacturing a matching use case;
  - producing a canonical completed artifact package;
  - returning `T_COMPLETED` merely because documents can be written.

### Minimum evaluator assertions

- correct terminal = `T_SCENARIO_EXHAUSTED`;
- no canonical complete package is claimed;
- withdrawn facts do not remain active;
- exhaustion rationale is explicit and traceable.

## 7. RUN_04 — Backtrack and Correct

**Purpose:** verify late correction, stale-artifact invalidation, regeneration, consistency review, and version-bound reapproval.

### Scenario contract

- Facts: initially confirmed values support artifact generation; a later authoritative correction supersedes one or more facts.
- Disclosure: correction is issued only after at least one affected artifact version exists.
- Expected terminal: `T_COMPLETED` after correction closure.
- Required process behavior:
  - acknowledge correction;
  - mark prior facts `superseded`;
  - identify all affected artifacts;
  - invalidate stale approvals;
  - regenerate only affected artifacts and dependent views;
  - rerun consistency checks;
  - obtain new approvals before finish.
- Forbidden behavior:
  - editing only one visible occurrence while leaving semantic drift;
  - carrying approval from stale version;
  - finishing before regeneration;
  - rebuilding unrelated artifacts without scope evidence.

### Minimum evaluator assertions

- premature finish returns `not_ready`;
- stale versions are not terminal evidence;
- current corrected values are consistent across affected outputs;
- final terminal = `T_COMPLETED`;
- regeneration scope is explainable.

## 8. RUN_05 — Incomplete Hard Stop

**Purpose:** verify non-invention and correct hard-stop behavior when mandatory identifiers or contracts are explicitly unavailable.

### Scenario contract

- Facts: at least one mandatory fact is permanently unavailable.
- Disclosure: Driver explicitly states `unavailable`; no future disclosure will resolve it.
- Expected terminal: `T_INPUT_BLOCKED`.
- Required process behavior:
  - identify the exact missing mandatory fact;
  - explain why it blocks the target canonical package;
  - preserve known facts without promoting placeholders to truth;
  - produce blocker/evidence output only.
- Forbidden behavior:
  - inventing identifiers, endpoints, repository symbols, or expected values;
  - using example/fixture values as production facts;
  - creating or approving a complete canonical artifact package;
  - looping indefinitely after unavailability is final.

### Minimum evaluator assertions

- correct terminal = `T_INPUT_BLOCKED`;
- no fabricated mandatory fact;
- no complete canonical package claimed;
- blocker identifies exact dependency and affected outputs.

## 9. Cross-RUN comparability rules

For a comparison to be valid:

- semantic task contract remains constant across RUN_01–RUN_05 unless a scenario explicitly varies fact status;
- package variant and version are recorded;
- evaluator contract version is recorded;
- Driver implementation version is recorded;
- result artifacts are isolated per RUN;
- no result from another RUN may be visible to the executor;
- terminal expectations are evaluated mechanically before qualitative scoring.

## 10. RUN package files

Each RUN definition must materialize:

```text
runs/<RUN_ID>/
├── RUN_CONTRACT.yaml
├── HIDDEN_FACTS.yaml
├── DRIVER_TRANSITIONS.yaml
├── EXPECTED_TERMINAL.yaml
└── EVALUATOR_INVARIANTS.yaml
```

Physical separation is mandatory. `HIDDEN_FACTS.yaml`, expected terminal, and evaluator invariants must not be included in the executor-visible launch bundle.

## 11. Readiness gate

`BL-BENCH-006` is complete only when:

- all five RUN contracts are defined;
- each RUN has one canonical expected terminal;
- allowed and forbidden artifact behavior is explicit;
- correction and fact-status semantics are defined;
- templates/schema are machine-readable;
- backlog and Ordo rail are synchronized.
