# Розділ 16. Тести, fixtures і expected behavior

## Навіщо це потрібно

Коли ми працюємо зі звичайним кодом, ми майже ніколи не вважаємо програму готовою тільки тому, що вона один раз правильно спрацювала вручну. Ми пишемо тести, перевіряємо різні сценарії, фіксуємо очікувану поведінку і запускаємо ці перевірки після змін.

З інструкціями для AI-моделей ситуація часто гірша. Інструкцію переписали, вона почала краще працювати в одному випадку, але непомітно зламала інший. Додали нове правило — модель почала ставити питання не в тому порядку. Посилили gate — модель перестала доходити до результату. Послабили gate — модель почала створювати фінальний артефакт раніше підтвердження.

Без тестів такі проблеми видно тільки випадково. А якщо playbook великий, знайти причину стає дуже складно.

Тому Ordo-програма має тестуватися не лише за фінальним текстом, а за поведінкою процесу.

![Nebu — ідея: тест перевіряє поведінку процесу](../assets/mascots/64x64/Nebu_idea_64x64.png)

Тест у Ordo відповідає не тільки на питання:

```text
чи правильний фінальний output?
```

Він відповідає на ширше питання:

```text
чи процес пройшов саме так, як мав пройти?
```

У v0.12 це стає ще важливішим, бо Ordo тепер явно розрізняє різні класи довіри: механічні перевірки, семантичні перевірки моделлю, повторні перевірки та рішення людини. Тест має бачити цю різницю, а не просто казати “gate пройшов”.

---

## Просте пояснення

У звичайному prompt-підході тест часто виглядає так:

```text
Я дав моделі вхідні дані.
Модель щось відповіла.
Відповідь наче нормальна.
```

Для Ordo цього недостатньо.

![Nebu — увага: тестувати треба не тільки фінальний output](../assets/mascots/64x64/Nebu_attention_64x64.png)

Ordo має перевіряти:

```text
- який path було обрано;
- які шляхи було відхилено;
- які питання модель поставила;
- які питання модель не мала ставити;
- як оброблено unmatched input;
- який state змінився;
- які gates пройдені;
- яким методом перевірялися gates;
- який trust_class мав кожен gate;
- які gates заблокували виконання;
- чи не створено заборонений output;
- чи правильно оброблено no-op сценарій;
- чи не було прихованого використання FREEFORM;
- чи не була виконана дія без approval;
- чи відповідає поведінка заявленому execution_mode;
- чи не порушено ASSERTION.
```

Тобто тест Ordo-програми — це перевірка execution behavior.

---

## Fixture: контрольований вхід

Щоб тест був повторюваним, він має мати fixture.

Fixture — це підготовлений набір вхідних даних для тесту.

У звичайному коді fixture може бути тестовим об’єктом, записом у базі або файлом. В Ordo fixture може містити:

```text
- повідомлення користувача;
- стартовий state;
- доступний context;
- execution_mode;
- control_level;
- підключені libraries;
- активний profile;
- domain pack;
- source documents;
- очікувані user confirmations;
- обмеження середовища;
- попередній trace, якщо тест replay-based.
```

Приклад:

```yaml
fixture:
  id: "FX_HISTORY_EVENT_A1_BASIC"
  execution_mode: "chat_internal"
  control_level: "standard"
  user_message: "Створюємо історичну подію зміни статусу компанії."
  initial_state:
    event_alias: null
    source_field: null
    contract_confirmed: false
  context:
    domain_pack: "history_event"
    available_paths:
      - "A1"
      - "A2"
      - "A4"
```

Fixture потрібен, щоб ми могли повторити той самий сценарій і отримати порівнюваний результат.

---

## Expected behavior: що саме має статися

У звичайних тестах часто перевіряють тільки результат. Наприклад:

```text
очікуємо файл package.zip
```

В Ordo цього мало. Потрібно описати expected behavior.

Expected behavior — це контракт очікуваної поведінки процесу.

Він може включати:

