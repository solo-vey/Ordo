# Додаток F. Практичний довідник op-кодів і YAML-атрибутів

Цей додаток доповнює короткий каталог op-кодів із додатка B. Там зручно швидко подивитися назви конструкцій. Тут інша мета: дати практичний довідник для людини, яка відкриває `*.ordo.yaml`, `program.ir.json` або намагається написати власний playbook.

Головне правило цього додатка:

```text
назва поля сама по собі ще нічого не пояснює;
для практичного використання треба знати тип поля, допустимі значення,
значення кожного варіанта і те, як поле читає compiler / runtime / validator.
```

Якщо значення поля є фіксованим enum, його не можна вигадувати довільно. Якщо значення є `convention string`, його можна вводити в межах пакета, але воно має бути описане в policy docs або package docs. Якщо значення є free text, воно допомагає людині й моделі, але не повинно використовуватися як deterministic runtime condition без окремого правила.

## F.1. Типи значень у YAML

Перед тим як читати окремі op-коди, треба розрізняти типи атрибутів.

### `strict enum`

Поле має закритий перелік дозволених значень.

Приклад:

```yaml
control_level: strict
```

Дозволені значення:

```text
light
standard
strict
```

Практичне правило: не додавайте нове значення без оновлення schema / compiler / validator. Якщо написати `very_strict`, людина може зрозуміти намір, але мова не зобов'язана це прийняти.

### `convention string`

Поле є рядком, але його значення має бути описане як домовленість пакета.

Приклад:

```yaml
resume_policy: return_to_current_node_after_deviation
```

Це не звичайний людський опис. Якщо runtime або AI-layer використовує це поле для поведінки, значення має бути пояснене в policy docs. Без цього воно перетворюється на магічний рядок.

### `free text`

Поле містить людський опис.

Приклад:

```yaml
description: "Користувач описує процес природною мовою."
```

Таке поле можна писати вільніше. Але compiler не має робити deterministic routing тільки на основі free text. Для routing потрібні gates, allowed answers, policies або інші структурні поля.

### `reference / id`

Поле посилається на інший об'єкт.

Приклад:

```yaml
entry: N_START
next: N_REVIEW
artifact: A_SUMMARY
```

Практичне правило: referenced id має існувати. Інакше граф може мати dead link.

### `path`

Поле містить шлях до файлу або шаблон шляху.

Приклад:

```yaml
path_pattern: "reports/{run_id}/summary.md"
```

Практичне правило: шлях не є просто текстом. Validator може перевіряти наявність файлу, розширення, формат або allowed output directory.

### `state selector`

Поле посилається на частину state.

Приклад:

```yaml
field: G_EVENT_IDENTITY_CONTRACT.alias
```

Практичне правило: selector має відповідати state schema або contract field. Інакше output може бути згенерований з неіснуючих даних.

---

## F.2. Program і metadata

### `PROGRAM.DEF` / верхній рівень програми

Призначення: описує програму як цілісний модуль: ідентичність, версію, сумісність і режим виконання.

Де живе: верхній рівень source YAML або header semantic JSON IR.

Поля:

```text
program_id / id
  required: yes
  type: id string
  meaning: стабільний ідентифікатор програми або модуля.
  example: ordo.applied_project_factory

ordo_version
  required: yes
  type: version string
  meaning: версія мовного пакета Ordo, з якою сумісна програма.
  example: "0.12"

control_level
  required: yes
  type: strict enum
  values: light, standard, strict
  meaning: рівень дисципліни runtime / validation.

execution_mode
  required: yes
  type: strict enum
  values: full_runtime, chat_internal, freeform_only
  meaning: спосіб виконання програми.

version
  required: recommended
  type: version string
  meaning: версія самого прикладного модуля.

module_id
  required: recommended for packages
  type: id string
  meaning: package/module identity у standard applied modules.

compatibility
  required: recommended
  type: object / freeform policy
  meaning: додаткові обмеження сумісності з runtime, CLI або schema.
```

Мінімальний приклад:

```yaml
program_id: ordo.applied_project_factory
ordo_version: "0.12"
control_level: standard
execution_mode: full_runtime
version: "0.1.0-rc.1"
```

Типова помилка: вказати `version` модуля, але не вказати `ordo_version` або `execution_mode`. Тоді незрозуміло, яким runtime-профілем це виконувати.

### `control_level`

Тип: strict enum.

Дозволені значення:

```text
light
  Мінімальна дисципліна. Добре для ранніх чернеток, але слабше для audit / handoff.

standard
  Нормальний режим для більшості прикладних процесів.

strict
  Найжорсткіший режим. Потрібен там, де важливі gates, trace, validation і release discipline.
```

Як це читає runtime: рівень контролю може впливати на те, чи дозволені freeform-відхилення, чи обов'язкові gates, наскільки суворо трактуються warnings.

Типова помилка: поставити `strict`, але залишити ключові рішення без gates або без confirmed state.

### `execution_mode`

Тип: strict enum.

Дозволені значення:

```text
full_runtime
  Очікується повний runtime / CLI-guided execution.

chat_internal
  Процес може виконуватися як дисциплінований чат із внутрішнім state.

freeform_only
  Структура мінімальна. Підходить для чернеток, але не для release-grade процесів.
```

Як це читає compiler/runtime: визначає очікувану форму виконання і набір обов'язкових артефактів. `full_runtime` має мати entry point, nodes, gates, state і validation artifacts.

---

## F.3. Interaction, Process Rail і conversation semantics

### `INTERACTION.MODEL`

Призначення: описує ролі людини, AI-моделі та deterministic helper/CLI layer.

Де живе: runtime model docs, IR ops або package policy.

Поля:

```text
op
  required: yes in IR ops
  type: strict opcode string
  value: INTERACTION.MODEL

id
  required: yes
  type: id string
  meaning: ідентифікатор interaction model.

roles / interaction_roles
  required: yes
  type: object
  meaning: хто за що відповідає.

raw_tool_output_policy
  required: recommended
  type: convention string / enum-like string
  common values: summarize_for_human, hide_raw_output, expose_on_request
  meaning: чи показувати користувачу сирий output tools або людське пояснення.

human_responsibility
  required: recommended
  type: free text / list
  meaning: рішення, які має підтвердити людина.

ai_responsibility
  required: recommended
  type: free text / list
  meaning: що може робити модель: вести процес, пояснювати, пропонувати next step.

cli_responsibility
  required: recommended
  type: free text / list
  meaning: deterministic checks, validation, compile, tests.
```

Приклад:

```yaml
op: INTERACTION.MODEL
id: interaction_model
roles:
  human: confirms_content_decisions
  ai: guided_process_driver
  cli: deterministic_validator
raw_tool_output_policy: summarize_for_human
```

Типова помилка: дозволити AI самостійно приймати змістові рішення, які мають бути confirmed by human.

### `PROCESS_RAIL.DEF` / `process_rail`

Призначення: задає дисципліну руху по процесу: чи можна відхилятися, як повертатися, чи дозволений backtracking.

Де живе: `process_rail` у semantic JSON IR або окрема op-операція.

Поля:

```text
rail_id
  required: recommended
  type: id string
  meaning: ідентифікатор rail policy.

state_tracking
  required: recommended
  type: strict enum
  values:
    required: runtime має вести state явно.
    optional: state може бути частковим або допоміжним.

allow_deviation
  required: recommended
  type: boolean
  meaning: чи може користувач тимчасово відійти від поточного node.

require_resume_after_deviation
  required: recommended
  type: boolean
  meaning: чи треба повернути користувача до перерваного node після відхилення.

backtracking
  required: recommended
  type: strict enum
  values:
    enabled: назад можна повертатися.
    disabled: назад повертатися не можна.
    restricted: назад можна, але за правилами invalidation / review.
```

Приклад:

```yaml
process_rail:
  rail_id: guided_intake_rail
  state_tracking: required
  allow_deviation: true
  require_resume_after_deviation: true
  backtracking: restricted
```

Типова помилка: дозволити backtracking, але не описати, які dependent state fields треба скидати або переглядати.

### `CONVERSATION.SEMANTICS`

Призначення: описує, як класифікувати людський ввід під час виконання процесу: відповідь на поточний node, уточнення, відхилення, повернення назад, нову вимогу.

Де живе: `conversation_semantics` у IR або runtime policy docs.

Поля:

```text
input_classes
  required: yes
  type: list[enum-like string]
  meaning: класи людського вводу, які runtime / AI-layer має розрізняти.

routing_rules
  required: yes
  type: map[input_class -> action]
  meaning: що робити після класифікації вводу.

unmatched_input_policy
  required: recommended
  type: strict/convention enum
  meaning: що робити, якщо ввід не можна класифікувати безпечно.

clarification_policy
  required: recommended
  type: object / convention string
  meaning: як просити уточнення без зміни state.

resume_policy
  required: recommended when deviations allowed
  type: convention string
  meaning: як повертатися до основного процесу після відхилення.
```

Типові `input_classes`:

```text
answer_current_node
  Користувач відповідає на поточне питання. Може змінювати state і routing.

clarification
  Користувач просить пояснення. State не повинен змінюватися без нової відповіді.

deviation
  Користувач тимчасово відходить від головного маршруту. Потрібен resume policy.

backtrack_request
  Користувач просить повернутися до попереднього кроку. Потрібна policy invalidation.

new_requirement
  Користувач додає нову вимогу. Не можна мовчки записувати її як confirmed state без review.
```

Типові `unmatched_input_policy`:

```text
clarify_before_state_change
  Не змінювати state, поки ввід не класифіковано.

reject
  Відхилити ввід як несумісний із поточним node.

log_and_continue
  Зафіксувати ввід, але не змінювати routing.
```

Приклад:

```yaml
conversation_semantics:
  input_classes:
    - answer_current_node
    - clarification
    - deviation
    - backtrack_request
  routing_rules:
    answer_current_node: evaluate_current_node_answer
    clarification: answer_without_state_change
    deviation: handle_deviation_then_resume
    backtrack_request: invoke_backtracking_policy
  unmatched_input_policy: clarify_before_state_change
  resume_policy: return_to_current_node_after_deviation
```

Типова помилка: трактувати будь-яку фразу користувача як відповідь на поточний node. Це швидко ламає state і пропускає clarification / deviation.

### `HYBRID_EXECUTION.MODEL`

Призначення: описує гібридну модель, де AI веде процес, а CLI/helper runtime виконує deterministic checks.

Поля:

```text
ai_layer
  type: convention string
  meaning: роль AI: guided_process_driver, reviewer, explainer.

cli_layer
  type: convention string
  meaning: роль CLI: deterministic_validator, compiler, artifact_checker.

deterministic_commands
  type: list[string]
  meaning: команди, які не має імітувати модель, а треба реально запускати.

human_review_points
  type: list[id/string]
  meaning: місця, де потрібне підтвердження людини.
```

Приклад:

```yaml
op: HYBRID_EXECUTION.MODEL
id: hybrid_execution
ai_layer: guided_process_driver
cli_layer: deterministic_validator
deterministic_commands:
  - lint
  - compile
  - test
  - validate-output
human_review_points:
  - approve_contract
  - approve_output_template
```

Типова помилка: описати CLI checks у тексті, але дозволити моделі “сказати, що перевірка пройдена” без реального tool/runtime evidence.

---

## F.4. Intent, Contract, Context

### `INTENT.DEF`

Призначення: фіксує, чого користувач хоче досягти.

