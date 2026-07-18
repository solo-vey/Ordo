# Розділ 15. Debug mode і діагностичний trace

## Навіщо це потрібно

У попередньому розділі ми зафіксували головну проблему: складну Ordo-програму неможливо нормально розвивати, якщо видно тільки фінальну відповідь моделі.

Фінальна відповідь — це лише верхівка процесу. Вона показує, що модель сказала в кінці, але не показує, як вона до цього прийшла.

Для простих задач цього іноді достатньо. Наприклад, якщо модель переписує коротке повідомлення, можна просто оцінити результат: звучить добре чи ні.

Але для playbook-а, domain pack-а, бібліотеки або багатокрокового процесу цього недостатньо. Там важливо знати:

```text
- який path було обрано;
- які paths були відхилені;
- які rules спрацювали;
- які gates були перевірені;
- які gates були пропущені;
- який state був до кроку;
- який state став після кроку;
- які знання або фрагменти інструкцій використані;
- де модель зробила припущення;
- де вона мала зупинитися, але не зупинилася.
```

Саме для цього в Ordo потрібен `debug mode`.

`Debug mode` — це режим виконання, у якому Ordo-програма не просто дає результат, а формує повний execution trace.

![Nebu — ідея: debug mode показує шлях виконання](../assets/mascots/64x64/Nebu_idea_64x64.png)

Простими словами:

```text
normal mode відповідає: що зроблено;
debug mode відповідає: чому це було зроблено саме так.
```

## Просте пояснення

Уявімо, що Ordo-програма — це маршрут у навігаторі.

У звичайному режимі навігатор просто веде вас до точки призначення.

У debug mode він додатково показує:

```text
- чому вибрав саме цю дорогу;
- які дороги відкинув;
- де були обмеження;
- де були затори;
- де він перебудував маршрут;
- на які дані спирався;
- що сталося б, якби обрати інший шлях.
```

Для Ordo це означає: модель має показати не приховане мислення, а формальну трасу виконання.

Це важлива різниця.

Ordo не повинна вимагати від моделі розкривати приватний chain of thought. Натомість Ordo повинна вимагати structured execution trace — тобто запис формальних рішень, які є частиною процесу.

![Nebu — увага: trace не є chain of thought](../assets/mascots/64x64/Nebu_attention_64x64.png)

Не потрібно бачити все, що модель “думала”. Потрібно бачити те, що вона **виконала**:

```text
- який NODE активний;
- який path selected;
- який gate evaluated;
- який state changed;
- який output allowed;
- який rule used;
- який warning raised.
```

Це не психологія моделі. Це журнал виконання програми.

## Debug mode як частина мови

У Ordo debug mode не повинен бути зовнішнім коментарем у стилі:

```text
Поясни, чому ти так зробив.
```

Це занадто слабко. Модель може пояснити красиво, але не обовʼязково точно.

У мові має бути формальна конструкція:

```yaml
run:
  mode: debug
  execution_mode: chat_internal
  trace_required: true
```

Або у compiled IR:

```json
{
  "op": "DEBUG.MODE",
  "mode": "debug",
  "execution_mode": "chat_internal",
  "trace_required": true
}
```

Це означає, що Ordo-програма запускається не тільки для результату, а й для збору execution trace.

У debug mode результат без trace вважається неповним.

У Ordo v0.12 поруч із `mode` обовʼязково фіксується `execution_mode`. Це чесно показує, у якому середовищі виконується процес:

```text
full_runtime   — переходи й hard gates примусово контролює runtime або helper-runner;
chat_internal  — модель веде процес у чаті, але частина перевірок може виконуватися кодом або файлами сесії;
freeform_only  — модель виконує дисципліну Ordo текстом без зовнішнього примусового контролю.
```

Це не дрібна технічна деталь. Один і той самий debug trace має різну силу залежно від того, хто реально контролював переходи: код, модель у чаті чи тільки текстова самодисципліна.

## Що таке execution trace

`Execution trace` — це структурований журнал виконання Ordo-програми.

Він має відповідати на питання:

