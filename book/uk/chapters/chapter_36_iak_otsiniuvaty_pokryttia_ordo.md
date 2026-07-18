# Розділ 36. Як оцінювати покриття Ordo

## Навіщо це потрібно

Коли Ordo-програма стає великою, вже недостатньо сказати: “у нас є правила”, “у нас є gates”, “у нас є тести”. Потрібно розуміти, яка частина цієї програми реально покрита структурою, тестами, debug trace і контрольованими механізмами перевірки.

У звичайному програмуванні для цього є поняття test coverage. Воно показує, які частини коду перевірені тестами. В Ordo потрібне ширше поняття, тому що Ordo-програма складається не тільки з коду або команд. Вона має intent, contract, nodes, paths, gates, outputs, state, FREEFORM, libraries, domain rules і human approval points.

Тому coverage в Ordo має відповідати не на одне питання, а на декілька:

```text
Які частини процесу формалізовані?
Які частини перевірені тестами?
Які частини видно в debug trace?
Які частини залишились у FREEFORM?
Які paths не мають regression tests?
Які gates існують у тексті, але не enforced у IR?
Які outputs перевіряються тільки за шаблоном, але не за rendered artifact?
```

Без такого покриття playbook може виглядати сильним, але реально мати великі “сліпі зони”.

## Просте пояснення

Покриття Ordo — це карта того, наскільки добре ми контролюємо поведінку моделі.

Якщо процес описаний тільки у prose, але не має nodes, gates і tests, його coverage низький.

Якщо процес має nodes і gates, але немає expected behavior tests, coverage середній.

Якщо процес має paths, gates, state checks, no-op tests, regression suite, FREEFORM coverage і rendered artifact validation, coverage високий.

Тобто coverage — це не про красу документації. Це про ступінь керованості.

## Що саме потрібно оцінювати

У Ordo треба оцінювати покриття щонайменше на таких рівнях:

```text
1. Intent coverage
2. Contract coverage
3. Path coverage
4. Node coverage
5. Gate coverage
6. State coverage
7. Output coverage
8. Negative assertion coverage
9. No-op coverage
10. FREEFORM coverage
11. Library coverage
12. Domain rule coverage
13. Rendered artifact coverage
14. Regression coverage
15. Feedback coverage
```

Це не означає, що кожна проста Ordo-програма має мати всі ці рівні. Але для великих playbook-ів і production workflows вони мають бути видимими.

## Path coverage

Path coverage показує, чи всі можливі маршрути процесу мають хоча б один test case.

Наприклад, якщо History Event Playbook має пʼять основних paths, але тести є тільки для трьох, coverage неповний.

```yaml
coverage:
  paths:
    total: 5
    covered: 3
    uncovered:
      - "A4_EXTERNAL_HISTORY_EVENT"
      - "A5_NO_EVENT"
```

Небезпека uncovered path у тому, що модель може формально знати про цей шлях, але ніколи не була перевірена на його реальному проходженні.

## Gate coverage

Gate coverage показує, які контрольні точки реально перевіряються.

Недостатньо мати gate у документації. Потрібно знати:

```text
- чи gate є в IR;
- чи gate має статус;
- чи gate blocking або warning;
- чи gate має test;
- чи є негативний test, де gate має заблокувати дію;
- чи gate видно в GATE.REPORT.
```

Приклад:

```yaml
coverage:
  gates:
    total: 14
    covered_by_tests: 11
    blocking_gates_without_negative_tests:
      - "G_PRE_ARCHIVE_APPROVAL"
      - "G_RENDERED_ARTIFACT_VALIDATED"
```

Якщо blocking gate не має негативного тесту, це ризик. Модель може пройти його у звичайному сценарії, але невідомо, чи вона правильно зупиниться, коли gate не виконаний.

## State coverage

State coverage показує, чи перевіряються ключові зміни стану.

У складних процесах саме state часто стає джерелом помилок. Модель може вважати щось підтвердженим, хоча користувач цього не підтверджував. Або може забути, що попередній status означав only_draft, а не ready_for_implementation.

Тому важливо перевіряти state до і після критичних кроків:

```yaml
expect:
  state:
    before:
      contract_confirmed: false
    after:
      contract_confirmed: true
    forbidden:
      final_archive_created: true
```

State coverage особливо важливий для approval, package generation, status semantics і improvement loop.

## Output coverage

Output coverage показує, чи перевіряється не тільки факт створення результату, а і його зміст, структура та відповідність contract.

Для Ordo output test може перевіряти:

```text
- чи створений правильний artifact;
- чи немає зайвих файлів;
- чи є mandatory sections;
- чи відповідає rendered artifact шаблону;
- чи не додано непідтверджені дані;
- чи є handoff note;
- чи є validation report;
- чи правильно відображені статуси.
```

Саме тут важливо відрізняти template validation від rendered artifact validation. Шаблон може бути правильним, але фінальний документ може бути зібраний неправильно.

## Negative assertion coverage

Negative assertion coverage показує, чи перевірені заборони.

У Ordo важливо тестувати не тільки те, що модель має зробити, а й те, чого вона не має робити.

Наприклад:

```yaml
expect_not:
  - "invent_missing_source_row"
  - "generate_final_archive_before_approval"
  - "treat_example_as_rule"
  - "apply_feedback_without_human_approval"
```

Якщо немає negative tests, модель може начебто виконувати процес, але робити небезпечні побічні дії.

## No-op coverage

No-op coverage потрібен для сценаріїв, де правильна дія — не робити нічого.

