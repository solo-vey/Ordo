# Розділ 22. Ordo Core

## Навіщо потрібен Ordo Core

До цього моменту ми вже розібрали багато окремих частин Ordo: intent, contract, state, nodes, gates, output, status semantics, debug, tests, feedback loop і FREEFORM. Але якщо залишити ці поняття просто набором ідей, кожен автор Ordo-програми почне збирати їх по-своєму.

Один автор назве стартовий вузол `start`.
Другий — `entry`.
Третій — `initial_question`.
Четвертий взагалі сховає початок процесу в довгому тексті.

Так само може статися з gates, статусами, output, state, перевірками, trace і FREEFORM. Формально всі будуть “писати Ordo”, але фактично кожна програма буде жити за власними правилами.

Саме тому потрібен `Ordo Core`.

`Ordo Core` — це мінімальний обовʼязковий набір понять, правил і конструкцій, без яких Ordo-програма не вважається повноцінною Ordo-програмою.

Core не описує всю предметну область. Він не знає, що таке історична подія, моніторингова подія, юридичний висновок, перевірка компанії чи QA-пакет. Core відповідає за інше: за базову форму керованого виконання.

Простіше кажучи:

```text
Ordo Core — це скелет мови.
```

![Nebu — ідея: Core як скелет мови](../assets/mascots/64x64/Nebu_idea_64x64.png)

На цей скелет потім накладаються profiles, domain packs, libraries і конкретні playbook-и.

## Що входить в Ordo Core

Ordo Core має відповідати на кілька базових питань:

```text
З чого починається виконання?
Який контракт потрібно підтвердити?
Який state ведеться під час процесу?
Які вузли процесу існують?
Які відповіді можуть бути прийняті?
Які gates блокують або дозволяють перехід?
Який output має бути створений?
Які negative assertions забороняють неправильні дії?
Як фіксується trace виконання?
Як позначається FREEFORM і його покриття?
```

Тобто Core — це не бібліотека готових рішень і не domain pack. Це базова граматика виконання.

У першій версії Ordo Core можна мислити через такі ключові блоки:

```text
ENTRY.DEF
NODE.DEF
STATE.SCHEMA
ANSWER.REGISTRY
OUTPUT.DEF
ASSERT.NOT
STATUS.SEMANTICS
ASSUMPTION.LEDGER
FREEFORM.COVERAGE
TRACE.REQUIRE
GATE.REQUIRE
```

Далі розберемо їх простими словами.

## ENTRY.DEF

`ENTRY.DEF` описує, як Ordo-програма починається.

У звичайному prompt-і початок часто неформальний. Користувач пише щось, модель якось інтерпретує це і починає відповідати.

В Ordo старт має бути визначеним.

Наприклад:

```yaml
entry:
  id: "ENTRY_MAIN"
  accepts:
    - "new_user_request"
    - "uploaded_playbook"
    - "existing_state"
  first_node: "NODE_CLASSIFY_REQUEST"
```

Це означає: коли приходить новий запит, програма не повинна одразу створювати фінальний результат. Вона має перейти в перший визначений вузол і класифікувати запит.

ENTRY потрібен для того, щоб модель не вигадувала, “з чого почати”.

## NODE.DEF

`NODE.DEF` описує один крок або вузол процесу.

Node — це не просто абзац інструкції. Це місце, де модель має виконати певну дію: поставити питання, прийняти відповідь, оновити state, вибрати path, перевірити gate або перейти далі.

Приклад:

```yaml
node:
  id: "NODE_COLLECT_ALIAS"
  purpose: "collect event alias"
  asks:
    question: "Який alias події?"
  writes_to_state:
    - "event.alias"
  next:
    when_answered: "NODE_COLLECT_SOURCE_FIELD"
```

Це вже не просто порада “запитай alias”. Це формальна частина execution flow.

Core не визначає, які саме nodes потрібні в кожній предметній області. Але Core визначає, що node має мати id, purpose, очікувану дію, вплив на state і правило переходу.

## STATE.SCHEMA

`STATE.SCHEMA` описує, які дані процес памʼятає під час виконання.

Без state модель легко втрачає контекст. Вона може двічі питати одне й те саме, забути підтвердження, переплутати чернетку з фінальним результатом або прийняти припущення за факт.

Приклад:

```yaml
state_schema:
  event:
    alias:
      type: "string"
      required: true
      status: "unconfirmed"
    source_field:
      type: "string"
      required: true
      status: "unconfirmed"
  approvals:
    pre_archive:
      type: "boolean"
      default: false
```

State schema не гарантує, що модель ніколи не помилиться. Але вона дає чітку карту того, що потрібно памʼятати і в якому статусі це перебуває.

