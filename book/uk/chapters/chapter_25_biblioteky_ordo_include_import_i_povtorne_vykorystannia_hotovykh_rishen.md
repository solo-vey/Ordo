# Розділ 25. Бібліотеки Ordo: include, import і повторне використання готових рішень

## Навіщо це потрібно

Коли Ordo-програма стає більшою за кілька простих кроків, у ній дуже швидко зʼявляються повтори. Одні й ті самі перевірки контракту, однакові gate-и перед фінальним результатом, схожі правила для approval, однакові вимоги до trace, подібні шаблони output, повторювані правила для тестів, regression і coverage.

У звичайних мовах програмування для цього давно існує поняття бібліотеки. Програміст не пише кожного разу все з нуля. Він підключає готовий модуль, функцію, пакет або framework. Наприклад, якщо потрібно працювати з датами, HTTP-запитами, JSON або тестами, розробник бере готову бібліотеку і використовує її у своєму коді.

В Ordo потрібен аналогічний механізм, але адаптований не до класичного коду, а до керування поведінкою AI-моделі. Ordo-бібліотека — це не просто файл із функціями. Це готовий пакет Ordo-конструкцій, які можна підключити до поточної Ordo-програми: gate-и, node-и, status semantics, output templates, approval chains, test patterns, debug rules, domain vocabulary, reusable flows.

Без бібліотек кожен великий playbook починає перетворюватися на ізольований all-in-one документ. У ньому накопичуються власні копії правил, власні формулювання, власні винятки й власні варіанти тих самих перевірок. Через деякий час такі документи стають важкими для підтримки: якщо потрібно змінити одне базове правило, його доводиться шукати в десятках місць.

Бібліотеки дозволяють перенести повторювані рішення в окремі пакети повторного використання і підключати їх явно.

![Nebu — ідея: бібліотека як явний пакет поведінки](../assets/mascots/64x64/Nebu_idea_64x64.png)

## Просте пояснення

У найпростішому вигляді Ordo Library — це готовий набір правил і конструкцій, який можна сказати Ordo-програмі використати.

Наприклад:

```yaml
include:
  - library: "ordo.validation.contract_first"
    version: "0.1"
    as: "contract_first"
```

Це означає: підключити бібліотеку `ordo.validation.contract_first`, використати саме версію `0.1` і дати їй локальне імʼя `contract_first`.

Після цього Ordo-програма може використовувати її частини:

```yaml
use:
  - contract_first.gates
  - contract_first.assertions
  - contract_first.approval_rules
```

Тобто замість того, щоб у кожному playbook-у заново описувати базові правила contract-first execution, ми підключаємо готову бібліотеку і використовуємо її exports.

## Чим бібліотека відрізняється від Core, Profile і Domain Pack

Важливо не змішувати бібліотеки з іншими частинами Ordo.

`Ordo Core` — це базова мова. Він визначає фундаментальні конструкції: intent, contract, state, node, gate, output, status, trace, assertion.

`Ordo Profile` — це спеціалізований режим або стиль використання Ordo. Наприклад, profile для документації, QA, approval, artifact generation, rendered validation.

`Domain Pack` — це пакет знань і правил для конкретної предметної області. Наприклад, History Event Domain Pack або Monitoring Event Domain Pack.

`Ordo Library` — це пакет повторного використання, який може містити частини Core-логіку, profile bindings, предметні блоки або патерни виконання, але не обовʼязково є повним domain pack-ом чи profile.

Бібліотека може бути маленькою. Наприклад, тільки набір стандартних gate-ів для pre-final validation.

Бібліотека може бути середньою. Наприклад, готовий pattern для guided intake.

Бібліотека може бути великою. Наприклад, повний пакет повторного використання для manual QA runbook generation.

Ключова відмінність бібліотеки — її призначення для повторного використання.

## Що може містити Ordo Library

Ordo-бібліотека може містити:

