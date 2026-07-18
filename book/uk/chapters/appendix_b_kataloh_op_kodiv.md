# Додаток B. Каталог op-кодів

Цей додаток містить базовий каталог op-кодів Ordo. Він не є фінальною повною специфікацією, але показує мінімальний набір конструкцій, які потрібні для опису, виконання, перевірки і покращення Ordo-програм.

## 1. Core op-коди

### `INTENT.DEF`

Описує намір користувача або процесу.

Використовується для фіксації того, що саме має бути досягнуто.

### `CONTRACT.DEF`

Описує execution contract: що дозволено, що заборонено, які підтвердження потрібні, який результат очікується.

### `CONTEXT.DEF`

Описує контекст виконання: джерела, документи, дані, обмеження, domain rules.

### `STATE.SCHEMA`

Описує структуру state, яку Ordo-програма має підтримувати під час виконання.

### `STATE.SET`

Встановлює або оновлює значення в state.

### `STATE.GET`

Читає значення зі state.

### `ENTRY.DEF`

Описує точку входу в процес.

### `NODE.DEF`

Описує вузол процесу: питання, рішення, дію або перехід.

### `PATH.DEF`

Описує можливий маршрут виконання.

### `PATH.SELECT`

Фіксує вибір конкретного path.

### `STEP.DEF`

Описує окремий крок у процесі.

### `OUTPUT.DEF`

Описує очікуваний output.

### `HANDOFF.DEF`

Описує правила передачі результату людині, системі або наступному процесу.

## 2. Gate і assertion op-коди

### `GATE.DEF`

Описує контрольну точку.

### `GATE.EVAL`

Оцінює, чи пройдений gate.

### `GATE.REPORT`

Формує звіт про проходження gates.

### `ASSERT.REQUIRE`

Вимагає наявності певної умови.

### `ASSERT.NOT`

Забороняє певну дію, стан або output.

### `ASSERT.EQUAL`

Перевіряє рівність очікуваного і фактичного значення.

### `ASSERT.EXISTS`

Перевіряє, що потрібне значення існує.

### `ASSERT.MISSING`

Перевіряє, що значення відсутнє, якщо саме це очікується.

## 3. Status op-коди

### `STATUS.DEF`

Описує допустимий статус.

### `STATUS.SEMANTICS`

Описує значення статусу для execution behavior.

### `STATUS.MAP`

Мапить зовнішній статус на внутрішній статус Ordo.

### `STATUS.EVAL`

Оцінює поточний статус і визначає дозволену поведінку.

## 4. FREEFORM op-коди

### `FREEFORM.DEF`

Описує контрольований FREEFORM-блок.

### `FREEFORM.BIND`

Прив’язує FREEFORM до конкретного node, gate, domain rule, output або library.

### `FREEFORM.REASON`

Пояснює, чому ця частина залишена у FREEFORM.

### `FREEFORM.COVERAGE`

Оцінює, наскільки FREEFORM-блок покритий тестами, gates або trace.

### `FREEFORM.MIGRATE.SUGGEST`

Пропонує формалізувати частину FREEFORM у structured Ordo-конструкції.

## 5. Profile і domain op-коди

### `PROFILE.DEF`

Описує Ordo Profile.

### `PROFILE.BIND`

Підключає profile до Ordo-програми.

### `DOMAIN.DEF`

Описує domain pack.

### `DOMAIN.RULE`

Описує предметне правило.

### `DOMAIN.VOCAB`

Описує domain vocabulary.

### `DOMAIN.GATE`

Описує domain-specific gate.

### `DOMAIN.OUTPUT`

Описує domain-specific output.

## 6. Library op-коди

### `LIB.DEF`

Описує Ordo Library.

### `LIB.INCLUDE`

Підключає бібліотеку до поточної Ordo-програми.

### `LIB.IMPORT`

Імпортує конкретні exports із бібліотеки.

### `LIB.USE`

Фіксує використання підключеної library-конструкції.

### `LIB.EXPORT`

Описує, які конструкції бібліотека надає назовні.

### `LIB.NAMESPACE`

Описує namespace бібліотеки.

### `LIB.ALIAS`

Встановлює локальний alias для бібліотеки або export.

### `LIB.VERSION.REQUIRE`

Фіксує вимогу до версії бібліотеки.

### `LIB.COMPAT.CHECK`

Перевіряє сумісність бібліотеки з версією Ordo, profile або domain pack.

### `LIB.CONFLICT.DETECT`

Виявляє конфлікти між підключеними бібліотеками або локальними правилами.

### `LIB.CONFLICT.RESOLVE`

Описує явне рішення для конфлікту.

### `LIB.OVERRIDE.ALLOW`

Дозволяє явний override.

### `LIB.OVERRIDE.DENY`

Забороняє override.

## 7. Debug op-коди

### `DEBUG.MODE`

Вмикає debug mode або описує параметри debug execution.

