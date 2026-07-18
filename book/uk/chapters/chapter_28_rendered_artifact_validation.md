# Розділ 28. Rendered artifact validation

## Навіщо це потрібно

У багатьох процесах модель створює не просто відповідь у чаті, а готовий артефакт: документ, архів, звіт, інструкцію, JSON, YAML, Markdown-файл, PDF, таблицю, пакет для Jira, QA-набір або набір файлів для передачі іншій команді.

На перший погляд здається, що достатньо перевірити шаблон. Якщо шаблон правильний, то й результат має бути правильний. Але в реальній роботі це часто не так.

Шаблон може бути правильним, а згенерований документ — ні.

Наприклад:

- у шаблоні є обовʼязковий розділ, але в готовому файлі він порожній;
- у структурі пакета передбачено 11 файлів, але в архів потрапило 12;
- у README написано одне, а в QA-файлі — інше;
- у JSON вказаний один alias, а в Markdown — інший;
- у шаблоні є gate перед фінальним архівом, але сам архів уже створено до проходження gate;
- у rendered документі випадково залишився placeholder;
- у фінальному файлі зʼявився зайвий технічний фрагмент, якого не мало бути.

Саме тому Ordo має перевіряти не тільки намір, не тільки source-програму і не тільки шаблон. Ordo має перевіряти готовий результат після рендерингу.

![Nebu — ідея: перевіряємо фактично створений артефакт](../assets/mascots/64x64/Nebu_idea_64x64.png)

Це і є `Rendered artifact validation`.

---

## Просте пояснення

`Rendered artifact validation` — це перевірка вже створеного артефакту, а не тільки правил, за якими він мав бути створений.

Можна уявити це так.

Шаблон — це креслення будинку.

Rendered artifact — це вже побудований будинок.

Перевірити креслення корисно, але цього недостатньо. Після будівництва потрібно перевірити сам будинок: чи є двері, чи сходи ведуть туди, куди треба, чи не забули дах, чи електрика підключена правильно, чи кімнати відповідають плану.

Так само і в Ordo:

```text
template validation → перевіряє план
rendered artifact validation → перевіряє фактичний результат
```

---

## Чому це окремий рівень Ordo

У звичайних prompt-процесах модель часто каже:

```text
Я перевірила результат.
```

Але це не завжди означає, що була перевірена фактична структура готового артефакту.

Ordo має змусити процес бути точнішим:

```text
1. Згенеруй артефакт.
2. Прочитай або проаналізуй саме згенерований артефакт.
3. Порівняй його з output contract.
4. Перевір обовʼязкові розділи.
5. Перевір consistency між файлами.
6. Перевір заборонені елементи.
7. Сформуй validation report.
8. Тільки після цього дозволяй handoff.
```

Тобто rendered validation — це gate між створенням результату і передачею результату користувачу.

---

## Основна конструкція

У Ordo цей механізм можна описати так:

```text
RENDER.VALIDATE
```

Ця конструкція означає:

```text
перевірити вже згенерований артефакт як фактичний output, а не тільки як очікувану структуру
```

У простому вигляді:

```yaml
render_validate:
  target: "final_package"
  against:
    - "output_contract"
    - "file_manifest"
    - "mandatory_sections"
    - "consistency_rules"
    - "forbidden_content"
  report: "VALIDATION_REPORT.json"
  blocking: true
```

Ключове слово тут — `blocking`.

![Nebu — увага: failed validation блокує handoff](../assets/mascots/64x64/Nebu_attention_64x64.png)

Якщо rendered validation не пройдено, результат не можна вважати готовим.

---

## Що саме перевіряється

Rendered artifact validation може перевіряти різні рівні.

### 1. Наявність файлів

Наприклад, пакет має містити рівно такі файли:

```text
README.md
SUMMARY.json
VALIDATION_REPORT.json
CONSISTENCY_CHECK_REPORT.json
01_HISTORY_EVENT_PASSPORT_<ALIAS>.md
02_JIRA_TASK_<ALIAS>.md
04_IMPLEMENTATION_PROMPT_<ALIAS>.md
05_QA_PACKAGE_<ALIAS>.md
07_PROCESS_IMPROVEMENT_FEEDBACK_<ALIAS>.md
08_QA_AUTOMATION_SPEC_<ALIAS>.yaml
09_QA_AUTOMATION_README_<ALIAS>.md
```

