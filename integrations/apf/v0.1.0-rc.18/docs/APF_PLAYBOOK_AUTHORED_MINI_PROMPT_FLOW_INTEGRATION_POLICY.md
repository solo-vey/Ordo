# APF — Playbook-authored mini-prompt flow integration policy

## Purpose

Integrate PMP-1 through PMP-4 into the canonical APF concrete-playbook authoring flow without introducing internal APF mini-prompts.

## Canonical authoring sequence

```text
startup and intake
→ decision tree and terminal paths
→ node / gate / artifact-generation contracts
→ Prompt Sufficiency Review
→ candidate proposal when required
→ explicit human approval
→ generated-playbook prompt registry / manifest / attachment map
→ prompt validation and test coverage
→ package assembly
→ final readiness validation
```

## Conditional package rule

Prompt-specific artifacts are included only when at least one result is:

- `existing_prompt_reuse`;
- `new_prompt_candidate`;
- `needs_human_decision`.

If every reviewed object is `simple_instruction_sufficient` or excluded with rationale, the playbook must not generate an empty prompt package.

## Blocking gates

A downstream playbook is not ready when:

- a relevant object has no Prompt Sufficiency Review record;
- a `new_prompt_candidate` has no human decision;
- an unapproved prompt is present in the active registry or attachment map;
- an approved prompt has no manifest checksum, attachment validation, or mandatory test scenarios;
- a prompt receives navigation, gate, confirmation, or state authority.

## Boundary

This policy applies only to prompts authored for playbooks created by APF. It does not authorize mini-prompts for APF internal nodes and does not modify Ordo core.
