# ARF Delivery Target Decision Gate

## Purpose

ARF always creates and validates one canonical Ordo playbook before choosing how it will be delivered. Delivery format must not distort discovery, contracts, process design, or validation.

## Decision point

The gate runs after the canonical playbook contract is stable and full project validation is ready. ARF evaluates risk, branch/gate/backtrack complexity, mechanical-enforcement needs, and prompt-only evidence. It then recommends one target:

- `engine_runtime`: full enforced runtime;
- `prompt_only`: direct model instructions with explicitly reduced guarantees;
- `both`: both outputs from the same source.

The analyst confirms the final target. Unclear or unsafe cases default to `engine_runtime`. A prompt-only override is blocked when mandatory engine reasons remain.

## Required evidence

Prompt-only requires repeated evidence meeting configured composite, branch, and backtrack thresholds. Model, source, compiler, or policy drift invalidates the decision and requires revalidation.

## Guarantee disclosure

Before selecting `prompt_only` or `both`, ARF must display the loss of mechanical gate enforcement, runtime state validation, enforced transitions, CSG protection, and default runtime evidence capture.

## CLI

```bash
ordo recommend-delivery-target --assessment assessment.json --out recommendation.json
ordo record-delivery-target --recommendation recommendation.json --target both --analyst-id analyst-01 --out decision.json
```