Це дуже важливо для історичних подій, моніторингових подій, змін у даних і будь-яких процесів, де не кожен input має породжувати output.

Приклад:

```yaml
test:
  id: "TC_NO_EVENT_FOR_UNCHANGED_VALUE"

expected:
  noop: true
  history_event_created: false
  change_record_created: false
```

Без no-op tests модель може створювати події там, де їх не має бути.

## FREEFORM coverage

FREEFORM не означає “неперевірене”. Якщо FREEFORM використовується у важливому процесі, треба знати:

```text
- який block FREEFORM існує;
- для чого він використовується;
- які decisions на нього спираються;
- чи є tests для сценаріїв із цього block;
- чи були problems/improvements, повʼязані з ним;
- чи можна частину FREEFORM формалізувати.
```

Якщо великий відсоток critical behavior живе у FREEFORM і не має tests, coverage низький, навіть якщо загальна документація виглядає повною.

## Library coverage

Після появи Ordo Libraries треба перевіряти не тільки локальний playbook, а й підключені бібліотеки.

Потрібно знати:

```text
- які libraries підключені;
- які exports реально використовуються;
- які versions зафіксовані;
- які library gates покриті тестами;
- чи є compatibility tests;
- чи є conflict resolution tests;
- чи є regression suite для library update.
```

Наприклад, якщо playbook підключає `ordo.validation.contract_first`, coverage має показати, які саме rules/gates із цієї бібліотеки використані й перевірені.

## Feedback coverage

Feedback coverage показує, чи перетворюються реальні зауваження користувача на structured improvement records.

Якщо користувач пʼять разів вказував на одну проблему, але жодного `IMPROVEMENT.RECORD` не створено, Ordo-процес втрачає знання.

Coverage має показувати:

```text
- скільки feedback records зібрано;
- скільки з них привʼязано до affected unit;
- скільки має proposed patch;
- скільки має suggested test;
- скільки очікує human approval;
- скільки закрито через regression suite.
```

Це робить розвиток playbook-а керованим, а не хаотичним.

## Приклад COVERAGE.REPORT

```yaml
coverage_report:
  id: "CR_HISTORY_EVENT_PLAYBOOK_001"

  paths:
    total: 5
    covered: 4
    uncovered:
      - "A4_EXTERNAL_HISTORY_EVENT"

  nodes:
    total: 18
    covered: 15
    uncovered:
      - "NODE_EXTERNAL_EVENT_MAPPING"

  gates:
    total: 14
    covered: 12
    missing_negative_tests:
      - "G_PRE_ARCHIVE_APPROVAL"

  state:
    tracked_fields: 22
    fields_with_expectations: 17
    untested_critical_fields:
      - "final_archive_created"
      - "rendered_artifact_validated"

  outputs:
    total: 11
    rendered_validation_covered: 9
    missing_rendered_validation:
      - "07_PROCESS_IMPROVEMENT_FEEDBACK"

  freeform:
    total_blocks: 5
    tested_blocks: 3
    formalization_candidates:
      - "FF_EDGE_CASE_DECISIONS"

  libraries:
    included: 2
    version_pinned: 2
    exports_used: 7
    exports_with_tests: 5

  feedback:
    records_total: 8
    linked_to_affected_unit: 6
    with_suggested_tests: 5
    pending_approval: 3

  overall:
    status: "partial"
    risk_level: "medium"
    recommendation: "add tests for A4, negative approval gate, and rendered validation for missing output"
```

## Типові помилки

Перша помилка — рахувати coverage тільки за кількістю тестів.

У Ordo один тест може перевіряти мало, а інший — критичний gate, state transition і output contract. Важлива не тільки кількість, а й те, що саме покрито.

Друга помилка — не рахувати FREEFORM.

Якщо FREEFORM впливає на рішення моделі, він має бути видимим у coverage.

Третя помилка — не рахувати negative tests.

Процес може вміти щось створювати, але не вміти зупинятися.

Четверта помилка — не рахувати no-op scenarios.

Для багатьох бізнесових процесів правильна поведінка часто полягає саме в тому, щоб не створювати зайвий результат.

Пʼята помилка — не оновлювати coverage після зміни library або domain pack.

Reusable рішення може змінити поведінку багатьох playbook-ів одночасно.

## Міні-вправа

Візьміть будь-який свій playbook і складіть простий coverage report.

Заповніть хоча б такі пункти:

```text
1. Скільки є основних paths?
2. Для скількох paths є tests?
3. Які gates є blocking?
4. Чи є для них negative tests?
5. Які state fields критичні?
6. Чи перевіряється rendered artifact?
7. Які частини залишаються у FREEFORM?
8. Чи є no-op tests?
9. Чи є feedback records?
10. Який найбільший uncovered risk?
```

Після цього виберіть одну uncovered частину і сформулюйте test, який її закриває.

## Короткий підсумок

Покриття Ordo — це оцінка того, наскільки поведінка моделі справді керована.

Добрий coverage report має показувати не тільки те, що вже працює, а й те, де процес ще небезпечний або непрозорий.

Для великих Ordo-програм потрібно оцінювати:

```text
- paths;
- nodes;
- gates;
- state;
- outputs;
- negative assertions;
- no-op scenarios;
- FREEFORM;
- libraries;
- domain rules;
- rendered artifacts;
- regression suite;
- feedback records.
```

Ordo-програма без coverage може виглядати завершеною, але залишатися непередбачуваною. Ordo-програма з coverage стає не тільки виконуваною, а й контрольованою.

---
