# Розділ 32. Package generation

## Навіщо це потрібно

У попередніх розділах ми розглядали Ordo як мову, що керує діалогом, збирає state, обирає path і проходить gates. Але у великих робочих процесах кінцевий результат майже ніколи не є просто однією відповіддю в чаті.

Часто результатом має бути пакет:

```text
набір markdown-документів;
JSON-звіт;
YAML-специфікація;
README;
QA-пакет;
Jira-опис;
validation report;
archive для передачі в роботу.
```

Саме тут зʼявляється тема `Package generation`.

Package generation — це не момент, коли модель “просто створює файли”. Це окремий етап Ordo-виконання, який має свій contract, gates, output definitions, validation і handoff.

Якщо цей етап не формалізувати, модель може:

```text
- створити зайві файли;
- пропустити обовʼязкові файли;
- змішати бізнесову і технічну документацію;
- не узгодити README з фактичним складом пакета;
- створити validation report, який не перевіряє реальний пакет;
- покласти в архів проміжні файли;
- видати пакет до підтвердження contract gates.
```

Ordo має зробити package generation керованою дією.

---

## Просте пояснення

Уявімо, що Ordo-програма — це не просто інструкція, а виробнича лінія.

Спочатку вона збирає вимоги. Потім перевіряє contract. Потім формує документи. Потім перевіряє їх. Потім збирає архів. Потім передає результат людині.

Package generation — це фінальна виробнича ділянка цієї лінії.

Вона має відповідати на питання:

```text
що саме створюємо;
з яких файлів складається пакет;
які файли є обовʼязковими;
які файли заборонені;
які формати допустимі;
які gates мають бути пройдені до генерації;
як перевірити, що пакет консистентний;
що саме передається користувачу.
```

---

## Package як Ordo Output

У простій задачі output може бути таким:

```yaml
output:
  type: "message"
  format: "text"
```

Але для package generation output має бути значно точнішим:

```yaml
output:
  type: "package"
  id: "history_event_analysis_package"
  required_files:
    - "README.md"
    - "SUMMARY.json"
    - "VALIDATION_REPORT.json"
    - "CONSISTENCY_CHECK_REPORT.json"
    - "01_HISTORY_EVENT_PASSPORT_<ALIAS>.md"
    - "02_JIRA_TASK_<ALIAS>.md"
    - "04_IMPLEMENTATION_PROMPT_<ALIAS>.md"
    - "05_QA_PACKAGE_<ALIAS>.md"
    - "07_PROCESS_IMPROVEMENT_FEEDBACK_<ALIAS>.md"
    - "08_QA_AUTOMATION_SPEC_<ALIAS>.yaml"
    - "09_QA_AUTOMATION_README_<ALIAS>.md"
  forbidden_files:
    - "drafts/*"
    - "tmp/*"
    - "raw_notes/*"
```

Така структура дозволяє моделі не гадати, що має бути в пакеті.

---

## Package generation не має починатися одразу

Одна з головних помилок у великих playbook-ах — створювати фінальний пакет занадто рано.

В Ordo має бути правило:

```text
Фінальний пакет не створюється, поки не пройдені всі gates, які впливають на його зміст.
```

Наприклад:

```yaml
gates_before_package_generation:
  - "G_INTENT_CONFIRMED"
  - "G_CONTRACT_CONFIRMED"
  - "G_PATH_SELECTED"
  - "G_REQUIRED_VALUES_CONFIRMED"
  - "G_OUTPUT_SET_CONFIRMED"
  - "G_QA_SCOPE_CONFIRMED"
```

Якщо хоча б один gate не пройдено, Ordo має зупинитися:

```yaml
package_generation:
  status: "blocked"
  blocked_by:
    - "G_REQUIRED_VALUES_CONFIRMED"
  message: "Пакет ще не можна формувати, бо не підтверджені required values."
```

Це важлива різниця між prompt-ом і Ordo. Prompt часто намагається виконати прохання негайно. Ordo спочатку перевіряє, чи має право це робити.

---

## Package plan

Перед створенням файлів Ordo має сформувати package plan.

```yaml
package_plan:
  package_id: "PKG_HISTORY_EVENT_LU_CHANGE_STATUS"
  alias: "LU_CHANGE_STATUS"

  files:
    - path: "README.md"
      purpose: "пояснює склад пакета і порядок використання"
      required: true

    - path: "01_HISTORY_EVENT_PASSPORT_LU_CHANGE_STATUS.md"
      purpose: "аналітичний паспорт історичної події"
      required: true

    - path: "05_QA_PACKAGE_LU_CHANGE_STATUS.md"
      purpose: "ручне тестування і QA-сценарії"
      required: true

  validation:
    required: true
    reports:
      - "VALIDATION_REPORT.json"
      - "CONSISTENCY_CHECK_REPORT.json"
```

Package plan — це контракт між Ordo-програмою і фінальним artifact.

Якщо в package plan є 11 файлів, то у фінальному архіві має бути саме очікуваний набір файлів, якщо немає окремого підтвердженого винятку.

---

## Rendered artifact validation

Package generation тісно повʼязаний із `Rendered artifact validation`.

Не достатньо перевірити шаблон. Потрібно перевірити вже створений результат.

Погано:

```text
Шаблон README містить секцію "Склад пакета", отже все добре.
```

Добре:

```text
Фактичний README містить список файлів, який збігається з реальним архівом.
```

