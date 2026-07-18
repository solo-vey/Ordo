# Розділ 35. Як не зламати playbook

## Навіщо це потрібно

Великий playbook — це не просто довга інструкція. Це система правил, рішень, зупинок, перевірок, прикладів, винятків і очікуваних результатів. Коли така система росте, її легко зламати навіть доброю зміною.

Найчастіше playbook ламається не тому, що хтось зробив очевидну помилку. Частіше все виглядає невинно:

```text
- додали нове уточнення;
- переставили блок вище;
- прибрали повторення;
- обʼєднали два правила;
- перенесли частину тексту у FREEFORM;
- змінили формулювання gate;
- додали новий path;
- виправили один сценарій, але не перевірили інші.
```

Після цього модель раптом починає ставити питання не в тому порядку, пропускати approval, генерувати фінальний artifact занадто рано або плутати приклад із правилом.

Ordo потрібна саме для того, щоб такі зміни не були сліпими.

## Просте пояснення

Зламати playbook — це означає порушити очікувану поведінку процесу.

Не обовʼязково зламати весь документ. Достатньо зламати одну важливу властивість:

```text
- модель пішла не тим path;
- gate перестав бути blocking;
- node почав питати зайві речі;
- state став оновлюватися раніше, ніж потрібно;
- output створюється без підтвердження;
- FREEFORM почав поводитися як приховане правило;
- бібліотека перезаписала локальне правило;
- тест проходить формально, але реальний artifact неправильний.
```

У звичайних інструкціях такі проблеми важко побачити. У Ordo кожна важлива частина playbook-а має бути повʼязана з path, node, gate, state, output, trace або test.

Тому головне правило просте:

```text
Не змінюй playbook як текст. Змінюй його як систему виконання.
```

## Що вважається небезпечною зміною

Не всі зміни однаково ризиковані.

Низький ризик:

```text
- виправлення помилки в тексті;
- уточнення пояснення без зміни правил;
- додавання прикладу, який явно позначений як приклад;
- покращення назви розділу без зміни execution flow.
```

Середній ризик:

```text
- додавання нового питання;
- зміна порядку node;
- уточнення condition;
- зміна output template;
- винесення частини логіки в library;
- зміна FREEFORM block.
```

Високий ризик:

```text
- зміна path selection;
- зміна gate semantics;
- зміна status semantics;
- зміна blocking rule;
- зміна approval flow;
- зміна ASSERT.NOT;
- зміна compiler mapping;
- зміна domain pack rule;
- зміна reusable library, яку використовують кілька playbook-ів.
```

Для Ordo це означає: чим ближче зміна до execution behavior, тим сильніша потрібна перевірка.

## Ordo-конструкція

Для безпечної зміни playbook-а в Ordo потрібен окремий change flow.

Мінімальна схема:

```text
CHANGE.PROPOSE
→ IMPACT.ANALYZE
→ AFFECTED.UNIT
→ TEST.SELECT
→ REGRESSION.RUN
→ TRACE.COMPARE
→ HUMAN.APPROVE
→ VERSION.NOTE
```

Це означає, що зміна не має просто “вноситися в текст”. Вона має пройти через опис впливу.

Приклад:

```yaml
change:
  id: "CH-001"
  type: "gate_semantics_update"
  summary: "Make package self-check gate blocking"

affected_units:
  - kind: "gate"
    id: "G_PACKAGE_SELF_CHECK"
  - kind: "assertion"
    id: "ASSERT_NO_ARCHIVE_BEFORE_SELF_CHECK"
  - kind: "test"
    id: "TC_NO_ARCHIVE_WITHOUT_SELF_CHECK"

risk:
  level: "high"
  reason: "Changes final package generation behavior"

required_checks:
  - "run_regression_suite"
  - "compare_debug_trace"
  - "validate_rendered_artifacts"
  - "human_approval"
```

## Принцип 1. Не змінювати rule без test

Кожна зміна правила має або використовувати наявний тест, або створювати новий.

Погано:

```text
Додали правило: перед архівом обовʼязково робити self-check.
```

Краще:

```text
Додали правило + додали test:
TC_NO_ARCHIVE_WITHOUT_SELF_CHECK
```

У Ordo це має бути майже автоматичною вимогою:

```text
RULE.CHANGE requires TEST.DEF or TEST.UPDATE
```

Інакше зміна може виглядати правильно, але не буде захищена від регресії.

## Принцип 2. Не змінювати gate без status semantics

Gate — це контрольна точка. Але gate має сенс тільки тоді, коли зрозуміло, що означають його статуси.

Наприклад:

```text
passed
failed
blocked
pending
not_applicable
```

Якщо змінити gate, але не перевірити status semantics, може виникнути небезпечна ситуація: модель бачить gate, але не розуміє, чи треба зупинитися.

Тому правило:

```text
GATE.CHANGE requires STATUS.SEMANTICS.CHECK
```

Особливо це важливо для blocking gates.

## Принцип 3. Не ховати поведінку у FREEFORM

FREEFORM корисний, коли частину інструкції ще рано формалізувати. Але FREEFORM не має ставати місцем для прихованих gates, path selection або approval rules.

Погано:

