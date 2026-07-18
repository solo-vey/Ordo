# Розділ 41. Contract → Artifact Coverage і Go/No-Go

Ordo потрібен не тільки для того, щоб провести людину через правильні питання. Його цінність зʼявляється тоді, коли підтверджені відповіді не губляться по дорозі до фінальних документів.

У звичайному процесі це часта проблема: аналітик підтвердив alias, назви події, джерело, поля, normalization, payload, тестову стратегію, але частина цього не потрапила в паспорт, Jira task або implementation prompt. Формально діалог пройшов успішно, але пакет став неповним.

Тому в Ordo вводиться окремий шар:

```text
confirmed contracts
→ expected artifact coverage
→ generated artifacts
→ deterministic validation
→ consistency report
→ go/no-go decision
```

## Contract

`Contract` — це не просто домовленість у чаті. Це структурований обʼєкт, який має статус.

Наприклад:

```json
{
  "kind": "contract",
  "id": "G_EVENT_IDENTITY_CONTRACT",
  "status": "confirmed",
  "fields": {
    "alias": {
      "value": "LU_CHANGE_CAPITAL",
      "status": "confirmed",
      "required": true
    },
    "name_uk": {
      "value": "Зміна статутного капіталу компанії",
      "status": "confirmed",
      "required": true
    }
  }
}
```

Поле може бути `missing`, `candidate`, `proposed`, `confirmed`, `blocked` або `not_applicable`. Це важливо: модель не має права подати `candidate` як підтверджене рішення.

## Artifact requirement

`Artifact requirement` описує, де саме має зʼявитися підтверджений контракт.

Наприклад, якщо підтверджено `HistoryEvent output contract`, його ключові поля мають бути не тільки в QA-пакеті, а також у паспорті, Jira task, implementation prompt і JSON-звітах.

```json
{
  "kind": "artifact_requirement",
  "id": "REQ_HISTORY_EVENT_OUTPUT_IN_PASSPORT_AND_JIRA",
  "when": {
    "contract": "G_HISTORY_EVENT_OUTPUT_CONTRACT",
    "status": "confirmed"
  },
  "requires": [
    {
      "artifact": "01_HISTORY_EVENT_PASSPORT",
      "must_include_fields": ["type", "sub_type", "source", "group", "groupPriority", "isEdr"]
    },
    {
      "artifact": "02_JIRA_TASK",
      "must_include_fields": ["type", "sub_type", "source", "group", "groupPriority", "isEdr"]
    }
  ]
}
```

## Чому compile недостатньо

`compile` може перевірити, що в Ordo package є правильні посилання: contract існує, artifact існує, requirement не посилається на невідомий id.

Але `compile` не може гарантувати, що згенерований markdown-файл реально містить потрібне поле. Для цього потрібна перевірка rendered artifacts.

## Rendered artifact validation

Rendered artifact validation перевіряє вже створені файли:

```text
01_HISTORY_EVENT_PASSPORT_<ALIAS>.md
02_JIRA_TASK_<ALIAS>.md
04_IMPLEMENTATION_PROMPT_<ALIAS>.md
05_QA_PACKAGE_<ALIAS>.md
SUMMARY.json
VALIDATION_REPORT.json
CONSISTENCY_CHECK_REPORT.json
```

Цей шар має відповідати на питання:

```text
Чи всі confirmed contracts реально присутні в потрібних документах?
Чи немає суперечностей між Passport, Jira, QA і JSON reports?
Чи не записано candidate/proposed значення як confirmed?
Чи не пропущено тестову стратегію?
```

## Go/No-Go

Після всіх перевірок Ordo має видати коротке машинозчитуване рішення:

```json
{
  "kind": "go_no_go",
  "status": "no_go_requires_artifact_fix",
  "blocking_issues": [
    {
      "code": "ORDO-COV-002",
      "message": "Confirmed contract field group is missing from Passport"
    }
  ],
  "warnings": []
}
```

Для людини це можна пояснити просто:

```text
Пакет не готовий: підтверджене поле group не потрапило в паспорт історичної події.
```

## Що це змінює для AI Ordo Developer

AI Ordo Developer більше не просто створює документи за шаблонами. Він має довести, що:

1. усі важливі contracts підтверджені;
2. для кожного confirmed contract є artifact coverage;
3. rendered documents не втратили підтверджені значення;
4. consistency report не містить blocking issues;
5. go/no-go decision дозволяє передавати пакет далі.

Це робить Ordo не просто мовою інструкцій, а мовою контрольованої передачі рішень у фінальні артефакти.

## M46.2: перший виконуваний шар перевірки

На рівні M46.1 ми описали нові поняття як частину мови. На рівні M46.2 вони починають працювати в CLI, але ще обмежено: Ordo перевіряє не самі згенеровані файли, а декларативний маршрут від контракту до артефакту.

Це означає:

```text
confirmed contract
→ artifact_requirement
→ required artifact
→ required contract fields
```

Якщо пакет каже, що контракт підтверджений, але не вказує, у яких артефактах він має бути відображений, `ordo coverage` має завершитися з помилкою.