Поля:

```text
id
  required: yes
  type: id string

goal
  required: yes
  type: free text
  meaning: людський опис мети.

scope
  required: recommended
  type: free text / list
  meaning: що входить у задачу.

out_of_scope
  required: recommended
  type: free text / list
  meaning: що не входить у задачу.

success_criteria
  required: recommended
  type: list[string]
  meaning: критерії, за якими людина погодить результат.
```

Приклад:

```yaml
op: INTENT.DEF
id: intent_create_playbook
goal: "Створити playbook для керованого intake процесу."
scope:
  - decision_tree
  - output_templates
out_of_scope:
  - production API integration
success_criteria:
  - "дерево має entry point і terminal paths"
  - "кожен terminal path має output decision"
```

Типова помилка: змішати `goal` і `success_criteria`. Goal пояснює напрям, success criteria дають перевірку.

### `CONTRACT.DEF` / `CONTRACT.INSTANCE`

Призначення: перетворює очікуваний результат на перевірюваний контракт із полями та статусами.

Де живе: `contracts` у IR або op-операція.

Поля:

```text
kind
  required in schema object
  type: const
  value: contract

id
  required: yes
  type: id string

status
  required: yes
  type: strict enum
  values: missing, candidate, proposed, confirmed, blocked, not_applicable

fields
  required: yes
  type: map[field_name -> field_object]
```

Статуси contract / field:

```text
missing
  Поле потрібне, але значення ще немає.

candidate
  Є можливе значення, але воно ще слабке.

proposed
  Значення запропоноване й чекає review.

confirmed
  Значення підтверджене і може використовуватись у output / validation.

blocked
  Поле не може бути завершене через проблему або зовнішню залежність.

not_applicable
  Поле явно не застосовується в цьому сценарії.
```

Приклад:

```yaml
contracts:
  - kind: contract
    id: project_intent_contract
    status: proposed
    fields:
      project_goal:
        value: "Створити applied module для формування playbook-ів."
        status: confirmed
        required: true
      runtime_entry:
        status: missing
        required: true
        description: "Entry point ще не погоджено."
```

Як це читає validator: confirmed contract fields можуть ставати вимогами до artifacts. `missing` або `blocked` можуть створювати warnings або no-go залежно від coverage policy.

Типова помилка: підставити `candidate` поле в фінальний output як підтверджене.

### `CONTEXT.DEF`

Призначення: описує, які джерела, обмеження й попередні рішення доступні процесу.

Поля:

```text
id
  required: yes
  type: id string

sources
  required: recommended
  type: list[path/reference/free text]
  meaning: документи, файли, попередні рішення.

constraints
  required: recommended
  type: list[string]
  meaning: обмеження, які треба врахувати.

assumptions
  required: optional
  type: list[string]
  meaning: припущення; не дорівнюють confirmed facts.
```

Типова помилка: записати припущення в context так, ніби воно вже підтверджений contract field.

---

## F.5. State і зміни стану

### `STATE.SCHEMA`

Призначення: описує, які поля state існують, які з них required, які мають типи, default або status.

Поля:

```text
id
  required: yes
  type: id string

fields
  required: yes
  type: map[field_name -> field_definition]

field.type
  required: recommended
  type: convention/JSON type
  examples: string, boolean, list, object, enum, path, reference

field.required
  required: recommended
  type: boolean

field.default
  required: optional
  type: any

field.allowed_values
  required: only for enum-like fields
  type: list[string]

field.description
  required: recommended
  type: free text
```

Приклад:

```yaml
op: STATE.SCHEMA
id: intake_state_schema
fields:
  current_node:
    type: reference
    required: true
    description: "Поточний node процесу."
  user_goal:
    type: string
    required: true
  terminal_path_ready:
    type: boolean
    default: false
  output_template_status:
    type: enum
    allowed_values:
      - missing
      - draft
      - reviewed
      - approved
```

Типова помилка: використовувати поле в gates або templates, але не описати його в state schema.

### `STATE.SNAPSHOT`

Призначення: фіксує стан на конкретному кроці виконання.

Поля:

```text
run_id
  type: id string

step_id
  type: id/reference

state
  type: object
  meaning: повний або частковий state snapshot.

source
  type: enum/convention
  examples: runtime_enforced, model_self_report, hybrid
```

Приклад:

```yaml
op: STATE.SNAPSHOT
id: snapshot_after_node_review
run_id: run_001
step_id: N_NODE_REVIEW
state:
  current_node: N_NODE_REVIEW
  node_review_status: approved
source: runtime_enforced
```

Типова помилка: використовувати snapshot як доказ виконання, хоча його source = model_self_report без runtime evidence.

### `STATE.DIFF`

Призначення: показує, що саме змінилося між двома станами.

Поля:

```text
before / after
  type: reference або object
  meaning: попередній і новий state.

changes
  type: list[change]
  meaning: список змінених полів.

change.field
  type: state selector

change.from / change.to
  type: any

reason
  type: free text / convention string
```

Приклад:

```yaml
op: STATE.DIFF
id: diff_after_output_binding
changes:
  - field: terminal_output_binding_status
    from: missing
    to: confirmed
    reason: user_approved_output_template
```

Типова помилка: змінювати state після clarification, хоча clarification не мала підтвердити нове значення.

---

## F.6. Entry, Node, Path і routing

### `ENTRY.DEF`

Призначення: визначає, з якого node або subflow починається програма.

Поля:

```text
id
  required: yes
  type: id string

start_node / entry_node
  required: yes
  type: reference
  meaning: id node, з якого починається execution.

initial_state
  required: optional
  type: object
  meaning: стартові значення state.
```

Приклад:

```yaml
op: ENTRY.DEF
id: main_entry
start_node: N_FACTORY_MODE_SELECTION
initial_state:
  terminal_path_ready: false
```

