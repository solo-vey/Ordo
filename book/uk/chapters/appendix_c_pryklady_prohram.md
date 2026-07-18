# Додаток C. Приклади програм

## Навіщо потрібен цей додаток

У попередніх розділах Ordo розглядалася як мова керування поведінкою моделі: з intent, contract, state, nodes, gates, outputs, debug trace, tests, libraries і improvement loop.

Цей додаток показує, як усе це може виглядати у вигляді невеликих Ordo-програм.

Це не фінальний синтаксис мови. Це навчальні приклади, які допомагають побачити головну ідею: Ordo-програма описує не просто те, що модель має написати, а те, як вона має вести процес.

## Приклад 1. Найменша Ordo-програма

### Завдання

Користувач хоче отримати коротку відповідь клієнту про затримку доставки.

Звичайний prompt міг би виглядати так:

```text
Напиши ввічливу відповідь клієнту про затримку доставки.
```

У Ordo це краще розкласти на intent, contract, context, gates і output.

```yaml
ordo:
  version: "0.11"

intent:
  id: "INTENT_DELAY_RESPONSE"
  goal: "Підготувати коротку ввічливу відповідь клієнту про затримку доставки."

contract:
  output_type: "customer_message"
  language: "uk"
  tone: "polite"
  max_length: "short"
  must_not:
    - "вигадувати точну дату доставки, якщо її немає в context"
    - "звинувачувати клієнта"
    - "обіцяти компенсацію без підтвердження"

context:
  known:
    delay_reason: "логістична затримка"
    exact_new_date: null

state:
  fields:
    delay_reason_confirmed: true
    exact_new_date_available: false

nodes:
  - id: "N_CHECK_DATE"
    type: "decision"
    question: "Чи є підтверджена нова дата доставки?"
    when:
      field: "exact_new_date_available"
      equals: false
    next: "N_GENERATE_WITHOUT_DATE"

  - id: "N_GENERATE_WITHOUT_DATE"
    type: "output"
    instruction: "Сформуй коротке повідомлення без точної нової дати."

gates:
  - id: "G_NO_FAKE_DATE"
    type: "ASSERT.NOT"
    rule: "output must not contain invented delivery date"

output:
  id: "OUT_CUSTOMER_MESSAGE"
  type: "chat_message"
```

### Що тут важливо

Ordo не просто просить модель написати текст. Вона явно каже:

```text
- що відомо;
- чого не відомо;
- що не можна вигадувати;
- яку перевірку пройти перед результатом;
- який тип output потрібен.
```

## Приклад 2. Та сама програма у Semantic JSON IR

Ordo Source може компілюватися в Semantic JSON IR.

```json
{
  "ordo_version": "0.11",
  "program_id": "CUSTOMER_DELAY_RESPONSE",
  "ops": [
    {
      "op": "INTENT.DEF",
      "id": "INTENT_DELAY_RESPONSE",
      "goal": "Підготувати коротку ввічливу відповідь клієнту про затримку доставки."
    },
    {
      "op": "CONTRACT.DEF",
      "id": "CONTRACT_OUTPUT",
      "output_type": "customer_message",
      "language": "uk",
      "tone": "polite",
      "must_not": [
        "invent_delivery_date",
        "blame_customer",
        "promise_compensation_without_confirmation"
      ]
    },
    {
      "op": "STATE.SCHEMA",
      "id": "STATE_MAIN",
      "fields": {
        "delay_reason_confirmed": "boolean",
        "exact_new_date_available": "boolean"
      }
    },
    {
      "op": "NODE.DEF",
      "id": "N_CHECK_DATE",
      "node_type": "decision",
      "condition": {
        "field": "exact_new_date_available",
        "equals": false
      },
      "next": "N_GENERATE_WITHOUT_DATE"
    },
    {
      "op": "ASSERT.NOT",
      "id": "G_NO_FAKE_DATE",
      "target": "OUT_CUSTOMER_MESSAGE",
      "rule": "output_contains_invented_delivery_date"
    },
    {
      "op": "OUTPUT.DEF",
      "id": "OUT_CUSTOMER_MESSAGE",
      "output_type": "chat_message"
    }
  ]
}
```

### Що показує приклад

Semantic JSON IR не обов’язково красивий для людини. Його завдання інше: бути достатньо структурованим, щоб модель, helper-runner або майбутній native Ordo executor могли виконувати його послідовно.

## Приклад 3. Gate як зупинка перед фінальним результатом

### Сценарій

Користувач просить створити фінальний пакет, але approval ще не отриманий.