```text
- expected path;
- expected node sequence;
- expected questions;
- expected state;
- expected gates;
- expected gate methods;
- expected trust classes;
- expected assertions;
- expected output;
- expected block;
- expected no-op;
- expected warnings;
- expected trace_source;
- expected absence of forbidden actions.
```

Приклад:

```yaml
expected:
  path:
    selected: "A1"

  questions:
    required:
      - intent: "request_event_alias_confirmation"
      - intent: "request_source_field_confirmation"
    forbidden:
      - intent: "request_final_archive_generation"

  gates:
    - id: "domain_pack.history_event.G_CONTRACT_CONFIRMED"
      method: "human"
      trust_class: "human_decision"
      status: "blocked"

  output:
    final_archive_created: false
```

Тут важливо, що тест не вимагає від моделі дослівно повторити текст. Він перевіряє смислову поведінку.

---

## TEST.DEF

У мові Ordo тест можна описати через `TEST.DEF`.

Спрощено:

```yaml
TEST.DEF:
  id: "TC_NO_FINAL_OUTPUT_BEFORE_APPROVAL"
  title: "Не створювати фінальний output до approval"
  mode: "test"

  fixture:
    execution_mode: "chat_internal"
    user_message: "Зроби фінальний архів одразу."
    initial_state:
      approval:
        pre_archive: false

  expected:
    gates:
      - id: "domain_pack.history_event.G_PRE_ARCHIVE_APPROVAL"
        method: "human"
        trust_class: "human_decision"
        status: "blocked"

    assertions:
      - id: "domain_pack.history_event.A_NO_ARCHIVE_BEFORE_APPROVAL"
        polarity: "not"
        status: "passed"

    output:
      final_archive_created: false

    not_allowed:
      - "archive.generate"
      - "handoff.mark_ready"
```

Цей тест каже: навіть якщо користувач просить зробити фінальний архів, Ordo-програма не має переходити через blocking gate без approval.

---

## ASSERTION у тестах

У v0.12 `ASSERTION` стає канонічним способом описати обов’язкову або заборонену умову.

`ASSERT.NOT`, `negative gate` і `EXPECT.NOT` більше не мають бути трьома окремими правилами, які автор підтримує вручну. Це різні проєкції одного assertion.

Наприклад:

```yaml
ASSERTION.DEF:
  id: "domain_pack.history_event.A_NO_INVENTED_ALIAS"
  polarity: "not"
  condition: "alias_created_without_user_confirmation"
  phase:
    - runtime
    - test
  severity: "block"
  on_fail: "STOP"
```

Компілятор розгортає це правило у runtime-перевірку:

```yaml
ASSERT.NOT:
  id: "domain_pack.history_event.A_NO_INVENTED_ALIAS"
  condition: "alias_created_without_user_confirmation"
  on_fail: "STOP"
```

і в test-time очікування:

```yaml
EXPECT.NOT:
  id: "domain_pack.history_event.A_NO_INVENTED_ALIAS"
  condition: "alias_created_without_user_confirmation"
```

Це захищає від поширеної помилки: правило є в playbook, але його забули додати в regression suite.

---

## EXPECT.PATH

`EXPECT.PATH` перевіряє, який шлях має бути обраний.

Наприклад:

```yaml
EXPECT.PATH:
  selected: "A1"
  rejected:
    - id: "A2"
      reason_required: true
    - id: "A4"
      reason_required: true
```

Це важливо для decision tree. Якщо модель обрала правильний output, але прийшла до нього неправильним шляхом, це все одно проблема. Бо в складному процесі неправильний path пізніше може зламати gates, state або QA.

---

## EXPECT.GATE

`EXPECT.GATE` перевіряє gate behavior.

У v0.12 тест має перевіряти не лише `status`, а й `method` та `trust_class`.

```yaml
EXPECT.GATE:
  - id: "domain_pack.history_event.G_SOURCE_FIELD_CONFIRMED"
    method: "human"
    trust_class: "human_decision"
    status: "blocked"
    because: "source field has not been confirmed by user"
```

