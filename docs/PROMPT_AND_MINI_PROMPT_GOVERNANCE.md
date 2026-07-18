# Prompt and Mini-Prompt Governance

Prompt registries are package-local, machine-audited execution-support contracts. A prompt may support interpretation or artifact generation, but it never owns navigation, gate outcomes, human confirmation, confirmed-state mutation, hidden business logic or package-scope expansion.

Repository governance requires:

- every active registry entry to have one manifest entry, one existing file and a matching SHA-256 and byte count;
- every runtime prompt reference to resolve to the local registry;
- lifecycle and authority fields to be explicit;
- packages without a registry to contain no prompt references;
- downstream mini-prompts to remain proposals until a complete human review explicitly permits activation;
- internal APF mini-prompts to remain prohibited or unnecessary unless repeatable replay evidence satisfies the documented reopening conditions.

The executable repository gate is `ordo.prompt_governance.audit_prompt_governance`.