### `TRACE.LOG`

Фіксує execution trace.

### `DECISION.LOG`

Фіксує рішення, прийняті під час виконання.

### `PATH.EXPLAIN`

Пояснює, чому обрано або відхилено певний path.

### `STATE.SNAPSHOT`

Фіксує знімок state.

### `STATE.DIFF`

Фіксує різницю між двома state snapshots.

### `KNOWLEDGE.TRACE`

Фіксує знання, документи, rules або examples, які були використані.

### `RUN.DRY`

Описує dry run без створення фінального output або зовнішньої зміни.

### `RUN.REPLAY`

Описує replay попереднього run.

### `FAILURE.EXPLAIN`

Пояснює причину помилки або блокування виконання.

## 8. Test op-коди

### `TEST.DEF`

Описує test case.

### `FIXTURE.DEF`

Описує вхідні дані для test case.

### `EXPECT.PATH`

Описує очікуваний path.

### `EXPECT.STATE`

Описує очікуваний state або state diff.

### `EXPECT.OUTPUT`

Описує очікуваний output.

### `EXPECT.NOOP`

Описує сценарій, де дія не має виконуватися.

### `EXPECT.GATE`

Описує очікуваний gate status.

### `EXPECT.NOT`

Описує те, що не повинно статися під час test run.

### `REGRESSION.SUITE`

Описує набір regression tests.

### `COVERAGE.REPORT`

Описує покриття paths, gates, nodes, outputs, FREEFORM blocks, libraries і domain rules.

## 9. Feedback і improvement op-коди

### `FEEDBACK.CAPTURE`

Фіксує feedback користувача.

### `ISSUE.RECORD`

Створює запис про проблему.

### `IMPROVEMENT.RECORD`

Створює запис про покращення.

### `PROBLEM.CLASSIFY`

Класифікує проблему.

### `ROOT_CAUSE.LINK`

Прив’язує проблему до ймовірної причини.

### `AFFECTED.UNIT`

Вказує, яку частину Ordo-програми зачіпає проблема або покращення.

Це може бути node, gate, rule, FREEFORM block, library, domain pack, profile або compiler rule.

### `PATCH.SUGGEST`

Пропонує зміну.

### `TEST.SUGGEST`

Пропонує тест, який треба додати.

### `REGRESSION.ADD`

Додає test case до regression suite.

### `VERSION.NOTE`

Фіксує зміст зміни для версії.

### `CHANGELOG.UPDATE`

Оновлює changelog.

### `LESSON.LEARNED`

Фіксує висновок, який треба враховувати в майбутніх версіях.

## 10. Documentation Runtime op-коди

### `DOC.SPLIT`

Описує розбиття великого документа на частини.

### `DOC.CATALOG`

Описує каталог доступних документів або секцій.

### `DOC.SELECT`

Фіксує вибір релевантних документів для поточного node або path.

### `DOC.RENDER`

Описує створення rendered artifact.

### `RENDER.VALIDATE`

Перевіряє готовий rendered artifact, а не тільки template.

### `DOC.TRACE`

Фіксує, які документи або секції були використані.

## 11. Approval op-коди

### `APPROVAL.REQUIRE`

Описує дію, яка потребує людського підтвердження.

### `APPROVAL.CAPTURE`

Фіксує отримане підтвердження.

### `APPROVAL.BLOCK`

Блокує виконання до підтвердження.

### `APPROVAL.REJECT`

Фіксує відхилення дії або зміни.

## 12. Мінімальний набір для production playbook

Для складного production playbook мінімально потрібні:

```text
INTENT.DEF
CONTRACT.DEF
CONTEXT.DEF
STATE.SCHEMA
ENTRY.DEF
NODE.DEF
PATH.DEF
GATE.DEF
ASSERT.NOT
STATUS.SEMANTICS
OUTPUT.DEF
HANDOFF.DEF
TRACE.LOG
GATE.REPORT
TEST.DEF
FIXTURE.DEF
EXPECT.PATH
EXPECT.GATE
EXPECT.OUTPUT
REGRESSION.SUITE
COVERAGE.REPORT
FEEDBACK.CAPTURE
IMPROVEMENT.RECORD
```

Якщо playbook використовує бібліотеки, додатково потрібні:

```text
LIB.INCLUDE
LIB.VERSION.REQUIRE
LIB.COMPAT.CHECK
LIB.CONFLICT.DETECT
LIB.OVERRIDE.ALLOW / LIB.OVERRIDE.DENY
```

Якщо playbook має значну частину у FREEFORM, додатково потрібні:

```text
FREEFORM.DEF
FREEFORM.BIND
FREEFORM.COVERAGE
FREEFORM.MIGRATE.SUGGEST
```

## Короткий підсумок

Op-коди Ordo — це не просто назви команд. Це спосіб зробити складну інструкцію видимою для виконання, перевірки, трасування і покращення.