Rendered validation має перевірити не лише те, що ці файли описані в інструкції, а що вони реально є у фінальному пакеті.

Також потрібно перевірити, що немає зайвих файлів, якщо пакет має бути compact canonical package.

---

### 2. Наявність обовʼязкових розділів

Наприклад, Jira-задача має містити:

```text
- загальний опис проблеми;
- очікувану поведінку;
- критерії прийняття;
- тестові сценарії;
- обмеження;
- залежності;
- що не входить у задачу.
```

Rendered validation має відкрити готовий Markdown-файл і перевірити, що ці розділи справді присутні.

---

### 3. Відсутність placeholder-ів

Це дуже практична перевірка.

Поганий результат:

```text
<ALIAS>
<TODO>
<CONFIRM_SOURCE_FIELD>
[insert description here]
```

Якщо у фінальному артефакті залишився placeholder, це майже завжди означає, що результат не готовий.

Ordo може мати правило:

```yaml
assert_not:
  rendered_artifact_contains:
    - "<TODO>"
    - "<ALIAS>"
    - "TBD"
    - "insert here"
```

---

### 4. Consistency між файлами

Це одна з найважливіших частин.

У складному пакеті одна й та сама інформація часто повторюється в різних місцях:

- alias;
- назва події;
- source field;
- status;
- expected output;
- test case id;
- route/path;
- список файлів;
- рівень змін;
- no-op поведінка;
- rollback rules.

Rendered validation має перевірити, що ці значення не суперечать одне одному.

![Nebu — подумати: consistency часто ламається між файлами](../assets/mascots/64x64/Nebu_thinking_64x64.png)

Наприклад:

```text
README.md каже: alias = LU_CHANGE_STATUS
QA_PACKAGE.md каже: alias = LU_CHANGE_CAPITAL
```

Це не дрібна помилка. Це провал consistency gate.

---

### 5. Відповідність output contract

Output contract визначає, що саме має бути створено.

Rendered artifact validation перевіряє:

```text
чи створено саме те, що було обіцяно
```

Якщо contract каже:

```text
створити тільки аналітичний пакет, без технічної реалізації
```

то в rendered artifact не має зʼявитися:

```text
готовий Java-код
міграції бази
конфігураційні зміни
реальні endpoint-и
```

Якщо contract каже:

```text
не включати зайві файли
```

то архів із зайвими payload-файлами має бути заблокований.

---

### 6. Заборонені дії або заборонений контент

Rendered validation має перевіряти не тільки те, що має бути, а й те, чого не має бути.

Наприклад:

```yaml
assert_not:
  - "final archive before approval"
  - "invented source row"
  - "unconfirmed alias"
  - "hidden implementation details"
  - "extra YAML with local secrets"
```

Це особливо важливо, коли модель працює з архівами, кодом, конфігураціями або документацією для інших команд.

---

## Приклад Ordo Source

```yaml
output:
  id: "history_event_package"
  type: "archive"
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

render_validation:
  id: "G_RENDERED_PACKAGE_VALID"
  target: "history_event_package"
  blocking: true
  checks:
    - required_files_present
    - no_extra_files
    - no_placeholders
    - alias_consistency
    - required_sections_present
    - validation_report_present
    - consistency_report_present
```

---

## Приклад Semantic JSON IR

```json
{
  "op": "RENDER.VALIDATE",
  "id": "G_RENDERED_PACKAGE_VALID",
  "target": "history_event_package",
  "blocking": true,
  "checks": [
    "required_files_present",
    "no_extra_files",
    "no_placeholders",
    "alias_consistency",
    "required_sections_present",
    "validation_report_present",
    "consistency_report_present"
  ],
  "on_fail": {
    "status": "blocked",
    "handoff_allowed": false,
    "required_action": "fix_rendered_artifact"
  }
}
```

---

## Звʼязок із gates

Rendered validation майже завжди має бути gate.

Не просто рекомендацією:

```text
бажано перевірити результат
```

А саме gate:

```text
результат не можна передавати, поки rendered validation не пройдено
```

Тому в Ordo це має бути повʼязано з gate system:

```yaml
gate:
  id: "G_RENDERED_OUTPUT_VALID"
  method: mechanical
  trust_class: deterministic
  type: "rendered_artifact_validation"
  blocking: true
  required_before:
    - "handoff"
    - "archive_delivery"
    - "send_to_developer"
```

