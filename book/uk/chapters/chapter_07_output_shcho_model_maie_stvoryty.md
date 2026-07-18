# Розділ 7. Output: що модель має створити

## 7.1. Навіщо Ordo окремо описує Output

У багатьох prompt-ах результат описаний нечітко.

Користувач пише:

```text
Підготуй мені пакет документів.
```

Але що саме входить у пакет?

Один документ?
Три файли?
Markdown?
JSON?
YAML?
PDF?
Чернетка в чаті?
Архів?
Звіт про перевірку?

Якщо це не визначити, модель починає вирішувати сама. Іноді це працює. Але в складних процесах така свобода небезпечна.

У Ordo результат має бути описаний явно.

![Nebu — ідея: Output як контракт результату](../assets/mascots/64x64/Nebu_idea_64x64.png)

Для цього використовується `OUTPUT.DEF`.

`OUTPUT.DEF` відповідає на питання:

```text
Що саме модель має створити?
```

Не в загальних словах, а як перевірюваний контракт.

---

## 7.2. Output — це не тільки текстова відповідь

У простому діалозі output — це відповідь у чаті.

Наприклад:

```text
Ось короткий підсумок.
```

Але в Ordo output може бути різним:

```text
документ;
набір документів;
JSON-звіт;
YAML-специфікація;
таблиця;
лист;
Jira-задача;
QA runbook;
automation spec;
архів;
короткий handoff-блок;
статус blocked із поясненням.
```

Тому output треба описувати як частину contract.

Приклад:

```json
{
  "op": "OUTPUT.DEF",
  "id": "OUT_HISTORY_EVENT_COMPACT_PACKAGE",
  "kind": "file_set",
  "required_files": [
    "README.md",
    "SUMMARY.json",
    "VALIDATION_REPORT.json",
    "CONSISTENCY_CHECK_REPORT.json",
    "01_HISTORY_EVENT_PASSPORT_<ALIAS>.md",
    "02_JIRA_TASK_<ALIAS>.md",
    "04_IMPLEMENTATION_PROMPT_<ALIAS>.md",
    "05_QA_PACKAGE_<ALIAS>.md",
    "07_PROCESS_IMPROVEMENT_FEEDBACK_<ALIAS>.md",
    "08_QA_AUTOMATION_SPEC_<ALIAS>.yaml",
    "09_QA_AUTOMATION_README_<ALIAS>.md"
  ]
}
```

Тепер модель не може вирішити, що достатньо одного короткого walkthrough.

Output contract каже: потрібен саме набір із визначених файлів.

---

## 7.3. Output має бути повʼязаний із terminal path

У процесі з деревом рішень різні terminal paths можуть мати різні outputs.

Наприклад, у support-процесі:

```text
incident ready → INCIDENT_REPORT.md + CUSTOMER_REPLY.md
incident needs triage → INCIDENT_TRIAGE_NOTE.md
change ready → CHANGE_BRIEF.md + ACCEPTANCE_CHECKLIST.md
change unclear → CHANGE_CLARIFICATION_NOTE.md
```

Це означає, що output не завжди один і той самий. Він залежить від обраного шляху.

В Ordo це можна описати так:

```yaml
terminal_outputs:
  T_INCIDENT_READY:
    outputs:
      - INCIDENT_REPORT.md
      - CUSTOMER_REPLY.md

  T_INCIDENT_NEEDS_TRIAGE:
    outputs:
      - INCIDENT_TRIAGE_NOTE.md

  T_CHANGE_READY:
    outputs:
      - CHANGE_BRIEF.md
      - ACCEPTANCE_CHECKLIST.md

  T_CHANGE_NEEDS_CLARIFICATION:
    outputs:
      - CHANGE_CLARIFICATION_NOTE.md
```

Це захищає процес від помилки, коли модель створює неправильний документ для правильного шляху.

---

## 7.4. Output може бути дозволений або заблокований

Не кожен output можна створювати в будь-який момент.

Наприклад, фінальний archive не можна створювати, якщо contracts не підтверджені.

Тому output має мати умови готовності.

Приклад:

```json
{
  "op": "OUTPUT.DEF",
  "id": "OUT_FINAL_ARCHIVE",
  "kind": "zip_archive",
  "allowed_when": [
    "path_confirmed",
    "mandatory_contracts_confirmed",
    "required_documents_approved",
    "validation_status_go"
  ],
  "blocked_when": [
    "unresolved_mandatory_contract",
    "proposed_contract_used_as_confirmed",
    "approval_missing",
    "validation_status_no_go"
  ]
}
```

![Nebu — увага: Output дозволений тільки після gates](../assets/mascots/64x64/Nebu_attention_64x64.png)

Це важливо: output — це не тільки “що створити”, а й “коли це дозволено створити”.

---

## 7.5. Draft output і final output

У реальному житті модель часто має створити спочатку чернетку.

Наприклад:

```text
спочатку draft passport у чаті;
потім користувач погоджує;
потім draft Jira task;
потім погодження;
потім QA package;
потім automation spec;
і тільки після approvals — фінальний archive.
```

Це означає, що є різні рівні output:

```text
draft output;
review output;
approved output;
final output.
```

У Ordo це треба описувати явно.

Наприклад:

```yaml
outputs:
  passport_draft:
    file: "01_HISTORY_EVENT_PASSPORT_<ALIAS>.md"
    status: draft
    requires_approval: true

  passport_final:
    file: "01_HISTORY_EVENT_PASSPORT_<ALIAS>.md"
    status: approved
    allowed_when:
      - passport_approval_passed
```

