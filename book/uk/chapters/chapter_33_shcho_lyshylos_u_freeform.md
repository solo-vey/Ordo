# Розділ 33. Що лишилось у FREEFORM

## Навіщо це потрібно

Ми вже говорили, що Ordo не повинна намагатися формалізувати абсолютно все. Для частини знань потрібен `FREEFORM`: пояснення, приклади, попередження, історичні нотатки, складні доменні формулювання.

Але після міграції великого playbook-а в Ordo завжди виникає питання:

```text
Що саме залишилось у FREEFORM?
```

Це не дрібниця. Відповідь на це питання показує рівень зрілості Ordo-програми.

Якщо у FREEFORM залишилось тільки те, що справді не варто формалізувати, — це нормально.

Якщо у FREEFORM випадково залишилися gates, required decisions, status rules або output contracts, — це проблема. Такі речі модель може пропустити, неправильно інтерпретувати або виконати непослідовно.

---

## Просте пояснення

FREEFORM — це зона, де Ordo дозволяє людському тексту залишатися людським.

Але ця зона має бути прозорою.

Після міграції потрібно подивитися:

```text
що вдалося перетворити на structured Ordo;
що залишилось у FREEFORM;
чому воно там залишилось;
чи це безпечно;
чи потрібні tests;
чи потрібно поступово формалізувати частину цього тексту.
```

Інакше FREEFORM може стати “темною кімнатою”, де заховані критичні правила.

---

## Що нормально залишати у FREEFORM

У FREEFORM нормально залишати:

```text
- пояснення для людини;
- приклади;
- довгі доменні описи;
- історію прийняття рішення;
- edge cases, які ще не стабілізовані;
- аналітичні коментарі;
- стилістичні рекомендації;
- тимчасові примітки;
- текстові шаблони, якщо вони не є execution rules.
```

Наприклад:

```yaml
freeform:
  id: "FF_DOMAIN_CONTEXT"
  purpose: "пояснення доменного контексту"
  content: |
    У цьому типі історичних подій важливо розрізняти зміну основної компанії
    і зміну повʼязаної сутності. Аналітик має уважно перевірити джерело зміни.
```

Це нормальний FREEFORM, якщо самі правила path selection уже формалізовані окремо.

---

## Що не можна ховати у FREEFORM

У FREEFORM не можна залишати те, що має впливати на виконання як обовʼязкове правило.

Наприклад, погано:

```yaml
freeform:
  content: |
    Перед створенням архіву обовʼязково треба зробити self-check.
```

Якщо це правило обовʼязкове, воно має бути gate:

```yaml
gate:
  id: "G_PACKAGE_SELF_CHECK"
  method: mechanical
  trust_class: deterministic
  type: "blocking"
  before:
    - "handoff"
    - "archive_delivery"
```

Так само не можна ховати у FREEFORM:

```text
- blocking gates;
- required fields;
- status semantics;
- output contracts;
- path selection rules;
- approval requirements;
- negative assertions;
- regression requirements;
- library conflict rules;
- no-op conditions.
```

---

## FREEFORM після міграції playbook-а

Коли старий markdown-playbook мігрує в Ordo, частина тексту стає structured IR, а частина залишається FREEFORM.

Наприклад:

```text
Було в markdown:
"Якщо подія стосується повʼязаної сутності, потрібно уточнити relation через Центр ідентифікації."

Після міграції:
- path rule → structured;
- required question → NODE.DEF;
- state field → STATE.SCHEMA;
- пояснення про Центр ідентифікації → FREEFORM.
```

Тобто FREEFORM не означає “не важливо”. Він означає:

```text
це знання потрібне, але воно не є самостійною execution instruction.
```

---

## FREEFORM Ledger

Для великої Ordo-програми потрібен FREEFORM ledger.

```yaml
freeform_ledger:
  - id: "FF_HISTORY_EVENT_CONTEXT"
    source_section: "old_playbook/domain_notes"
    reason: "domain explanation, not executable rule"
    bound_to:
      - "DOMAIN_PACK.history_event"
      - "PATH.A2"
    risk: "low"
    tests_required: false

  - id: "FF_EDGE_CASES_EXTERNAL_EVENTS"
    source_section: "old_playbook/external_history_event_notes"
    reason: "edge cases not fully formalized yet"
    bound_to:
      - "PATH.A4"
    risk: "medium"
    tests_required: true
```

Ledger потрібен для того, щоб не втратити контроль над залишковим людським текстом.

---

## FREEFORM Coverage

