# Розділ 17. Regression suite і coverage

## Навіщо це потрібно

Коли Ordo-програма маленька, її можна перевірити вручну. Достатньо один раз прогнати сценарій і подивитися, чи модель поставила правильне питання, чи не пропустила gate, чи створила потрібний output.

Але як тільки Ordo-програма стає більшою, ручної перевірки вже недостатньо.

Зʼявляється типова проблема:

```text
ми виправили одну помилку →
але зламали інший сценарій →
потім виправили другий сценарій →
але випадково послабили важливий gate →
потім додали нове правило →
але воно почало конфліктувати зі старим правилом.
```

У звичайній роботі з prompt-ами це майже неможливо контролювати. Користувач бачить тільки, що модель “стала поводитися дивно”. Але не завжди зрозуміло, яка саме зміна це спричинила.

В Ordo для цього потрібні дві речі:

```text
Regression suite
Coverage report
```

`Regression suite` перевіряє, що старі сценарії не зламалися після зміни інструкцій.

![Nebu — ідея: regression suite захищає поведінку](../assets/mascots/64x64/Nebu_idea_64x64.png)

`Coverage report` показує, які частини Ordo-програми реально покриті тестами, а які існують тільки на папері.

Починаючи з Ordo v0.12, coverage має перевіряти не тільки paths, nodes і outputs. Він також має показувати, чи покриті:

```text
gate.method;
trust_class;
execution_mode;
control_level;
ASSERTION-проєкції;
layer conflict rules;
FREEFORM maturity lifecycle.
```

Інакше можна мати гарний coverage report, але не бачити, що всі критичні семантичні gates перевіряються тільки самою моделлю, а не механічно або через окремий critic-прохід.

---

## Що таке regression suite

Regression suite — це набір тестів, який потрібно запускати після зміни Ordo-програми, library, domain pack, profile або compiler rule.

Простими словами:

```text
Regression suite — це захист від випадкового ламання того, що вже працювало.
```

Наприклад, у нас є Ordo-playbook для створення історичних подій. Він підтримує кілька шляхів:

```text
A1 — зміна поля в source row;
A2 — зміна повʼязаної сутності;
A3 — ручний сценарій;
A4 — зовнішня історична подія;
A5 — no-op / expected no-change.
```

Ми змінюємо логіку A1, щоб краще обробляти зміну статусу. Але після цього треба переконатися, що:

```text
A2 не зламався;
A4 не почав трактувати external payload як звичайний delta.field;
A5 досі правильно зупиняє no-op сценарії;
pre-archive gates досі блокують фінальний пакет до підтвердження;
manual QA package досі має потрібні перевірки;
усі blocking gates мають method;
trace не видає model_self_report за runtime_enforced;
ASSERTION не загубила test-проєкцію.
```

Саме це робить regression suite.

---

## Regression suite як частина мови

У Ordo regression suite не має бути зовнішньою домовленістю на кшталт “не забудь потім перевірити”.

Вона має бути частиною самої Ordo-програми або повʼязаного з нею test package.

Наприклад:

```yaml
regression_suite:
  id: "RS_HISTORY_EVENT_PLAYBOOK"
  target:
    kind: "domain_pack"
    name: "history_event"
    version: "0.12"

  control_level: strict
  execution_modes:
    - full_runtime
    - chat_internal

  tests:
    - "TC_PATH_A1_BASIC"
    - "TC_PATH_A2_RELATED_ENTITY"
    - "TC_PATH_A4_EXTERNAL_EVENT"
    - "TC_NO_FINAL_ARCHIVE_BEFORE_APPROVAL"
    - "TC_EXPECTED_NO_CHANGE"
    - "TC_FREEFORM_BINDING_VISIBLE"
    - "TC_GATE_METHODS_DECLARED"
    - "TC_ASSERTIONS_PROJECTED_TO_TESTS"
    - "TC_TRACE_SOURCE_VISIBLE"

  required_before:
    - "domain_pack_publish"
    - "library_version_publish"
    - "compiler_rule_change"
    - "production_use"
```

Тут важливі чотири речі.

Перше: suite має ціль. Він перевіряє не “все на світі”, а конкретну Ordo-програму, library, profile або domain pack.

Друге: suite має список тестів. Кожен тест перевіряє конкретну поведінку.

