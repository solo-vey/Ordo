# M71.1 — Stable Prompt Identity and Versioning Convention Report

Status: `accepted-convention / passed-validation`

## Outcome

M71.1 extends the existing M65 Prompt Registry with a stable semantic identity and lineage convention.

## Accepted rules

- `prompt_id != node_id`;
- canonical form is `<namespace>.<semantic_role>.v<major>`;
- `prompt_family` omits the version suffix;
- `version` is a positive integer and must match the suffix;
- `supersedes` links only within one family;
- stable IDs are immutable;
- exact non-breaking content revisions are identified by manifest checksum;
- `prompt_refs` are authoritative attachment records;
- registry reverse mappings are derived metadata;
- application phases use a controlled vocabulary;
- prompt authority remains local and cannot alter navigation.

## Scope

This milestone changes language convention, schema documentation, and design documentation only.

No package prompt IDs, prompt files, node refs, navigation, runtime, compiler, opcode, or compiled IR were changed.