Типова помилка: мати nodes, але не мати entry point.

### `NODE.DEF`

Призначення: описує питання, дію або review point у процесі.

Зафіксовані schema-поля:

```text
id
  required: yes
  type: id string

question
  required: yes
  type: free text
  meaning: питання або інструкція, яку бачить користувач / AI.

allowed_answers
  required: optional but recommended for deterministic nodes
  type: list[string]
  meaning: допустимі відповіді.

on_unmatched_input.action
  required: optional
  type: strict enum
  values: CLARIFY.REQUEST, escalate_to_human, block

on_unmatched_input.strategy
  required: optional
  type: strict enum
  values: rephrase_and_narrow, ask_for_exact_choice, explain_allowed_answers

on_unmatched_input.max_attempts
  required: optional
  type: integer

unmatched_policy
  required: optional
  type: strict enum
  values: handled, impossible_by_source
```

Значення `on_unmatched_input.action`:

```text
CLARIFY.REQUEST
  Попросити уточнення без зміни state.

escalate_to_human
  Передати рішення людині або зупинити автоматичне routing.

block
  Заблокувати рух далі, поки ввід не стане сумісним із node.
```

Значення `on_unmatched_input.strategy`:

```text
rephrase_and_narrow
  Переформулювати питання і звузити варіанти.

ask_for_exact_choice
  Попросити вибрати один із allowed_answers.

explain_allowed_answers
  Пояснити, що означає кожен дозволений варіант.
```

Приклад:

```yaml
nodes:
  - id: N_FACTORY_MODE_SELECTION
    question: "Яким способом створюємо процес?"
    allowed_answers:
      - domain_model_and_decision_tree
      - manual_decision_tree
      - free_dialogue
      - improve_existing_process
    on_unmatched_input:
      action: CLARIFY.REQUEST
      strategy: ask_for_exact_choice
      max_attempts: 2
    unmatched_policy: handled
```

Типова помилка: залишити `allowed_answers` порожнім там, де наступний крок має бути deterministic.

### `PATH.DEF`

Призначення: описує послідовність node/steps або terminal path.

Поля:

```text
id
  required: yes
  type: id string

steps
  required: yes
  type: list[reference]
  meaning: node або step ids у порядку проходження.

terminal
  required: optional
  type: boolean
  meaning: чи завершується шлях.

expected_output
  required: recommended for terminal path
  type: reference/list[reference]
  meaning: artifact або output binding.
```

Типова помилка: назвати шлях terminal, але не визначити expected output або явне рішення `no output required`.

### `CLARIFY.REQUEST`

Призначення: контрольоване уточнення, коли ввід не можна безпечно класифікувати.

Поля:

```text
id
  type: id string

question
  type: free text
  meaning: уточнення до користувача.

allowed_answers
  type: list[string]
  meaning: якщо уточнення має обмежені варіанти.

state_change_allowed
  type: boolean
  recommended value: false
```

Приклад:

```yaml
op: CLARIFY.REQUEST
id: clarify_factory_mode
question: "Виберіть один із чотирьох режимів створення процесу."
allowed_answers:
  - domain_model_and_decision_tree
  - manual_decision_tree
  - free_dialogue
  - improve_existing_process
state_change_allowed: false
```

Типова помилка: під час clarification змінити state так, ніби користувач уже дав відповідь на node.

---

## F.7. Gates і assertions

### `GATE.DEF`

Призначення: контрольна точка, яка вирішує, чи можна рухатися далі.

Зафіксовані schema-поля:

```text
id
  required: yes
  type: id string

method
  required: yes
  type: strict enum
  values: mechanical, self_verification, self_consistency, human

trust_class
  required: yes
  type: strict enum
  values: deterministic, model_judgment, repeated_model_judgment, human_decision

assert
  required: yes
  type: expression/free text condition
  meaning: що саме перевіряється.

source
  required: optional
  type: reference/path/free text

params
  required: optional
  type: object

protocol
  required: optional
  type: list[string]

on_fail / on_pass
  required: optional
  type: reference/action convention
```

Значення `method`:

```text
mechanical
  Перевірка виконується deterministic способом: schema, script, file check, compiler.

self_verification
  Модель сама перевіряє відповідь. Слабший рівень довіри.

self_consistency
  Модель або кілька проходів порівнюються між собою.

human
  Рішення приймає людина.
```

Значення `trust_class`:

```text
deterministic
  Можна відтворити через tool/runtime/compiler.

model_judgment
  Це оцінка моделі, не абсолютний доказ.

repeated_model_judgment
  Посилене model judgment через повторення / порівняння.

human_decision
  Підтверджено людиною.
```

Приклад:

```yaml
gates:
  - id: G_TEMPLATE_REVIEWED
    method: human
    trust_class: human_decision
    assert: "Користувач переглянув приклад заповненого шаблону."
    on_fail: N_TEMPLATE_REVIEW
    on_pass: N_TERMINAL_READY_CHECK
```

Типова помилка: поставити `trust_class: deterministic` для перевірки, яку фактично зробила модель словами.

### `GATE.CHECK`

Призначення: результат виконання gate.

Поля:

```text
gate
  required: yes
  type: reference
  meaning: id gate, який перевіряли.

result
  required: yes
  type: enum/convention
  common values: pass, fail, blocked, warning

evidence
  required: recommended
  type: path/reference/free text
  meaning: чим підтверджено результат.
```

Типова помилка: мати gate definition, але не мати gate result у trace/report.

### `ASSERTION.DEF`

Призначення: стабільна перевірка умови, яка може проєктуватися в runtime/test/debug.

Schema-поля:

```text
id
  required: yes
  type: id string

polarity
  required: yes
  type: strict enum
  values: must, not

condition
  required: yes
  type: expression/free text condition

phase
  required: yes
  type: list[enum]
  values: runtime, test, debug

severity
  required: yes
  type: strict enum
  values: block, warn, info

on_fail
  required: optional
  type: action/reference

message
  required: optional
  type: free text
```

Значення `polarity`:

```text
must
  Умова має виконуватися.

not
  Умова не повинна відбуватися. Це канонічна форма негативної перевірки.
```

Значення `severity`:

```text
block
  Порушення блокує подальше виконання або release.

warn
  Порушення не блокує, але має бути видиме.

info
  Інформаційне повідомлення.
```

Приклад:

```yaml
assertions:
  - id: A_NO_TERMINAL_WITHOUT_OUTPUT_DECISION
    polarity: not
    condition: "terminal_path_ready == true and selected_terminal_outputs is missing"
    phase:
      - runtime
      - test
    severity: block
    message: "Terminal path cannot be ready without output decision."
```

Типова помилка: писати негативну перевірку тільки в тексті, але не робити її assertion.

---

## F.8. Output, artifact і template layer

### `OUTPUT.DEF`

Призначення: описує, який результат може створити процес.

Поля:

```text
id
  required: yes
  type: id string

type
  required: recommended
  type: convention/enum-like string
  examples: document, report, yaml_package, runtime_package, no_output_required

artifact
  required: recommended when output creates file
  type: reference

template
  required: recommended when rendered
  type: reference/path

status
  required: recommended
  type: convention enum
  examples: missing, draft, reviewed, approved, not_applicable
```

Приклад:

```yaml
outputs:
  - id: O_RUNTIME_PACKAGE
    type: runtime_package
    artifact: A_RUNTIME_ZIP
    template: T_RUNTIME_PACKAGE_README
    status: approved
```

Типова помилка: terminal path вказує на output, але output не має artifact або template review status.

### `ARTIFACT.DEF` / `Artifact`

Schema-поля:

```text
kind
  required: yes
  type: const
  value: artifact

id
  required: yes
  type: id string

path_pattern
  required: yes
  type: path pattern

format
  required: yes
  type: strict enum
  values: markdown, json, yaml, text, other

required
  required: optional
  type: boolean

description
  required: optional
  type: free text
```

Приклад:

```yaml
artifacts:
  - kind: artifact
    id: A_VALIDATION_REPORT
    path_pattern: "reports/{run_id}/VALIDATION_REPORT.json"
    format: json
    required: true
    description: "Machine-readable validation result."
```

Типова помилка: назвати artifact required, але не мати coverage rule або rendered artifact assertion.

### `ARTIFACT.REQUIREMENT`

Призначення: зв'язує confirmed contract fields із required artifacts.

Schema-поля:

```text
kind
  required: yes
  value: artifact_requirement

id
  required: yes
  type: id string

when.contract
  required: yes
  type: contract reference

when.status
  required: yes
  type: strict enum
  values: missing, candidate, proposed, confirmed, blocked, not_applicable

requires
  required: yes
  type: list[requirement]

requires[].artifact
  required: yes
  type: artifact reference

requires[].must_include_fields
  required: optional
  type: list[state/contract selectors]

requires[].must_include_sections
  required: optional
  type: list[string]

requires[].forbidden_sections
  required: optional
  type: list[string]
```

Приклад:

```yaml
artifact_requirements:
  - kind: artifact_requirement
    id: R_CONTRACT_TO_REPORT
    when:
      contract: project_intent_contract
      status: confirmed
    requires:
      - artifact: A_VALIDATION_REPORT
        must_include_fields:
          - project_intent_contract.fields.project_goal
        must_include_sections:
          - validation_summary
```

Типова помилка: confirmed contract fields існують, але жоден artifact не зобов'язаний їх містити.

### `RenderingTemplate` / `OUTPUT.TEMPLATE`

Schema-поля:

```text
id
  required: yes
  type: id string

type
  required: optional
  type: convention string

format
  required: optional
  type: strict enum
  values: markdown, json, yaml, text

path
  required: optional
  type: path

template
  required: yes
  type: path or inline template string

render_mode
  required: yes
  type: strict enum
  values: deterministic, model_assisted

renderer
  required: yes
  type: strict enum
  values: ordo.simple, ai.markdown, ai.yaml, ai.json

requires_model_rendering
  required: optional
  type: boolean

validation
  required: optional
  type: strict enum
  value: strict_confirmed_state_only

tbd_policy
  required: optional
  type: strict enum
  value: preserve_tbd_until_confirmed

explicit_tbd_defaults
  required: optional
  type: list[string]

forbidden_inference_rules
  required: optional
  type: list[string]

forbidden_unconfirmed_terms
  required: optional
  type: list[string]
```

Значення `render_mode`:

```text
deterministic
  Шаблон рендериться без творчої інтерпретації моделі.

model_assisted
  Модель може допомагати з формулюванням, але має отримати handoff packet і validation constraints.
```

Значення `renderer`:

```text
ordo.simple
  Простий deterministic renderer для контрольованих підстановок.

ai.markdown
  Модель допомагає створювати markdown artifact.

ai.yaml
  Модель допомагає створювати YAML artifact.

ai.json
  Модель допомагає створювати JSON artifact.
```

Приклад:

```yaml
rendering_templates:
  - id: T_SUMMARY
    format: markdown
    path: output_templates/summary.md
    template: output_templates/summary.md
    render_mode: deterministic
    renderer: ordo.simple
    validation: strict_confirmed_state_only
    tbd_policy: preserve_tbd_until_confirmed
```

Типова помилка: використовувати `model_assisted`, але не заборонити моделі вигадувати missing fields.

### `TEMPLATE.MOCK_RENDER`

Статус: validation/review pattern, не обов'язковий core opcode у поточній лінії.