Третє: suite має правило запуску. Наприклад, перед публікацією нової версії domain pack regression suite є обовʼязковим.

Четверте: suite має знати `control_level` і `execution_modes`, для яких він справедливий. Тест, який достатній для `freeform_only`, може бути занадто слабким для `strict`-режиму.

---

## Що має перевіряти regression suite

Regression suite має перевіряти не тільки фінальний текст.

Це ключова думка.

У звичайному prompt-testing часто перевіряють результат:

```text
чи відповідь виглядає нормально?
```

В Ordo потрібно перевіряти поведінку процесу:

```text
чи правильний path був обраний;
чи правильний node був активований;
чи правильне питання поставила модель;
чи правильний state змінився;
чи правильний gate спрацював;
чи правильний method має кожен gate;
чи trust_class відповідає реальному способу перевірки;
чи trace_source не завищує рівень гарантії;
чи ASSERTION розгорнулась у runtime і test expectations;
чи правильний output був створений;
чи не була виконана заборонена дія;
чи зберігся handoff contract;
чи не було прихованого використання FREEFORM;
чи не зникло обовʼязкове пояснення.
```

Тобто regression suite має дивитися на Ordo-програму як на процес, а не як на генератор тексту.

---

## Приклад regression test

Припустимо, ми хочемо перевірити, що фінальний архів не створюється до approval gate.

Тест може виглядати так:

```yaml
test:
  id: "TC_NO_ARCHIVE_BEFORE_APPROVAL"
  title: "Фінальний архів не створюється до підтвердження"
  execution_mode: full_runtime

fixture:
  user_message: "зроби фінальний архів одразу"
  state:
    contract_confirmed: true
    pre_archive_approval: false
    validation_passed: false

expected:
  selected_path: "package_generation"

  gates:
    - id: "domain_pack.history_event.G_PRE_ARCHIVE_APPROVAL"
      method: human
      trust_class: human_decision
      status: blocked

  assertions:
    - id: "domain_pack.history_event.A_NO_ARCHIVE_BEFORE_APPROVAL"
      polarity: not
      phase: [runtime, test]
      status: passed

  output:
    final_archive_created: false

  forbidden_actions:
    - "ARCHIVE.CREATE"
    - "HANDOFF.MARK_READY"
```

Цей тест не питає, чи модель написала красиву відповідь. Він перевіряє інше:

```text
чи модель не зробила того, що їй заборонено робити.
```

Це набагато важливіше для складних процесів.

---

## Тестування `gate.method`

![Nebu — увага: gate без method не є повноцінним gate](../assets/mascots/64x64/Nebu_attention_64x64.png)

У v0.12 `gate.method` — це не декоративне поле. Це частина довіри до gate.

Тому regression suite має мати окремі тести або lint-перевірки:

```yaml
test:
  id: "TC_GATE_METHODS_DECLARED"

expected:
  all_gates_have_method: true
  allowed_methods:
    - mechanical
    - self_verification
    - self_consistency
    - human

  forbidden:
    - gate_without_method
    - gate_with_unknown_method
```

Окремо потрібно перевіряти, що `trust_class` не суперечить `method`:

```yaml
expected:
  method_trust_mapping:
    mechanical: deterministic
    self_verification: model_judgment
    self_consistency: repeated_model_judgment
    human: human_decision
```

Це не гарантує, що кожне семантичне судження правильне. Але це не дозволяє приховати семантичне судження під виглядом механічної перевірки.

---

## Тестування `execution_mode`

Одна й та сама Ordo-програма може виконуватись у різних режимах:

```text
full_runtime;
chat_internal;
freeform_only.
```

Regression suite має явно показувати, для якого режиму виконання справедливий тест.

Наприклад:

```yaml
test:
  id: "TC_TRACE_SOURCE_IN_CHAT_INTERNAL"
  execution_mode: chat_internal

expected:
  trace:
    trace_source: hybrid

  gates:
    - id: "domain_pack.history_event.G_RENDERED_ARTIFACT_VALIDATED"
      method: mechanical
      status: passed

  warnings_allowed:
    - "gate_invocation_not_runtime_enforced"
```

У `chat_internal` режимі код може реально виконати перевірку, але сам момент запуску перевірки не є примусово контрольованим зовнішнім runtime. Тому тест має дозволяти чесний warning, а не робити вигляд, що це повний `full_runtime`.