```text
що було на вході;
який стан був на початку;
який path обрано;
чому саме цей path;
які paths відхилені;
які вузли пройдені;
які gates перевірені;
які decisions прийняті;
які state changes сталися;
які outputs дозволені;
які outputs заблоковані;
які джерела або знання використані;
які warning або violation виникли.
```

Мінімальна структура trace може виглядати так:

```yaml
trace:
  run_id: "RUN-001"
  mode: "debug"
  execution_mode: "chat_internal"
  trace_source: "model_self_report"

  input_snapshot:
    user_message: "створюємо подію зміни статусу компанії"

  selected_path:
    id: "A1"
    reason: "користувач описав зміну поля в основному source row"

  rejected_paths:
    - id: "A2"
      reason: "немає підтвердження, що зміна стосується повʼязаної сутності"
    - id: "A4"
      reason: "немає ExternalHistoryEvent"

  nodes:
    - id: "NODE_SELECT_PATH"
      status: "completed"
    - id: "NODE_COLLECT_CONTRACT"
      status: "active"

  gates:
    - id: "G_CONTRACT_CONFIRMED"
      status: "pending"
      reason: "source field ще не підтверджено"

  state_changes:
    - field: "event_alias"
      before: null
      after: "LU_CHANGE_STATUS"

  warnings:
    - "source field not confirmed"

  violations: []
```

Цей trace не є фінальним документом для користувача. Це службовий, але контрольований артефакт виконання.

## Trace source

У Ordo v0.12 кожен trace має явно показувати, звідки походить його довіра.

Для цього додається поле:

```yaml
trace_source: model_self_report | runtime_enforced | hybrid
```

`model_self_report` означає, що trace сформувала сама модель. Це корисно для пояснення логіки, але не є таким самим доказом, як журнал зовнішнього runtime.

`runtime_enforced` означає, що trace сформований кодом runner-а або оркестратора на основі реальних переходів стану, фактичних викликів gate і записаних state snapshots.

`hybrid` означає змішаний режим: частина trace сформована кодом, а частина є семантичним поясненням моделі. Наприклад, `STATE.DIFF` може бути runtime-enforced, а `PATH.EXPLAIN.reason` — model self-report.

Це поле потрібне для чесності. Без нього debug trace може виглядати як класичний лог програми, хоча насправді може бути лише структурованим самозвітом моделі.

Приклад:

```yaml
trace:
  run_id: "RUN-001"
  mode: "debug"
  execution_mode: "chat_internal"
  trace_source: "hybrid"

  runtime_enforced:
    - "state_snapshot"
    - "mechanical_gate_status"

  model_self_report:
    - "path_reason"
    - "semantic_evidence_summary"
```

Правило Ordo v0.12: trace без `trace_source` вважається неповним.

## Run ID

Кожен запуск Ordo-програми має мати `run_id`.

Без `run_id` складно зрозуміти, про який саме запуск іде мова.

Особливо це важливо, коли користувач каже:

```text
ось тут воно пішло не так
```

Ordo має мати можливість привʼязати це зауваження до конкретного run:

```yaml
run:
  id: "RUN-2026-07-05-014"
  program: "history_event_playbook"
  version: "0.12"
  mode: "debug"
  execution_mode: "chat_internal"
  trace_source: "hybrid"
```

Потім improvement record може сказати:

```yaml
observed_in:
  run_id: "RUN-2026-07-05-014"
  node: "NODE_PRE_ARCHIVE_CHECK"
  gate: "G_PACKAGE_SELF_CHECK"
```

Це робить покращення не абстрактним, а привʼязаним до фактичного виконання.

## Input snapshot

Debug trace має містити snapshot входу.

Це не обовʼязково повна копія всіх даних, особливо якщо там є конфіденційна інформація. Але має бути достатньо, щоб зрозуміти, з чого почався run.

Наприклад:

```yaml
input_snapshot:
  user_intent: "створити HistoryEvent для зміни статусу"
  provided_fields:
    - "alias"
    - "old_value"
    - "new_value"
  missing_fields:
    - "source_field"
    - "fixture_id"
```

Так видно, що модель не мала права переходити до фінального пакета, бо частина контракту ще не була підтверджена.

## Path explain

![Nebu — подумати: path explain показує не тільки вибір](../assets/mascots/64x64/Nebu_thinking_64x64.png)

