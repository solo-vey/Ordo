# APF Mini-Prompt Candidate Proposal and Human Approval Policy

## Status

- Milestone: `PMP-2`
- Scope: mini-prompts authored for downstream playbooks created by APF
- Internal APF mini-prompts: out of scope

## Entry condition

APF may create a candidate only after a completed Prompt Sufficiency Review classifies the target object as `new_prompt_candidate` and the contract-strengthening gate has passed.

## Proposal, not activation

A candidate is a review artifact. Before explicit human approval it must remain inactive:

```text
proposal created
→ human review pending
→ no registry entry
→ no manifest entry
→ no prompt_ref
→ no runtime application
```

Approval permits the candidate to proceed to PMP-3. Approval itself does not create or activate the registry entry.

## Mandatory content

A proposal must identify the target object, the exact problem, why deterministic contract strengthening and existing prompt reuse are insufficient, the proposed semantic prompt identity, prompt text, allowed use phase, required context, prohibited authority, fallback behavior and test scenarios.

## Human review dimensions

The process owner or delegated human verifier must decide separately on:

1. whether a prompt is truly needed;
2. whether the wording is acceptable;
3. whether the target scope is correct;
4. whether the `use` phase is correct;
5. whether authority boundaries are explicit;
6. whether fallback behavior is safe;
7. whether validation scenarios are sufficient.

General approval of the playbook does not count as prompt approval.

## Change invalidation

Any material change to prompt text, target scope, intended use phase or authority boundary invalidates the prior approval and returns the candidate to `needs_revision` or `proposed`.

## Decision outcomes

- `approved` — may proceed to PMP-3, but remains unattached until registry generation.
- `needs_revision` — revise and resubmit.
- `rejected` — do not generate registry or attachment artifacts.
- `deferred` — preserve the proposal as non-active evidence.

## Authority boundary

A candidate must never own navigation, gate outcomes, human confirmation, confirmed-state mutation, hidden business logic or package-scope expansion.
