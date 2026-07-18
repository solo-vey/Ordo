# M65.1 — APF / History Event Factory Prompt Adoption Plan Report

Status: `accepted-adoption-plan / no source rewrite`

## Scope

M65.1 applies the M65.0 Prompt Registry Standard to the concrete History Event Factory / guided intake package as an adoption plan.

It defines where prompt files should live, how they should attach to current package nodes/artifacts/repair flows, how README/START_HERE should expose them, and which validation/smoke checks should block a future implementation patch.

## Added files

- `packages/history_event_guided_intake/PROMPT_REGISTRY_ADOPTION_PLAN.md`
- `packages/history_event_guided_intake/PROMPT_REGISTRY_TARGET_STRUCTURE.md`
- `packages/history_event_guided_intake/PROMPT_REGISTRY_ADOPTION_MATRIX.md`
- `packages/history_event_guided_intake/PROMPT_REGISTRY_ADOPTION_MATRIX.csv`
- `packages/history_event_guided_intake/PROMPT_REGISTRY_VALIDATION_PROFILE.md`
- `packages/history_event_guided_intake/PROMPT_REGISTRY_SMOKE_TEST_PLAN.md`
- `docs/design_decisions/DD-ORDO-M65-002_APF_HISTORY_EVENT_FACTORY_PROMPT_ADOPTION_PLAN.md`
- `language/improvement_intake/m65_1/M65_1_APF_HISTORY_EVENT_FACTORY_PROMPT_ADOPTION_PLAN_REPORT.md`
- `language/improvement_intake/m65_1/M65_1_APF_HISTORY_EVENT_FACTORY_PROMPT_ADOPTION_PLAN_REPORT.json`
- `language/improvement_intake/m65_1/M65_1_VALIDATION_REPORT.json`

## Changed files

- `packages/history_event_guided_intake/README.md`
- `CHANGELOG.md`
- `FUTURE_BACKLOG.md`
- `STABLE_PACKAGE_INDEX.md`
- `language/CHANGELOG.md`
- `language/VALIDATION_REPORT.json`

## Key adoption decisions

1. Start with `prompts/QUICK_START_PROMPT.md` as the first required prompt file in the next implementation milestone.
2. Map proposed APF node ids to the current package node ids instead of referencing non-existing nodes.
3. Use current nodes:
   - `N_PATH_SELECT` for source/path selection;
   - `N_SOURCE_FIELD` for external fact/source intake;
   - `N_VALUE_SEMANTICS` for comparison and normalization guidance;
   - `N_DISPLAY_NAME_UK` / `N_DISPLAY_NAME_EN` for human/UI text guidance.
4. Register artifact helper prompts for passport, Jira, implementation prompt, and QA package generation.
5. Register repair helper prompts for gate failure, backtracking invalidation, and missing artifact resolution.
6. Require manifest/checksum coverage before prompt files become package contract artifacts.

## Non-changes

- no source YAML rewrite;
- no prompt files created as final package artifacts;
- no runtime core changes;
- no compiler behavior changes;
- no CLI command changes;
- no opcode promotion;
- no APF branch logic rewrite.

## Acceptance result

M65.1 is accepted as a concrete package adoption plan.

Next recommended milestone:

```text
M65.2 — History Event Factory prompt files + registry skeleton implementation patch
```
