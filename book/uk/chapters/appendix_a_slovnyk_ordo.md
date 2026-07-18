# Додаток A. Словник Ordo

Цей словник пояснює базові терміни Ordo простими словами. Він не замінює повну специфікацію мови, але допомагає швидко згадати сенс основних понять.

## AI Agent Programming Language

Мова для опису поведінки AI-агентів: їхніх ролей, дій, правил, станів, перевірок, outputs і зупинок.

Ordo належить саме до цього класу мов. Вона не є мовою навчання моделей. Вона є мовою керування поведінкою моделей і агентів.

## Ordo

Мова перетворення людських інструкцій на керований execution contract для AI-моделі.

Коротко:

```text
Ordo = intent → contract → context → state → path → steps → gates → result → handoff
```

## Ordo Source

Людинозрозумілий запис Ordo-програми.

Ordo Source може бути написаний у форматі YAML, markdown-like structure або іншому читабельному форматі.

Його задача — бути зрозумілим для автора playbook-а, аналітика або архітектора.

## Ordo IR

Проміжне представлення Ordo-програми, яке зручніше для виконання моделлю або runner-ом.

Найкращий поточний формат для IR — Semantic JSON IR.

## Semantic JSON IR

JSON-представлення Ordo-програми, у якому кожен елемент має семантичний сенс: entry, node, gate, state, output, assertion, test, trace тощо.

Це не просто JSON-версія markdown. Це виконувана карта процесу.

## Compact Opcode IR

Майбутній компактний формат Ordo IR, де інструкції записуються як короткі op-коди.

Наприклад:

```text
ENTRY.DEF
NODE.DEF
GATE.REPORT
ASSERT.NOT
```

Цей формат може бути корисним для native model support.

## Intent

Намір користувача.

Відповідає на питання:

```text
Що користувач насправді хоче зробити?
```

Intent не завжди дорівнює буквальному тексту повідомлення користувача.

## Contract

Погоджені умови виконання.

Contract визначає:

```text
що робимо;
що не робимо;
що треба підтвердити;
де модель має зупинитися;
який результат очікується.
```

## Context

Дані, правила, обмеження і ситуація, у межах яких виконується Ordo-програма.

Context може включати документи, приклади, domain rules, user preferences, source rows, попередні рішення.

## State

Поточний стан виконання.

State відповідає на питання:

```text
Що вже відомо?
Що підтверджено?
Що ще очікує рішення?
Який path обрано?
Які gates пройдено?
```

## Entry

Точка входу в Ordo-програму.

Entry визначає, з чого починається процес, які дані очікуються і який перший крок має виконати модель.

## Node

Окремий вузол процесу.

Node може бути питанням, рішенням, перевіркою, кроком збору даних або переходом до іншого node.

## Path

Обраний маршрут виконання.

Path визначає, який сценарій застосовується до конкретного input.

## Step

Конкретна дія в межах path або node.

Наприклад: поставити питання, оновити state, перевірити gate, сформувати output.

## Gate

Контрольна точка, яку треба пройти перед переходом далі.

Gate — це не порада. Це умова виконання.

## Blocking gate

Gate, який зупиняє процес, якщо умова не виконана.

Наприклад: не можна створювати фінальний архів без self-check.

## ASSERT.NOT

Негативна перевірка, яка явно забороняє певну дію або стан.

Наприклад:

```text
не створювати фінальний output до підтвердження контракту
```

## Status semantics

Правила значення статусів.

Status semantics визначає, що означає статус: чи можна виконувати дію, чи треба чекати, чи потрібне людське рішення, чи це no-op.

## Output

Результат, який має створити Ordo-програма.

Output може бути відповіддю, документом, архівом, JSON, тестовим пакетом, handoff note або іншим артефактом.

## Handoff

Передача результату людині, іншій системі або наступному процесу.

Handoff має містити не тільки файл або текст, а й стан, обмеження, warnings, validation result і next steps.