Призначення: показати користувачу приклад заповненого шаблону до release/handoff.

Практичні поля:

```text
template
  type: template reference

mock_state
  type: object/path

output_path
  type: path

review_status
  type: convention enum
  suggested values: generated, reviewed, approved, rejected

reviewer
  type: human/model reference
```

Типова помилка: вважати шаблон погодженим, якщо користувач бачив тільки порожню структуру, але не бачив mock-rendered example.

---

## F.9. Validation, coverage і go/no-go

### `COVERAGE.RULE`

Schema-поля:

```text
kind
  required: yes
  value: coverage_rule

id
  required: yes
  type: id string

input
  required: yes
  type: strict enum
  values: confirmed_contracts, all_contracts, rendered_artifacts

output
  required: yes
  type: strict enum
  values: artifact_requirements, consistency_report, go_no_go

failure_policy
  required: yes
  type: strict enum
  values: warn, fail, no_go

description
  required: optional
  type: free text
```

Значення `failure_policy`:

```text
warn
  Показати попередження, але не блокувати.

fail
  Вважати validation failed.

no_go
  Перетворити проблему на no-go decision.
```

Приклад:

```yaml
coverage_rules:
  - kind: coverage_rule
    id: C_CONFIRMED_CONTRACTS_TO_ARTIFACTS
    input: confirmed_contracts
    output: artifact_requirements
    failure_policy: no_go
```

### `RENDERED_ARTIFACT.ASSERT`

Schema-поля:

```text
kind
  required: yes
  value: rendered_artifact_assertion

id
  required: yes
  type: id string

field
  required: yes
  type: contract/state selector

must_appear_in
  required: yes
  type: list[artifact reference/path]

severity
  required: optional
  type: strict enum
  values: block, warn, info

message
  required: optional
  type: free text
```

Приклад:

```yaml
rendered_artifact_assertions:
  - kind: rendered_artifact_assertion
    id: A_PROJECT_GOAL_VISIBLE
    field: project_intent_contract.fields.project_goal
    must_appear_in:
      - A_SUMMARY_REPORT
    severity: block
```

### `GO_NO_GO.DECISION`

Schema-поля:

```text
kind
  required: yes
  value: go_no_go

status
  required: yes
  type: strict enum
  values:
    go
    no_go_requires_confirmation
    no_go_requires_artifact_fix
    no_go_requires_template_fix
    no_go_requires_runner_contract

blocking_issues
  required: yes
  type: list[issue]

warnings
  required: yes
  type: list[warning]
```

Значення `status`:

```text
go
  Можна передавати далі.

no_go_requires_confirmation
  Потрібне людське підтвердження.

no_go_requires_artifact_fix
  Треба виправити artifacts.

no_go_requires_template_fix
  Треба виправити templates.

no_go_requires_runner_contract
  Треба виправити runtime/runner contract.
```

Приклад:

```yaml
go_no_go:
  kind: go_no_go
  status: go
  blocking_issues: []
  warnings:
    - code: consistency_contract_defaults
      message: "Default-value coverage warning remains visible."
```

Типова помилка: приховати warnings, якщо статус `go`. У Ordo warning не блокує, але має залишатися видимим.

---

## F.10. Trace, debug і replay

### `TRACE.LOG` / `Trace`

Schema-поля:

```text
run_id
  required: yes
  type: id string

execution_mode
  required: yes
  type: strict enum
  values: full_runtime, chat_internal, freeform_only

trace_source
  required: yes
  type: strict enum
  values: model_self_report, runtime_enforced, hybrid

selected_path
  required: optional
  type: object

rejected_paths
  required: optional
  type: array

decision_log
  required: optional
  type: array

state_snapshots
  required: optional
  type: array

state_diffs
  required: optional
  type: array

gate_report
  required: optional
  type: array

warnings / violations
  required: optional
  type: array
```

Значення `trace_source`:

```text
model_self_report
  Модель описала, що вона зробила. Це корисно, але слабше за runtime evidence.

runtime_enforced
  Trace створений або перевірений runtime/CLI.

hybrid
  Комбінація AI-led execution і deterministic helper evidence.
```

Приклад:

```yaml
run_id: run_001
execution_mode: full_runtime
trace_source: hybrid
selected_path:
  terminal_node: N_FINAL_HANDOFF
state_diffs:
  - field: go_no_go.status
    from: no_go_requires_template_fix
    to: go
warnings: []
violations: []
```

Типова помилка: приймати `model_self_report` як повний proof program без deterministic evidence.

### `DECISION.LOG`

Призначення: записує, чому було прийнято конкретне рішення.

Поля:

```text
decision_id
  type: id string

node
  type: node reference

selected_option
  type: enum/reference/string

rejected_options
  type: list[string]

reason
  type: free text

evidence
  type: path/reference/free text
```

### `PATH.EXPLAIN`

Призначення: пояснює, чому обрано один path, а не інші.

Поля:

```text
current_node
  type: reference

selected_path
  type: reference

rejected_paths
  type: list[reference]

gates_used
  type: list[gate reference]

human_readable_explanation
  type: free text
```

---

## F.11. Tests, fixtures і regression

### `TEST.DEF`

Призначення: описує один тестовий сценарій.

Практичні поля:

```text
id
  required: yes
  type: id string

title
  required: recommended
  type: free text

fixture
  required: recommended
  type: fixture reference

steps
  required: recommended
  type: list[step]

expected_path / expected_state / expected_output / expected_gate
  required: recommended
  type: expectation object/reference
```

Приклад:

```yaml
op: TEST.DEF
id: T_FREE_DIALOGUE_TO_DRAFT_TREE
title: "Free dialogue produces draft tree before YAML generation"
fixture: F_FREE_DIALOGUE_INPUT
expected_path: P_FREE_DIALOGUE_REVIEW
expected_state:
  draft_subtree_status: proposed
```

