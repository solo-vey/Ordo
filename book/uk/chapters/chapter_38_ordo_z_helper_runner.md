# Розділ 38. Ordo з helper-runner

## Навіщо потрібен helper-runner

У попередньому розділі ми розглянули найпростіший спосіб використання Ordo: без окремого runtime, коли модель сама читає Ordo Source або Semantic JSON IR і намагається виконувати правила дисципліновано.

Цей режим корисний для старту. Але в складних процесах швидко з’являються межі.

Модель може забути gate. Може неявно змінити state. Може перескочити через node. Може сказати, що перевірка пройдена, хоча в trace немає доказу. Може не сформувати improvement record, хоча користувач прямо вказав на проблему.

Саме тут з’являється проміжний рівень:

```text
Ordo з helper-runner
```

Helper-runner — це не повноцінна “розумна модель” і не заміна LLM. Це допоміжний виконавчий шар, який бере на себе контроль процесу.

Його завдання проста:

```text
модель думає і формує зміст,
runner контролює порядок, state, gates, tests і trace.
```

![Nebu — ідея](../assets/mascots/64x64/Nebu_idea_64x64.png)

Іншими словами, helper-runner робить Ordo не просто інструкцією для моделі, а виконуваним процесом із зовнішнім контролем.

## Просте пояснення

Можна уявити Ordo без runtime як кухаря, який читає рецепт і сам вирішує, чи все зробив правильно.

А Ordo з helper-runner — це кухня, де є ще й технологічна карта, контрольні точки, журнал дій і контролер якості.

Кухар усе ще готує страву. Але система стежить, щоб він:

```text
- не пропустив обов’язковий крок;
- не подав страву до перевірки;
- не замінив інгредієнт без дозволу;
- записав, що саме зробив;
- пояснив, чому обрав саме цей шлях.
```

У світі Ordo це означає:

```text
- runner зберігає state;
- runner визначає current node;
- runner блокує перехід через blocking gate;
- runner передає моделі тільки релевантний фрагмент інструкції;
- runner збирає trace;
- runner запускає tests;
- runner формує gate report;
- runner збирає feedback records.
```

Модель залишається семантичним виконавцем. Runner стає процесним контролером.

## Що саме робить helper-runner

Helper-runner може виконувати кілька ролей.

### 1. Завантаження Ordo-програми

Runner читає Ordo Source або compiled IR.

Наприклад:

```text
- main Ordo program;
- included libraries;
- selected profile;
- selected domain pack;
- templates;
- gates;
- tests;
- freeform ledger.
```

Він не покладається на те, що модель сама правильно прочитає весь довгий документ. Він сам визначає, які частини потрібні для поточного кроку.

### 2. Контроль state

Runner зберігає state поза моделлю.

Це дуже важливо. Бо якщо state існує тільки в контексті діалогу, його легко втратити або непомітно змінити.

У runner-based режимі state може бути окремим JSON-об’єктом:

```json
{
  "run_id": "RUN-001",
  "current_node": "NODE_COLLECT_CONTRACT",
  "confirmed": {
    "alias": true,
    "source_field": false
  },
  "outputs": {
    "final_package_created": false
  },
  "gates": {
    "G_CONTRACT_CONFIRMED": "blocked"
  }
}
```

Модель не має права просто сказати, що state змінився. Вона має запропонувати зміну, а runner має її застосувати або заблокувати.

### 3. Контроль переходів

Runner перевіряє, чи можна перейти з одного node в інший.

Наприклад, модель хоче перейти до package generation. Runner дивиться:

```text
Чи підтверджено contract?
Чи пройдені approval gates?
Чи є source row?
Чи виконано self-check?
Чи немає ASSERT.NOT порушень?
```

Якщо ні, runner блокує перехід.

Це принципово відрізняється від звичайного prompt-а. У prompt-і модель “має пам’ятати”, що не можна переходити. У runner-based Ordo перехід технічно не дозволяється.

![Nebu — зверніть увагу](../assets/mascots/64x64/Nebu_attention_64x64.png)

### 4. Формування task для моделі

Runner не обов’язково передає моделі всю Ordo-програму.

Він може передати тільки поточний execution slice:

```yaml
model_task:
  current_node: "NODE_SOURCE_FIELD_CONFIRMATION"
  allowed_actions:
    - "ask_one_question"
    - "update_state_proposal"
  forbidden_actions:
    - "generate_final_package"
    - "mark_contract_confirmed_without_user_answer"
  context:
    known:
      alias: "LU_CHANGE_STATUS"
    missing:
      - "source_field"
  expected_output:
    type: "question"
```

Це зменшує ризик, що модель заплутається в довгому playbook-у.

### 5. Gate enforcement

Runner може робити gates реальними блокувальниками.

Наприклад:

```yaml
gate:
  id: "G_PRE_ARCHIVE_APPROVAL"
  method: human
  trust_class: human_decision
  type: "blocking"
  condition:
    user_approved_archive_generation: true
```

Якщо умова не виконана, runner не дозволяє виконати дію:

```text
generate_archive
```

Навіть якщо модель намагається це зробити.

### 6. Trace і audit

Runner може збирати повний trace незалежно від того, наскільки дисципліновано модель його описала.

Trace має містити:

```text
- input;
- current node;
- selected path;
- rejected paths;
- state before;
- state after;
- gates;
- model proposals;
- runner decisions;
- warnings;
- violations;
- final outputs.
```

Це робить процес перевірюваним.

### 7. Test execution

Runner може запускати `TEST.DEF`.

Наприклад:

```text
взяти fixture →
запустити Ordo-програму →
перевірити expected path →
перевірити expected gates →
перевірити forbidden output →
побудувати report.
```

Це вже набагато ближче до звичайного тестування програмного забезпечення.

### 8. Improvement capture

Runner може автоматично збирати зауваження користувача і перетворювати їх на `IMPROVEMENT.RECORD`.

Наприклад, якщо користувач каже:

```text
Тут ти мав спитати source field раніше.
```

Runner може прив’язати це до:

```text
- run_id;
- node;
- path;
- gate;
- instruction fragment;
- domain pack;
- library version.
```

Потім він може запропонувати patch і regression test.

## Ordo-конструкція

У Source-форматі режим із helper-runner може виглядати так:

```yaml
execution:
  mode: "normal"
  runtime:
    type: "helper_runner"
    responsibilities:
      - "state_management"
      - "node_routing"
      - "gate_enforcement"
      - "trace_capture"
      - "test_execution"
      - "feedback_capture"

state:
  storage: "external"
  format: "semantic_json"

gates:
  enforcement: "runner_blocking"

trace:
  trace_source: "model_self_report"
  required: true
  level: "decision"

model:
  role: "semantic_executor"
  allowed_to:
    - "interpret_context"
    - "propose_state_update"
    - "generate_candidate_output"
    - "explain_reasoning_summary"
  not_allowed_to:
    - "override_blocking_gate"
    - "silently_change_state"
    - "skip_required_node"
```

У compiled IR це може бути представлено як набір операцій:

```json
[
  {
    "op": "RUNTIME.DEF",
    "runtime": "helper_runner",
    "responsibilities": [
      "state_management",
      "gate_enforcement",
      "trace_capture"
    ]
  },
  {
    "op": "STATE.EXTERNAL",
    "format": "semantic_json"
  },
  {
    "op": "GATE.ENFORCE",
    "mode": "runner_blocking"
  },
  {
    "op": "MODEL.ROLE",
    "role": "semantic_executor"
  }
]
```

## Важлива межа відповідальності

Helper-runner не повинен робити вигляд, що він сам розуміє весь зміст доменної задачі.

Наприклад, у History Event Playbook runner може знати:

```text
- які path-и існують;
- які gates треба пройти;
- які fields обов’язкові;
- який output не можна створювати раніше approval;
- які tests треба запустити.
```

Але модель усе ще потрібна для:

```text
- пояснення бізнесового сенсу;
- формування людського тексту;
- аналізу неоднозначних формулювань;
- пропозиції назв;
- формування документації;
- узагальнення feedback.
```

Тобто runner не замінює модель. Він обмежує й організовує її роботу.

![Nebu — подумати](../assets/mascots/64x64/Nebu_thinking_64x64.png)

## Малий приклад

Без helper-runner користувач пише:

```text
Створи нову історичну подію.
```