---

## Тестування `ASSERTION`

У v0.12 `ASSERT.NOT`, negative gate і `EXPECT.NOT` більше не мають жити окремо.

Канонічним примітивом є `ASSERTION`:

```yaml
assertion:
  id: "domain_pack.history_event.A_NO_INVENTED_ALIAS"
  polarity: not
  condition: "alias_created_without_user_confirmation"
  phase: [runtime, test]
  severity: block
  on_fail: STOP
```

Regression suite має перевіряти, що така assertion дала потрібні проєкції:

```yaml
expected:
  projections:
    runtime:
      includes: "ASSERT.NOT"
    test:
      includes: "EXPECT.NOT"
    debug:
      includes: "violation_record"
```

Це зменшує ризик, що правило є в основному playbook, але його забули в regression suite.

---

## Що таке coverage

Coverage — це відповідь на питання:

```text
Яку частину Ordo-програми ми реально перевірили?
```

У класичному програмуванні coverage часто показує, які рядки коду або гілки були виконані тестами.

В Ordo coverage має бути ширшим. Тут потрібно перевіряти не тільки “рядки”, а семантичні частини процесу:

```text
paths;
nodes;
gates;
gate methods;
trust classes;
execution modes;
control levels;
status transitions;
outputs;
assertions;
ASSERTION projections;
FREEFORM blocks;
FREEFORM maturity;
libraries;
layer conflicts;
domain rules;
error paths;
no-op сценарії;
handoff rules.
```

Наприклад, playbook може мати пʼять шляхів, але тести перевіряють тільки два. Формально тести є, але насправді більша частина поведінки не захищена.

Coverage має це показати явно.

---

## Приклад coverage report

```yaml
coverage_report:
  target:
    kind: "domain_pack"
    name: "history_event"
    version: "0.12"

  control_level: strict

  execution_modes:
    full_runtime:
      covered: true
    chat_internal:
      covered: true
    freeform_only:
      covered: false
      reason: "not supported for this production pack"

  paths:
    total: 5
    covered: 4
    uncovered:
      - "A4_EXTERNAL_HISTORY_EVENT"

  nodes:
    total: 18
    covered: 15
    uncovered:
      - "NODE_EXTERNAL_EVENT_NORMALIZATION"
      - "NODE_MANUAL_EXCEPTION_REVIEW"

  gates:
    total: 14
    covered: 12
    uncovered:
      - "domain_pack.history_event.G_EXTERNAL_EVENT_MAPPING_CONFIRMED"
      - "domain_pack.history_event.G_RENDERED_ARTIFACT_VALIDATED"

  gate_methods:
    mechanical:
      total: 6
      covered: 6
    self_verification:
      total: 4
      covered: 3
    self_consistency:
      total: 1
      covered: 0
    human:
      total: 3
      covered: 3

  trust_classes:
    deterministic: "covered"
    model_judgment: "partially_covered"
    repeated_model_judgment: "not_covered"
    human_decision: "covered"

  assertions:
    total: 9
    covered: 7
    uncovered:
      - "domain_pack.history_event.A_NO_ARCHIVE_BEFORE_SELF_CHECK"

  assertion_projections:
    runtime: "covered"
    test: "partially_covered"
    debug: "covered"

  freeform:
    total_blocks: 5
    covered: 3
    maturity:
      stable: 2
      volatile: 2
      candidate_for_formalization: 1
    uncovered:
      - "FF_DOMAIN_EXAMPLES"
      - "FF_EDGE_CASE_NOTES"

  outputs:
    total: 11
    covered: 10
    uncovered:
      - "07_PROCESS_IMPROVEMENT_FEEDBACK"
```

Такий report одразу показує слабкі місця.

Наприклад, якщо `G_RENDERED_ARTIFACT_VALIDATED` не покритий тестами, це ризик. Модель може знову перевірити template замість реально згенерованого artifact, і тест це не зловить.

А якщо `self_consistency` gates мають `covered: 0`, це ще один сигнал: критичні семантичні рішення формально описані, але не захищені regression-пакетом.

---

## Coverage не означає якість автоматично

![Nebu — увага: coverage не дорівнює якості](../assets/mascots/64x64/Nebu_attention_64x64.png)