Якщо `artifact_requirement` посилається на поле, якого немає в контракті, `ordo compile` має завершитися з помилкою. Це важливо: помилка в моделі покриття має ловитися до того, як аналітик або PM отримає красиві, але неповні документи.

M46.2 ще не читає rendered Markdown або JSON. Це наступний шар. Поточний шар відповідає на простіше питання: чи сам Ordo package взагалі знає, які підтверджені контракти мають потрапити в які артефакти.

Практичний pipeline тепер виглядає так:

```text
lint
→ compile       # reference checks для contract/artifact model
→ coverage      # completeness checks для confirmed contracts
→ validate-state
→ generate-output
→ validate-artifacts   # наступний шар
→ consistency          # наступний шар
→ go-no-go             # фінальне рішення
```



## M46.3: перевірка вже згенерованих артефактів

На рівні M46.3 зʼявляється перша виконувана команда для rendered artifact validation:

```bash
ordo validate-artifacts <package>
```

Вона читає не тільки Ordo Source, а й фактичні файли в `generated_outputs/`. Це важливо, бо `compile` і `coverage` можуть довести, що маршрут `contract → artifact` описаний, але вони ще не доводять, що готовий Markdown або JSON справді містить підтверджене значення.

Приклад проблеми:

```text
G_EVENT_IDENTITY_CONTRACT.event_alias = LU_CHANGE_CAPITAL
але 02_JIRA_TASK_LU_CHANGE_CAPITAL.md не містить LU_CHANGE_CAPITAL
```

У такому випадку `validate-artifacts` має повернути blocking issue з кодом `ORDO-COV-002`.

Поточний шар M46.3 ще не є повним semantic consistency engine. Він виконує детерміновану перевірку наявності підтверджених значень у потрібних rendered files. Наступний шар — `consistency` — має перевіряти суперечності між Passport, Jira, QA, Prompt і JSON-звітами.

## M46.4: Consistency report between generated artifacts

Після `validate-artifacts` Ordo має ще один рівень перевірки: `consistency`.

`validate-artifacts` відповідає на питання: “чи є підтверджене значення в потрібному документі?”.

`consistency` відповідає на інше питання: “чи всі згенеровані документи говорять одне й те саме про один і той самий підтверджений контракт?”.

Типовий приклад:

```text
alias = LU_CHANGE_CAPITAL
```

Якщо Passport містить `LU_CHANGE_CAPITAL`, але Jira task містить інший alias або не містить alias взагалі, пакет не можна вважати готовим до передачі розробнику. У такому випадку `ordo consistency` має сформувати `CONSISTENCY_CHECK_REPORT.json` із blocking issue.

Мінімальний pipeline для аналітичного пакета тепер такий:

```text
lint
→ compile
→ coverage
→ intake/run
→ generate-output
→ validate-output
→ validate-artifacts
→ consistency
```

Це не замінює ревʼю аналітика, але прибирає клас помилок, коли підтверджений контракт є в процесі, але в різних фінальних документах він відображений неповно або неузгоджено.

## M46.5: фінальний go/no-go helper

Після `validate-artifacts` і `consistency` потрібна одна коротка відповідь: чи можна передавати generated package далі. Для цього додається команда:

```bash
ordo go-no-go <package>
```

Вона не замінює окремі перевірки, а збирає їх в один pipeline:

```text
lint → compile → coverage → validate-state → validate-artifacts → consistency → go/no-go
```

Результатом є `reports/GO_NO_GO_REPORT.json`. Якщо є хоча б один blocking issue, команда повертає no-go статус і ненульовий exit code.

Важливо: це deterministic helper, а не виконання ШІ-моделі чи бізнесового runtime. Команда відповідає тільки на питання: чи узгоджені Ordo source, підтверджені contracts, generated artifacts і consistency report.

## M46.6: pre-release audit and state reuse

M46.6 не додає новий великий мовний шар. Це pre-release audit після M46.1–M46.5. Головна перевірка: чи вся нова лінія `contract → artifact → consistency → go/no-go` працює як єдиний helper pipeline.

Практичне уточнення M46.6: якщо guided intake уже був виконаний і пакет має `reports/intake_report.json`, команда `ordo go-no-go <package>` може використати цей state без повторного `--answers`. Це краще відповідає реальному процесу:

```text
intake → generate-output → validate-artifacts → consistency → go-no-go
```

Це не змінює принцип: `go-no-go` залишається deterministic helper і не виконує AI model або бізнесовий runtime. Він лише перевіряє, чи підтверджені contracts дійшли до generated artifacts і чи артефакти не суперечать одне одному.

## M46.7: чистий pre-release candidate

M46.7 не вводить нову семантику мови. Це крок консолідації перед pre-release: вихідний архів має містити source-файли, документацію, тести й package definitions, але не має нести за собою старі результати локальних запусків.

Практичне правило M46.7:

```text
compiled/          generated by ordo compile
reports/           generated by helper commands
runtime/           generated by intake/run flows
generated_outputs/ generated by ordo generate-output
```

У source archive ці каталоги можуть містити лише `.gitkeep`. Реальні reports, compiled IR, runtime snapshots і generated documents мають створюватися поточним запуском CLI. Це підтримує головний принцип Ordo: не довіряти старому самозвіту, а відтворювати evidence з актуального source state.

