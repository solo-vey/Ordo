# APF Prompt Registry Policy — A3

## Status

`A3-applied-working-state / package-level convention`

## Authority

APF prompts support explanation, clarification, recovery, startup, and validation interpretation. They do not own routing, gates, transitions, state confirmation, artifact scope, or release approval.

Canonical rule:

```text
prompt_id != node_id
```

Prompt identity is semantic and versioned. Object-side `prompt_refs` are authoritative attachments. Registry-side `attached_to` fields are descriptive metadata and must not override the attachment map.

## Scope of A3

A3 migrates existing APF prompt-like surfaces only:

- package quick start;
- runtime start discipline;
- resume-after-deviation explanation;
- backtracking invalidation explanation;
- gate-failure explanation;
- validation-report interpretation.

A3 does not perform an APF-wide node mini-prompt applicability review and does not start `BL-APF-002`.

## Application and evidence

The current object is resolved before prompts. Only its prompt refs may be applied. Same-phase source-list order is normative. Package-local evidence may record `prompt_id`, `use`, `sha256`, and `ordinal` after checksum verification.

This does not extend the Ordo session-trace writer and is not claimed as full runtime enforcement.