Без цього модель може переплутати чернетку з фінальним документом.

---

## 7.6. Output і Template

У багатьох Ordo-процесах output створюється не з нуля, а за шаблоном.

Наприклад:

```text
Jira task має мати Summary, Context, Acceptance criteria, Out of scope, QA reference data.
```

Тоді одного `OUTPUT.DEF` недостатньо. Потрібен зв’язок із template.

Це вже конструкція профілю:

```text
TEMPLATE.BIND
```

Приклад:

```json
{
  "op": "TEMPLATE.BIND",
  "output": "02_JIRA_TASK_<ALIAS>.md",
  "template": "templates/TEMPLATE_JIRA_TASK.md",
  "required_sections": [
    "Summary",
    "Context",
    "Acceptance criteria",
    "Out of scope",
    "QA reference data",
    "Test coverage"
  ]
}
```

`OUTPUT.DEF` каже, що файл має існувати.

`TEMPLATE.BIND` каже, за якою структурою його створити.

---

## 7.7. Output має бути перевірюваним

Якщо output не можна перевірити, модель може сказати, що все готово, хоча це не так.

Поганий output contract:

```text
Створи хороший QA package.
```

Що таке “хороший”? Для моделі це може бути короткий summary. Для тестувальника — повний покроковий runbook.

Кращий output contract:

```yaml
output:
  file: "05_QA_PACKAGE_<ALIAS>.md"
  required_for_each_executable_tc:
    - goal
    - preconditions
    - source_lookup_before_action
    - preflight_restore
    - rest_action
    - source_lookup_after_action
    - changerecord_lookup_or_expected_absence
    - history_processing_step
    - history_event_lookup_or_expected_absence
    - change_errors_lookup
    - rollback
    - post_rollback_source_lookup
    - expected_result
    - diagnostics
```

Тепер output можна перевірити.

Модель не може обмежитися фразою “дивись загальний flow”.

---

## 7.8. Output може бути не створений — і це теж результат

Іноді правильний результат — не створити документ.

Наприклад, якщо mandatory contracts не підтверджені, правильна поведінка не “вигадати пакет”, а зупинитися.

Тоді output може бути таким:

```json
{
  "op": "OUTPUT.DEF",
  "id": "OUT_BLOCKED_STATUS",
  "kind": "handoff_status",
  "status": "blocked_requires_confirmation",
  "include": [
    "missing_contracts",
    "open_questions",
    "next_required_action"
  ]
}
```

![Nebu — подумати: blocked handoff теж результат](../assets/mascots/64x64/Nebu_thinking_64x64.png)

Це важлива ідея.

У Ordo результатом може бути не тільки готовий artifact, а й чесний blocked handoff.

Краще чесно сказати:

```text
Пакет не можна фіналізувати, бо не підтверджено HistoryEvent.item.values.
```

ніж створити красивий, але неправильний документ.

---

## 7.9. Output і Handoff

Output — це те, що створюється.

Handoff — це те, як це передається далі.

Наприклад, output може бути набором файлів, а handoff — коротким повідомленням:

```text
Статус: ready_for_review
Створено: passport draft, Jira draft, QA draft
Блокери: automation runner contract not confirmed
Наступна дія: погодити QA package
```

У Ordo ці речі краще не змішувати.

`OUTPUT.DEF` описує artifact.

`HANDOFF.EMIT` описує передачу статусу користувачу або наступному процесу.

Приклад:

```json
{
  "op": "HANDOFF.EMIT",
  "include": [
    "status",
    "created_outputs",
    "gate_report",
    "open_questions",
    "next_action"
  ]
}
```

---

## 7.10. Типові помилки з Output

Перша помилка — описати output занадто загально.

```text
Зроби пакет.
```

Друга помилка — не сказати, скільки файлів має бути.

Третя помилка — не відрізнити draft від final.

Четверта помилка — не прив’язати output до template.

П’ята помилка — не описати readiness conditions.

Шоста помилка — вважати, що якщо модель щось написала, то output уже valid.

Сьома помилка — не передбачити blocked output.

У складних процесах правильне “не можу фіналізувати, бо…” часто цінніше за неправильне “готово”.

---

## 7.11. Короткий підсумок розділу

`OUTPUT.DEF` визначає, що саме модель має створити.

Output може бути:

```text
відповіддю в чаті;
документом;
набором документів;
JSON-звітом;
YAML-специфікацією;
архівом;
blocked handoff status.
```

Хороший output contract має відповідати на питання:

```text
що створюємо;
у якому форматі;
за яким шаблоном;
коли це дозволено;
що блокує створення;
як перевірити результат;
чи це draft, review або final.
```

Головний принцип:

```text
результат має бути не просто красивим, а дозволеним, структурованим і перевірюваним.
```

---

## Міні-вправа

Візьміть задачу:

```text
Модель має підготувати документ для передачі розробнику.
```

Опишіть `OUTPUT.DEF`:

```yaml
output:
  id: OUT_DEVELOPER_HANDOFF
  kind: document
  file_name: "IMPLEMENTATION_PROMPT.md"
  required_sections:
    - goal
    - context
    - files_to_check
    - required_changes
    - what_not_to_change
    - tests
    - acceptance_criteria
  status: draft
  allowed_when:
    - business_contract_confirmed
  blocked_when:
    - missing_acceptance_criteria
    - unresolved_scope
```

Потім дайте відповідь:

```text
1. Які секції є mandatory?
2. Що блокує створення final version?
3. Який template потрібен?
4. Як перевірити, що rendered document не порожній?
```

---

<!-- REVIEWED: chapter 07; Nebu markers checked -->