Один із найважливіших елементів debug mode — це `PATH.EXPLAIN`.

Він має показати не тільки обраний path, а й причину вибору.

Поганий варіант:

```yaml
selected_path: "A1"
```

Кращий варіант:

```yaml
selected_path:
  id: "A1"
  reason: "input describes a direct change in the main source row"
  evidence:
    - "user provided old/new values"
    - "no related entity context was confirmed"
```

Ще кращий варіант — показати rejected paths:

```yaml
rejected_paths:
  - id: "A2"
    reason: "related entity was not confirmed"
  - id: "A4"
    reason: "external history event payload was not provided"
```

Це дуже важливо для дебагу.

Без rejected paths ми бачимо тільки рішення. З rejected paths ми бачимо межі рішення.

## Decision log

`DECISION.LOG` — це журнал формальних рішень.

Decision — це не будь-яке речення моделі. Це точка, де Ordo-програма могла піти різними шляхами.

Наприклад:

```yaml
decision_log:
  - id: "D001"
    node: "NODE_SELECT_PATH"
    decision: "select_path_A1"
    reason: "direct source row change"
    evidence:
      - "field change described"
      - "no external event"

  - id: "D002"
    node: "NODE_OUTPUT_ALLOWED"
    decision: "block_final_archive"
    reason: "pre-archive approval gate is not passed"
    evidence:
      - "G_PRE_ARCHIVE_APPROVAL = pending"
```

Decision log має бути коротким, але достатньо точним.

Він не має перетворюватися на довгий художній опис.

## State snapshot і State diff

У складній Ordo-програмі state — це памʼять процесу.

Debug mode має показувати не тільки поточний state, а й зміни state.

Для цього потрібні дві конструкції:

```text
STATE.SNAPSHOT
STATE.DIFF
```

`STATE.SNAPSHOT` показує стан у певний момент.

`STATE.DIFF` показує, що саме змінилося.

Наприклад:

```yaml
state_snapshot:
  at: "before_NODE_COLLECT_CONTRACT"
  state:
    event_alias: null
    source_field: null
    output_allowed: false
```

Після кроку:

```yaml
state_diff:
  step: "NODE_COLLECT_ALIAS"
  changes:
    - field: "event_alias"
      before: null
      after: "LU_CHANGE_STATUS"
```

Це дозволяє бачити, де модель передчасно заповнила state або, навпаки, не заповнила те, що вже було підтверджено.

## Gate report

У normal mode gate може просто блокувати або дозволяти дію.

У debug mode gate має пояснювати свій статус.

Наприклад:

```yaml
gate_report:
  - gate_id: "domain_pack.history_event.G_PRE_ARCHIVE_APPROVAL"
    method: "human"
    trust_class: "human_decision"
    trace_source: "runtime_enforced"
    status: "blocked"
    reason: "user has not approved package generation"
    required_evidence:
      - "explicit user approval"
    actual_evidence: []
```

Це краще, ніж просто:

```text
архів не можна створити
```

Бо видно, чого саме бракує.

Gate report має містити щонайменше:

```text
- full namespaced gate id;
- method;
- trust_class;
- trace_source;
- status;
- reason;
- required evidence;
- actual evidence;
- blocking / non-blocking;
- next required action.
```

Це особливо важливо для gates з різним рівнем довіри. `method: mechanical` і `method: self_verification` можуть обидва мати `status: passed`, але це не однаковий тип гарантії. Перший пройшов детерміновану перевірку, другий — семантичне судження моделі за протоколом evidence.

## Knowledge trace

Ordo-програма часто спирається на різні джерела:

```text
- Core;
- Profile;
- Domain Pack;
- Library;
- user-provided data;
- uploaded playbook;
- runtime context;
- FREEFORM block.
```

У debug mode має бути видно, які знання були використані.

Наприклад:

```yaml
trace_source: "model_self_report"
knowledge_trace:
  - source_type: "domain_pack"
    source_id: "history_event_domain_pack"
    section: "Path A1"
    used_for: "path selection"

  - source_type: "library"
    source_id: "ordo.validation.contract_first"
    export: "G_CONTRACT_CONFIRMED"
    used_for: "contract validation"

  - source_type: "freeform"
    source_id: "FF_ANALYST_STYLE_GUIDE"
    used_for: "response tone"
```