```yaml
gates:
  - id: "G_PRE_FINAL_APPROVAL"
    type: "APPROVAL.REQUIRE"
    required_before:
      - "OUTPUT.FINAL"
    approval_source: "human_user"
    status_on_missing: "blocked"

assertions:
  - id: "A_NO_FINAL_WITHOUT_APPROVAL"
    type: "ASSERT.NOT"
    rule: "final_output_created_before_G_PRE_FINAL_APPROVAL_passed"
```

Очікувана поведінка:

```text
Модель не створює фінальний пакет.
Модель пояснює, який gate блокує дію.
Модель ставить питання або просить підтвердження.
```

Погана поведінка:

```text
Модель усе одно створює пакет, а потім пише: “я припустила, що підтвердження є”.
```

У Ordo така поведінка має вважатися violation.

## Приклад 4. Debug run

Той самий процес можна запустити в debug mode.

```yaml
run:
  mode: "debug"
  trace_source: "model_self_report"
  input: "Зроби фінальний пакет одразу"

trace:
  selected_path:
    id: "PACKAGE_GENERATION"
    reason: "user requested final package"

  gates:
    - id: "G_PRE_FINAL_APPROVAL"
      status: "blocked"
      reason: "human approval is missing"

  decisions:
    - id: "D_BLOCK_FINAL_OUTPUT"
      reason: "required gate is blocked"
      result: "final output not created"

  violations: []

  output:
    final_package_created: false
    response_type: "gate_block_message"
```

Debug run потрібен не для користувацького фінального тексту, а для пояснення поведінки Ordo-програми.

## Приклад 5. Test case для gate

```yaml
test:
  id: "TC_NO_FINAL_PACKAGE_WITHOUT_APPROVAL"
  method: human
  trust_class: human_decision
  mode: "test"

fixture:
  user_message: "Зроби фінальний пакет одразу"
  state:
    pre_final_approval: false

expect:
  path:
    selected: "PACKAGE_GENERATION"

  gate:
    id: "G_PRE_FINAL_APPROVAL"
    status: "blocked"

  output:
    final_package_created: false

  not_allowed:
    - "create_archive"
    - "mark_package_ready"
```

Цей test case перевіряє не красу відповіді, а правильну поведінку.

## Приклад 6. No-op test

No-op сценарії дуже важливі. Іноді правильна дія — не створювати нову подію, не змінювати state і не генерувати зайвий output.

```yaml
test:
  id: "TC_NOOP_SAME_VALUE"
  mode: "test"

fixture:
  before:
    field: "status"
    value: "ACTIVE"
  after:
    field: "status"
    value: "ACTIVE"

expect:
  noop: true
  no_new_event: true
  no_change_record: true
  explanation_required: true
```

У звичайному prompt-підході модель часто намагається “щось зробити”, навіть коли зміни немає. Ordo має вміти явно сказати: правильний результат — no-op.

## Приклад 7. Підключення бібліотеки

Ordo-програма може підключати готові правила повторного використання.

```yaml
libraries:
  include:
    - id: "ordo.validation.contract_first"
      version: "0.1"
      as: "contract_first"

    - id: "ordo.validation.rendered_artifact"
      version: "0.1"
      as: "render_validation"

use:
  - "contract_first.required_contract_gate"
  - "render_validation.rendered_output_check"
```

Це означає, що програма не дублює стандартні gates, а явно використовує готові перевірені конструкції.

Правило:

```text
Бібліотека не повинна підключатися неявно.
Версія має бути зафіксована.
Конфлікти мають бути явними.
Override має бути дозволений окремо.
```

## Приклад 8. Conflict між бібліотеками

```yaml
libraries:
  include:
    - id: "ordo.status.strict"
      version: "0.1"
      as: "strict_status"

    - id: "ordo.status.legacy"
      version: "0.1"
      as: "legacy_status"
```

Якщо обидві бібліотеки визначають різну семантику одного статусу, Ordo має зупинитися.

```yaml
conflict:
  id: "CONFLICT_STATUS_READY"
  type: "STATUS.SEMANTICS_CONFLICT"
  symbol: "ready_for_first_run"
  sources:
    - "strict_status"
    - "legacy_status"
  resolution_required: true
```

Погана поведінка:

```text
Модель мовчки обрала одну з версій.
```

Правильна поведінка:

```text
Модель повідомляє про conflict і просить resolution rule або human decision.
```

## Приклад 9. Feedback & Improvement Loop

Користувач під час роботи каже:

```text
Ти поставив питання про output занадто рано. Спочатку потрібно було підтвердити source field.
```

Ordo має створити improvement record.

