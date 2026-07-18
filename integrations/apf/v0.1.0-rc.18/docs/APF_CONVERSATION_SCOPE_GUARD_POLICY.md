# APF Conversation Scope Guard Policy — CSG-0

## Decision

APF adopts the Ordo `Conversation Scope Guard` contract as an optional capability that APF can design for generated playbooks. APF does not enable this capability for its own authoring process by default.

## Required authoring boundary

For every stateful conversational playbook, APF must explicitly decide whether the capability is unsupported, supported but disabled, or enabled. Enabling it requires human confirmation of mode, accepted context, deviation taxonomy, escalation, state protection, response behavior, pause/resume/exit handling, trace hooks, and regression tests.

## Mandatory invariants when enabled

- unrelated input cannot complete the active node;
- unrelated input cannot change path or confirmed state;
- unclassifiable input cannot be accepted as an answer;
- valid control intents and safety messages cannot be blocked;
- escalation must be scoped and reset predictably;
- package assembly must fail if required guard evidence is unresolved.

## Non-goals

CSG does not determine business scope automatically, replace process design, or force all playbooks into a locked mode.