```text
У FREEFORM написано: “зазвичай перед архівом треба перевірити пакет”.
```

Краще:

```text
Gate:
  id: G_PACKAGE_SELF_CHECK
  blocking: true

FREEFORM:
  пояснює, як саме аналітик зазвичай перевіряє пакет.
```

Тобто FREEFORM може пояснювати правило, але не має замінювати саме правило.

## Принцип 4. Не робити implicit override

Коли playbook використовує libraries, profiles або domain packs, легко випадково перезаписати поведінку.

Наприклад, бібліотека має gate:

```text
G_CONTRACT_CONFIRMED
```

А локальний playbook додає gate з такою самою назвою, але з іншою логікою.

Ordo не має мовчки приймати це.

Правильно:

```yaml
override:
  target: "contract_first.G_CONTRACT_CONFIRMED"
  allow: true
  reason: "Domain pack requires additional source row confirmation"
  approved_by: "human"
```

Без явного override зміна має бути заблокована або позначена як conflict.

## Принцип 5. Перевіряти не тільки template, а rendered artifact

Одна з типових помилок — перевірити шаблон, але не перевірити готовий документ.

Наприклад, template може містити правильний блок, але у фінальному artifact цей блок не зʼявився через помилку render step.

Тому в Ordo має бути правило:

```text
Artifact is valid only after rendered artifact validation.
```

Не достатньо сказати:

```text
шаблон має секцію self-check
```

Потрібно перевірити:

```text
готовий файл має секцію self-check у правильному місці і з правильним змістом
```

## Принцип 6. Порівнювати trace до і після зміни

Для складних playbook-ів недостатньо знати, що тести пройшли. Потрібно ще бачити, чи змінився шлях виконання.

До зміни:

```text
input → path A1 → node collect_alias → gate contract_confirmed → output draft
```

Після зміни:

```text
input → path A1 → node collect_source_field → node collect_alias → gate contract_confirmed → output draft
```

Це може бути правильна зміна. Але вона має бути видимою.

Тому Ordo має підтримувати:

```text
TRACE.COMPARE
```

Trace compare показує:

```text
- які path змінилися;
- які nodes додані або прибрані;
- які gates змінили статус;
- які state fields змінилися;
- які outputs змінили структуру;
- які warnings зʼявилися або зникли.
```

## Малий приклад

Уявімо, що playbook для історичних подій іноді створює фінальний архів без self-validation.

Погане виправлення:

```text
Додати в текст: “Не забувай зробити перевірку перед архівом”.
```

Таке формулювання може знову загубитися.

Краще Ordo-виправлення:

```yaml
assert_not:
  id: "ASSERT_NO_ARCHIVE_BEFORE_VALIDATION"
  method: mechanical
  trust_class: deterministic
  condition: "final_archive_created == true and validation_passed != true"
  severity: "blocking"

expected_behavior:
  if_assertion_triggered:
    action: "stop"
    message: "Cannot create final archive before validation is passed."

test:
  id: "TC_NO_ARCHIVE_BEFORE_VALIDATION"
  fixture:
    user_message: "створи архів одразу"
  expected:
    output:
      final_archive_created: false
    gate:
      id: "G_VALIDATION_BEFORE_ARCHIVE"
      status: "blocked"
```

Тепер це не просто порада. Це частина execution contract.

## Типові помилки

Перша помилка — редагувати playbook як статтю.

Якщо playbook сприймати як текст, автор буде думати про красу формулювань. Якщо сприймати його як Ordo-програму, автор буде думати про поведінку моделі.

Друга помилка — додавати правила без tests.

Правило без тесту легко зламати через два дні, навіть якщо сьогодні воно виглядає очевидним.

Третя помилка — не відрізняти приклад від правила.

Приклади допомагають моделі, але якщо вони не позначені явно, модель може почати виконувати приклад як обовʼязковий сценарій.

Четверта помилка — вважати, що якщо документ став коротшим, то він став кращим.

Стиснення може знищити важливі gates, warnings або domain-specific винятки.

Пʼята помилка — не перевіряти старі сценарії після нового покращення.

Багато змін виглядають правильними локально, але ламають сусідній path.

## Міні-вправа

Візьміть будь-який складний playbook або інструкцію і виберіть одну зміну, яку хочеться внести.

Перед зміною запишіть:

```text
1. Яку поведінку ця зміна має покращити?
2. Який path або node вона зачіпає?
3. Який gate може змінити статус?
4. Який state field може змінитися?
5. Який output може змінитися?
6. Який test потрібно додати?
7. Який regression test потрібно прогнати?
8. Чи потрібен human approval?
```

Якщо на ці питання немає відповідей, зміна ще не готова.

## Короткий підсумок

Playbook ламається тоді, коли його змінюють як текст, а не як систему виконання.

Щоб не зламати playbook, Ordo вимагає:

```text
- описувати impact зміни;
- привʼязувати зміну до affected units;
- не змінювати rule без test;
- не змінювати gate без status semantics;
- не ховати поведінку у FREEFORM;
- не робити implicit override;
- перевіряти rendered artifact;
- порівнювати trace до і після зміни;
- запускати regression suite;
- фіксувати version note.
```

Без цього будь-яке покращення може випадково стати новою помилкою.
