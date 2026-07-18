# Generated Playbook Prompt Registry and Attachment Policy

## Decision

Each playbook created by APF owns its own Prompt Registry, Prompt Manifest and attachment map. The APF registry is not reused as the generated playbook registry.

## Activation sequence

```text
approved candidate
→ prompt file generated
→ generated-playbook registry entry
→ manifest entry and SHA-256
→ object-side prompt_ref
→ attachment validation
```

Approval authorizes generation, but does not itself activate a prompt. Activation requires a valid registry entry, matching checksum and valid attachment.

## Authority boundary

A prompt may guide explanation, clarification, recovery or rendering. It may not select `next_node`, bypass a gate, confirm state, or introduce hidden process rules.

## Empty-package rule

If no prompt is approved, APF must not create an empty prompt package for the generated playbook.
