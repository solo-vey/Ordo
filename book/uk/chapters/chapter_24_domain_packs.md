# Розділ 24. Domain Packs

## Навіщо потрібні Domain Packs

У попередніх розділах ми розділили Ordo на кілька рівнів.

`Ordo Core` задає мінімальну мову виконання.

`Ordo Profiles` додають правила для типових режимів роботи: документація, QA, погодження, guided intake, debug і тестування.

Але цього все ще недостатньо для реальних процесів.

Бо майже кожен серйозний процес має свою предметну логіку.

Наприклад, створення історичної події має свої поняття:

```text
HistoryEvent
ChangeRecord
source row
alias
display name
old value
new value
Path A1
Path A2
Path A4
no-op
rollback
manual QA package
automation spec
```

Моніторингова подія матиме інші поняття:

```text
monitoring event
configuration
translation tree
sandbox evaluate
REST runbook
business passport
technical package
trigger condition
expected notification
```

Юридичний аналіз матиме ще інші поняття:

```text
jurisdiction
legal basis
risk factor
evidence
finding
recommendation
exception
```

Це не варто класти в Core.

Також це не зовсім Profile. Profile каже: “цей процес має QA”, “цей процес має погодження”, “цей процес має documentation runtime”.

А Domain Pack каже: “у цій предметній області є такі об’єкти, такі правила, такі шляхи, такі gates, такі edge cases”.

Тому в Ordo потрібен окремий рівень:

```text
Domain Pack
```

![Nebu — ідея: Domain Pack як предметний шар Ordo](../assets/mascots/64x64/Nebu_idea_64x64.png)

## Просте пояснення

`Domain Pack` — це пакет предметних знань і правил для конкретної сфери.

Якщо пояснювати дуже просто:

```text
Core — це граматика Ordo.
Profile — це стиль роботи.
Domain Pack — це знання конкретної області.
```

Або так:

```text
Core знає, що таке NODE і GATE.
Profile знає, що в QA-процесі потрібні tests і coverage.
Domain Pack знає, що для History Event треба відрізняти A1 від A2, no-op від real change, source row від generated event.
```

Domain Pack перетворює загальну мову Ordo на інструмент для конкретної роботи.

![Nebu — подумати: Domain Pack не замінює Core або Profile](../assets/mascots/64x64/Nebu_thinking_64x64.png)

## Чому Domain Pack не можна замінити довгим prompt-ом

Можна, звичайно, написати в prompt-і великий опис предметної області.

Але тоді виникають знайомі проблеми:

```text
- модель не розуміє, які правила є обов’язковими;
- приклади змішуються з правилами;
- edge cases губляться;
- gates не виконуються як blocking;
- нові сценарії додаються хаотично;
- немає test coverage;
- незрозуміло, яку частину інструкції змінювати;
- feedback користувача не прив’язаний до конкретного rule або path.
```

Domain Pack має виправити це.

Він робить предметну область структурованою:

```text
- які є об’єкти;
- які є статуси;
- які є paths;
- які питання треба ставити;
- які gates є blocking;
- які outputs створюються;
- які edge cases існують;
- які правила залишаються в controlled FREEFORM;
- які tests перевіряють поведінку.
```

## Що входить у Domain Pack

Мінімальний Domain Pack може містити такі частини:

```text
DOMAIN.DEF
DOMAIN.VOCABULARY
DOMAIN.OBJECTS
DOMAIN.PATHS
DOMAIN.RULES
DOMAIN.GATES
DOMAIN.STATUS
DOMAIN.OUTPUTS
DOMAIN.FREEFORM
DOMAIN.TESTS
DOMAIN.COVERAGE
```

### DOMAIN.DEF

Це визначення предметної області.

Наприклад:

```yaml
domain:
  id: "history_event"
  name: "History Event Domain Pack"
  version: "0.1"
  purpose: "Guided intake and package generation for history event creation or update."
```

Цей блок відповідає на питання:

```text
Що це за область?
Для чого вона потрібна?
Яку задачу вона допомагає виконувати?
```

### DOMAIN.VOCABULARY

Це словник термінів.

Наприклад:

```yaml
vocabulary:
  HistoryEvent: "final internal historical event shown in company/person history"
  ChangeRecord: "technical record describing detected source-level change"
  source_row: "input source object from which change is detected"
  no_op: "case where no new event should be created"
```

Словник потрібен не для краси. Він зменшує ризик, що модель змішає близькі поняття.

Наприклад, якщо не визначити різницю між `ChangeRecord` і `HistoryEvent`, модель може почати трактувати технічний record як готову історичну подію.

