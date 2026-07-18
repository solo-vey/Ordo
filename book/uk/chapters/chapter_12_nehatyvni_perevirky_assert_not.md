# Розділ 12. Негативні перевірки: ASSERT.NOT → ASSERTION

## Навіщо це потрібно

У звичайних інструкціях ми часто пишемо моделі, що вона має зробити:

- створи документ;
- постав питання;
- перевір структуру;
- сформуй відповідь;
- підготуй архів;
- дай короткий підсумок.

Але в реальних процесах не менш важливо сказати, чого модель **не має права** робити.

Наприклад:

- не вигадувати відсутні дані;
- не переходити до наступного кроку без підтвердження;
- не створювати фінальний пакет до проходження перевірок;
- не вважати приклад правилом;
- не замінювати бізнесове рішення технічною здогадкою;
- не включати у пакет зайві файли;
- не ховати невизначеність у фінальному результаті.

У prompt-ах такі заборони часто губляться. Модель може прочитати їх, погодитися, але все одно виконати дію, яка формально не дозволена. Саме тому в Ordo негативні перевірки мають бути не просто текстовими застереженнями, а окремим контрольованим правилом.

![Nebu — ідея: ASSERTION як захист від заборонених дій](../assets/mascots/64x64/Nebu_idea_64x64.png)

У ранніх версіях Ordo для цього використовувалась конструкція:

```text
ASSERT.NOT
```

Починаючи з Ordo v0.12, точніше говорити так:

```text
ASSERTION — канонічний примітив.
ASSERT.NOT — скорочена форма для ASSERTION з polarity: not.
```

Це важлива зміна. `ASSERT.NOT` більше не є окремим паралельним механізмом поруч із gate і тестами. Це одна з форм єдиного правила `ASSERTION`, яке може бути розгорнуте в runtime-перевірку, test expectation і debug violation record.

## Просте пояснення

`ASSERTION` — це формальне твердження про те, що в процесі має бути істинним або не має статися.

У нього є полярність:

```text
must — потрібний стан має бути виконаний;
not  — заборонений стан не має статися.
```

Тому `ASSERT.NOT` можна мислити як assertion навпаки:

```text
Чи точно не сталося заборонене?
```

Наприклад:

```text
Gate:
усі mandatory секції присутні.

ASSERT.NOT:
у фінальному пакеті немає зайвих файлів.
```

Або:

```text
Gate:
користувач підтвердив alias.

ASSERT.NOT:
модель не вигадала alias самостійно.
```

Це дуже важлива різниця. Бо позитивна перевірка не завжди ловить порушення.

![Nebu — увага: позитивна перевірка не ловить зайве](../assets/mascots/64x64/Nebu_attention_64x64.png)

Можна мати документ, у якому всі потрібні розділи присутні, але водночас у ньому є зайві, небезпечні або суперечливі блоки. Звичайний gate може сказати “структура є”, але assertion з `polarity: not` має сказати “зайвого немає”.

## Чому Ordo v0.12 вводить ASSERTION

До v0.12 у мові легко виникали три схожі конструкції:

```text
ASSERT.NOT — заборона під час виконання;
negative gate — gate, який перевіряє відсутність проблеми;
EXPECT.NOT — очікування в тестах, що заборонений стан не зʼявиться.
```

Усі три говорять про одну і ту саму ідею: **певний стан або дія не мають статися**. Якщо тримати їх окремо, автору доводиться вручну синхронізувати правила між виконанням, тестами й debug-звітом.

Наприклад, автор може додати:

```text
ASSERT.NOT final_output_before_validation
```

але забути додати відповідний `EXPECT.NOT` у regression suite. Тоді правило є в playbook-у, але тест його не захищає.

Тому в Ordo v0.12 канонічним стає один примітив:

```text
ASSERTION
```

А `ASSERT.NOT`, `EXPECT.NOT` і negative gate стають його проєкціями.

## Ordo-конструкція

У Source-форматі assertion може виглядати так:

```yaml
assertions:
  - id: "A_NO_INVENTED_ALIAS"
    polarity: "not"
    condition: "alias_created_without_user_confirmation"
    phase: ["runtime", "test"]
    method: "self_verification"
    severity: "block"
    on_fail: "STOP"
    message: "Alias не може бути вигаданий моделлю без підтвердження користувача."
```

