# Prompt ID migration map

M71.3 authoritative compatibility map. Runtime and nodes use only the new semantic IDs; legacy IDs are retained for audit/migration reference.

| Legacy prompt ID | Stable prompt ID | Old path | New path |
|---|---|---|---|
| `quick_start_prompt` | `hp.package.quick_start.v1` | `prompts/QUICK_START_PROMPT.md` | `prompts/hp.package.quick_start.v1.md` |
| `history_event_runtime_start_prompt` | `hp.runtime.start.v1` | `prompts/runtime/START_PROMPT_HISTORY_EVENT_FACTORY_RUNTIME_MODE.md` | `prompts/hp.runtime.start.v1.md` |
| `N_PATH_SELECT_source_type_clarification` | `hp.source_type.clarification.v1` | `prompts/nodes/N_PATH_SELECT_source_type_clarification.md` | `prompts/hp.source_type.clarification.v1.md` |
| `N_SOURCE_FIELD_external_fact_intake_helper` | `hp.source_row.intake.v1` | `prompts/nodes/N_SOURCE_FIELD_external_fact_intake_helper.md` | `prompts/hp.source_row.intake.v1.md` |
| `N_VALUE_SEMANTICS_comparison_rule_helper` | `hp.normalization.value_comparison.v1` | `prompts/nodes/N_VALUE_SEMANTICS_comparison_rule_helper.md` | `prompts/hp.normalization.value_comparison.v1.md` |
| `N_DISPLAY_TEXTS_human_ui_texts_helper` | `hp.localization.bilingual_texts.v1` | `prompts/nodes/N_DISPLAY_TEXTS_human_ui_texts_helper.md` | `prompts/hp.localization.bilingual_texts.v1.md` |
| `passport_generation_helper` | `hp.artifact.history_event_passport.v1` | `prompts/artifacts/passport_generation_helper.md` | `prompts/hp.artifact.history_event_passport.v1.md` |
| `jira_task_generation_helper` | `hp.artifact.jira_task.v1` | `prompts/artifacts/jira_task_generation_helper.md` | `prompts/hp.artifact.jira_task.v1.md` |
| `implementation_prompt_generation_helper` | `hp.artifact.implementation_prompt.v1` | `prompts/artifacts/implementation_prompt_generation_helper.md` | `prompts/hp.artifact.implementation_prompt.v1.md` |
| `qa_package_generation_helper` | `hp.qa.package_generation.v1` | `prompts/artifacts/qa_package_generation_helper.md` | `prompts/hp.qa.package_generation.v1.md` |
| `gate_failure_explanation_helper` | `hp.repair.gate_failure_explanation.v1` | `prompts/repair/gate_failure_explanation_helper.md` | `prompts/hp.repair.gate_failure_explanation.v1.md` |
| `backtracking_invalidation_helper` | `hp.repair.backtracking_invalidation.v1` | `prompts/repair/backtracking_invalidation_helper.md` | `prompts/hp.repair.backtracking_invalidation.v1.md` |
| `missing_artifact_resolution_helper` | `hp.repair.missing_artifact_resolution.v1` | `prompts/repair/missing_artifact_resolution_helper.md` | `prompts/hp.repair.missing_artifact_resolution.v1.md` |