```yaml
feedback_capture:
  id: "FB-001"
  source: "user_feedback"
  message: "Ти поставив питання про output занадто рано. Спочатку потрібно було підтвердити source field."

improvement_record:
  id: "IR-001"
  classification:
    type: "wrong_question_order"
    severity: "medium"

  affected_unit:
    kind: "node"
    id: "N_OUTPUT_DETAILS"
    owner:
      layer: "domain_pack"
      name: "history_event"

  root_cause_hypothesis:
    - "NODE order allows output collection before source field confirmation"

  proposed_patch:
    - "move N_OUTPUT_DETAILS after G_SOURCE_FIELD_CONFIRMED"
    - "add gate before output details question"

  suggested_tests:
    - id: "TC_SOURCE_FIELD_BEFORE_OUTPUT_DETAILS"
      expected:
        required_order:
          - "G_SOURCE_FIELD_CONFIRMED"
          - "N_OUTPUT_DETAILS"

  approval:
    required: true
    status: "pending"
```

Цей приклад показує, що feedback в Ordo не губиться в чаті. Він стає структурованим кандидатом на покращення.

## Приклад 10. Малий guided intake

```yaml
entry:
  id: "ENTRY_NEW_EVENT"
  goal: "Почати guided intake нової історичної події."

state:
  fields:
    event_alias: null
    source_field: null
    old_value: null
    new_value: null
    path_confirmed: false

nodes:
  - id: "N_SELECT_PATH"
    type: "question"
    ask: "Який тип зміни потрібно описати?"
    writes:
      - "path_candidate"

  - id: "N_CONFIRM_SOURCE_FIELD"
    type: "question"
    ask: "Яке source field змінюється?"
    writes:
      - "source_field"

  - id: "N_COLLECT_VALUES"
    type: "question"
    ask: "Які old/new values потрібно зафіксувати?"
    requires:
      - "source_field"
    writes:
      - "old_value"
      - "new_value"

gates:
  - id: "G_SOURCE_FIELD_CONFIRMED"
    type: "APPROVAL.REQUIRE"
    required_before:
      - "N_COLLECT_VALUES"

  - id: "G_NO_PACKAGE_BEFORE_CONTRACT"
    type: "ASSERT.NOT"
    rule: "final_package_created_before_required_contract_fields_confirmed"
```

Тут guided intake — це не просто діалог. Це керований процес, де кожне питання має місце, writes, requirements і gates.

## Приклад 11. FREEFORM з binding

```yaml
freeform:
  id: "FF_DOMAIN_EDGE_CASES"
  type: "controlled_freeform"
  purpose: "Описати складні доменні edge cases, які ще не формалізовані в окремі gates."
  binding:
    used_by:
      - "N_SELECT_PATH"
      - "G_DOMAIN_REVIEW"
    must_not_override:
      - "ASSERT.NOT"
      - "APPROVAL.REQUIRE"
      - "STATUS.SEMANTICS"
  content: |
    У деяких випадках зміна може виглядати як оновлення поля, але фактично бути появою зовнішньої події.
    Якщо є ExternalHistoryEvent, потрібно перейти до path A4, а не трактувати запис як простий field delta.
```

FREEFORM тут не є “смітником для правил”. Він має purpose, binding і межі впливу.

## Приклад 12. Coverage report

```yaml
coverage_report:
  program: "history_event_playbook"

  paths:
    total: 5
    covered: 4
    uncovered:
      - "A4"

  gates:
    total: 14
    covered: 12
    uncovered:
      - "G_EXTERNAL_EVENT_NORMALIZED"
      - "G_RENDERED_ARTIFACT_VALIDATED"

  freeform:
    total_blocks: 5
    covered_by_tests: 3
    untested:
      - "FF_DOMAIN_EDGE_CASES"
      - "FF_EXAMPLES_LEGACY"

  libraries:
    included: 2
    compatibility_checked: 2
    conflicts: 0
```

Coverage report потрібен для чесної відповіді на питання: наскільки ця Ordo-програма справді контрольована тестами й трасуванням?

## Короткий підсумок

Приклади в цьому додатку показують головну різницю між prompt-ом і Ordo-програмою.

Prompt зазвичай каже моделі:

```text
Зроби ось це.
```

Ordo каже:

```text
Ось мета.
Ось контракт.
Ось state.
Ось допустимі шляхи.
Ось gates.
Ось заборонені дії.
Ось output.
Ось debug trace.
Ось tests.
Ось improvement loop.
```

Саме тому Ordo можна не тільки читати, а й виконувати, дебажити, тестувати, покращувати і поступово переносити до native model support.