### DOMAIN.OBJECTS

Це опис основних об’єктів області.

```yaml
objects:
  - id: "HistoryEvent"
    required_fields:
      - "alias"
      - "display_name"
      - "event_date"
      - "old_value"
      - "new_value"

  - id: "ChangeRecord"
    required_fields:
      - "field"
      - "old"
      - "new"
      - "status"
```

У реальному Domain Pack ці поля можуть бути складнішими. Але ідея проста: модель має знати, з якими сутностями вона працює.

### DOMAIN.PATHS

Це опис основних сценаріїв.

Наприклад:

```yaml
paths:
  - id: "A1"
    name: "direct source row field change"
    when:
      - "change is detected directly in source row"
    requires:
      - "source field confirmed"
      - "old/new values confirmed"

  - id: "A2"
    name: "related entity change"
    when:
      - "change belongs to entity related through identification center"
    requires:
      - "main entity confirmed"
      - "related entity confirmed"
      - "relation context confirmed"
```

Paths потрібні, щоб модель не “вгадувала” сценарій на основі загального враження.

Вона має вибрати path і пояснити чому.

### DOMAIN.RULES

Це предметні правила.

Наприклад:

```yaml
rules:
  - id: "R_NO_EVENT_FOR_NOOP"
    text: "If old and new normalized values are equal, no HistoryEvent should be created."
    enforcement: "blocking"

  - id: "R_CURRENCY_NORMALIZATION"
    text: "Capital amount comparison must use normalized amount and normalized currency."
    enforcement: "required"
```

Правило має бути не просто абзацом у документації. Воно має мати ідентифікатор і enforcement semantics.

### DOMAIN.GATES

Це контрольні точки, специфічні для області.

```yaml
gates:
  - id: "G_SOURCE_FIELD_CONFIRMED"
    type: "approval"
    blocking: true
    description: "Source field must be confirmed before generating event passport."

  - id: "G_NOOP_CHECK_DONE"
    type: "validation"
    blocking: true
    description: "No-op check must be completed before event creation decision."
```

Domain Pack може використовувати загальні gates із Profile, але додавати свої предметні gates.

### DOMAIN.OUTPUTS

Це опис результатів, які має створювати процес.

Наприклад:

```yaml
outputs:
  - id: "history_event_passport"
    format: "markdown"
    required: true

  - id: "jira_task"
    format: "markdown"
    required: true

  - id: "manual_qa_package"
    format: "markdown"
    required: true
```

Це важливо, бо в різних доменах outputs різні.

### DOMAIN.FREEFORM

Навіть у Domain Pack частина знань може залишатися у controlled FREEFORM.

Наприклад:

```yaml
freeform:
  - id: "FF_DOMAIN_EXAMPLES"
    purpose: "Examples of valid and invalid history event descriptions."
    binding:
      applies_to:
        - "DOMAIN.PATHS"
        - "DOMAIN.RULES"
    must_not_contain:
      - "blocking gates"
      - "status semantics"
```

Тобто Domain Pack не забороняє вільний текст. Він робить його контрольованим.

### DOMAIN.TESTS

Domain Pack має містити або підключати тести.

```yaml
tests:
  - id: "TC_A1_DIRECT_FIELD_CHANGE"
    expects:
      path: "A1"
      required_gates:
        - "G_SOURCE_FIELD_CONFIRMED"

  - id: "TC_NOOP_NORMALIZED_VALUES_EQUAL"
    expects:
      noop: true
      history_event_created: false
```

Без тестів Domain Pack дуже швидко починає ламатися під час змін.

## Domain Pack як contract між людьми і моделлю

Domain Pack — це не просто технічна специфікація.

Це contract між:

```text
- автором предметної логіки;
- аналітиком;
- моделлю;
- compiler/runtime;
- тестами;
- майбутніми користувачами.
```

Автор предметної області каже:

```text
У цій сфері ми працюємо ось так.
Ось наші поняття.
Ось наші paths.
Ось наші gates.
Ось де модель має зупинитись.
Ось що вона не має робити.
Ось як перевірити, що вона не зламалась.
```

Модель не повинна сама винаходити domain logic з повітря.

Вона має виконувати Domain Pack.

## Приклад: History Event Domain Pack

Для History Event Domain Pack основні частини можуть виглядати так:

```text
DOMAIN.DEF:
  History Event guided intake and package generation

DOMAIN.VOCABULARY:
  HistoryEvent
  ChangeRecord
  source row
  ExternalHistoryEvent
  no-op
  rollback
  manual QA
  automation spec

DOMAIN.PATHS:
  A1 — direct source row field change
  A2 — related entity change through identification center
  A3 — generated/calculated data change
  A4 — external history event input
  A5 — correction / rollback / special case

DOMAIN.GATES:
  G_ALIAS_CONFIRMED
  G_DISPLAY_NAME_CONFIRMED
  G_SOURCE_ROW_CONFIRMED
  G_VALUES_CONFIRMED
  G_NOOP_CHECK_DONE
  G_PRE_ARCHIVE_APPROVAL
  G_SELF_CHECK_DONE

DOMAIN.OUTPUTS:
  README
  SUMMARY
  VALIDATION_REPORT
  CONSISTENCY_CHECK_REPORT
  HISTORY_EVENT_PASSPORT
  JIRA_TASK
  IMPLEMENTATION_PROMPT
  QA_PACKAGE
  PROCESS_IMPROVEMENT_FEEDBACK
  QA_AUTOMATION_SPEC
  QA_AUTOMATION_README
```

Це вже не “довгий prompt”. Це предметна система правил.

## Приклад: Monitoring Event Domain Pack

Інший домен матиме інший пакет.

```text
DOMAIN.DEF:
  Monitoring Event business and technical package generation

DOMAIN.VOCABULARY:
  monitoring event
  business passport
  registry row
  Monitoring Center config
  translation tree
  sandbox evaluation
  REST runbook
  notification payload

DOMAIN.PATHS:
  business passport creation
  technical config package
  sandbox QA
  REST execution runbook
  registry row after Confluence URL

DOMAIN.GATES:
  G_BUSINESS_CONFIRMATION
  G_CONFIG_VALUES_CONFIRMED
  G_SANDBOX_EVALUATION_READY
  G_REST_RUNBOOK_SELF_CONTAINED
  G_CONFLUENCE_URL_REQUIRED_BEFORE_REGISTRY_ROW
```

Цей Domain Pack може використовувати ті самі Core і Profiles, але предметні rules будуть іншими.

## Зв’язок Domain Pack із Core

Domain Pack не має перевизначати Core.

![Nebu — увага: Domain Pack не повинен переписувати Core](../assets/mascots/64x64/Nebu_attention_64x64.png)

Погано:

```text
Domain Pack змінює значення NODE або GATE.
```

Добре:

```text
Domain Pack використовує NODE і GATE для своїх предметних правил.
```

Core має бути стабільним.

Domain Pack має бути розширенням, а не переписуванням базової мови.

## Зв’язок Domain Pack із Profiles

Domain Pack може вимагати певні Profiles.

Наприклад:

```yaml
domain:
  id: "history_event"

requires_profiles:
  - "ordo.profile.guided_intake"
  - "ordo.profile.documentation"
  - "ordo.profile.qa"
  - "ordo.profile.approval"
  - "ordo.profile.debug_test_improvement"
```

Це означає:

```text
Для цього домену недостатньо просто Core.
Тут обов’язково потрібні guided intake, documentation, QA, погодження і debug/test/improvement.
```

Profile дає загальні механізми.

Domain Pack наповнює їх предметним змістом.

## Зв’язок Domain Pack із Libraries

Domain Pack може використовувати libraries.

Наприклад:

```yaml
include:
  - library: "ordo.validation.noop_checks"
    version: "0.1"
    as: "noop"

  - library: "ordo.qa.manual_runbook"
    version: "0.1"
    as: "manual_qa"
```

Але Domain Pack не є просто бібліотекою.

Різниця така:

```text
Library — reusable готове рішення.
Domain Pack — предметна система правил для конкретної області.
```

Domain Pack може включати багато libraries, але залишається власником domain semantics.

## Версіонування Domain Pack

Domain Pack обов’язково має мати версію.

```yaml
domain:
  id: "history_event"
  version: "0.10"
```

Це потрібно тому, що зміна domain rules може змінити поведінку моделі.

Наприклад, якщо у версії `0.10` Path A4 трактував ExternalHistoryEvent одним способом, а у версії `0.11` правила уточнили, старі тести можуть поводитись інакше.

Тому важливо знати:

```text
- яка версія Domain Pack використана;
- які tests пройдені;
- які compatibility checks виконані;
- які breaking changes внесені;
- чи оновлений changelog.
```

## Domain Pack і компілятор

Компілятор Ordo має вміти перевіряти Domain Pack.

Мінімальні перевірки:

```text
- DOMAIN.DEF існує;
- vocabulary не має критичних прогалин;
- paths мають умови вибору;
- blocking gates мають enforcement;
- outputs мають required/optional статус;
- tests покривають основні paths;
- FREEFORM blocks мають binding;
- Domain Pack не перевизначає Core без явного дозволу;
- потрібні Profiles підключені;
- libraries мають зафіксовані versions.
```

Для складних Domain Packs компілятор має також генерувати:

```text
- coverage report;
- conflict report;
- unresolved ambiguity report;
- compatibility report;
- improvement backlog.
```

## Domain Pack і debug

Debug mode має показувати, які саме частини Domain Pack були використані.

Наприклад:

```yaml
trace_source: "model_self_report"
knowledge_trace:
  - source: "history_event_domain_pack"
    version: "0.10"
    section: "DOMAIN.PATHS.A1"
    used_for: "path selection"

  - source: "history_event_domain_pack"
    version: "0.10"
    section: "DOMAIN.GATES.G_NOOP_CHECK_DONE"
    used_for: "gate evaluation"
```

Без цього користувач бачить тільки відповідь.

З цим користувач бачить, яка domain rule спричинила рішення.

## Domain Pack і improvement loop

Коли користувач вказує на проблему, improvement record має прив’язувати її до Domain Pack.

Наприклад:

```yaml
improvement_record:
  classification:
    type: "missing_domain_gate"
    severity: "high"

  affected_unit:
    kind: "domain_pack"
    id: "history_event"
    version: "0.10"
    section: "DOMAIN.GATES"

  proposed_patch:
    - "add blocking gate G_MANUAL_QA_INSTRUCTIONS_ARE_ACTIONABLE"
    - "add regression test TC_MANUAL_QA_NOT_TOO_GENERIC"
```

Це дуже важливо: проблема не губиться в чаті, а стає зміною до конкретної частини domain logic.

## Типові помилки

### Помилка 1. Робити Domain Pack суцільним текстом

Якщо Domain Pack — це просто 100 сторінок markdown, модель знову буде працювати з ним як із довгим prompt-ом.

Потрібна структура:

```text
vocabulary
objects
paths
rules
gates
outputs
tests
freeform
```

### Помилка 2. Класти загальні правила в Domain Pack

Якщо правило стосується будь-якої документації, воно має бути в Documentation Profile або library, а не в конкретному domain pack.

Наприклад:

```text
Rendered artifact must be validated, not only template.
```

Це загальне правило. Його краще винести в Profile або library.

### Помилка 3. Не відокремлювати examples від rules

Приклади можуть бути у FREEFORM, але вони не мають ставати правилами без явного `DOMAIN.RULE`.

### Помилка 4. Не мати tests

Domain Pack без тестів — це нестабільна інструкція.

Він може працювати сьогодні і зламатися після найменшої зміни.

### Помилка 5. Не фіксувати версію

Якщо Domain Pack змінюється, але версія не змінюється, неможливо зрозуміти, чому стара поведінка більше не відтворюється.

## Міні-вправа

Візьміть будь-який процес, який ви добре знаєте.

Наприклад:

```text
- створення історичної події;
- підготовка моніторингової події;
- перевірка договору;
- аналіз ризиків компанії;
- створення Jira-задачі;
- підготовка QA-інструкцій.
```

Спробуйте описати для нього Domain Pack:

```text
1. Яка назва домену?
2. Які основні терміни потрібно визначити?
3. Які є головні об’єкти?
4. Які є paths?
5. Які правила є blocking?
6. Які gates обов’язкові?
7. Які outputs створюються?
8. Які частини можна залишити у FREEFORM?
9. Які tests мають бути мінімально?
10. Які problems/improvements треба збирати після реального використання?
```

Це не обов’язково має бути ідеально з першої спроби.

Головне — почати відрізняти domain logic від загальних інструкцій.

## Короткий підсумок

`Domain Pack` — це пакет предметної логіки для конкретної області.

Core задає базову мову.

Profiles задають режими роботи.

Libraries дають reusable готові рішення.

Domain Packs описують конкретну предметну область: vocabulary, objects, paths, rules, gates, outputs, tests і controlled FREEFORM.

Domain Pack потрібен, щоб модель не вигадувала domain logic сама, а виконувала узгоджені правила.

Добрий Domain Pack має бути структурованим, версіонованим, тестованим і видимим для debug/improvement layer.

У складних Ordo-процесах саме Domain Pack часто стає головним місцем, де живе реальна бізнесова логіка.

<!-- REVIEWED: chapter 24; Nebu markers checked -->