Такий тест захищає від ситуації, коли модель сама “додумала” відсутнє підтвердження.

Для Ordo це критично. Якщо gate є в документації, але не блокує виконання, це не gate, а декоративний текст.

---

## EXPECT.STATE

`EXPECT.STATE` перевіряє, як змінюється state.

```yaml
EXPECT.STATE:
  after_node: "N_COLLECT_ALIAS"
  values:
    event_alias: "LU_CHANGE_STATUS"
    contract_confirmed: false
```

State-тести потрібні, бо багато помилок виникає не у фінальному output, а раніше: модель неправильно запам’ятала рішення, переплутала confirmed і assumed, або перенесла значення з прикладу в реальний контракт.

---

## EXPECT.OUTPUT

`EXPECT.OUTPUT` перевіряє результат, але в Ordo результат — це не обов’язково текст.

Output може бути:

```text
- документ;
- JSON;
- archive;
- checklist;
- question;
- blocked status;
- handoff;
- validation report;
- improvement record.
```

Приклад:

```yaml
EXPECT.OUTPUT:
  type: "question"
  must_request:
    - "source_field"
    - "old_value"
    - "new_value"
  must_not_create:
    - "final_package"
```

Це означає: правильний output на цьому етапі — не фінальний документ, а питання до користувача.

---

## EXPECT.NOOP

No-op сценарії дуже важливі.

No-op — це ситуація, де правильна поведінка полягає в тому, щоб нічого не створювати або нічого не змінювати.

![Nebu — подумати: no-op теж очікувана поведінка](../assets/mascots/64x64/Nebu_thinking_64x64.png)

У класичних інструкціях такі сценарії часто ламаються, бо модель вважає, що має “щось зробити”. Але в реальних процесах правильна відповідь іноді така:

```text
нічого не змінюємо;
не створюємо подію;
не генеруємо ChangeRecord;
не створюємо archive;
зупиняємо процес.
```

Приклад:

```yaml
TEST.DEF:
  id: "TC_EXPECTED_NO_CHANGE"
  title: "Не створювати подію, якщо значення не змінилося"

  fixture:
    old_value: "active"
    new_value: "active"

  expected:
    noop: true
    no_new_change_record: true
    no_history_event_created: true
```

No-op тести захищають систему від зайвої активності.

---

## EXPECT.NOT

`EXPECT.NOT` залишається корисною назвою для тестового очікування, але в v0.12 вона має бути проєкцією `ASSERTION`, а не окремим правилом.

Наприклад:

```yaml
EXPECT.NOT:
  - assertion_id: "domain_pack.history_event.A_NO_FINAL_ARCHIVE_BEFORE_APPROVAL"
  - assertion_id: "domain_pack.history_event.A_NO_INVENTED_SOURCE_ROW"
  - assertion_id: "domain_pack.history_event.A_NO_ASSUMPTION_AS_CONFIRMED"
  - assertion_id: "core.assertions.A_NO_HIDDEN_GATE_INSIDE_FREEFORM"
```

Це дозволяє перевіряти не тільки те, що модель має зробити, а й те, чого вона не має робити.

---

## EXPECT.CLARIFY

У v0.12 для `NODE.DEF` зʼявляється контрольований escape hatch `on_unmatched_input`. Тому тест має вміти перевіряти не тільки нормальні `allowed_answers`, а й ситуацію, коли відповідь користувача не входить у дерево.

```yaml
EXPECT.CLARIFY:
  node: "domain_pack.history_event.N_EVENT_KIND"
  when_input: "зроби як минулого разу"
  expected_action: "CLARIFY.REQUEST"
  strategy: "rephrase_and_narrow"
  max_attempts: 2
  on_exhausted: "escalate_to_human"
```

Цей тест захищає від неконтрольованої імпровізації: модель не повинна сама вигадувати новий path, якщо input не відповідає жодній дозволеній відповіді.

---

## Тестувати треба поведінку, а не стиль відповіді

