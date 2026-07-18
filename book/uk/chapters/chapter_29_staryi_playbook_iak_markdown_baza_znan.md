# Розділ 29. Старий playbook як markdown-база знань

## Навіщо це потрібно

Багато складних інструкцій народжуються не як мова, не як програма і не як формальний workflow. Вони народжуються як великий markdown-документ: правила, приклади, винятки, таблиці, нагадування, чеклисти, історичні пояснення, рішення, які колись були прийняті в чаті або в задачах.

Такий документ може бути дуже корисним. Він зберігає знання команди. Він пояснює контекст. Він показує, як аналітик думає про процес. Але проблема в тому, що великий markdown-playbook не є виконуваною інструкцією.

![Nebu — ідея: markdown-playbook є базою знань, а не runtime](../assets/mascots/64x64/Nebu_idea_64x64.png)

Модель може прочитати його, але це не означає, що вона виконає його однаково кожного разу.

Вона може:

```text
- пропустити важливий gate;
- переплутати приклад і правило;
- взяти застарілий фрагмент як актуальний;
- використати інструкцію не для того path;
- забути, що певне рішення потребує підтвердження людини;
- прочитати all-in-one документ як звичайний текст, а не як процес.
```

Саме тому старий markdown-playbook потрібно розглядати не як кінцевий формат, а як базу знань, з якої поступово виділяється Ordo-програма.

---

## Просте пояснення

Старий playbook — це як велика папка з інструкціями на столі.

У ній може бути все:

```text
- опис процесу;
- бізнесові правила;
- технічні правила;
- приклади;
- винятки;
- шаблони;
- чеклисти;
- історія рішень;
- примітки для майбутнього;
- попередження про помилки.
```

Але якщо попросити людину або модель “просто виконай усе з цієї папки”, виникне проблема: незрозуміло, що є обовʼязковим, що є довідковим, що є прикладом, що є старою приміткою, а що є активним правилом.

Ordo пропонує інший підхід:

```text
markdown-playbook → knowledge source → structured extraction → Ordo Source → compiled IR → execution
```

Тобто старий playbook не викидається. Він стає джерелом знань. Але виконання має відбуватися не напряму з хаотичного тексту, а через структурований Ordo-шар.

---

## Що в старому playbook-у є корисним

У старому markdown-playbook-у важливо не тільки знайти готові правила. Важливо правильно класифікувати різні типи інформації.

Наприклад:

```text
1. Обовʼязкові правила
2. Decision tree
3. Questions / intake flow
4. Gates
5. Output templates
6. QA rules
7. Validation rules
8. Examples
9. Anti-patterns
10. Domain notes
11. Historical decisions
12. Process improvement feedback
```

Усе це не має однакового статусу.

Обовʼязкове правило має стати gate або assertion.

Decision tree має стати набором `NODE.DEF` і path rules.

Шаблон має стати `OUTPUT.DEF` або `TEMPLATE.BIND`.

Приклад може залишитися у FREEFORM, але з binding до конкретного rule або node.

Попередження про типову помилку може стати `ASSERT.NOT`.

Зауваження користувача може стати `IMPROVEMENT.RECORD` або regression test.

---

## Чому all-in-one markdown небезпечний

All-in-one документ здається зручним, бо все лежить в одному місці. Але для виконання це небезпечно.

![Nebu — увага: all-in-one небезпечний як runtime source](../assets/mascots/64x64/Nebu_attention_64x64.png)

Причини:

```text
- модель може загубитися в довгому контексті;
- різні частини документа можуть суперечити одна одній;
- old note може виглядати як active rule;
- приклад може бути помилково виконаний як універсальний шаблон;
- важко зрозуміти, які правила покривають який path;
- важко дебажити, який саме фрагмент вплинув на рішення;
- важко тестувати, що зміна не зламала старий сценарій.
```

У Ordo all-in-one може бути корисним як rendered artifact або архівна форма, але не як головний runtime source.

Головний runtime source має бути структурований.

---

## Як Ordo дивиться на markdown-playbook

Ordo не каже:

```text
Markdown поганий.
```

Ordo каже:

```text
Markdown добрий для пояснення, але недостатній для керованого виконання.
```

Тому старий playbook потрібно розділити на шари:

```text
1. Human explanation layer
   Текст для людей.

2. Ordo Source layer
   Людинозрозуміла структурована програма.

3. Semantic JSON IR layer
   Машинно-орієнтована execution map.

4. Debug/Test layer
   Траси, тести, coverage, improvement records.
```

Markdown може залишатися у першому шарі. Але все, що впливає на виконання, має бути або формалізоване, або явно привʼязане як controlled FREEFORM.

---

## Приклад класифікації фрагмента

Уявімо, що в старому playbook-у є фраза:

```text
Перед створенням фінального архіву потрібно виконати self-check і перевірити, що пакет не містить зайвих файлів.
```

