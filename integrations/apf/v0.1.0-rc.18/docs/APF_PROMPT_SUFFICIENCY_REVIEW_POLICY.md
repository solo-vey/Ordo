# APF Prompt Sufficiency Review Policy

## Status

- contract: `apf.prompt_sufficiency_review.v1`
- milestone: `PMP-1`
- applies to: playbooks authored by APF
- enforcement level: APF authoring policy and package validation gate

## Purpose

Prompt Sufficiency Review determines whether a relevant playbook object is already executable from its deterministic contract or whether additional local guidance is justified.

The review does **not** generate or approve prompt text. It produces a controlled classification that becomes the input to later PMP milestones.

## Mandatory order

```text
complete object contract
→ attempt deterministic strengthening
→ search approved reusable prompts
→ classify prompt sufficiency
→ continue, block, request human decision, or open a candidate path
```

A mini-prompt must never be used to conceal an incomplete node, gate, schema or transition contract.

## Objects that require review

Review is required for objects where execution quality can depend on explanation, local context, recovery or complex artifact generation:

- decision nodes;
- complex question nodes;
- confirmation nodes;
- recovery and backtracking handlers;
- blocking gates;
- artifact-generation steps;
- complex human-review steps;
- validation-report interpretation steps.

Simple metadata, enums, mechanical rules and obvious transitions may be excluded, but the exclusion must be recorded with a reason.

## Classification outcomes

### `simple_instruction_sufficient`

Use when the deterministic contract is complete and unambiguous, and a prompt would merely repeat it.

Result: no prompt subsystem is added for that object.

### `existing_prompt_reuse`

Use when the object contract is complete but local guidance is useful and an already approved compatible prompt exists.

PMP-1 only records the result. Registry resolution and attachment are defined later in PMP-3.

### `new_prompt_candidate`

Use only when:

- the contract is complete;
- deterministic strengthening was attempted;
- no compatible approved prompt exists;
- the remaining need is local, guidance-oriented and testable;
- the prompt would not own navigation, gates, confirmation or state.

PMP-1 does not create the candidate text. Candidate creation and human approval belong to PMP-2.

### `prompt_prohibited`

Use when a proposed prompt would introduce hidden authoritative logic, bypass a gate, select navigation, confirm a decision, or compensate for a weak contract.

Result: prompt creation is blocked and the authoritative contract must be corrected.

### `needs_human_decision`

Use when prompt necessity or reuse choice changes the playbook experience materially, acceptable variation is unknown, or multiple valid guidance approaches exist.

Result: the playbook checkpoint remains open until a human decision is recorded.

## Minimum review questions

For every reviewed object:

1. Is the deterministic contract complete?
2. Can fields, schemas, enums, gate criteria or transition rules remove the ambiguity?
3. Can a deterministic helper or validation rule replace prose guidance?
4. Would a prompt merely restate the contract?
5. Is special explanation, recovery or rendering guidance still needed?
6. Was the downstream playbook's approved prompt catalog searched?
7. Would a prompt stay within non-authoritative guidance boundaries?
8. Can the expected benefit be validated later?

## Readiness gate

A playbook with prompt-capable objects is not prompt-ready when:

- a required object has no review record;
- the review is incomplete;
- classification is missing;
- `new_prompt_candidate` is selected without a completed contract-strengthening attempt;
- `needs_human_decision` remains unresolved;
- a prompt exists for an object classified as `prompt_prohibited`.

`simple_instruction_sufficient` is a valid and desirable result. APF must not create empty prompt registries or placeholder prompts merely to demonstrate prompt support.

## Boundary of PMP-1

PMP-1 adds only the sufficiency-review contract, policy and review-record template.

It does not:

- generate candidate prompt text;
- approve or activate prompts;
- create the downstream registry;
- define final prompt test cases;
- add mini-prompts to APF itself;
- modify Ordo core.
