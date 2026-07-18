# Приклад пропущеної implementation-гілки та антипатерни APF

## Інцидент

Після підтвердження `04_IMPLEMENTATION_PROMPT_LU_CHANGE_CAPITAL.md` процес перейшов одразу до складання та підтвердження `LU_CHANGE_CAPITAL_DRAFT_PACKAGE.zip`. У ZIP були Passport, Jira, implementation prompt, Manual QA та automation spec, але не було module/provider code, event definition, tests, repository patch або code validation evidence.

Правильна rail:

```text
IMPLEMENTATION_PROMPT_CONFIRMED
→ REPOSITORY_DISCOVERY
→ MODULE_ANALYSIS
→ IMPACT_ANALYSIS
→ IMPLEMENTATION_PLAN
→ CODE_IMPLEMENTATION
→ IMPLEMENTATION_MATERIALIZATION_GATE
→ CODE_REVIEW
→ TEST_EXECUTION
→ PACKAGE_COMPLETENESS_GATE
→ PACKAGE_ASSEMBLY
```

## AP-29. PROMPT_AS_IMPLEMENTATION

**Помилка:** instruction artifact прийнято як матеріалізовану реалізацію.

**Приклад:** `04_IMPLEMENTATION_PROMPT_*.md` було використано як доказ завершення implementation branch.

**Ризик:** package виглядає готовим, хоча code artifacts відсутні.

**Рішення:** artifact roles і gate `PROMPT_NOT_IMPLEMENTATION_01`.

## AP-30. PACKAGE_VALIDATION_WITHOUT_COMPLETENESS_VALIDATION

**Помилка:** перевіряється валідність наявних файлів, але не наявність усіх required artifact classes.

**Рішення:** `PACKAGE_COMPLETENESS_01` та truthful package labels: `analysis_package`, `implementation_ready_package`, `implementation_complete_package`, `release_candidate_package`.

## AP-31. MANDATORY_BRANCH_SHORT_CIRCUIT

**Помилка:** process переходить від підтвердженого prompt прямо до package assembly або terminal completion.

**Рішення:** direct-successor contract і заборонені transitions.

## AP-32. FINAL_LABEL_OVERCLAIM

**Помилка:** analysis-only ZIP називається final draft/implementation package.

**Рішення:** package label повинен відповідати фактичній lifecycle completeness.

## Targeted recovery

Зберегти: Passport, Jira, implementation prompt, Manual QA, automation spec і confirmed contracts. Інвалідувати лише package completeness, final package confirmation і completion status. Відновити процес у `CODE_IMPLEMENTATION`.