Це означає:

```text
Якщо alias був створений без явного підтвердження користувача,
процес потрібно зупинити, а тестовий набір має містити очікування,
що такий стан не допускається.
```

У compiled IR це може розгорнутися в кілька представлень.

Runtime-представлення:

```json
{
  "op": "ASSERT.NOT",
  "id": "domain_pack.history_event.A_NO_INVENTED_ALIAS",
  "source_assertion": "domain_pack.history_event.A_NO_INVENTED_ALIAS",
  "condition": "alias_created_without_user_confirmation",
  "method": "self_verification",
  "severity": "block",
  "on_fail": "STOP"
}
```

Test-представлення:

```json
{
  "op": "EXPECT.NOT",
  "id": "domain_pack.history_event.TE_NO_INVENTED_ALIAS",
  "source_assertion": "domain_pack.history_event.A_NO_INVENTED_ALIAS",
  "condition": "alias_created_without_user_confirmation"
}
```

Debug-представлення:

```json
{
  "op": "VIOLATION.RECORD",
  "source_assertion": "domain_pack.history_event.A_NO_INVENTED_ALIAS",
  "status": "not_triggered",
  "method": "self_verification"
}
```

Важливо: `ASSERT.NOT` не просто попереджає. Якщо `severity: block`, то це жорстка зупинка.

## Method для assertion

Ordo v0.12 додає `method` не тільки для gate, а й для assertion, якщо assertion перевіряється під час виконання.

Наприклад:

```yaml
assertions:
  - id: "A_NO_EXTRA_FILES"
    polarity: "not"
    condition: "package_contains_unapproved_files"
    phase: ["runtime", "test"]
    method: "mechanical"
    severity: "block"
```

Тут `method: mechanical`, бо runner або скрипт може детерміновано порівняти фактичний список файлів із дозволеним списком.

А ось інший приклад:

```yaml
assertions:
  - id: "A_NO_UNCONFIRMED_BUSINESS_DECISION"
    polarity: "not"
    condition: "final_output_contains_business_decision_without_user_confirmation"
    phase: ["runtime", "test"]
    method: "self_verification"
    severity: "block"
```

Це вже семантичне судження. Його може перевіряти critic-крок моделі за evidence-протоколом, але не можна робити вигляд, що така перевірка така сама надійна, як підрахунок файлів.

## Приклад без Ordo

Уявімо prompt:

```text
Підготуй аналітичний пакет. Переконайся, що всі файли є.
Не додавай зайвих файлів.
```

Модель може створити пакет, у якому є всі потрібні файли, але також додати:

```text
debug_notes.md
draft_old.md
extra_payload.json
```

Потім вона може відповісти:

```text
Пакет готовий. Усі файли присутні.
```

Формально вона перевірила позитивну частину. Але заборона була порушена.

## Приклад з Ordo v0.12

В Ordo це краще описати так:

```yaml
output:
  required_files:
    - "README.md"
    - "SUMMARY.json"
    - "VALIDATION_REPORT.json"

allowed_files:
  - "README.md"
  - "SUMMARY.json"
  - "VALIDATION_REPORT.json"

gates:
  - id: "G_REQUIRED_FILES_PRESENT"
    method: "mechanical"
    trust_class: "deterministic"
    check: "all_required_files_exist"
    on_fail: "STOP"

assertions:
  - id: "A_NO_EXTRA_FILES"
    polarity: "not"
    condition: "package_contains_files_outside_allowed_files"
    phase: ["runtime", "test"]
    method: "mechanical"
    severity: "block"
    on_fail: "STOP"
```

Тоді фінальна відповідь можлива тільки якщо:

```text
1. усі потрібні файли є;
2. немає жодного зайвого файлу;
3. обидві перевірки мають явний method;
4. test suite автоматично отримує EXPECT.NOT для забороненого стану.
```

Це набагато сильніше, ніж загальна фраза “перевір пакет”.

## Типові випадки для ASSERTION з polarity: not

Негативні assertions особливо важливі там, де модель може:

```text
- поспішити;
- здогадатися;
- “допомогти” понад інструкцію;
- непомітно змінити зміст;
- додати зайву структуру;
- перейти до наступного етапу без дозволу;
- приховати невизначеність;
- видати проміжний результат як фінальний.
```