Важливо не сплутати coverage з якістю.

Високий coverage не гарантує, що Ordo-програма добра. Він тільки означає, що багато її частин були виконані тестами.

Можна мати 90% coverage і все одно мати погані тести.

Наприклад, тест може перевіряти тільки те, що output існує:

```yaml
expected:
  output_exists: true
```

Але не перевіряти, що output створено після правильного gate.

Або тест може перевіряти, що gate має `status: passed`, але не перевіряти його `method` і `trust_class`.

Тому для Ordo важливо мати не тільки coverage, а й якість очікувань:

```text
expected path;
expected state;
expected gates;
expected gate.method;
expected trust_class;
expected trace_source;
expected assertion projections;
expected forbidden actions;
expected evidence;
expected no-op;
expected handoff status.
```

Coverage показує, де ми були. Якість тестів показує, що саме ми там перевірили.

---

## Мінімальний coverage для production playbook

Для простих Ordo-програм coverage може бути неповним.

Але для production playbook-ів, domain packs і libraries потрібно встановити мінімальні вимоги.

Наприклад:

```yaml
coverage_policy:
  required_for: "production_domain_pack"
  control_level: strict

  minimum:
    paths: "100%"
    blocking_gates: "100%"
    gate_methods_declared: "100%"
    mechanical_gates_tested: "100%"
    human_gates_have_approval_fixture: "100%"
    self_verification_gates_have_protocol_tests: "100%"
    negative_assertions: "100%"
    assertion_test_projection: "100%"
    outputs: "90%"
    freeform_blocks: "at_least_linked"
    no_op_scenarios: "required_if_supported"

  release_rule:
    if_below_minimum: "block_release"
```

Тут важливо, що blocking gates мають бути покриті всі.

Якщо gate має зупиняти процес, але для нього немає тесту, це небезпечно. Такий gate існує тільки як текстова декларація.

Для `control_level: strict` це має бути не рекомендацією, а правилом компіляції або release-gate.

---

## Regression після feedback

Regression suite особливо важливий після user feedback.

Користувач каже:

```text
Ти пропустив self-check перед архівом.
```

Ordo створює improvement record і пропонує patch:

```text
зробити G_PACKAGE_SELF_CHECK blocking;
додати ASSERTION A_NO_ARCHIVE_BEFORE_SELF_CHECK;
додати test TC_NO_ARCHIVE_WITHOUT_SELF_CHECK.
```

Після внесення зміни треба прогнати regression suite.

Чому? Бо новий blocking gate може випадково заблокувати легітимний сценарій, де self-check уже виконаний, але state названий інакше.

Тобто improvement без regression може виправити одну проблему і створити іншу.

Правильний цикл:

```text
feedback → improvement record → patch → new assertion/test → regression suite → coverage report → release decision
```

---

## Regression для бібліотек

![Nebu — подумати: бібліотечна зміна може зламати багато playbook-ів](../assets/mascots/64x64/Nebu_thinking_64x64.png)

Коли в Ordo зʼявляються libraries, regression стає ще важливішим.

Бібліотека може використовуватися в десятках playbook-ів. Якщо змінити її gate, assertion або status semantics, можна непомітно зламати всі програми, які її підключають.

Тому library має мати власний regression suite:

```yaml
library:
  id: "ordo.validation.contract_first"
  version: "0.2.0"

regression_suite:
  id: "RS_CONTRACT_FIRST_LIBRARY"
  tests:
    - "TC_CONTRACT_REQUIRED_BEFORE_OUTPUT"
    - "TC_MISSING_CONTRACT_BLOCKS_EXECUTION"
    - "TC_EXPLICIT_OVERRIDE_REQUIRED"
    - "TC_ALL_EXPORTED_GATES_HAVE_METHOD"
```

А Ordo-програма, яка використовує бібліотеку, має мати integration tests:

```yaml
integration_tests:
  libraries:
    - id: "ordo.validation.contract_first"
      version: "^0.2.0"
      tests:
        - "TC_PLAYBOOK_CONTRACT_GATE_BINDING"
        - "TC_LAYER_CONFLICT_REQUIRES_OVERRIDE"
```

Це означає: бібліотека працює сама по собі, але також перевірено, що вона правильно підключена до конкретного playbook-а.

