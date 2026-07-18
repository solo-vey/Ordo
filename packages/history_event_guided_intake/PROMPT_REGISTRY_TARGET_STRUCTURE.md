# Prompt Registry Target Structure — History Event Factory

Status: `M65.2 target-structure / implemented-skeleton`

## Target structure

```text
packages/history_event_guided_intake/
  prompts/
    QUICK_START_PROMPT.md
    runtime/
      START_PROMPT_HISTORY_EVENT_FACTORY_RUNTIME_MODE.md
    nodes/
      hp.source_type.clarification.v1.md
      hp.source_row.intake.v1.md
      hp.normalization.value_comparison.v1.md
      hp.localization.bilingual_texts.v1.md
    artifacts/
      hp.artifact.history_event_passport.v1.md
      hp.artifact.jira_task.v1.md
      hp.artifact.implementation_prompt.v1.md
      hp.qa.package_generation.v1.md
    repair/
      hp.repair.gate_failure_explanation.v1.md
      hp.repair.backtracking_invalidation.v1.md
      hp.repair.missing_artifact_resolution.v1.md
```

## File naming rule

Use current node ids when attaching to existing package nodes. If the future APF process later promotes branch-specific ids such as `ROOT_N1`, `B4_N1`, `B5_N3`, `COMMON_N4A`, or `B1_N4B`, the registry can add compatibility aliases or replace prompt ids through a controlled migration.

## Required first file

`prompts/hp.package.quick_start.v1.md` should be the first real prompt file added in the next implementation milestone.

Target content:

```text
Запусти History Event Guided Intake / History Event Factory з наданого пакета.
Веди мене по процесу по одному кроку, людською мовою, без YAML якщо я не попрошу.
Спирайся на START_HERE_RUNTIME_MODE.md і CLI Runtime Mode protocol.
Почни з runtime-entry / next-step, якщо CLI доступний.
```

This prompt must not claim that the model can skip CLI evidence or read compiled IR directly.