## ANSWER.REGISTRY

`ANSWER.REGISTRY` описує, які типи відповідей користувача Ordo-програма може приймати.

Це важливо для guided intake. Користувач не завжди відповідає ідеально структуровано. Він може написати:

```text
так
підтверджую
ні
змінив рішення
повернись назад
давай далі
це не те
```

Без registry модель кожного разу сама вирішує, що означає відповідь. Це небезпечно.

Приклад:

```yaml
answer_registry:
  confirm:
    examples:
      - "так"
      - "підтверджую"
      - "ок"
    effect: "mark_current_contract_part_confirmed"

  reject:
    examples:
      - "ні"
      - "не підходить"
      - "це не те"
    effect: "keep_state_unconfirmed"

  go_next:
    examples:
      - "далі"
      - "йдемо далі"
    effect: "advance_if_current_gate_passed"
```

Core не повинен знати всі фрази кожної мови. Але Core має вимагати, щоб важливі відповіді були класифіковані і мали визначений effect.

## OUTPUT.DEF

`OUTPUT.DEF` описує, що саме Ordo-програма має створити.

Output — це не просто “дай відповідь”. Це визначена структура результату.

Наприклад:

```yaml
output:
  id: "FINAL_PACKAGE"
  type: "archive"
  required_files:
    - "README.md"
    - "SUMMARY.json"
    - "VALIDATION_REPORT.json"
    - "CONSISTENCY_CHECK_REPORT.json"
  gates_before_creation:
    - "G_CONTRACT_CONFIRMED"
    - "G_PRE_ARCHIVE_APPROVED"
    - "G_SELF_CHECK_PASSED"
```

Output definition потрібен, щоб модель не змішувала чернетку, пояснення, фінальний документ і handoff в один хаотичний текст.

## ASSERT.NOT

`ASSERT.NOT` — це негативні перевірки. Вони описують, чого Ordo-програма не має права робити.

Наприклад:

```yaml
assert_not:
  - id: "NO_FINAL_ARCHIVE_BEFORE_APPROVAL"
    condition: "pre_archive_approval != true"
    forbidden_action: "create_final_archive"
```

У Core це особливо важливо. Бо позитивні правила кажуть, що треба зробити. Але для AI-моделі часто ще важливіше явно сказати, чого робити не можна.

Особливо це стосується:

```text
- не створювати фінальний output до approval;
- не вигадувати відсутні дані;
- не позначати unconfirmed як confirmed;
- не ховати gate у FREEFORM;
- не трактувати приклад як правило;
- не змінювати domain logic без explicit instruction.
```

## STATUS.SEMANTICS

`STATUS.SEMANTICS` описує значення статусів.

У складних процесах слова “готово”, “підтверджено”, “чернетка”, “blocked”, “passed” можуть легко змішуватися.

Core має вимагати, щоб статуси мали чітку семантику.

Наприклад:

```yaml
status_semantics:
  draft:
    meaning: "created but not approved"
    allows_final_handoff: false

  confirmed:
    meaning: "explicitly approved by user"
    allows_gate_pass: true

  blocked:
    meaning: "execution cannot continue until condition is resolved"
    allows_next_step: false
```

Це особливо важливо в Ordo, бо мова працює не тільки з текстом, а з процесом.

## ASSUMPTION.LEDGER

`ASSUMPTION.LEDGER` — це журнал припущень.

Модель часто змушена робити припущення. Проблема не в самих припущеннях, а в тому, що вони стають невидимими.

Core має вимагати, щоб важливі припущення були зафіксовані.

Наприклад:

```yaml
assumption_ledger:
  - id: "A-001"
    assumption: "source field belongs to EDR factual data"
    reason: "user provided EDR-like payload"
    status: "needs_confirmation"
    used_for:
      - "path_selection"
```

Якщо припущення впливає на path, gate або output, воно не може бути прихованим.

## FREEFORM.COVERAGE

Core не забороняє FREEFORM. Навпаки, він визнає, що частина інструкцій може залишатися вільною мовою.

Але Core має вимагати, щоб FREEFORM був контрольованим.

Для цього потрібен `FREEFORM.COVERAGE`:

```yaml
freeform_coverage:
  entries_total: 5
  structured_bindings: 4
  unbound_entries:
    - "FF_DOMAIN_EXAMPLES"
  risk: "medium"
```

Це дозволяє бачити, які частини playbook-а ще не формалізовані і де можуть виникати помилки.

## TRACE.REQUIRE

Після появи Debug, Test & Improvement Layer Core має включати мінімальну вимогу до trace.