Це особливо важливо для FREEFORM.

Якщо модель прийняла важливе рішення на основі FREEFORM, trace має це показати. Можливо, після цього стане зрозуміло, що цей FREEFORM треба формалізувати.

## Warning і violation

Debug trace має розрізняти warnings і violations.

`warning` — це ризик або неповнота, яка не обовʼязково зупиняє процес.

`violation` — це порушення правила.

Наприклад:

```yaml
warnings:
  - id: "W_SOURCE_FIELD_MISSING"
    message: "source field is not confirmed yet"
    blocking: false
```

```yaml
violations:
  - id: "V_ARCHIVE_CREATED_BEFORE_APPROVAL"
    rule: "ASSERT.NOT final_archive_created before G_PRE_ARCHIVE_APPROVAL"
    severity: "critical"
```

Якщо є critical violation, Ordo-програма не повинна робити вигляд, що результат валідний.

## Debug output для людини

Повний trace може бути довгим. Тому Ordo має відрізняти:

```text
machine trace
human debug summary
```

Machine trace потрібен для runtime, тестів і компілятора.

Human debug summary потрібен користувачу.

Наприклад:

```text
Debug summary:
Обрано Path A1, бо вхідні дані описують зміну поля в основному source row.
Path A2 відхилено, бо не підтверджено повʼязану сутність.
Фінальний архів заблоковано, бо gate G_PRE_ARCHIVE_APPROVAL ще не пройдений.
Потрібна наступна дія: підтвердити source field і fixture.
```

Це коротко, зрозуміло і не перевантажує людину повним JSON.

## Debug mode і privacy

Debug trace не повинен бездумно виводити всі сирі дані.

У trace можуть бути конфіденційні payload-и, персональні дані, внутрішні назви або технічні деталі.

Тому Ordo має підтримувати рівні trace:

```text
trace_level: summary
trace_level: standard
trace_level: full
trace_level: redacted
```

Наприклад:

```yaml
run:
  mode: "debug"
  trace_level: "redacted"
```

У такому режимі trace може показати, що поле було використано, але приховати значення:

```yaml
state_diff:
  - field: "tax_id"
    before: "[REDACTED]"
    after: "[REDACTED]"
```

Це важливо, якщо Ordo буде використовуватися в реальних продуктах.

## Execution mode і рівень гарантії

`Debug mode` пояснює виконання, але не сам по собі гарантує, що кожен gate справді був примусово виконаний. Для цього Ordo v0.12 додає окреме поле `execution_mode`.

```yaml
program: history_event_playbook
execution_mode: full_runtime
```

Базові режими:

```text
full_runtime  — runtime або helper-runner контролює state, node transitions і hard gates;
chat_internal — модель працює в чаті, може запускати скрипти або вести state у файлах, але точка виклику gate не є повністю примусовою;
freeform_only — Ordo-дисципліна виконується текстом без зовнішнього контролю.
```

Таблиця чесних гарантій:

| execution_mode | Хто визначає момент виклику gate | Хто виконує перевірку | Рівень гарантії |
|---|---|---|---|
| `full_runtime` | код / runner | код або модель за протоколом | найвищий |
| `chat_internal` | модель у чаті | код у сесії або модель | середній |
| `freeform_only` | модель | модель текстом | найнижчий |

Ця таблиця потрібна, щоб не перебільшувати силу Ordo. У `chat_internal` режимі механічна перевірка може бути реально виконана кодом, але без зовнішнього runtime модель усе ще має сама вчасно її запустити.

## Debug mode і compiler

Компілятор Ordo має вміти автоматично додавати trace points.

Автор Ordo Source не повинен вручну логувати кожну дрібницю.

Наприклад, якщо у Source є:

```yaml
nodes:
  - id: "NODE_SELECT_PATH"
    branches:
      - path: "A1"
        when: "direct source row change"
      - path: "A2"
        when: "related entity change"
```

Компілятор має автоматично створити в IR trace points:

```json
{
  "op": "PATH.EXPLAIN",
  "node": "NODE_SELECT_PATH",
  "required": true,
  "trace_source": "model_self_report"
}
```