## FREEFORM

Контрольована зона для інструкцій, які ще не варто або неможливо повністю формалізувати.

FREEFORM не має бути смітником для всіх складних правил. Він має мати binding, reason, scope і coverage.

## FREEFORM.COVERAGE

Оцінка того, яка частина інструкцій залишилася у FREEFORM і наскільки вона контрольована.

## Ordo Core

Базова частина мови, яка містить універсальні конструкції: intent, contract, state, node, output, gates, assertions, trace тощо.

## Ordo Profile

Набір спеціалізованих правил для певного типу роботи.

Наприклад: документаційний profile, QA profile, approval profile.

## Domain Pack

Пакет правил для конкретної предметної області.

Наприклад: History Event Domain Pack або Monitoring Event Domain Pack.

## Ordo Library

Reusable пакет готових Ordo-конструкцій, який можна підключити до поточної Ordo-програми.

Бібліотека може містити gates, tests, templates, profiles, execution patterns або domain rules.

## include

Механізм підключення бібліотеки або її частини до Ordo-програми.

## import

Механізм імпорту конкретних exports із бібліотеки.

## use

Механізм фактичного використання підключеної конструкції в поточному процесі.

## namespace

Простір імен, який запобігає конфліктам між однаковими назвами gates, nodes, templates або rules.

## alias

Локальна коротка назва для підключеної бібліотеки або конструкції.

## Debug mode

Режим запуску, у якому Ordo-програма формує повний trace виконання.

## Trace

Журнал виконання, який показує, що сталося під час run.

## Decision log

Журнал рішень моделі або runner-а.

Пояснює, чому було обрано певний path, node або дію.

## State snapshot

Знімок state у конкретний момент виконання.

## State diff

Різниця між двома state snapshots.

## Gate report

Звіт про проходження або провал gates.

## Knowledge trace

Список знань, правил або джерел, які були використані при виконанні.

## Test case

Опис тестового сценарію для Ordo-програми.

## Fixture

Вхідні дані для test case.

## Expected behavior

Очікувана поведінка Ordo-програми: path, state, output, gate status, no-op або заборонена дія.

## Regression suite

Набір тестів, який перевіряє, що нова зміна не зламала стару поведінку.

## Coverage report

Звіт про те, які paths, gates, nodes, outputs, FREEFORM blocks і rules покриті тестами.

## Feedback capture

Механізм фіксації зауважень користувача під час роботи з Ordo-програмою.

## Improvement record

Структурований запис про проблему або покращення.

Має містити affected unit, severity, root cause, proposed patch і suggested tests.

## Human approval

Людське підтвердження перед застосуванням важливої зміни.

Ordo не повинна автоматично змінювати playbook, library або compiler rules без такого підтвердження.

## Helper-runner

Зовнішній виконавчий шар, який допомагає моделі виконувати Ordo-програму: зберігає state, перевіряє gates, пише trace, запускає tests.

## Native model language

Режим, у якому модель підтримує Ordo як власну мову виконання, а не просто читає її як текст.

---

---

## Оновлення словника для Ordo v0.12

## gate.method

Обовʼязкове поле gate, яке визначає спосіб перевірки контрольної точки.

Допустимі значення:

```text
mechanical
self_verification
self_consistency
human
```

`gate.method` потрібен, щоб не змішувати механічні перевірки з семантичними судженнями моделі або людськими рішеннями.

## trust_class

Клас довіри до результату перевірки.

Приклади:

```text
deterministic
model_judgment
repeated_model_judgment
human_decision
```

`trust_class` допомагає читачу gate report зрозуміти, що означає `passed`: код порахував, модель оцінила, кілька проходів погодилися, або людина прийняла рішення.

## mechanical gate

Gate, який можна перевірити детерміновано кодом або runner-ом.

Наприклад: кількість пунктів, наявність поля, формат дати, закриття code block.

## self_verification gate

Gate, який перевіряється моделлю через окремий evidence-протокол.

