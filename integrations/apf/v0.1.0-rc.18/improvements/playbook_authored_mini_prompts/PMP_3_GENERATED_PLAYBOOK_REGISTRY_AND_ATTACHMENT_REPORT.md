# PMP-3 — Generated-playbook registry and attachment model

Status: completed

Implemented:
- separate Prompt Registry for each generated playbook;
- manifest and checksum requirements;
- object-side `prompt_refs` as attachment source of truth;
- controlled use phases and ordering;
- prohibition on activating unapproved candidates;
- prohibition on mixing APF internal prompts with generated-playbook prompts;
- no empty prompt package when no prompts are approved.

Not implemented yet:
- full prompt validation/test contract (PMP-4);
- integration into canonical APF authoring flow and package templates (PMP-5);
- real playbook pilot.
