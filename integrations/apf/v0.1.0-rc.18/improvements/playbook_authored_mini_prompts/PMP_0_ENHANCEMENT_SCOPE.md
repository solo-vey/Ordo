# PMP-0 — Playbook-Authored Mini-Prompt Support Enhancement Contract

## Status

- milestone: `PMP-0`
- status: `accepted-scope / design-baseline`
- confirmed APF baseline: `v0.1.0-rc.13-ordo-v0.12-adaptation-confirmed-closure`
- implementation scope selected by process owner: `2026-07-10`

## Purpose

Extend APF so that, while APF is creating a new playbook, it can determine whether a normal structured instruction is sufficient for a playbook object or whether a reusable local mini-prompt should be proposed, reviewed by a human, registered, attached, validated, and packaged with that generated playbook.

This enhancement is for prompts authored **for downstream playbooks**. It does not yet introduce mini-prompts into APF's own internal nodes.

## Canonical lifecycle

```text
playbook object designed
→ instruction sufficiency reviewed
→ contract strengthened when possible
→ existing prompt reused when appropriate
→ new mini-prompt candidate created only when justified
→ human review and approval
→ generated-playbook registry entry
→ prompt attachment
→ validation and test scenarios
→ playbook package readiness
```

## In scope

- Prompt Sufficiency Review for relevant objects of a playbook being authored.
- Classification of the result as:
  - `simple_instruction_sufficient`;
  - `existing_prompt_reuse`;
  - `new_prompt_candidate`;
  - `prompt_prohibited`;
  - `needs_human_decision`.
- Contract-first decision rule before proposing a prompt.
- Structured candidate mini-prompt proposal.
- Explicit human review and approval gate.
- Generation of a prompt registry, manifest and attachment map for the downstream playbook.
- Validation of identity, checksum, attachment, authority boundaries and test coverage.
- Conditional inclusion of prompt artifacts in the generated playbook package.
- First real-playbook pilot with a deliberately limited number of approved prompts.

## Out of scope

- Mini-prompts attached to APF's own internal nodes.
- APF-wide internal-node applicability review.
- Automatic activation of a proposed prompt without human approval.
- Prompt-owned navigation, gate decisions or state confirmation.
- Modification of Ordo language/compiler/runtime core.
- Generalized core runtime prompt-application writer.
- BL-APF-001 real-case replay framework.
- Production claim for multi-runtime transcript replay.

## Authority rules

1. Contract, schema, state, gate and transition rules remain authoritative.
2. A prompt may guide explanation, clarification, recovery, validation interpretation or artifact generation.
3. A prompt may not introduce hidden process or business logic.
4. A prompt may not select `next_node`, bypass a gate, confirm a decision or alter confirmed state.
5. A proposed prompt remains inactive until explicitly approved by the designated human reviewer.
6. The downstream playbook owns its own prompt registry; APF's internal Prompt Registry is not reused as the downstream registry.

## Contract-first priority

```text
improve deterministic contract
→ add deterministic rule when possible
→ reuse an approved shared prompt
→ propose a new mini-prompt only when guidance still requires it
```

A weak node contract must not be hidden behind a prompt.

## Delivery milestones

1. `PMP-0` — enhancement scope and design decision.
2. `PMP-1` — Prompt Sufficiency Review contract.
3. `PMP-2` — candidate proposal and human approval gate.
4. `PMP-3` — generated-playbook registry and attachment model.
5. `PMP-4` — validation and test contracts.
6. `PMP-5` — templates and APF authoring-flow integration.
7. `PMP-6` — regression validation and release-candidate assembly.
8. `PMP-7` — real playbook pilot.
9. `PMP-8` — retrospective and decision on internal APF mini-prompts.

## Activation boundary

`BL-APF-002A` is activated for stepwise implementation.

`BL-APF-002B` remains deferred until the real playbook pilot is completed and explicitly reviewed by the process owner.

`BL-APF-001` remains deferred.