Це не дає абсолютної гарантії, але робить семантичну перевірку явною і трасованою.

## self_consistency gate

Gate, який перевіряється кількома незалежними проходами моделі з агрегацією результатів.

Використовується для критичних семантичних рішень, де один модельний прохід недостатній.

## human gate

Gate, який завершується рішенням людини.

Модель може підготувати дані, але не може самостійно прийняти бізнесове, юридичне або незворотне рішення.

## trace_source

Поле debug trace, яке показує джерело довіри до trace.

Допустимі значення:

```text
model_self_report
runtime_enforced
hybrid
```

`trace_source` потрібен, щоб не плутати пояснювальний самозвіт моделі зі справжнім runtime log.

## execution_mode

Режим виконання Ordo-програми.

Базові значення v0.12:

```text
full_runtime
chat_internal
freeform_only
```

`full_runtime` дає найвищий рівень контролю, `chat_internal` є проміжним режимом, а `freeform_only` є найслабшим і найближчим до дисциплінованого prompt-а.

## ASSERTION

Канонічний примітив Ordo для правила, яке має бути виконане або заборонене.

`ASSERT.NOT`, negative gate і `EXPECT.NOT` розглядаються як проєкції або скорочення від `ASSERTION`.

## ASSERTION projection

Автоматичне розгортання одного `ASSERTION` у runtime-перевірку, test expectation і debug violation record.

Це зменшує ризик, що правило є в playbook, але забуте в regression suite.

## on_unmatched_input

Правило вузла `NODE.DEF`, яке визначає, що робити, якщо відповідь користувача не відповідає жодному `allowed_answer`.

Зазвичай запускає `CLARIFY.REQUEST`, а після вичерпання спроб може переводити процес до людини.

## CLARIFY.REQUEST

Окремий тип дії для контрольованого уточнення відповіді користувача.

Це не звичайне питання, а спеціальний вихід із ситуації, коли input не вклався в дерево рішень.

## node_coverage_gap

Клас проблеми у feedback loop, який означає, що вузол не покриває реальні відповіді користувачів.

Якщо такі випадки повторюються, playbook потрібно розширити або уточнити.

## control_level

Рівень строгості Ordo-програми.

Допустимі значення:

```text
light
standard
strict
```

`light` підходить для простих задач, `standard` — для звичайних Ordo-програм, `strict` — для критичних процесів із mandatory gates, debug trace і regression coverage.

## namespaced ID

Повний ідентифікатор Ordo-одиниці у compiled IR.

Наприклад:

```text
domain_pack.history_event.G_CONTRACT_CONFIRMED
library.contract_first.G_NO_FINAL_OUTPUT
```

У Source можна використовувати короткі локальні назви, але у trace, gate report і improvement record потрібні повні namespaced IDs.

## layer priority

Правило пріоритету шарів Ordo при конфліктах.

Базова ієрархія:

```text
Core > active Profile > active Domain Pack > explicitly included Libraries > controlled FREEFORM
```

Нижчий шар не може мовчки перекрити вищий.

## explicit override

Явний дозвіл на заміну або уточнення правила з іншого шару.

Override має містити target, reason і, для критичних випадків, human approval.

## FREEFORM.maturity

Стан зрілості FREEFORM-блоку.

Базові значення:

```text
stable
volatile
candidate_for_formalization
```

`FREEFORM.maturity` допомагає відстежувати, чи не настав час перетворити повторюваний FREEFORM-фрагмент на gate, assertion, test або domain rule.

## incident_threshold

Поріг кількості інцидентів для FREEFORM-блоку.

Коли `incident_count >= incident_threshold`, Ordo має рекомендувати формалізацію через `FREEFORM_FORMALIZATION_RECOMMENDED`.

## Process Rail

Опорна структура процесу, яка допомагає ШІ вести гнучкий діалог, але не втрачати state, route, gates, backtracking і output readiness.

## AI Ordo Developer