Навіть якщо run не запущений у повному debug mode, складна Ordo-програма має залишати базові сліди виконання:

```text
- який entry використано;
- який path обрано;
- які gates пройдено;
- які gates заблоковано;
- які state fields змінено;
- який output створено;
- які warnings були зафіксовані.
```

Це не завжди має бути великий детальний лог. Але виконання не повинно бути повністю непрозорим.

## GATE.REQUIRE

Core також має вимагати, щоб важливі переходи були захищені gates.

Наприклад, фінальний output не повинен створюватися просто тому, що користувач написав “давай”. Має бути перевірено, чи виконані умови.

```yaml
gate_require:
  before:
    - action: "create_final_output"
      required_gates:
        - "G_CONTRACT_CONFIRMED"
        - "G_VALIDATION_PASSED"
```

Це один із головних принципів Ordo: gate — це не рекомендація, а контрольна точка.

## Чим Core відрізняється від Profile

Core відповідає за базову мову.

Profile відповідає за тип процесу.

Наприклад:

```text
Core каже: output має бути визначений.
Profile каже: для документації output має мати шаблон, rendered validation і catalog.

Core каже: gates мають бути явними.
Profile каже: для QA-пакета потрібні gates manual QA readiness і automation readiness.

Core каже: state має бути описаний.
Profile каже: для guided intake state має містити current node, confirmed answers і pending questions.
```

Тобто profile розширює Core, але не замінює його.

## Чим Core відрізняється від Domain Pack

Domain Pack знає предметну область.

Core не знає, що таке `HistoryEvent`, `ChangeRecord`, `ExternalHistoryEvent`, `Monitoring Center`, `EDR`, `source row` або `QA package`.

Domain Pack описує такі речі:

```text
- domain vocabulary;
- domain-specific paths;
- domain gates;
- domain statuses;
- domain outputs;
- domain examples;
- domain no-op rules.
```

А Core забезпечує, щоб усе це було виконуваним, контрольованим і перевірюваним.

## Чим Core відрізняється від Library

Library — це reusable готове рішення.

Наприклад, бібліотека може містити готовий набір contract-first gates або rendered artifact validation.

Core же визначає, як такі речі взагалі підключаються, перевіряються і не конфліктують із програмою.

Коротко:

```text
Core — базова мова.
Profile — стиль/тип процесу.
Domain Pack — предметна область.
Library — готовий reusable фрагмент.
```

![Nebu — подумати: не змішувати Core, Profile, Domain Pack і Library](../assets/mascots/64x64/Nebu_thinking_64x64.png)

## Типові помилки

### Помилка 1. Робити Core занадто великим

Core не має містити все. Якщо покласти в Core історичні події, QA-пакети, юридичні висновки, API-конфігурації і шаблони документів, Core стане неповоротким.

Core має бути мінімальним.

![Nebu — увага: Core не має ставати занадто великим](../assets/mascots/64x64/Nebu_attention_64x64.png)

### Помилка 2. Ховати правила Core у FREEFORM

Якщо правило блокує виконання, воно не має жити тільки в пояснювальному тексті.

Погано:

```text
Перед архівом бажано зробити self-check.
```

Добре:

```yaml
gate:
  id: "G_SELF_CHECK_PASSED"
  method: mechanical
  trust_class: deterministic
  blocking: true
```

### Помилка 3. Вважати Core документацією

Core — це не опис для читання. Це частина виконуваної моделі процесу.

### Помилка 4. Дозволяти domain pack-у ламати Core

Domain Pack може розширювати Core, але не повинен скасовувати базові правила без explicit override і trace.

## Міні-вправа

Візьміть будь-який складний prompt, який ви використовували раніше, і спробуйте виділити в ньому Core-частину:

```text
1. Де починається процес?
2. Які вузли або кроки там є?
3. Який state потрібно вести?
4. Які gates мають бути blocking?
5. Який output очікується?
6. Які дії потрібно явно заборонити?
7. Які припущення можуть виникнути?
8. Що треба логувати для debug?
```

Якщо на ці питання немає відповіді, перед вами ще не Ordo-програма, а тільки неформальна інструкція.

## Короткий підсумок

`Ordo Core` — це мінімальний обовʼязковий набір конструкцій, який робить Ordo-програму керованою.

Core не описує предметну область і не замінює domain pack. Він задає базову форму execution:

```text
entry → node → state → gate → output → trace
```

Без Core Ordo перетвориться на набір красивих prompt-шаблонів.

З Core вона стає мовою керування поведінкою AI-моделі.

---

<!-- REVIEWED: chapter 22; Nebu markers checked -->
