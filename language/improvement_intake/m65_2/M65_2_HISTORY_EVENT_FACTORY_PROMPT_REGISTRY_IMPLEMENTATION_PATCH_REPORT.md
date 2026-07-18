# M65.2 — History Event Factory Prompt Registry Implementation Patch Report

Status: `implemented-skeleton / passed-prompt-registry-validation`

## Scope

M65.2 applies the M65.1 adoption plan to `packages/history_event_guided_intake/` as a package-local prompt registry skeleton implementation.

## Added files

- `packages/history_event_guided_intake/prompts/QUICK_START_PROMPT.md`
- `packages/history_event_guided_intake/prompts/runtime/START_PROMPT_HISTORY_EVENT_FACTORY_RUNTIME_MODE.md`
- `packages/history_event_guided_intake/prompts/nodes/N_PATH_SELECT_source_type_clarification.md`
- `packages/history_event_guided_intake/prompts/nodes/N_SOURCE_FIELD_external_fact_intake_helper.md`
- `packages/history_event_guided_intake/prompts/nodes/N_VALUE_SEMANTICS_comparison_rule_helper.md`
- `packages/history_event_guided_intake/prompts/nodes/N_DISPLAY_TEXTS_human_ui_texts_helper.md`
- `packages/history_event_guided_intake/prompts/artifacts/passport_generation_helper.md`
- `packages/history_event_guided_intake/prompts/artifacts/jira_task_generation_helper.md`
- `packages/history_event_guided_intake/prompts/artifacts/implementation_prompt_generation_helper.md`
- `packages/history_event_guided_intake/prompts/artifacts/qa_package_generation_helper.md`
- `packages/history_event_guided_intake/prompts/repair/gate_failure_explanation_helper.md`
- `packages/history_event_guided_intake/prompts/repair/backtracking_invalidation_helper.md`
- `packages/history_event_guided_intake/prompts/repair/missing_artifact_resolution_helper.md`
- `packages/history_event_guided_intake/PROMPT_MANIFEST.json`
- `packages/history_event_guided_intake/PROMPT_REGISTRY_IMPLEMENTATION_SUMMARY.md`
- `docs/design_decisions/DD-ORDO-M65-003_HISTORY_EVENT_FACTORY_PROMPT_REGISTRY_SKELETON.md`

## Changed files

- `packages/history_event_guided_intake/source/program.ordo.yaml`
- `packages/history_event_guided_intake/README.md`
- `packages/history_event_guided_intake/START_HERE_RUNTIME_MODE.md`
- `packages/history_event_guided_intake/START_PROMPT_RUNTIME_MODE.md`
- `packages/history_event_guided_intake/PROMPT_REGISTRY_ADOPTION_PLAN.md`
- `packages/history_event_guided_intake/PROMPT_REGISTRY_ADOPTION_MATRIX.md`
- `packages/history_event_guided_intake/PROMPT_REGISTRY_ADOPTION_MATRIX.csv`
- `packages/history_event_guided_intake/PROMPT_REGISTRY_TARGET_STRUCTURE.md`

## Key implementation decisions

1. Created all prompt files listed by the M65.1 target structure.
2. Added a full package-local `prompt_registry` block to `source/program.ordo.yaml`.
3. Added `prompt_refs` to selected current nodes:
   - `N_PATH_SELECT`;
   - `N_SOURCE_FIELD`;
   - `N_VALUE_SEMANTICS`;
   - `N_DISPLAY_NAME_UK`;
   - `N_DISPLAY_NAME_EN`.
4. Added artifact helper refs to the four required package artifacts.
5. Added repair helper refs for gate failure explanation and missing artifact resolution.
6. Added a transitional `PROMPT_MANIFEST.json` with SHA-256 checksums.

## Non-changes

- no runtime core change;
- no compiler behavior change;
- no CLI command change;
- no opcode promotion;
- no compiled IR regeneration claimed;
- no APF branch logic rewrite;
- no deterministic natural-language classifier.

## Acceptance result

M65.2 is accepted as a package-local prompt registry skeleton implementation patch.