---

## Coverage для `control_level`

`control_level` визначає, наскільки суворо має бути перевірена Ordo-програма.

```yaml
program:
  id: "history_event.guided_intake"
  control_level: strict
```

Для `light`-програми достатньо базових перевірок intent і contract.

Для `standard`-програми вже потрібні state, gates і базова regression suite.

Для `strict`-програми потрібні:

```text
обовʼязковий debug trace;
обовʼязковий trace_source;
обовʼязкові gate.method;
обовʼязкові tests для mandatory gates;
обовʼязковий coverage report;
обовʼязковий feedback/improvement path;
обовʼязкова release-перевірка.
```

Coverage report має показувати, чи відповідає тестовий пакет заявленому `control_level`.

---

## Типові помилки

### Помилка 1. Тестувати тільки фінальний текст

Погано:

```text
модель щось відповіла — значить тест пройшов.
```

Добре:

```text
перевірити path, state, gates, output і forbidden actions.
```

---

### Помилка 2. Не запускати regression після дрібної зміни

У складних інструкціях “дрібна зміна” часто має великий ефект.

Одна фраза може змінити пріоритет path, послабити gate або зробити FREEFORM надто широким.

---

### Помилка 3. Вважати coverage доказом якості

Coverage показує, що щось було виконано. Але він не показує автоматично, що очікування були правильні.

---

### Помилка 4. Не покривати negative assertions

У Ordo дуже важливо тестувати не тільки те, що модель має зробити, а й те, чого вона не має робити.

Наприклад:

```text
не створювати архів до approval;
не вигадувати source row;
не переходити до package generation без contract;
не ховати gate у FREEFORM;
не вважати draft final result.
```

---

### Помилка 5. Не тестувати no-op сценарії

No-op — це повноцінний expected behavior.

Якщо правильний результат — нічого не створювати, це теж має бути тестом.

---

### Помилка 6. Не перевіряти `gate.method`

Погано:

```yaml
gates:
  - id: "G_NO_UNSUPPORTED_FACTS"
    status: passed
```

Добре:

```yaml
gates:
  - id: "domain_pack.history_event.G_NO_UNSUPPORTED_FACTS"
    method: self_verification
    trust_class: model_judgment
    status: passed
```

Якщо тест бачить тільки `passed`, але не бачить `method`, він не розуміє, який рівень довіри має цей результат.

---

### Помилка 7. Не розрізняти `full_runtime` і `chat_internal`

Тест для `full_runtime` не можна автоматично вважати доказом для `chat_internal`, і навпаки.

У `chat_internal` частина перевірок може бути реально виконана кодом, але точка їх виклику не є примусовою без зовнішнього runtime.

---

## Міні-вправа

Візьміть будь-яку Ordo-програму або великий prompt, з яким ви працювали.

Спробуйте скласти для нього маленький regression suite з пʼяти тестів:

```text
1. Основний успішний сценарій.
2. Сценарій із відсутнім contract.
3. Сценарій, де має спрацювати blocking gate.
4. Сценарій, де модель не має виконувати заборонену дію.
5. No-op або expected no-change сценарій.
```

Після цього додайте v0.12-питання:

```text
Які gates мають method?
Які gates є mechanical, а які self_verification?
Чи є tests для assertion projections?
Які execution modes покриті?
Чи відповідає coverage заявленому control_level?
Які FREEFORM-блоки впливають на рішення, але не мають тестів?
```

Це і є перший простий coverage analysis.

---

## Короткий підсумок

Regression suite потрібен, щоб Ordo-програма не ламалася після кожного покращення.

Coverage потрібен, щоб бачити, які частини процесу реально перевірені.

У Ordo потрібно тестувати не тільки output, а всю поведінку:

```text
path → node → state → gate → assertion → output → handoff
```

Починаючи з v0.12, сильна Ordo-програма також має перевіряти:

```text
gate.method → trust_class → trace_source → execution_mode → control_level
```

Сильна Ordo-програма — це не та, яка один раз дала правильну відповідь. Сильна Ordo-програма — це та, яка має regression suite, coverage report і може безпечно розвиватися.

<!-- REVIEWED: chapter 17; UPDATED_FOR_ORDO_V0_12; Nebu markers checked -->
