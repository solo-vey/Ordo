# M71.0 — Delta review: current Prompt Registry vs stable semantic IDs

Status: `accepted-delta-review / passed-scope-validation`

## Conclusion

The repository already contains a Prompt Registry implementation from M65. The new improvement is therefore a migration and hardening of prompt identity, not a second registry implementation.

## Existing implementation to retain

- package-level registry in `packages/history_event_guided_intake/source/program.ordo.yaml`;
- node-level `prompt_refs` with application phase `use`;
- prompt files grouped by runtime/node/artifact/repair roles;
- `PROMPT_MANIFEST.json` with file checksums;
- lifecycle, visibility, audience and authority boundaries;
- existing registry schema and validation profile.

## Confirmed delta

The current package contains 13 prompt IDs. Four are directly coupled to node IDs and filenames:

- `N_DISPLAY_TEXTS_human_ui_texts_helper`
- `N_PATH_SELECT_source_type_clarification`
- `N_SOURCE_FIELD_external_fact_intake_helper`
- `N_VALUE_SEMANTICS_comparison_rule_helper`

The remaining generic IDs are also migration candidates because they are unversioned and not namespaced consistently.

## Accepted decisions

1. Keep `prompt_refs`; do not introduce a second normative `guidance_refs` field.
2. Make node attachments authoritative. Any `current_nodes` registry field is derived or a validated mirror.
3. Use semantic, versioned IDs independent from node IDs.
4. Add `prompt_family`, `version`, and `supersedes` conventions in the next contract step.
5. Treat `applies_when` as descriptive metadata only; executable applicability remains in the decision model.
6. Extend the current validation framework rather than adding a parallel validation system.
7. Later trace evidence should record prompt ID, phase and checksum without exposing hidden prompt text.

## Scope

No prompt IDs, prompt files, node references, navigation, runtime, compiler, opcodes, or applied package behavior were changed in M71.0.
