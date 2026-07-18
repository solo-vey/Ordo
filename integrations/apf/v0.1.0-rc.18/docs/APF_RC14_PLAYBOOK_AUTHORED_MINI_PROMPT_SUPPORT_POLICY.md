# APF rc.14 — Playbook-Authored Mini-Prompt Support

## Status

`release-candidate-ready-for-human-confirmation`

## Added capability

APF can now evaluate prompt sufficiency while creating a downstream playbook and conditionally produce governed mini-prompt assets.

Canonical flow:

```text
object contract
→ contract-strengthening review
→ Prompt Sufficiency Review
→ existing prompt reuse or candidate proposal
→ explicit human approval
→ downstream registry / manifest / attachment
→ validation and test evidence
→ conditional package assembly
```

## Authority boundary

Mini-prompts may provide local guidance, clarification, recovery help, or artifact-rendering instructions. They may not own navigation, gates, confirmed state, or business decisions.

## Package boundary

Prompt artifacts are generated only when needed. A simple playbook does not receive an empty Prompt Registry package.

## Exclusions

This release does not:

- add mini-prompts to APF internal nodes;
- activate History Event Playbook pilot candidates;
- start replay-based analyst-experience validation;
- modify Ordo core.