Тобто debug layer не має бути “допискою збоку”. Він має бути частиною компіляції.

## Debug mode і помилки моделі

Debug trace допомагає відрізнити різні типи проблем.

Наприклад, якщо результат неправильний, причина може бути різною:

```text
1. неправильна інструкція;
2. неповний contract;
3. неоднозначний context;
4. помилковий path selection;
5. пропущений gate;
6. неправильний output template;
7. слабкий FREEFORM;
8. конфлікт бібліотек;
9. модель не виконала IR;
10. користувач змінив вимогу посеред процесу.
```

Без trace усе це виглядає однаково:

```text
модель помилилась
```

З trace можна сказати точніше:

```text
помилка виникла на NODE_SELECT_PATH;
модель обрала A1, хоча fixture відповідав A2;
причина — у branch condition немає правила для related entity через Центр ідентифікації.
```

Це вже не просто скарга. Це діагноз.

## Типові помилки

### Помилка 1. Просити модель “пояснити”, але не вимагати trace

Пояснення після факту може бути красивим, але неперевірним.

Краще мати structured trace під час виконання.

### Помилка 2. Логувати тільки selected path

Selected path сам по собі не показує, чому інші paths відкинуті.

Потрібно логувати rejected paths with reasons.

### Помилка 3. Не логувати state diff

Якщо видно тільки фінальний state, важко зрозуміти, де саме він зіпсувався.

Потрібен state diff після важливих nodes.

### Помилка 4. Ховати gate report у тексті відповіді

Gate report має бути структурованим.

Інакше його складно тестувати.

### Помилка 5. Виводити занадто багато debug-інформації людині

Повний trace потрібен машині й автору playbook-а.

Користувачу часто достатньо debug summary.

### Помилка 6. Плутати execution trace з chain of thought

Ordo не потребує приватного reasoning-тексту моделі.

Ordo потребує формального журналу виконання: node, path, gate, state, output, evidence.

### Помилка 7. Не вказувати `trace_source`

Trace без `trace_source` створює хибне враження, що це завжди runtime-log.

У v0.12 потрібно явно показувати: це `model_self_report`, `runtime_enforced` чи `hybrid`.

### Помилка 8. Не вказувати `execution_mode`

Якщо не вказати режим виконання, читач або наступний процес не розуміє, який рівень гарантії має trace.

`full_runtime`, `chat_internal` і `freeform_only` — це різні рівні контролю, а не різні назви одного й того самого режиму.

## Міні-вправа

Візьміть просту інструкцію:

```text
Підготуй пакет для нової історичної події, але не створюй фінальний архів, поки я не підтверджу source field і QA-сценарії.
```

Спробуйте описати, що має зʼявитися в debug trace.

Мінімально визначте:

```text
- run_id;
- execution_mode;
- trace_source;
- input snapshot;
- selected path;
- rejected paths;
- state before/after підтвердження source field;
- gate для заборони архіву;
- gate status до підтвердження;
- warning, якщо QA-сценарії ще не визначені;
- human debug summary.
```

Після цього спробуйте сформулювати violation, якщо модель все ж створила архів до підтвердження.

## Короткий підсумок

`Debug mode` — це режим виконання Ordo-програми, у якому результат супроводжується structured execution trace.

Execution trace має показувати:

```text
- run_id;
- execution_mode;
- trace_source;
- input snapshot;
- selected і rejected paths;
- decision log;
- state snapshots;
- state diffs;
- gate report;
- knowledge trace;
- warnings;
- violations;
- human debug summary.
```

Головна цінність debug mode у тому, що він перетворює проблему з:

```text
модель чомусь зробила не те
```

на:

```text
на такому node було обрано такий path з такої причини; такий gate був пропущений; такий state змінився неправильно; ось де потрібно виправити Ordo-програму.
```

Саме тому debug mode — це не сервісна функція навколо Ordo, а частина самої мови.


> **Оновлення M72.1.** Цей розділ пояснює debug-представлення trace. Повний нормативний core-елемент `EXECUTION_TRACE`, його поля, event catalog, replay та integrity описані в розділі 74.
