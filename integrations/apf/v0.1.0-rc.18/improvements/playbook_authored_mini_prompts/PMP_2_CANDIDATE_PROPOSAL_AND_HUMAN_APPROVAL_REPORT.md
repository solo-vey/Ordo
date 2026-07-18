# PMP-2 — Candidate Proposal and Human Approval Gate Report

## Result

PMP-2 is complete. APF now has a normative proposal contract and blocking human approval gate for mini-prompts authored for downstream playbooks.

## Added

- `docs/APF_MINI_PROMPT_CANDIDATE_PROPOSAL_CONTRACT.yaml`
- `docs/APF_MINI_PROMPT_HUMAN_APPROVAL_GATE.yaml`
- `docs/APF_MINI_PROMPT_CANDIDATE_AND_APPROVAL_POLICY.md`
- `templates/MINI_PROMPT_CANDIDATE_PROPOSAL.template.yaml`
- `templates/MINI_PROMPT_HUMAN_REVIEW_RECORD.template.yaml`

## Behavioral outcome

A `new_prompt_candidate` result from PMP-1 can now produce a structured proposal. The proposal remains inactive until a named human reviewer makes an explicit decision. Approval permits progression to PMP-3 but does not itself create a registry entry, manifest entry or `prompt_ref`.

## Boundaries preserved

- No mini-prompt was created for an actual playbook.
- No internal APF mini-prompt was added.
- No prompt was activated or attached.
- Ordo core was not changed.
- BL-APF-001 and BL-APF-002B remain deferred.

## Next milestone

`PMP-3 — Generated-playbook registry and attachment model`.
