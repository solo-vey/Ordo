# BL-BENCH-048 — Internal Dry Evaluation and User Acceptance Gate Before External Blind Testing

**Status:** DONE  
**Priority:** High  
**Type:** Benchmark workflow / evaluation / promotion gate  
**Depends on:** BL-BENCH-044, BL-BENCH-045, BL-BENCH-047

## Problem

The pre-release self-validation campaign can execute the Playbook and preserve RUN evidence, but it does not yet define a mandatory decision phase in which the same working context immediately evaluates those generated results, explains route and gate behavior, and asks the user whether the observed quality is acceptable before launching expensive and less observable external blind tests.

Without this phase, teams either:

- send immature Playbook versions into external chats too early;
- manually transfer run packages between contexts for analysis;
- lose the model's immediate understanding of why it selected a route or activated a gate;
- repeat diagnosis that could have been completed in the development chat;
- confuse internal pre-release evidence with externally blind benchmark evidence.

## Objective

Add a two-stage promotion workflow:

1. **Internal dry/self-evaluation stage** — execute and evaluate the current Playbook against the canonical scenarios inside the development context, retain full route reasoning evidence, score the results and present them to the user.
2. **External blind-testing stage** — permit creation of an external testing package only after explicit user acceptance that internal results satisfy the expected quality threshold.

Internal results are development evidence only. They must not be inserted into canonical external benchmark results or used as a substitute for blind execution.

## Required behavior

### 1. Immediate post-campaign evaluation

After `RUN_01–RUN_05` self-validation, automatically audit each result using the canonical evidence and scoring contracts. For every RUN produce:

- Process Quality;
- Document Quality;
- Final Quality;
- terminal-state correctness;
- validator and Driver receipt status;
- selected route and gate trace;
- corrections/regenerations performed;
- unresolved risks and limitations.

### 2. Development-context diagnostic analysis

Use the same execution context to explain:

- why a particular branch was selected;
- which gates passed, failed or regenerated artifacts;
- whether route selection indicates a Playbook defect, scenario defect, validator gap or expected behavior;
- what targeted Playbook improvement is justified by the evidence.

The process must not expose private model chain-of-thought. It must preserve safe, structured decision evidence such as state transitions, gate inputs/outputs, selected branches and validator receipts.

### 3. Acceptance thresholds

Support configurable minimum thresholds for:

- per-RUN process score;
- per-RUN document score;
- per-RUN final score;
- campaign average;
- mandatory zero-tolerance defects;
- expected positive and negative terminal outcomes.

Threshold failure blocks external-test promotion unless the user explicitly overrides it with a recorded rationale.

### 4. Explicit user acceptance gate

After showing the internal evaluation, the Playbook must ask for one explicit disposition:

- `ACCEPT_FOR_EXTERNAL_BLIND_TESTING`;
- `REJECT_AND_IMPROVE`;
- `ACCEPT_WITH_RECORDED_RISK`;
- `PAUSE_FOR_OWNER_INPUT`.

No external blind-testing package or launch prompt may be marked ready before this decision is recorded.

### 5. Improvement loop before promotion

When the user rejects the results or scores are below threshold:

1. classify defects;
2. create scoped improvement tasks;
3. patch the Playbook through the canonical improvement workflow;
4. rerun the internal self-validation campaign;
5. reevaluate all affected RUNs;
6. request acceptance again.

Previous internal results must remain versioned and immutable.

### 6. Strict evidence separation

Internal dry results must be marked:

```text
INTERNAL_DRY_EVALUATION
NOT_BLIND
NOT_CANONICAL_BENCHMARK_EVIDENCE
```

External blind results must remain in a separate evidence namespace and must never inherit internal scores or approval automatically.

### 7. External test handoff generation

Only after acceptance, generate a neutral external-testing bundle containing:

- sealed approved candidate Playbook;
- neutral prompts for RUN_01–RUN_05;
- canonical scenario inputs;
- integrity manifests and checksums;
- no internal diagnosis, score hints, change descriptions or expected-answer leakage;
- acceptance receipt binding the bundle to the reviewed candidate SHA-256.

## Mandatory outputs

- internal evaluation campaign report;
- five per-RUN evaluation reports;
- safe route/gate trace reports;
- threshold configuration and evaluation result;
- user acceptance receipt;
- improvement-loop history when applicable;
- external blind-test promotion report;
- neutral handoff bundle generated only after acceptance;
- fail-closed gate that blocks external-test readiness without valid acceptance.

## Acceptance criteria

1. Every self-validation RUN receives Process, Document and Final scores before promotion.
2. Results and route/gate evidence are presented to the user in the development context.
3. Configured score thresholds and zero-tolerance defects are machine-evaluated.
4. External testing remains blocked until an explicit user decision is recorded.
5. Rejection starts a scoped improvement and rerun loop without overwriting previous evidence.
6. Internal dry evidence is clearly separated from external blind benchmark evidence.
7. The generated external launch prompts contain no internal findings or benchmark hints.
8. The external bundle is checksum-bound to the exact user-accepted candidate version.
9. An acceptance override records the acknowledged risks and user rationale.
10. No claim is made that internal self-evaluation is equivalent to independent blind testing.

## Expected value

This stage shortens the improvement cycle, keeps diagnosis close to execution, prevents unnecessary external runs, and reserves external blind testing for candidates whose internally observed quality has already reached an acceptable level.

## Implementation closure

Implemented deterministic internal evaluation, score thresholds, safe route/gate evidence, explicit acceptance receipt, fail-closed promotion, rejection/risk dispositions, and neutral external handoff generation. Current promotion remains blocked until the user records a decision.