Модель сама має згадати весь playbook, вибрати path, поставити питання, не перейти далі, не створити пакет раніше часу.

З helper-runner процес виглядає інакше.

Runner створює run:

```json
{
  "run_id": "RUN-100",
  "current_node": "ENTRY_START",
  "state": {},
  "allowed_actions": ["classify_input", "ask_entry_question"]
}
```

Модель пропонує:

```json
{
  "proposed_action": "ask_question",
  "question": "Який тип зміни потрібно перетворити на історичну подію?"
}
```

Runner перевіряє, що це дозволена дія, і віддає питання користувачу.

Потім користувач відповідає. Runner оновлює state. Модель пропонує path. Runner перевіряє gates. І тільки тоді процес рухається далі.

У результаті модель не “веде весь процес у голові”. Вона працює крок за кроком у межах, які контролює runner.

## Чим helper-runner відрізняється від native Ordo

Helper-runner — це проміжний рівень.

Модель ще не підтримує Ordo нативно. Вона не має внутрішнього execution engine для Ordo. Але зовнішній runner допомагає їй виконувати Ordo-програму правильно.

Native Ordo означало б, що модель сама вміє:

```text
- розуміти Ordo IR;
- виконувати gates;
- вести state;
- повертати trace;
- працювати з tests;
- підтримувати libraries;
- пояснювати decisions у стандартному форматі.
```

Helper-runner робить частину цієї роботи зовні.

Тому можна сказати:

```text
Ordo без runtime — це дисциплінований prompt-based режим.
Ordo з helper-runner — це контрольований execution-assisted режим.
Native Ordo — це модель, яка сама підтримує Ordo як мову виконання.
```

## Коли helper-runner особливо потрібен

Helper-runner потрібен, коли:

```text
- процес має багато вузлів;
- gates мають бути blocking;
- є багато state transitions;
- є regression tests;
- потрібно підключати libraries;
- потрібно версіонувати domain packs;
- потрібен audit trail;
- є production outputs;
- помилка може дорого коштувати;
- декілька людей або моделей працюють з одним playbook-ом.
```

Особливо він корисний для playbook-ів, які поступово ростуть і стають занадто великими для надійного виконання через один довгий prompt.

## Типові помилки

Перша помилка — думати, що helper-runner має бути дуже складним із першої версії.

Ні. Мінімальний runner може робити тільки кілька речей:

```text
- зберігати state;
- знати current node;
- блокувати critical gates;
- писати trace;
- запускати прості tests.
```

Цього вже достатньо, щоб сильно покращити керованість.

Друга помилка — віддати runner-у семантичні рішення, які має приймати модель або людина.

Runner не повинен вигадувати бізнесовий сенс. Він має контролювати процес.

Третя помилка — дозволити моделі напряму змінювати state.

Правильніше:

```text
модель пропонує state update;
runner перевіряє;
runner застосовує або відхиляє.
```

Четверта помилка — не логувати відхилені дії.

Якщо модель спробувала перейти через gate, runner має записати це у trace. Інакше буде незрозуміло, чому процес був заблокований.

П’ята помилка — не пов’язати runner із improvement loop.

Якщо runner бачить повторювану проблему, це має ставати issue або improvement record.

## Міні-вправа

Уявіть, що у вас є Ordo-playbook для підготовки аналітичного пакета.

Опишіть мінімальний helper-runner для нього.

Вкажіть:

```text
- який state він має зберігати;
- які gates він має блокувати;
- які дії моделі дозволені;
- які дії моделі заборонені;
- який trace треба писати;
- які tests треба запускати;
- які user feedback потрібно перетворювати на improvement records.
```

Потім запитайте себе:

```text
Яка частина процесу має залишатися за моделлю?
Яка частина процесу має контролюватися runner-ом?
Яка частина процесу має вимагати людського підтвердження?
```

## Короткий підсумок

Ordo з helper-runner — це практичний середній рівень між prompt-based використанням і native Ordo support у моделях.

У цьому режимі модель залишається семантичним виконавцем, але runner контролює state, path-и, gates, trace, tests і feedback records.

Це різко підвищує надійність складних Ordo-програм. Особливо там, де важливо не просто отримати відповідь, а довести, що процес був виконаний правильно, перевірено і з можливістю подальшого покращення.

---