Ordo має перевіряти:

```text
- чи всі required files створені;
- чи немає forbidden files;
- чи README описує фактичний склад;
- чи SUMMARY.json збігається з файлами пакета;
- чи validation report посилається на реальні перевірки;
- чи всі alias/file names узгоджені;
- чи немає placeholder-ів;
- чи немає суперечностей між документами.
```

---

## Self-check перед handoff

Перед передачею пакета користувачу має бути self-check.

```yaml
self_check:
  required: true
  before:
    - "handoff"
    - "archive_delivery"

  checks:
    - id: "SC_REQUIRED_FILES"
      description: "усі обовʼязкові файли присутні"

    - id: "SC_NO_FORBIDDEN_FILES"
      description: "немає заборонених або проміжних файлів"

    - id: "SC_README_MATCHES_PACKAGE"
      description: "README відповідає фактичному пакету"

    - id: "SC_VALIDATION_REPORT_PRESENT"
      description: "validation report створений"

    - id: "SC_CONSISTENCY_REPORT_PRESENT"
      description: "consistency check report створений"
```

Якщо self-check не пройдений, пакет не має передаватися.

```yaml
handoff:
  status: "blocked"
  reason: "self_check_failed"
```

---

## Package generation у compiled IR

У compiled IR це може виглядати так:

```json
[
  {
    "op": "OUTPUT.DEF",
    "id": "OUT_ANALYTICAL_PACKAGE",
    "output_type": "package",
    "required_files": [
      "README.md",
      "SUMMARY.json",
      "VALIDATION_REPORT.json"
    ]
  },
  {
    "op": "GATE.REQUIRE",
    "id": "G_BEFORE_PACKAGE",
    "requires": [
      "G_CONTRACT_CONFIRMED",
      "G_OUTPUT_SET_CONFIRMED"
    ]
  },
  {
    "op": "PACKAGE.PLAN",
    "id": "PKG_PLAN_1",
    "from_output": "OUT_ANALYTICAL_PACKAGE"
  },
  {
    "op": "PACKAGE.GENERATE",
    "id": "PKG_GENERATE_1",
    "allowed_after": "G_BEFORE_PACKAGE"
  },
  {
    "op": "RENDER.VALIDATE",
    "id": "VALIDATE_RENDERED_PACKAGE"
  },
  {
    "op": "GATE.REPORT",
    "id": "G_PACKAGE_VALIDATED"
  }
]
```

Це ще раз показує, що package generation — не проста генерація тексту, а execution phase.

---

## Package generation і debug mode

У debug mode Ordo має пояснити:

```text
- чому пакет можна або не можна створювати;
- які gates дозволили package generation;
- які outputs мали бути створені;
- які файли реально створені;
- які перевірки пройдені;
- які warnings залишились;
- який artifact передано в handoff.
```

Наприклад:

```yaml
package_debug:
  generation_allowed: false
  blocked_by:
    - "G_QA_SCOPE_CONFIRMED"
  reason: "QA scope was not confirmed by user"
```

Або:

```yaml
package_debug:
  generation_allowed: true
  required_files_expected: 11
  required_files_created: 11
  forbidden_files_found: 0
  validation_status: "passed"
```

---

## Package generation і improvement loop

Package generation часто породжує корисні зауваження.

Користувач може сказати:

```text
у пакеті не вистачає runbook для тестувальника
```

або:

```text
README не пояснює, який файл відкривати першим
```

Ordo має створити improvement record:

```yaml
improvement_record:
  type: "package_structure_improvement"
  affected_unit:
    kind: "output_definition"
    id: "OUT_ANALYTICAL_PACKAGE"
  proposed_patch:
    - "add 10_ANALYST_RUNBOOK.md to required_files"
    - "update README required sections"
  suggested_test:
    id: "TC_PACKAGE_README_START_HERE"
```

Так структура пакетів стає кращою через контрольований цикл покращення.

---

## Типові помилки

### Помилка 1. Створювати пакет без package plan

Без плану модель може створити красивий, але неправильний набір файлів.

### Помилка 2. Перевіряти шаблон, а не створений artifact

Шаблон може бути правильним, але конкретний файл може бути порожнім або суперечливим.

### Помилка 3. Не розділяти draft і final

Проміжні нотатки не повинні випадково потрапляти у фінальний пакет.

### Помилка 4. Не блокувати handoff після failed validation

Якщо validation failed, пакет не готовий.

### Помилка 5. Вважати архів “готовим”, бо він створений

Архів готовий тільки після self-check, validation і consistency check.

---

## Міні-вправа

Візьміть будь-який процес, де результатом є набір файлів.

Наприклад:

```text
Пакет документів для зміни monitoring event.
```

Спробуйте визначити:

```text
1. Які файли мають бути required?
2. Які файли мають бути forbidden?
3. Який README потрібен?
4. Які gates мають бути пройдені до генерації?
5. Який validation report потрібен?
6. Що має блокувати handoff?
```

---

## Короткий підсумок

Package generation — це окрема execution phase в Ordo. Вона має бути керованою, перевірюваною і заблокованою до проходження необхідних gates.

Ordo не просто створює файли. Вона спочатку визначає package contract, формує package plan, генерує required artifacts, перевіряє rendered result, виконує self-check і тільки після цього передає пакет користувачу.

Це дозволяє працювати з великими playbook-ами не як з хаотичною генерацією документів, а як із контрольованим виробництвом artifacts.