Для FREEFORM теж потрібне покриття.

Coverage має відповідати на питання:

```text
- скільки FREEFORM-блоків є в програмі;
- які з них привʼязані до paths/nodes/gates;
- які мають tests;
- які мають known risks;
- які треба формалізувати пізніше;
- які вже породжували user feedback або problems.
```

Приклад:

```yaml
freeform_coverage:
  total_blocks: 5
  bound_blocks: 5
  tested_blocks: 3
  untested_blocks:
    - "FF_EDGE_CASES_EXTERNAL_EVENTS"
    - "FF_LEGACY_STATUS_NOTES"

  high_risk_blocks:
    - "FF_LEGACY_STATUS_NOTES"

  recommended_actions:
    - "formalize status notes into STATUS.SEMANTICS"
    - "add regression tests for external event edge cases"
```

---

## FREEFORM і Debug Layer

У debug mode Ordo має показувати, коли рішення спиралося на FREEFORM.

Наприклад:

```yaml
trace_source: "model_self_report"
knowledge_trace:
  - source_type: "freeform"
    id: "FF_EDGE_CASES_EXTERNAL_EVENTS"
    used_for: "path disambiguation"
    risk: "medium"
```

Це важливо, бо якщо неправильне рішення було прийняте на основі FREEFORM, ми бачимо, який саме блок треба покращувати.

Без цього модель може сказати:

```text
я так зрозуміла інструкцію
```

А Ordo має сказати точніше:

```text
рішення було прийнято з використанням FREEFORM-блоку FF_EDGE_CASES_EXTERNAL_EVENTS, який має medium risk і не має regression test.
```

---

## FREEFORM і Improvement Loop

Якщо користувач вказує на проблему, повʼязану з FREEFORM, Ordo має створити improvement record.

```yaml
improvement_record:
  type: "freeform_caused_ambiguity"
  affected_unit:
    kind: "freeform"
    id: "FF_LEGACY_STATUS_NOTES"
  problem:
    description: "status rule was interpreted inconsistently"
  proposed_patch:
    - "extract status meanings into STATUS.SEMANTICS"
    - "leave only explanation in FREEFORM"
  suggested_tests:
    - "TC_STATUS_READY_FOR_FIRST_RUN"
```

Це робить FREEFORM не просто “залишковим текстом”, а керованою частиною мови.

---

## Як вирішити, що формалізувати далі

Після міграції не потрібно одразу формалізувати все. Але потрібно мати критерії.

Формалізувати далі варто, якщо FREEFORM-блок:

```text
- часто використовується для прийняття рішень;
- впливає на gates;
- впливає на status;
- часто викликає помилки;
- має різні трактування;
- потрібен для regression scenarios;
- повторюється в багатьох domain packs;
- може стати reusable library.
```

Залишити у FREEFORM можна, якщо блок:

```text
- лише пояснює контекст;
- не змінює path;
- не блокує output;
- не визначає required fields;
- не має конфлікту з structured rules;
- легко перевіряється людиною.
```

---

## Типові помилки

### Помилка 1. Вважати FREEFORM смітником

FREEFORM — це не місце для всього, що лінь формалізувати.

### Помилка 2. Ховати gates у тексті

Якщо правило блокує дію, воно має бути gate.

### Помилка 3. Не вести FREEFORM ledger

Без ledger неможливо зрозуміти, що залишилось неформалізованим.

### Помилка 4. Не тестувати risky FREEFORM

Якщо FREEFORM впливає на рішення, потрібні tests.

### Помилка 5. Не повертатися до FREEFORM після feedback

Якщо користувач кілька разів вказує на проблему, FREEFORM треба покращувати або формалізувати.

---

## Міні-вправа

Візьміть будь-який довгий документ з інструкціями.

Випишіть пʼять фрагментів, які складно формалізувати.

Для кожного визначте:

```text
1. Це пояснення чи правило?
2. Воно впливає на path?
3. Воно блокує output?
4. Воно має бути gate?
5. Воно потребує test?
6. Його можна залишити у FREEFORM?
```

---

## Короткий підсумок

Після міграції playbook-а в Ordo важливо не тільки показати, що було формалізовано. Не менш важливо показати, що залишилось у FREEFORM.

FREEFORM має бути контрольованим, привʼязаним до конкретних частин програми, покритим tests там, де це потрібно, і видимим для debug та improvement loop.

Добрий FREEFORM — це не хаос. Це чесно позначена зона людського знання, яка ще не стала повністю формальною, але вже керується правилами Ordo.