### `FIXTURE.DEF`

Призначення: задає вхідні дані для тесту.

Поля:

```text
id
  type: id string

input
  type: object / text / path

initial_state
  type: object

expected_contracts
  type: object/list
```

### `EXPECT.*`

Призначення: очікуваний path, state, output або gate result.

Практичні поля:

```text
EXPECT.PATH
  selected_path, terminal_node, forbidden_nodes

EXPECT.STATE
  field, expected_value, status

EXPECT.OUTPUT
  artifact, must_exist, must_include, must_not_include

EXPECT.GATE
  gate, expected_result, severity
```

Типова помилка: тестувати лише final output і не тестувати path/state, через що runtime може пройти неправильним маршрутом, але все одно створити схожий документ.

---

## F.12. Libraries, freeform і improvement records

### `LIB.INCLUDE`

Schema-поля:

```text
library
  required: yes
  type: library id/path

version
  required: yes
  type: semver requirement

as
  required: optional
  type: namespace alias

exports
  required: optional
  type: list[string]
```

Приклад:

```yaml
libraries:
  - library: standard_review_patterns
    version: ">=0.1.0"
    as: review
    exports:
      - NODE.REVIEW
      - BRANCH.REVIEW
```

Типова помилка: імпортувати library без namespace і отримати конфлікт локальних ids.

### `FREEFORM.DEF`

Schema-поля:

```text
id
  required: yes
  type: id string

role
  required: yes
  type: strict enum
  values: domain_explanation, example, warning, template_note, edge_case_note

binding
  required: optional
  type: reference/string

maturity
  required: optional
  type: strict enum
  values: stable, volatile, candidate_for_formalization

incident_count
  required: optional
  type: integer >= 0

incident_threshold
  required: optional
  type: integer >= 1
```

Значення `maturity`:

```text
stable
  Freeform блок прийнятий як пояснювальний текст.

volatile
  Блок часто змінюється або містить нестабільну логіку.

candidate_for_formalization
  Блок треба винести в формальну конструкцію, якщо він впливає на execution.
```

Типова помилка: ховати gate або routing rule у freeform-тексті.

### `IMPROVEMENT.RECORD`

Schema-поля:

```text
id
  required: yes
  type: id string

type
  required: yes
  type: convention string
  examples: missed_required_gate, node_coverage_gap, freeform_overuse

severity
  required: yes
  type: strict enum
  values: low, medium, high, critical

affected_unit.id
  required: yes
  type: reference

affected_unit.kind
  required: yes
  type: strict enum
  values: gate, assertion, node, freeform, library, domain_pack, profile, compiler_rule

root_cause_hypothesis
  required: optional
  type: array

proposed_patch
  required: optional
  type: array

suggested_tests
  required: optional
  type: array

approval
  required: yes
  type: object
```

Типова помилка: записати improvement як коментар у тексті, але не прив'язати його до affected unit і approval status.

---

## F.13. APF-патерни, які ще не треба робити core opcodes

У M63 APF став standard applied module, але його патерни не треба автоматично піднімати в core runtime / IR. Їх треба читати так:

```text
APF-local pattern
  працює в межах APF або standard applied module docs.

reusable applied-module pattern
  може повторюватися в інших пакетах, але ще не є core opcode.

future IR candidate
  потребує окремого design milestone, schema і validator semantics.
```

### `INPUT.POLICY`

Класифікація: schema pattern або APF subflow.

Поля, які варто описувати:

```text
required_input_artifacts
optional_input_artifacts
input_unknown_or_deferred
missing_input_policy
```

Статус: usable in APF; candidate for future generic schema support.

### `TERMINAL.OUTPUT.BIND`

Класифікація: APF subflow / possible future IR concept.

Практичні поля:

```text
terminal_node
selected_outputs
output_template_status
mock_filled_example_status
required_state_fields
user_review_status
terminal_path_ready
```

Статус: keep APF-local for rc.1.

Типова помилка: вважати terminal path готовим тільки тому, що дерево дійшло до кінця. У APF terminal path готовий тільки після output/template decision.

### `TREE.AUTHOR.PROGRESSIVE`

Класифікація: APF workflow pattern.

Практичні поля:

```text
user_tree_vision_depth
draft_subtree_status
draft_nodes
draft_branches
terminal_candidates
open_questions
```

Статус: reusable applied-module pattern, not core opcode yet.

### `NODE.REVIEW`, `BRANCH.REVIEW`, `SUBTREE.REVIEW`

Класифікація: applied-module review patterns.

Практичні поля:

```text
review_target
review_status
reviewer
approved_fields
open_questions
required_changes
next_step_decision
```

Типові `review_status`:

```text
draft
proposed
approved
needs_changes
deferred
```

Статус: document and test in APF; future generic review layer candidate.

### `TREE.NORMALIZE`

Класифікація: adapter pattern.

Призначення: перетворити ручний або вільний опис дерева в нормалізовану структуру nodes/branches/gates.

Статус: APF-local; useful for future import utilities.

### `DIALOGUE.EXTRACT`

Класифікація: AI-assisted extraction pattern.

Призначення: витягнути з вільного діалогу candidate nodes, branches, outputs, assumptions і open questions.

Статус: APF-local; do not make deterministic opcode yet.

### `TEMPLATE.RECIPE`

Класифікація: template authoring pattern.

Призначення: описати, як створюється output template: секції, required fields, TBD policy, forbidden inference.

Статус: strong candidate for standard template-layer docs.

### `VALIDATION.HANDOFF.TAIL`

Класифікація: reusable applied-module tail.

Призначення: спільний фінальний шлях: minimal validation, full validation, review, fix loop, go/no-go, package handoff.

Статус: document as standard pattern; do not hardcode into core.