```text
- готові NODE.DEF;
- готові GATE.DEF;
- готові ASSERT.NOT;
- готові STATUS.SEMANTICS;
- готові TEMPLATE.BIND;
- готові OUTPUT.DEF;
- готові RENDER.VALIDATE rules;
- готові EVIDENCE.MATRIX schemas;
- готові APPROVAL.REQUIRE chains;
- готові DEBUG.MODE profiles;
- готові TEST.DEF templates;
- готові REGRESSION.SUITE patterns;
- готові FREEFORM.COVERAGE rules;
- готові патерни виконання;
- готові document templates;
- готові domain-specific rule sets.
```

Тобто бібліотека в Ordo — це пакет поведінки, а не просто пакет тексту.

## Базові мовні конструкції

Для бібліотек Ordo потрібні такі конструкції:

```text
LIB.DEF
INCLUDE
IMPORT
USE
EXPORT
NAMESPACE
ALIAS
VERSION.REQUIRE
COMPAT.CHECK
CONFLICT.DETECT
CONFLICT.RESOLVE
OVERRIDE.ALLOW
OVERRIDE.DENY
TRUST.LEVEL
```

Це мінімальний набір, без якого бібліотеки швидко стануть небезпечними.

## LIB.DEF

`LIB.DEF` описує саму бібліотеку.

Наприклад:

```yaml
library:
  id: "ordo.validation.contract_first"
  version: "0.1"
  name: "Contract-first validation library"

exports:
  gates:
    - "G_CONTRACT_CONFIRMED"
    - "G_NO_FINAL_OUTPUT_WITHOUT_APPROVAL"

  assertions:
    - "ASSERT_NOT_FINAL_BEFORE_CONTRACT"

requires:
  ordo_version: ">=0.11"
```

Цей опис дає Ordo-компілятору зрозуміти, що саме містить бібліотека, що вона експортує і з якою версією Ordo сумісна.

## INCLUDE

`INCLUDE` означає фізичне або логічне підключення бібліотеки до Ordo-програми.

```yaml
include:
  - library: "ordo.validation.contract_first"
    version: "0.1"
    as: "contract_first"
```

Правило Ordo: бібліотеки не повинні підключатися неявно. Якщо playbook використовує бібліотеку, це має бути видно в source і compiled IR.

Погано:

```text
модель сама здогадалась застосувати правила contract-first
```

Добре:

```yaml
include:
  - library: "ordo.validation.contract_first"
    version: "0.1"
```

## IMPORT і USE

`IMPORT` і `USE` можуть мати різну семантику.

`IMPORT` означає: зробити певні exports бібліотеки доступними в поточній Ordo-програмі.

`USE` означає: реально застосувати підключені конструкції в конкретному місці виконання.

Наприклад:

```yaml
import:
  - from: "contract_first"
    items:
      - "G_CONTRACT_CONFIRMED"
      - "ASSERT_NOT_FINAL_BEFORE_CONTRACT"

use:
  - gate: "contract_first.G_CONTRACT_CONFIRMED"
    at: "before_output_generation"
```

Це важливе розділення. Бібліотека може бути підключена, але не всі її частини обовʼязково використовуються.

![Nebu — подумати: include не означає автоматичне використання всього](../assets/mascots/64x64/Nebu_thinking_64x64.png)

## EXPORT

`EXPORT` визначає, що бібліотека дозволяє використовувати зовні.

Наприклад:

```yaml
exports:
  gates:
    - id: "G_CONTRACT_CONFIRMED"
      visibility: "public"

  internal_rules:
    - id: "R_CONTRACT_PARSE_HELPER"
      visibility: "private"
```

Не все всередині бібліотеки має бути доступним. Частина правил може бути внутрішньою реалізацією самої бібліотеки.

## NAMESPACE і ALIAS

Namespace потрібен, щоб уникати конфліктів назв.

Без namespace дві бібліотеки можуть мати gate з однаковою назвою:

```text
G_APPROVAL_REQUIRED
```

Але в різних бібліотеках це можуть бути різні правила.

Тому правильне посилання має бути повним:

```text
contract_first.G_APPROVAL_REQUIRED
artifact_validation.G_APPROVAL_REQUIRED
```

Alias робить довгі назви коротшими:

```yaml
include:
  - library: "ordo.artifact.render_validation"
    version: "0.1"
    as: "render_validation"
```

Після цього можна писати:

```yaml
use:
  - render_validation.G_RENDERED_ARTIFACT_CHECK
```

## Version pinning

