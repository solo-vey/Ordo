# 016. Blind Isolation Rules

**Backlog:** `BL-BENCH-016`  
**Status:** implemented contract

## 1. Isolation domains

The benchmark uses physically and logically separated domains:

1. **Executor-visible** — package instructions, disclosed facts, public runtime contracts.
2. **Driver-private** — hidden scenario facts, disclosure schedule, correction triggers.
3. **Evaluator-only** — expected terminal, reference invariants, scoring rules, caps, hidden answer keys.
4. **Historical registry** — prior outputs, scores, diagnoses and improvements.

A role receives only its minimum necessary domain.

## 2. Forbidden executor exposure

Before and during execution, the executor must not receive:

- expected process/document/overall scores;
- evaluator rubrics or failure caps unless the same rule is an explicit execution contract;
- expected terminal route;
- reference artifacts or golden answers;
- prior outputs from the same test case/RUN;
- prior evaluator findings or causal diagnoses;
- hidden facts not yet disclosed by the Driver;
- identities or comparative rankings of other variants.

## 3. Forbidden Driver exposure/use

The Driver may know the private scenario schedule, but must not use:

- score rubrics to steer questions;
- golden document wording;
- prior executor outputs as response hints;
- evaluator conclusions to repair the run.

## 4. Evaluator timing

The evaluator receives the immutable returned result, execution trace and evaluator-only contract only after the execution terminal is sealed. Evaluation cannot mutate the original trace or result package.

## 5. Contamination controls

Preflight must record:

- clean workspace/session identifier;
- exact package and scenario hashes;
- absence of previous run artifacts in executor-visible storage;
- prompt/context inventory by visibility class;
- model/session identity;
- isolation exceptions, if any.

Any exception is blocking unless explicitly approved in the test-case contract and reflected in comparability metadata.

## 6. Context construction rule

Executor context is built from an allowlist, not by deleting known secrets from a combined bundle. Private and evaluator files must reside outside the executor package root.

## 7. Leakage incident handling

On suspected leakage:

1. stop the run;
2. seal current trace as invalid attempt;
3. record exposed material and exposure time;
4. mark result `non_blind / not comparable`;
5. create a fresh attempt with a clean session after remediation;
6. never overwrite or silently discard the contaminated attempt.

## 8. Cross-variant isolation

Each variant run uses a fresh executor context. Variant B cannot inherit Variant A output, feedback or diagnostic material. Common source evidence is permitted only when declared as shared canonical benchmark input.

## 9. Evidence

An isolation manifest must include role-to-file mapping, hashes, context inventory, workspace cleanliness result, leak checks, exceptions and final blind-integrity status.

## 10. Gate

Blind integrity passes only when all required separation and cleanliness checks pass. A process score cannot compensate for an isolation failure.