### `FLOW.JOIN` і `SHARED.TAIL.REFERENCE`

Класифікація: future IR candidates.

Чому не core зараз:

```text
current YAML can express joins by repeated target ids,
but reusable shared-tail references need stable semantics:
- як перевіряти входи в shared tail;
- як зберігати trace;
- як рахувати coverage;
- як пояснювати path;
- як уникати циклів і прихованих переходів.
```

Статус: backlog.

---

## F.14. Практичне правило для автора YAML

Перед тим як додати нове поле в YAML, поставте три питання:

```text
1. Це поле читає compiler/runtime/validator?
   Якщо так — потрібен тип, allowed values і schema/policy.

2. Це поле є домовленістю пакета?
   Якщо так — потрібне пояснення в package docs.

3. Це лише пояснення для людини?
   Якщо так — не використовуйте його як deterministic condition.
```

Коротка формула:

```text
enum = контракт;
convention string = домовленість, яку треба описати;
free text = пояснення, а не runtime-доказ.
```

Саме це розрізнення робить Ordo-процес не просто красивим YAML, а практично виконуваною мовою керованих процесів.


## `execution_trace`

Top-level core block для повної історії виконання. Основні атрибути: `id`, `version`, `run`, `status`, `started_at`, `finished_at`, `actor`, `source`, `capture_level`, `events`, `final_state`, `outputs`, `replay`, `integrity`. Нові програми використовують `execution_trace:`, а старий `trace:` вважається legacy compatibility view.

---

## Універсальні шаблони та команда `ordo template`

Ordo розрізняє три режими шаблонів. `deterministic` повністю рендериться утилітою; `model_rendered` передається моделі як контрольоване завдання; `hybrid` поєднує детерміновану структуру й обмежені модельні секції.

Кожен універсальний шаблон має стабільний `template_id`, семантичну версію, `input_schema`, `output_contract`, `review_profile` і діапазон сумісності. Для модельного або гібридного шаблону також обов’язковий `model_contract`, який містить посилання на prompt і вимогу зберігати provenance.

Початкова перевірка виконується командою:

```bash
ordo template validate path/to/template.yaml
```

Команда не створює документ. Вона перевіряє, чи шаблон достатньо формалізований, щоб надалі його можна було безпечно рендерити, тестувати, порівнювати й рев’ювати спільними засобами Ordo.

## Template Registry

`Template Registry` — це єдиний реєстр повторно використовуваних output-шаблонів. Він не містить сам текст документа, а зв'язує стабільний `template_id` і версію з template contract, checksum, режимом рендерингу та playbook-ами, які його використовують.

```yaml
schema_version: ordo.template.registry.v1
templates:
  - template_id: qa.package
    version: 2.0.0
    status: active
    contract_ref: qa_package.template.yaml
    sha256: <sha256>
    render_mode: model_rendered
    used_by:
      - history_event.guided_intake
```

`status` може бути `active`, `experimental`, `deprecated` або `disabled`. Команда `ordo template registry-check <registry>` блокує дублікати, відсутні contract-файли, stale checksum, розбіжність ID/версії та кілька одночасно активних версій одного шаблону.


## Generic renderer interface

Команда `ordo template render` працює з трьома режимами. `deterministic` створює артефакт локально; `model_rendered` формує контрольований `model_render_job.json`; `hybrid` спочатку створює детермінований scaffold, а потім job для моделі. Кожен запуск формує `render_evidence.json` із checksum контракту та вхідних даних. Прихований виклик моделі заборонений.

## Generic Template Review Engine

Після рендерингу шаблону артефакт перевіряється окремою командою `ordo template review`. Review engine не покладається на фразу моделі «PASS», а формує структурований evidence-файл `ordo.template.review_evidence.v1` з окремими checks, findings, severity, location, checksum і рішенням `approve` або `reject`.

```bash
ordo template review qa.package.template.yaml \
  --artifact qa_package.md \
  --render-evidence render_evidence.json \
  --out template_review_evidence.json
```

Основні перевірки: наявність і непорожність артефакту, формат, обов'язкові розділи, заборонений вміст, обмеження розміру, parseability JSON/YAML та відповідність provenance. Для `review_profile.mode: strict` файл render evidence є обов'язковим; відсутність або невідповідність checksum блокує review.

## Template version diff і breaking-change gate

Команда `ordo template diff OLD NEW` порівнює дві версії контракту шаблону. Зміна режиму рендерингу, формату виходу, додавання обов'язкового input/section, видалення поля або посилення review profile вважається breaking change.

Breaking change потребує збільшення MAJOR-версії та явного блоку `migration` з `required: true` і `guide_ref`. Утиліта лише формує diff і рішення gate; вона не переписує шаблон автоматично.

## Generic template tooling: реальна інтеграція

Playbook підключає універсальний template tooling через `generic_template_tooling.registry_ref` і окремі bindings. Кожен binding вказує стабільний `template_id`, version, render profile, review profile та input mapping; бізнес-логіка playbook-а при цьому не дублює renderer або review engine.

Для `model_rendered` шаблону CLI створює контрольований model job і provenance evidence. Для `deterministic` шаблону CLI сам створює артефакт, після чого той самий generic review engine перевіряє формат, required sections і render evidence.

## `allowed_from`, `entry_modes` і `node_context`

`allowed_from` перелічує лише безпосередні попередні вузли, з яких дозволено ввійти в поточний вузол; `entry_modes` явно дозволяє спеціальні входи `root`, `resume`, `retry`, `recovery` або `migration`, а `node_context` визначає обмежений набір стану, знань, інструментів і вихідних зобов’язань поточного вузла.

Перед виконанням дії runtime звіряє `previous_node_id` із `allowed_from`; невідповідність блокує виконання та запускає діагностику переходу без зміни стану.