Бібліотеки мають підключатися з версією.

Погано:

```yaml
include:
  - library: "ordo.qa.manual_runbook"
```

Добре:

```yaml
include:
  - library: "ordo.qa.manual_runbook"
    version: "0.1"
```

Причина проста: якщо бібліотека зміниться, playbook може почати поводитися інакше. Для Ordo це критично, бо ми керуємо не просто текстом, а поведінкою моделі.

Версія має бути частиною execution contract.

## Compatibility check

Компілятор Ordo має перевіряти сумісність бібліотеки з поточною мовою, profile, domain pack і runtime.

Наприклад:

```yaml
compatibility:
  requires_ordo: ">=0.11"
  requires_profiles:
    - "documentation_runtime"
    - "debug_test_improvement"
  incompatible_with:
    - "legacy_all_in_one_mode"
```

У compiled IR це може бути окремий op:

```json
{
  "op": "LIB.COMPAT.CHECK",
  "library": "ordo.qa.manual_runbook",
  "version": "0.1",
  "requires_ordo": ">=0.11"
}
```

Якщо compatibility check не пройдений, Ordo не повинна мовчки продовжувати виконання.

## Conflict detection

Конфлікти між бібліотеками мають бути явними.

Наприклад, одна бібліотека каже:

```text
ready_for_first_run = можна запускати
```

А інша каже:

```text
ready_for_first_run = потребує ручного підтвердження
```

Ordo не має сама вибирати, хто правий.

Має бути:

```yaml
conflict:
  type: "status_semantics_conflict"
  key: "ready_for_first_run"
  sources:
    - "library_a"
    - "library_b"
  resolution: "required"
```

Після цього можливі варіанти:

```text
- запитати людину;
- застосувати явно заданий priority;
- заблокувати compilation;
- дозволити override тільки з reason.
```

## Override rules

Override — одна з найнебезпечніших частин бібліотек.

Якщо підключена бібліотека може непомітно переписати gate, status або assertion, вся надійність Ordo руйнується.

Тому правило таке:

```text
Будь-який override має бути явним.
```

Наприклад:

```yaml
override:
  allow:
    - target: "contract_first.G_NO_FINAL_OUTPUT_WITHOUT_APPROVAL"
      by: "history_event.G_PRE_ARCHIVE_APPROVAL"
      reason: "domain pack has stricter equivalent gate"
```

Без такого запису override має бути заборонений.

![Nebu — увага: override має бути явним](../assets/mascots/64x64/Nebu_attention_64x64.png)

## Trust level

Не всі бібліотеки однаково надійні. Тому Ordo має підтримувати trust level.

Наприклад:

```yaml
library:
  id: "ordo.validation.contract_first"
  version: "0.1"
  trust_level: "official"
```

Можливі рівні:

```text
official
verified
project_local
experimental
untrusted
```

У production workflows бажано забороняти `experimental` або `untrusted` бібліотеки без окремого approval.

## Бібліотеки і debug/test/improvement layer

Бібліотеки мають бути видимими для debug, testing і improvement.

Якщо gate прийшов із бібліотеки, trace має це показати:

```yaml
trace_source: "model_self_report"
gate_report:
  - gate_id: "contract_first.G_CONTRACT_CONFIRMED"
    source:
      kind: "library"
      id: "ordo.validation.contract_first"
      version: "0.1"
    status: "passed"
```

Якщо користувач вказує проблему, improvement record має вміти привʼязати її до бібліотеки:

```yaml
affected_unit:
  kind: "library"
  id: "ordo.validation.contract_first"
  version: "0.1"
  export: "G_CONTRACT_CONFIRMED"
```

Це дозволяє покращувати не тільки конкретний playbook, а й reusable рішення.

## Бібліотеки і FREEFORM

Бібліотека може містити FREEFORM, але це має бути контрольований FREEFORM.

Погано:

```yaml
freeform:
  text: "тут багато правил, модель сама розбереться"
```

Добре:

```yaml
freeform:
  id: "FF_CONTRACT_EDGE_CASES"
  binding:
    used_by:
      - "G_CONTRACT_CONFIRMED"
    reason: "domain examples are too nuanced for full formalization"
  coverage:
    required: true
```