---

## Звʼязок із Debug Layer

У debug mode rendered validation має показувати:

```text
- які файли перевірялись;
- які розділи знайдені;
- які правила пройдені;
- які правила провалені;
- які значення порівнювались;
- де саме знайдено inconsistency;
- який gate заблокував handoff.
```

Наприклад:

```yaml
trace_source: "model_self_report"
render_validation_trace:
  target: "final_archive"
  checks:
    - id: "required_files_present"
      status: "passed"
    - id: "no_extra_files"
      status: "failed"
      evidence:
        extra_files:
          - "payload_update.json"
    - id: "alias_consistency"
      status: "passed"

result:
  gate: "G_RENDERED_PACKAGE_VALID"
  status: "blocked"
```

---

## Звʼязок із Test Layer

Rendered artifact validation теж потрібно тестувати.

Наприклад:

```yaml
test:
  id: "TC_RENDER_BLOCKS_EXTRA_FILE"
  method: mechanical
  trust_class: deterministic

fixture:
  package_files:
    - "README.md"
    - "SUMMARY.json"
    - "payload_update.json"

expected:
  gate:
    id: "G_RENDERED_PACKAGE_VALID"
    status: "blocked"

  reason:
    - "extra_file_detected"
```

Або:

```yaml
test:
  id: "TC_RENDER_BLOCKS_PLACEHOLDER"
  method: mechanical
  trust_class: deterministic

fixture:
  file_content:
    path: "02_JIRA_TASK.md"
    content: "Alias: <ALIAS>"

expected:
  gate:
    id: "G_RENDERED_OUTPUT_VALID"
    status: "blocked"

  violation:
    - "placeholder_detected"
```

---

## Звʼязок із Feedback & Improvement Loop

Якщо користувач після отримання артефакту каже:

```text
У README одна назва події, а в QA-файлі інша.
```

Ordo має створити improvement record:

```yaml
improvement_record:
  classification:
    type: "rendered_artifact_inconsistency"
    severity: "high"

  affected_unit:
    kind: "render_validation_rule"
    id: "alias_consistency"

  proposed_patch:
    - "add consistency check between README.md and QA_PACKAGE.md"
    - "add regression test for mismatched event display name"

  suggested_tests:
    - "TC_RENDER_BLOCKS_DISPLAY_NAME_MISMATCH"
```

Тобто кожна помилка у фінальному артефакті має ставати джерелом покращення validation rules.

---

## Типові помилки

### Помилка 1. Перевіряти тільки шаблон

Шаблон може бути правильним, але результат — неправильним.

Ordo має перевіряти rendered artifact.

---

### Помилка 2. Вважати self-check текстовою обіцянкою

Фраза:

```text
Я перевірив результат
```

не дорівнює validation report.

Потрібен структурований gate report.

---

### Помилка 3. Не перевіряти consistency між файлами

У великих пакетах основні помилки часто не в одному файлі, а між файлами.

---

### Помилка 4. Дозволяти handoff після failed validation

Якщо validation failed, handoff має бути заблокований.

---

### Помилка 5. Не тестувати validation rules

Правила перевірки також можуть бути неповними. Їх треба тестувати як частину Ordo-програми.

---

## Міні-вправа

Візьміть будь-який документ або пакет файлів, який модель має створити.

Спробуйте відповісти:

```text
1. Які файли або розділи мають бути обовʼязково?
2. Які placeholder-и не можна залишати?
3. Які значення мають бути однаковими в різних місцях?
4. Яких зайвих файлів або розділів не має бути?
5. Який gate має заблокувати передачу результату?
6. Який validation report має бути сформований?
```

Якщо ви можете відповісти на ці питання, ви вже маєте основу для `RENDER.VALIDATE`.

---

## Короткий підсумок

Rendered artifact validation — це перевірка фактичного результату після його створення.

У Ordo це важливо тому, що модель може правильно зрозуміти шаблон, але помилитися у готовому документі або пакеті.

Головне правило:

```text
не перевірений rendered artifact не можна передавати як готовий результат
```

Для складних процесів `RENDER.VALIDATE` має бути blocking gate перед handoff.

---

<!-- REVIEWED: chapter 28; Nebu markers checked -->