Одна з помилок — тестувати Ordo-програму як текстовий шаблон.

Погано:

```text
Модель має дослівно написати: "Підтвердіть alias події".
```

Краще:

```yaml
expected:
  question_intent:
    - "request_event_alias_confirmation"
```

Тобто ми перевіряємо не буквальне формулювання, а смислову дію.

Це важливо, бо AI-модель може сформулювати питання різними словами, але виконати той самий Ordo-крок.

---

## Тест як захист від деградації інструкцій

Коли Ordo-програма розвивається, тести стають захистом від випадкової деградації.

Наприклад, ми додали нову бібліотеку:

```yaml
include:
  - library: "ordo.artifact.validation"
    version: "0.1"
```

Після цього потрібно перевірити, що старі сценарії не зламалися:

```text
- Path A1 все ще обирається правильно.
- Gate перед архівом все ще blocking.
- Gate має правильний method.
- self_verification gate не видається за mechanical gate.
- FREEFORM не почав перекривати structured rules.
- No-op сценарії не створюють зайвих подій.
- ASSERTION розгортається у runtime і test checks.
```

Без тестів ми побачимо проблему тільки під час реальної роботи.

---

## Типові помилки

### Помилка 1. Тестувати тільки фінальний документ

Якщо фінальний документ виглядає правильно, це ще не означає, що процес був правильний. Модель могла пропустити approval або вигадати частину state.

### Помилка 2. Не тестувати blocking gates

Gate без тесту легко перетворюється на рекомендацію.

### Помилка 3. Не тестувати `method` і `trust_class`

У v0.12 тест має бачити, чи gate був механічним, модельним або людським. Інакше semantic self-check може випадково виглядати як deterministic verification.

### Помилка 4. Не тестувати no-op

Якщо no-op не тестується, система майже гарантовано почне створювати зайві результати.

### Помилка 5. Тестувати тільки happy path / основний успішний сценарій

Складні Ordo-програми мають тестувати також відмови, зупинки, неповні дані, конфлікти, unmatched input і неправильні запити користувача.

### Помилка 6. Не прив’язувати тест до node/gate/path/assertion

Якщо тест падає, але незрозуміло, яку частину програми він перевіряє, debug стає значно складнішим.

### Помилка 7. Тримати `EXPECT.NOT` окремо від `ASSERTION`

Якщо негативне правило описане окремо в runtime і окремо в тестах, вони рано чи пізно розʼїдуться. У v0.12 джерелом має бути `ASSERTION`, а `EXPECT.NOT` — його тестова проєкція.

---

## Міні-вправа

Візьміть просту інструкцію:

```text
Підготуй відповідь клієнту про затримку доставки.
```

Опишіть для неї один Ordo test case:

```text
1. Який fixture?
2. Який execution_mode?
3. Який expected path?
4. Які питання модель має поставити?
5. Який gate має заблокувати фінальну відповідь?
6. Який method і trust_class має цей gate?
7. Який ASSERTION забороняє вигадати причину затримки?
8. Який output заборонений до підтвердження?
9. Який no-op сценарій можливий?
```

Наприклад, no-op може бути таким: якщо користувач просить відповісти клієнту, але не дав жодної інформації про причину затримки, модель не має вигадувати причину. Вона має зупинитися і запросити контекст.

---

## Короткий підсумок

Ordo-тест — це не перевірка красивого тексту. Це перевірка поведінки процесу.

Тест має фіксувати:

```text
input → fixture → expected path → expected state → expected gates → expected assertions → expected output → forbidden actions
```

У v0.12 тест також має бачити:

```text
execution_mode → gate.method → trust_class → trace_source → assertion projections
```

Саме це дозволяє розвивати складні інструкції без хаосу.

Без тестів Ordo-програма поступово перетворюється назад на великий prompt, який важко змінювати і майже неможливо надійно дебажити.

---

<!-- REVIEWED: chapter 16; updated for Ordo v0.12 ASSERTION/test projections; Nebu markers checked -->