Типові `ASSERT.NOT` для Ordo:

```text
ASSERT.NOT invented_value
ASSERT.NOT skipped_gate
ASSERT.NOT implicit_approval
ASSERT.NOT hidden_freeform_rule
ASSERT.NOT unexpected_file
ASSERT.NOT unconfirmed_contract
ASSERT.NOT unresolved_conflict
ASSERT.NOT ambiguous_status
ASSERT.NOT final_output_before_validation
ASSERT.NOT example_used_as_rule
```

У v0.12 це бажано описувати як `ASSERTION`:

```yaml
assertions:
  - id: "A_NO_FINAL_OUTPUT_BEFORE_VALIDATION"
    polarity: "not"
    condition: "final_output_created_before_validation_passed"
    phase: ["runtime", "test"]
    method: "mechanical"
    severity: "block"
```

## Негативні перевірки і статуси

`ASSERTION` тісно пов’язаний зі статусами.

Наприклад, якщо статус процесу:

```text
needs_user_decision
```

то має бути негативна assertion:

```text
ASSERT.NOT continue_without_user_decision
```

Якщо статус:

```text
blocked_by_missing_contract
```

то має бути:

```text
ASSERT.NOT generate_final_artifact
```

Інакше статус стає декоративним. Модель ніби знає, що процес заблокований, але все одно може продовжити.

В Ordo статус має впливати на дозволені дії.

## Негативні перевірки і FREEFORM

![Nebu — подумати: FREEFORM не повинен ховати контрольні правила](../assets/mascots/64x64/Nebu_thinking_64x64.png)

Одне з найнебезпечніших місць — FREEFORM.

FREEFORM потрібен, коли частину знання ще рано або неможливо повністю формалізувати. Але він не має ставати сховищем прихованих правил.

Тому для FREEFORM корисні такі assertions:

```text
ASSERT.NOT core_gate_hidden_in_freeform
ASSERT.NOT mandatory_output_hidden_in_freeform
ASSERT.NOT approval_rule_hidden_in_freeform
ASSERT.NOT business_decision_hidden_in_freeform
```

Простіше кажучи:

```text
Пояснення може бути у FREEFORM.
Але контрольна точка має бути формальною.
```

Якщо правило зупиняє процес, змінює path, визначає output або потребує підтвердження людини, воно не повинно бути лише у FREEFORM.

## Негативні перевірки в роботі з документами

Для документації assertions з `polarity: not` майже обов’язкові.

Приклади:

```text
ASSERT.NOT duplicate_section
ASSERT.NOT unresolved_placeholder
ASSERT.NOT obsolete_term
ASSERT.NOT inconsistent_alias
ASSERT.NOT missing_traceability
ASSERT.NOT markdown_link_to_internal_draft
ASSERT.NOT raw_runtime_note_in_final_document
```

Це допомагає ловити те, що звичайна позитивна перевірка часто пропускає.

Наприклад, документ може мати всі потрібні секції, але все ще містити:

```text
<TODO>
<ASK_USER_LATER>
old_alias
draft only
```

Позитивний gate “структура правильна” цього не зловить. Негативна assertion — зловить.

## Severity: коли зупиняти, а коли попереджати

Не кожна негативна перевірка однаково критична.

Тому в Ordo для `ASSERTION` потрібна severity:

```text
info
warn
block
```

Наприклад:

```yaml
assertions:
  - id: "A_NO_TODO_IN_FINAL"
    polarity: "not"
    condition: "final_artifact_contains_todo_marker"
    phase: ["runtime", "test"]
    method: "mechanical"
    severity: "block"

  - id: "A_NO_MINOR_STYLE_DRIFT"
    polarity: "not"
    condition: "document_contains_minor_style_inconsistency"
    phase: ["runtime"]
    method: "self_verification"
    severity: "warn"
```

Правило просте:

```text
Якщо порушення може зробити результат неправильним або небезпечним — block.
Якщо порушення лише погіршує якість, але не ламає результат — warn.
```

## Compiler projection

У v0.12 компілятор має вміти розгортати assertion у кілька цільових форм.

Наприклад:

```yaml
assertions:
  - id: "A_NO_SKIPPED_GATE"
    polarity: "not"
    condition: "required_gate_was_skipped"
    phase: ["runtime", "test", "debug"]
    method: "mechanical"
    severity: "block"
```

Компілятор може створити:

```text
runtime: ASSERT.NOT required_gate_was_skipped
test:    EXPECT.NOT required_gate_was_skipped
debug:   VIOLATION.RECORD if required_gate_was_skipped is true
```

Це зменшує ризик, що заборона описана в одному місці, але забута в іншому.

## Типові помилки

### Помилка 1. Формулювати заборону тільки словами

Погано:

```text
Не роби помилок.
```

Краще:

```text
ASSERT.NOT skipped_gate
ASSERT.NOT invented_required_value
ASSERT.NOT final_output_before_validation
```

Ще краще у v0.12:

```yaml
assertions:
  - id: "A_NO_FINAL_OUTPUT_BEFORE_VALIDATION"
    polarity: "not"
    condition: "final_output_before_validation"
    phase: ["runtime", "test"]
    method: "mechanical"
    severity: "block"
```

Заборона має бути перевірною.

### Помилка 2. Об’єднувати все в один великий gate

Погано:

```text
Перевір, що все добре.
```

Краще:

```text
GATE required_files_present
ASSERT.NOT unexpected_files_present
ASSERT.NOT unresolved_placeholders_present
ASSERT.NOT validation_report_missing
```

Один великий gate створює ілюзію контролю, але не дає точного trace.

### Помилка 3. Робити негативні перевірки занадто абстрактними

Погано:

```text
ASSERT.NOT bad_result
```

Краще:

```text
ASSERT.NOT result_contains_unconfirmed_business_decision
```

Модель і runtime мають розуміти, що саме перевіряється.

### Помилка 4. Не вказувати наслідок

Погано:

```yaml
assertions:
  - condition: "missing_approval"
```

Краще:

```yaml
assertions:
  - id: "A_NO_MISSING_APPROVAL"
    polarity: "not"
    condition: "missing_approval"
    phase: ["runtime"]
    method: "mechanical"
    severity: "block"
    on_fail: "STOP"
```

Без наслідку перевірка може стати просто коментарем.

### Помилка 5. Забути test projection

Погано:

```text
Правило є в runtime, але його немає в regression suite.
```

Краще:

```yaml
phase: ["runtime", "test"]
```

Тоді компілятор має створити runtime assertion і test expectation з одного джерела.

## Міні-вправа

Візьміть просту інструкцію:

```text
Підготуй фінальний документ для передачі розробнику.
```

Спробуйте виписати п’ять негативних перевірок.

Наприклад:

```text
1. Не має бути unresolved placeholders.
2. Не має бути вигаданих технічних деталей.
3. Не має бути суперечності між описом задачі і acceptance criteria.
4. Не має бути посилань на проміжні чернетки.
5. Не має бути фінального статусу без self-check.
```

Потім перепишіть їх у стилі Ordo v0.12:

```yaml
assertions:
  - id: "A_NO_UNRESOLVED_PLACEHOLDER"
    polarity: "not"
    condition: "unresolved_placeholder_present"
    phase: ["runtime", "test"]
    method: "mechanical"
    severity: "block"

  - id: "A_NO_INVENTED_TECHNICAL_DETAIL"
    polarity: "not"
    condition: "invented_technical_detail_present"
    phase: ["runtime", "test"]
    method: "self_verification"
    severity: "block"
```

## Короткий підсумок

`ASSERTION` — це канонічний спосіб описати правило, яке має бути виконане або не має бути порушене.

`ASSERT.NOT` — це скорочена форма для assertion з `polarity: not`.

Звичайний gate перевіряє, що потрібне виконано. `ASSERT.NOT` перевіряє, що заборонене не сталося.

Для Ordo це критично, бо AI-модель часто помиляється не тільки тоді, коли щось не зробила, а й тоді, коли зробила зайве: вигадала, перескочила, додала, приховала, змішала або передчасно завершила.

Добра Ordo-програма має не лише список того, що треба зробити, а й список того, чого робити не можна. У v0.12 це краще описувати один раз як `ASSERTION`, а компілятор має розгорнути це правило у runtime, test і debug-представлення.