Роль ШІ у режимі створення Ordo-проєкту. PM описує задачу природною мовою, а AI Ordo Developer проектує YAML, запускає helper checks, компілює Semantic JSON IR і пояснює PM-у стан проєкту.

## AI Ordo Executor

Роль ШІ у режимі виконання готового Ordo-проєкту. AI Ordo Executor читає Semantic JSON IR як Process Rail, веде людину по процесу, обробляє відхилення й використовує deterministic helper tools.

## Deterministic Helper

Інструмент або CLI-команда, яка перевіряє механічну частину процесу: syntax, state, gates, next step, diff або validation. Deterministic Helper не замінює ШІ й не говорить із користувачем напряму.

## Contract → Artifact Coverage

**Contract** — структуровано підтверджене або запропоноване рішення процесу зі статусом поля.

**Artifact requirement** — правило, яке описує, у яких generated artifacts має зʼявитися confirmed contract або його поля.

**Rendered artifact assertion** — перевірка вже згенерованого Markdown/JSON/YAML-файлу, а не лише шаблону.

**Go/No-Go decision** — машинозчитуване рішення, чи можна передавати пакет далі, чи він блокується через confirmation/artifact/template/runner issue.


## json-ir

Canonical machine target Ordo runtime. У поточній реалізації це `compiled/program.ir.json`. CLI виконує runtime logic саме з нього.

## ordo-code-view

AI-facing code-like projection Ordo-програми. Вона пояснює node contracts моделі, але не є source of truth.

## session-trace

Append-only proof program runtime-сесії. Його пише CLI після кожного accepted `intake --submit`.

## targets.manifest.json

Manifest, який фіксує runtime targets, їхні ролі, hashes і звʼязок із canonical IR hash.

## runtime_view

Package-level режим, який визначає, який AI-facing формат embedded CLI має показувати за замовчуванням: `json`, `ordo-code` або `json,ordo-code`.

## verify-targets

CLI-команда, яка перевіряє, що target files відповідають `compiled/targets.manifest.json` і не дрейфували від canonical IR.

## verify-session

CLI-команда фінальної runtime-перевірки. Вона перевіряє target-set, session-chain, session-trace і canary scan.

## scenario testing

Перевірка поведінки моделі на повному runtime-сценарії, а не лише перевірка окремих CLI-команд.

## PathWalk

Companion-утиліта або benchmark-підхід для тестування того, чи модель коректно проходить Ordo decision path через CLI-enforced runtime protocol. PathWalk не є обовʼязковою частиною runtime-пакета.

## model_access_mode

Режим доступу моделі під час scenario testing. Наприклад: `enforced`, `ir_readable`, `freeform`.

## protocol_compliance

Оцінка того, чи модель дотримувалась runtime-протоколу: використовувала embedded CLI, не читала `compiled/*` напряму, показувала evidence/digest і не переходила до наступного вузла без accepted submit.

## path correctness

Оцінка того, чи фактично прийнятий CLI шлях збігся з очікуваним сценарним ground truth.

## Restore-session

Runtime-команда Ordo M60.4 для безпечного повернення до попереднього snapshot. Restore не видаляє історію, а додає окрему append-only подію з evidence report, state snapshot, session trace step і оновленням live session state.

## PathWalk matrix smoke

No-API compatibility smoke for the PathWalk scenario-testing utility. It checks that PathWalk can build and score current M60 runtime packages across `json`, `ordo-code`, and `json,ordo-code` runtime views before real model/API benchmark runs.

## Benchmark readiness

A pre-benchmark condition: the testing utility can generate score files, aggregate summaries, and runtime metadata against the current Ordo runtime protocol without using legacy launchers or direct `compiled/*` reads.


## EXECUTION_TRACE

Повний append-only артефакт історії одного запуску Ordo-процесу. Містить ordered trace events, посилання на state, decisions, gates і outputs, а також replay та integrity metadata. Не є приватним chain of thought.
