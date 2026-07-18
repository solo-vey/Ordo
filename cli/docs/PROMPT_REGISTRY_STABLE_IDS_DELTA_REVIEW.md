# M71.0 — Prompt Registry stable-ID delta matrix

| Area | Current state | Decision | M71 treatment |
|---|---|---|---|
| Registry object | Exists in `program.ordo.yaml` | Reuse | Extend fields/conventions later |
| `prompt_refs` on nodes | Exists with `prompt_id` + `use` | Reuse | Remains authoritative attachment |
| `guidance_refs` | Not needed | Reject parallel field | Optional transitional alias only if external packages require it |
| Prompt IDs | Mixed; several node-coupled | Migrate | Stable semantic, versioned IDs |
| Prompt filenames | Several begin with node IDs | Migrate | Semantic filename equals stable prompt ID |
| Manifest/checksum | Exists | Reuse | Update entries during migration |
| Lifecycle/visibility/authority | Exists | Reuse | Preserve and tighten validation |
| `current_nodes` in registry | Not authoritative today | Derived mirror only | Never use for navigation/runtime selection |
| `applies_when` | Not executable today | Metadata only | Must not become a second decision engine |
| Application phases | Existing controlled values | Reuse/normalize | Define closed vocabulary and deterministic ordering |
| Rename/split/merge stability | Not explicitly validated | Add checks | Extend current validation profile |
| Trace evidence | Prompt application not fully proven | Add later | Record ID, use phase and checksum, not hidden prompt text |

## Current node-coupled IDs

- `N_DISPLAY_TEXTS_human_ui_texts_helper` → candidate `hp.localization.bilingual_texts.v1`
- `N_PATH_SELECT_source_type_clarification` → candidate `hp.source_type.clarification.v1`
- `N_SOURCE_FIELD_external_fact_intake_helper` → candidate `hp.source_row.intake.v1`
- `N_VALUE_SEMANTICS_comparison_rule_helper` → candidate `hp.normalization.value_comparison.v1`

## Important boundary

This review does not rename prompts, edit package nodes, change navigation, or introduce executable prompt conditions.