Каталог op-кодів потрібен для того, щоб Ordo-програми можна було не тільки читати, а й компілювати, тестувати, порівнювати, дебажити і поступово переводити до native model support.


---

---

## 12. Конструкції Ordo v0.12: reliability, trust semantics і execution modes

### `GATE.METHOD`

Описує спосіб перевірки gate.

Допустимі значення:

```text
mechanical
self_verification
self_consistency
human
```

Gate без `method` у v0.12 має вважатися помилкою компіляції.

### `TRUST.CLASS`

Описує клас довіри до результату перевірки.

Приклади:

```text
deterministic
model_judgment
repeated_model_judgment
human_decision
```

### `TRACE.SOURCE`

Фіксує джерело довіри до execution trace.

Допустимі значення:

```text
model_self_report
runtime_enforced
hybrid
```

### `EXECUTION.MODE`

Фіксує режим виконання програми.

Допустимі значення:

```text
full_runtime
chat_internal
freeform_only
```

### `ASSERTION.DEF`

Описує канонічне правило, яке має бути виконане або заборонене.

Приклад:

```yaml
assertion:
  id: A_NO_FINAL_OUTPUT_BEFORE_APPROVAL
  polarity: not
  condition: final_output_before_approval
  phase: [runtime, test]
  severity: block
  on_fail: STOP
```

### `ASSERTION.PROJECT`

Розгортає `ASSERTION` у runtime-перевірку, test expectation і debug violation record.

### `CLARIFY.REQUEST`

Окремий op-код для контрольованого уточнення, коли input користувача не відповідає жодному allowed answer.

### `NAMESPACE.RESOLVE`

Розгортає локальні IDs у повні namespaced IDs у compiled IR.

### `VERSION.REQUIRE`

Фіксує вимогу до версії Core, Profile, Domain Pack або Library.

### `LAYER.CONFLICT.CHECK`

Перевіряє конфлікти між Core, Profile, Domain Pack, Libraries і FREEFORM.

### `OVERRIDE.DEF`

Описує явний override правила з іншого шару.

Override має містити target, reason і approval policy.

### `CONTROL_LEVEL.DEF`

Описує рівень строгості Ordo-програми:

```text
light
standard
strict
```

### `FREEFORM.MATURITY`

Фіксує стан зрілості FREEFORM-блоку:

```text
stable
volatile
candidate_for_formalization
```

### `FREEFORM.INCIDENT_COUNT`

Рахує кількість feedback/improvement інцидентів, повʼязаних із конкретним FREEFORM-блоком.

### `FREEFORM.FORMALIZATION.WARNING`

Попереджає, що FREEFORM-блок перевищив incident threshold і має бути розглянутий для формалізації.

### `G_NO_UNRESOLVED_LAYER_CONFLICT`

Системний gate, який блокує виконання, якщо знайдено конфлікт між шарами без явного `OVERRIDE.DEF`.

Рекомендований метод:

```yaml
method: mechanical
trust_class: deterministic
```

## Contract and Artifact Coverage

| Op / construct | Призначення |
|---|---|
| `CONTRACT.DEF` | Описує підтверджений або запропонований контракт процесу. |
| `CONTRACT.FIELD` | Описує поле контракту та його статус. |
| `CONTRACT.STATUS` | Вказує `missing`, `candidate`, `proposed`, `confirmed`, `blocked`, `not_applicable`. |
| `ARTIFACT.DEF` | Описує generated artifact, який має бути створений. |
| `ARTIFACT.REQUIREMENT` | Звʼязує confirmed contract fields з required artifacts. |
| `COVERAGE.RULE` | Описує deterministic coverage policy. |
| `RENDERED_ARTIFACT.ASSERT` | Перевіряє вже згенерований файл. |
| `CONSISTENCY.REPORT` | Фіксує cross-artifact consistency result. |
| `GO_NO_GO.DECISION` | Дає фінальне machine-readable рішення. |



## M46.2 contract/artifact op-коди

- `CONTRACT.INSTANCE` — декларація конкретного process contract з полями та статусами.
- `ARTIFACT.DEF` — декларація очікуваного generated artifact.
- `ARTIFACT.REQUIREMENT` — правило, яке мапить поля підтвердженого контракту в артефакти.
- `COVERAGE.RULE` — політика перевірки contract → artifact coverage.
- `RENDERED_ARTIFACT.ASSERT` — майбутня runtime/assertion-проекція для перевірки rendered files.
- `GO_NO_GO.DECISION` — машинозчитуване рішення щодо готовності пакета.


## EXECUTION_TRACE.DEF

Оголошує canonical execution-trace artifact для одного run. Визначає metadata, capture level, replay policy, integrity contract і ordered event stream.

## TRACE.EVENT.APPEND

Зарезервований op-код для append-only додавання canonical trace event. Фактична compiler/runtime семантика вводиться в наступній частині інтеграції.
