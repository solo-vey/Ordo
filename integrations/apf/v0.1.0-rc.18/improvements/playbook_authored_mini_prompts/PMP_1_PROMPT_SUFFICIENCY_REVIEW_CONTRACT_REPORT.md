# PMP-1 — Prompt Sufficiency Review Contract Report

## Result

PMP-1 adds the normative review contract that APF must use while designing relevant objects of a downstream playbook.

## Added artifacts

- `docs/APF_PROMPT_SUFFICIENCY_REVIEW_CONTRACT.yaml`
- `docs/APF_PROMPT_SUFFICIENCY_REVIEW_POLICY.md`
- `templates/PROMPT_SUFFICIENCY_REVIEW_MATRIX.template.yaml`

## Implemented behavior

APF must now classify every relevant playbook object as one of:

- `simple_instruction_sufficient`;
- `existing_prompt_reuse`;
- `new_prompt_candidate`;
- `prompt_prohibited`;
- `needs_human_decision`.

Before `new_prompt_candidate` can be selected, APF must prove that the object contract is complete, deterministic strengthening was attempted, no compatible approved prompt exists, and the remaining need is guidance-oriented rather than authoritative process logic.

## Deliberately not implemented in PMP-1

- candidate prompt schema and prompt text generation;
- human approval record for prompt content;
- generated-playbook prompt registry;
- prompt attachment activation;
- final prompt test model;
- internal APF mini-prompts.

These remain assigned to PMP-2 and later milestones.

## Regression boundary

- confirmed rc.13 baseline identity is unchanged;
- Ordo core is unchanged;
- no real playbook or intake session has been started;
- BL-APF-001 and BL-APF-002B remain deferred;
- no candidate prompt has been created or activated.
