# Anti-pattern reference pack — index

Цей каталог навмисно містить не лише taxonomy/schema, а й **приклади, каталоги, fixtures, runtime binding, APF wiring та historical reports**. Це зроблено, щоб наступний чат не втратив додаткові файли BL-ORDO-020 / anti-pattern line.

## Рекомендований порядок читання

1. `language/ANTIPATTERN_FUNDAMENTAL_TAXONOMY.md`
2. `language/improvement_intake/bl_ordo_020_references/APF_PATTERNS_AND_ANTIPATTERNS_CATALOG.md`
3. усі файли в `language/improvement_intake/bl_ordo_020_references/` — тут конкретні anti-pattern examples із реальних APF/History Event failures;
4. `language/registries/fundamental_antipattern_registry.v1.json`
5. `language/registries/antipattern_registry.v1.json`
6. `language/schemas/antipattern_*.schema.json`
7. `language/runtime/fixtures/*antipattern*` — executable/negative examples;
8. `language/runtime/antipattern_runtime.py` і signal extractors;
9. `language/integration/*antipattern*` — gate adapter/wiring;
10. `packages/ordo_applied_project_factory/docs/APF_ANTIPATTERN_*`
11. APF integration fixtures/tests/validators;
12. reports — historical evidence only; враховувати recovery warning про generated reports.

## Особливо важливі приклади

- `APF_IMPLEMENTATION_PROMPT_AS_IMPLEMENTATION_ANTIPATTERNS_UK.md`
  - AP-29 PROMPT_AS_IMPLEMENTATION
  - AP-30 PACKAGE_VALIDATION_WITHOUT_COMPLETENESS_VALIDATION
  - AP-31 MANDATORY_BRANCH_SHORT_CIRCUIT
  - AP-32 FINAL_LABEL_OVERCLAIM
- `APF_SCOPE_CONFIRMATION_EXECUTION_ROUTING_ANTIPATTERNS_UK.md`
  - scope confirmation ≠ implementation authorization
  - complexity routing/execution mixing
- `HISTORY_EVENT_FACTORY_ANTIPATTERNS_FROM_RECENT_FAILURES_UK.md`
  - concrete failure-derived examples
- `APF_PLAYBOOK_ANTIPATTERNS_AND_PATTERNS_CATALOG_UK.md`
  - playbook-oriented patterns/anti-patterns
- `APF_PATTERNS_AND_ANTIPATTERNS_CATALOG.md`
  - broader catalog.

## Recovery caveat

У recovered baseline ще присутні generated APF anti-pattern reports у package source tree. За BL-ORDO-032 closure history 10 таких report files були видалені з canonical source і перенесені в disposable evidence lifecycle. Тому їх присутність тут — **recovery artifact, не доказ правильної canonical placement policy**.
