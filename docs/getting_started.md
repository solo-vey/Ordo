# Getting started з Ordo

1. Встановіть CLI у editable-режимі з каталогу `cli/`.
2. Перевірте один із актуальних reference packages у `packages/`.
3. Для authoring-сценарію використовуйте `packages/ordo_project_builder`.
4. Для execution-сценарію використовуйте `packages/ordo_hybrid_executor`.

```bash
cd cli
python -m pip install -e .
ordo lint ../packages/ordo_project_builder
ordo compile ../packages/ordo_project_builder
ordo test ../packages/ordo_project_builder
ordo coverage ../packages/ordo_project_builder
ordo validate-state ../packages/ordo_project_builder --answers ../packages/ordo_project_builder/run_inputs/authoring_success.yaml
ordo next-step ../packages/ordo_project_builder --answers ../packages/ordo_project_builder/run_inputs/authoring_success.yaml
```

CLI у цьому workspace є helper layer: він перевіряє, компілює й пояснює стан Process Rail, але не замінює AI Ordo Developer / AI Ordo Executor.
