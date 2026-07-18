# Розділ 21. FREEFORM.COVERAGE

У попередніх розділах ми домовилися, що `FREEFORM` потрібен Ordo. Не все можна або варто перетворювати на строгі op-коди, таблиці й gates. Частина знань завжди залишатиметься у вигляді пояснень, прикладів, доменних нюансів, історичних зауважень або інструкцій для людини.

Але з цього виникає нова проблема.

Якщо `FREEFORM` дозволений, то потрібно розуміти:

```text
скільки важливої логіки залишилося у FREEFORM;
де саме вона знаходиться;
на що вона впливає;
чи можна її тестувати;
чи не приховані там критичні правила;
що з цього треба формалізувати пізніше.
```

Саме для цього в Ordo потрібна конструкція `FREEFORM.COVERAGE`.

## Навіщо потрібен FREEFORM.COVERAGE

Без coverage `FREEFORM` швидко перетворюється на чорну скриньку.

На перший погляд playbook може виглядати структурованим: є paths, nodes, gates, outputs, statuses. Але частина справжніх правил може залишитися у вільному тексті.

Наприклад:

```text
У складних випадках не створюй фінальний пакет без додаткової перевірки.
```

Якщо це просто фраза у FREEFORM, модель може виконати її один раз, пропустити інший раз, інтерпретувати по-своєму або не зрозуміти, що це blocking rule.

`FREEFORM.COVERAGE` потрібен, щоб такі місця були видимими.

Він відповідає на питання:

```text
Яка частина процесу вже формалізована, а яка ще живе у вільному тексті?
```

## FREEFORM не є помилкою

Важливо не сприймати `FREEFORM` як щось погане.

У хорошому Ordo-документі `FREEFORM` може бути абсолютно нормальним і потрібним. Проблема не в тому, що він існує. Проблема в тому, що ми не знаємо, яку роль він відіграє.

Є безпечний FREEFORM:

```text
пояснення для аналітика;
приклади формулювань;
опис доменного контексту;
історичні причини появи правила;
пояснення термінів;
рекомендації щодо стилю.
```

І є небезпечний FREEFORM:

```text
приховані gates;
приховані заборони;
умови переходу між paths;
правила створення output;
умови зупинки процесу;
винятки, які змінюють поведінку моделі.
```

`FREEFORM.COVERAGE` допомагає розрізняти ці два випадки.

## Що саме потрібно покривати

Coverage має показувати не лише кількість тексту у FREEFORM. Обсяг тексту сам по собі не головний.

Набагато важливіше зрозуміти, чи впливає FREEFORM на виконання.

Для кожного FREEFORM-блоку потрібно знати:

```text
id блоку;
де він знаходиться;
до якого path/node/gate/output він прив’язаний;
яку роль він виконує;
чи впливає на рішення моделі;
чи містить правила;
чи містить приклади;
чи потрібні для нього tests;
чи є improvement records, пов’язані з цим блоком;
чи потрібно його формалізувати пізніше.
```

У простому вигляді це можна уявити так:

```yaml
freeform_coverage:
  entries:
    - id: "FF_DOMAIN_CONTEXT_01"
      location: "History Event Domain Pack / Path A1"
      role: "domain_explanation"
      affects_execution: false
      test_required: false
      formalization_needed: false

    - id: "FF_EDGE_CASE_02"
      location: "Package Generation / Final Archive"
      role: "conditional_rule"
      affects_execution: true
      test_required: true
      formalization_needed: true
      suggested_formalization:
        - "convert to GATE.DEF"
        - "add ASSERT.NOT before final archive"
```

## Ролі FREEFORM-блоків

Щоб coverage був корисним, кожен FREEFORM-блок має мати роль.

Базові ролі можуть бути такими:

```text
explanation
example
note
warning
domain_context
style_guidance
edge_case
conditional_rule
human_instruction
migration_note
implementation_hint
```

Не всі ролі однаково ризикові.

Наприклад:

```text
example — зазвичай низький ризик;
explanation — низький або середній ризик;
warning — середній ризик;
edge_case — середній або високий ризик;
conditional_rule — високий ризик;
human_instruction — залежить від контексту;
implementation_hint — високий ризик, якщо впливає на output або tests.
```

Тому coverage має не просто рахувати блоки, а давати risk view.

## Risk view

У Ordo можна ввести просту класифікацію ризику:

```text
low
medium
high
critical
```

Наприклад:

```yaml
freeform_risk_summary:
  total_entries: 12
  low: 6
  medium: 3
  high: 2
  critical: 1

critical_entries:
  - id: "FF_NO_ARCHIVE_WITHOUT_SELF_CHECK"
    reason: "contains blocking behavior but is not represented as gate"
    action: "formalize_before_release"
```

Якщо FREEFORM-блок має рівень `critical`, Ordo-програма не повинна вважатися готовою до production-використання без рішення:

```text
формалізувати;
покрити тестом;
або явно прийняти ризик.
```

## FREEFORM.COVERAGE і тести

FREEFORM, який впливає на поведінку, має бути покритий тестами.

Наприклад, якщо у FREEFORM сказано:

```text
Якщо користувач просить створити архів до approval, потрібно зупинитися.
```

Це вже не просто пояснення. Це поведінкове правило.

Для нього потрібен test case:

```yaml
test:
  id: "TC_FREEFORM_NO_ARCHIVE_BEFORE_APPROVAL"
  method: human
  trust_class: human_decision

fixture:
  user_message: "створи архів одразу"

expected:
  gate:
    id: "G_PRE_ARCHIVE_APPROVAL"
    status: "blocked"

  output:
    archive_created: false
```

Coverage має показувати, що цей FREEFORM-блок або вже формалізований як gate, або хоча б перевірений тестом.

## FREEFORM.COVERAGE і Improvement Loop

Якщо користувач кілька разів вказує на проблему, яка походить із FREEFORM-блоку, це сильний сигнал.

Наприклад:

```text
Тут знову було неправильно витлумачено edge case.
```

Тоді improvement record має посилатися не тільки на run або node, а й на конкретний FREEFORM-блок:

```yaml
improvement_record:
  id: "IR-002"
  classification:
    type: "ambiguous_freeform_rule"
    severity: "high"

  affected_unit:
    kind: "freeform"
    id: "FF_EDGE_CASE_02"

  proposed_patch:
    - "split FREEFORM block into explanation and rule"
    - "convert rule part into GATE.DEF"
    - "add regression test"
```

Так `FREEFORM.COVERAGE` стає не просто звітом, а частиною циклу покращення Ordo-програми.

## Формалізація з часом

У першій версії playbook-а частина логіки може залишатися у FREEFORM. Це нормально.

Але Ordo має підтримувати поступову формалізацію.

Цикл може виглядати так:

```text
FREEFORM explanation
→ feedback показує проблему
→ debug trace показує місце
→ coverage позначає high risk
→ author формалізує правило
→ додається gate/assertion/test
→ regression suite перевіряє зміну
```

Тобто `FREEFORM.COVERAGE` допомагає розвивати Ordo-програму без різкого переписування всього документа.

## Мінімальний звіт FREEFORM.COVERAGE

Для простих Ordo-програм достатньо короткого звіту:

```yaml
freeform_coverage_report:
  total_entries: 5
  execution_affecting_entries: 1
  tested_entries: 1
  high_risk_entries: 0
  formalization_required: false
```

Для великих playbook-ів потрібен детальніший звіт:

```yaml
freeform_coverage_report:
  total_entries: 28
  by_role:
    explanation: 8
    example: 6
    domain_context: 5
    edge_case: 4
    conditional_rule: 3
    warning: 2

  execution_affecting:
    total: 7
    covered_by_tests: 5
    not_covered:
      - "FF_EDGE_CASE_07"
      - "FF_STATUS_WARNING_02"

  formalization_candidates:
    - id: "FF_EDGE_CASE_07"
      suggested_target: "GATE.DEF"
    - id: "FF_STATUS_WARNING_02"
      suggested_target: "STATUS.SEMANTICS"

  release_status: "blocked_until_review"
```

## Типові помилки

Перша помилка — рахувати тільки кількість FREEFORM.

Може бути багато безпечного FREEFORM і мало небезпечного. А може бути один короткий FREEFORM-блок, який фактично змінює всю поведінку процесу.

Друга помилка — не прив’язувати FREEFORM до конкретного місця execution.

Якщо блок не прив’язаний до path, node, gate, output або domain rule, його важко тестувати й покращувати.

Третя помилка — залишати blocking rule у FREEFORM.

Усе, що має зупиняти процес, має бути gate або assertion.

Четверта помилка — не тестувати FREEFORM edge cases.

Якщо FREEFORM описує складний виняток, для нього потрібен test case.

П’ята помилка — не переносити повторювані проблеми з FREEFORM у improvement backlog.

Якщо одна й та сама помилка виникла кілька разів, це вже не випадковість. Це сигнал, що Ordo-програму треба покращувати.

## Міні-вправа

Візьміть будь-який фрагмент playbook-а з вільним текстом і дайте відповідь на п’ять питань:

```text
1. Це пояснення, приклад, warning чи правило?
2. Чи впливає цей текст на рішення моделі?
3. Чи може неправильне тлумачення цього тексту зламати процес?
4. Чи є для нього тест?
5. Чи потрібно формалізувати його як gate, assertion, status або output rule?
```

Якщо відповідь на друге або третє питання — “так”, цей FREEFORM-блок має бути видимим у coverage report.

## Короткий підсумок

`FREEFORM.COVERAGE` потрібен, щоб Ordo не перетворилася назад на великий некерований prompt.

FREEFORM дозволяє зберегти людський сенс, доменні пояснення й складні нюанси. Але все, що впливає на execution, має бути видимим, прив’язаним, оціненим за ризиком і, за потреби, покритим тестами.

Головна ідея розділу проста:

```text
FREEFORM дозволений, але він не має бути невидимим.
```

У зрілій Ordo-програмі кожен важливий FREEFORM-блок має відповідь на три питання:

```text
де він використовується;
на що він впливає;
як ми перевіряємо, що він не ламає процес.
```


---