У markdown це просто речення.

В Ordo це має стати:

```yaml
- op: "GATE.DEF"
  id: "G_PACKAGE_SELF_CHECK"
  type: "blocking"
  before: "HANDOFF.FINAL_PACKAGE"
  requires:
    - "validation_report.status == passed"
    - "unexpected_files == []"
```

А також negative assertion:

```yaml
- op: "ASSERT.NOT"
  id: "A_NO_HANDOFF_WITHOUT_SELF_CHECK"
  condition: "final_package_created == true and self_check_passed != true"
  severity: "blocking"
```

І test case:

```yaml
test:
  id: "TC_NO_PACKAGE_WITHOUT_SELF_CHECK"
  method: mechanical
  trust_class: deterministic
  expected:
    gate: "G_PACKAGE_SELF_CHECK"
    final_package_created: false
```

Так одна фраза з markdown стає виконуваною частиною Ordo-програми.

---

## Що не треба формалізувати одразу

Не весь старий playbook потрібно одразу перетворювати на строгі op-коди.

Деякі частини можуть тимчасово залишатися у controlled FREEFORM:

```text
- довгі бізнесові пояснення;
- приклади для аналітика;
- історичні причини появи правила;
- edge cases, які ще не стабілізовані;
- пояснення термінів;
- domain commentary.
```

Але кожен FREEFORM-блок має мати binding:

```yaml
freeform:
  id: "FF_HISTORY_EVENT_EDGE_CASES"
  bound_to:
    - "NODE.SELECT_PATH"
    - "G_SOURCE_FIELD_CONFIRMED"
  reason: "domain examples are not yet fully formalized"
```

Без binding FREEFORM знову перетворюється на хаотичний markdown.

---

## Роль traceability

Під час міграції старого playbook-а важливо не втратити звʼязок між старим текстом і новими Ordo-конструкціями.

Тому потрібна traceability matrix:

![Nebu — подумати: потрібно зберегти звʼязок між старим текстом і Ordo-обʼєктами](../assets/mascots/64x64/Nebu_thinking_64x64.png)

```text
старий фрагмент → Ordo Source object → IR op → test coverage → rendered artifact
```

Наприклад:

```yaml
traceability:
  source_fragment: "section_12.self_check_before_archive"
  mapped_to:
    - "G_PACKAGE_SELF_CHECK"
    - "ASSERT.NOT.A_NO_HANDOFF_WITHOUT_SELF_CHECK"
    - "TC_NO_PACKAGE_WITHOUT_SELF_CHECK"
```

Це дозволяє відповісти на питання:

```text
- де в Ordo тепер живе це правило?
- чи покрите воно тестом?
- чи воно blocking?
- чи воно потрапляє в compiled IR?
- чи воно використовується під час виконання?
```

---

## Типові помилки

### Помилка 1. Просто перейменувати markdown у Ordo

Якщо взяти старий markdown і назвати його Ordo Source, нічого не зміниться.

Ordo вимагає структури: nodes, gates, state, outputs, tests, traceability.

---

### Помилка 2. Перенести все в FREEFORM

FREEFORM — це контрольована лазейка, а не смітник для невідформатованих правил.

Якщо все лишити у FREEFORM, Ordo не отримає керованості.

---

### Помилка 3. Втратити історію рішень

Під час формалізації легко викинути пояснення, чому правило зʼявилось.

Але історія важлива для майбутнього покращення. Її можна зберегти як note, evidence або improvement history.

---

### Помилка 4. Не додати тести

Міграція без тестів — це косметична зміна.

Ordo-міграція має завершуватися test layer і coverage report.

---

### Помилка 5. Не перевірити rendered artifacts

Якщо playbook генерує документи або пакети, потрібно перевіряти не тільки rules, а й готовий результат.

---

## Міні-вправа

Візьміть будь-який великий документ з інструкціями.

Позначте в ньому фрагменти пʼятьма кольорами або категоріями:

```text
1. rule
2. gate
3. example
4. explanation
5. warning / anti-pattern
```

Потім спробуйте для кожного rule відповісти:

```text
- це має бути NODE, GATE, ASSERT.NOT, OUTPUT чи FREEFORM?
- чи треба для цього тест?
- чи це правило має бути blocking?
- чи воно застосовується завжди, чи тільки для одного path?
```

Це перший крок до міграції старого playbook-а в Ordo.

---

## Короткий підсумок

Старий markdown-playbook — це цінна база знань, але не надійний формат виконання.

Ordo не знищує markdown. Вона витягує з нього виконувану структуру:

```text
rules → gates
questions → nodes
templates → outputs
warnings → ASSERT.NOT
examples → controlled FREEFORM
decisions → state/status semantics
feedback → improvement records
```

Головна думка розділу:

```text
старий playbook — це джерело знань, а не runtime execution layer
```

---