Якщо бібліотечний FREEFORM часто спричиняє помилки, improvement loop має запропонувати формалізувати його частину.

## Типи бібліотек

Практично Ordo-бібліотеки можна поділити на кілька типів.

### Core utility libraries

Містять універсальні дрібні конструкції: стандартні assertions, common gates, status helpers.

### Profile libraries

Містять готові блоки для документації, QA, approval, validation, rendered artifact checks.

### Domain libraries

Містять reusable частини для конкретної сфери: History Event, Monitoring Event, Legal Review.

### Pattern libraries

Містять патерни виконання: guided intake, contract-first flow, pre-archive approval, self-check before handoff.

### Template libraries

Містять шаблони документів, структури output, package layouts.

### Connector/tool libraries

Містять правила роботи із зовнішніми інструментами, API, файлами, runner-ами.

## Малий приклад

Уявімо Ordo-програму, яка має створити аналітичний пакет.

Без бібліотек вона може містити десятки локальних правил:

```text
- спочатку підтвердити contract;
- не створювати фінальний пакет до approval;
- перевірити rendered artifacts;
- сформувати validation report;
- сформувати consistency report;
- зафіксувати improvement feedback;
- виконати regression tests.
```

З бібліотеками це можна оформити так:

```yaml
include:
  - library: "ordo.validation.contract_first"
    version: "0.1"
    as: "contract_first"

  - library: "ordo.artifact.render_validation"
    version: "0.1"
    as: "render_validation"

  - library: "ordo.debug_test.basic_regression"
    version: "0.1"
    as: "regression"

use:
  - contract_first.required_contract_gates
  - render_validation.pre_handoff_checks
  - regression.minimum_suite
```

Це коротше, чистіше і безпечніше, якщо кожна бібліотека має версію, namespace, compatibility check і tests.

## Типові помилки

Перша помилка — вважати бібліотеку просто шматком тексту. У Ordo бібліотека має бути structured package, який компілятор може перевірити.

Друга помилка — підключати бібліотеки без версій. Це робить поведінку нестабільною.

Третя помилка — дозволяти implicit imports. Якщо модель сама “здогадалася” використати бібліотеку, це не Ordo execution.

Четверта помилка — не фіксувати conflicts. Конфліктні status semantics або gates не можна вирішувати мовчки.

Пʼята помилка — дозволяти hidden override. Бібліотека не повинна непомітно змінювати поведінку основного playbook-а.

Шоста помилка — не тестувати бібліотеки. Якщо пакет повторного використання не має tests і coverage, він просто переносить помилки з одного playbook-а в багато playbook-ів.

## Міні-вправа

Візьміть будь-який великий prompt або playbook і знайдіть у ньому повторювані частини.

Спробуйте виписати:

```text
- які gate-и повторюються;
- які шаблони output повторюються;
- які правила approval повторюються;
- які checks можна винести в reusable library;
- які частини мають бути exported;
- які частини мають залишитися private;
- які версії і compatibility rules потрібні.
```

Після цього спробуйте назвати одну бібліотеку, яка могла б існувати окремо.

Наприклад:

```text
ordo.validation.contract_first
ordo.artifact.pre_handoff_validation
ordo.qa.manual_runbook
ordo.debug_test.basic_regression
```

## Короткий підсумок

Бібліотеки Ordo потрібні для того, щоб не переписувати однакові правила в кожному playbook-у.

Ordo Library — це пакет повторного використання Ordo-конструкцій: gate-ів, node-ів, assertions, status semantics, templates, tests, debug rules, domain rules або патерни виконання.

Бібліотеки мають підключатися явно через include/import/use, мати namespace, alias, version pinning, compatibility checks, conflict detection, explicit override rules і trust level.

Добре спроєктовані бібліотеки роблять Ordo-програми коротшими, стабільнішими і зручнішими для розвитку.

Погано спроєктовані бібліотеки створюють приховані залежності, конфлікти і неконтрольовані зміни поведінки моделі.

Головне правило:

```text
У Ordo бібліотека — це не прихований текстовий фрагмент, а явний, версіонований і перевірюваний пакет поведінки.
```

---

<!-- REVIEWED: chapter 25; Nebu markers checked -->
