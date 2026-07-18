# DD-ORDO-M71-001 — Stable Prompt Identity and Versioning

## Decision

Prompt identity is semantic and independent of executable tree coordinates.

```text
prompt_id != node_id
```

Canonical identifiers use a semantic family plus an immutable major version suffix.

## Rationale

Node-coupled identifiers create cascade renames across registry entries, files, refs, manifests, tests, and release notes. Stable semantic IDs keep prompts reusable across node rename, split, merge, and relocation.

## Consequences

- existing M65 registry structures are retained;
- `prompt_family`, integer `version`, and optional `supersedes` become the versioning convention;
- package refs migrate explicitly in a later step;
- checksums continue to identify exact content revisions;
- navigation authority remains with the executable decision model.

## Rejected alternatives

- naming prompt files by node ID;
- using unversioned generic identifiers;
- adding a second `guidance_refs` attachment mechanism;
- treating `applies_when` as executable logic.
