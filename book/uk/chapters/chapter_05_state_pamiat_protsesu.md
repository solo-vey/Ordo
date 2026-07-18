# Розділ 5. State: памʼять процесу

## 5.1. Навіщо Ordo потрібен State

Коли людина веде складний процес, вона майже завжди тримає в голові проміжний стан.

Наприклад, аналітик памʼятає:

```text
- який тип задачі вже обрано;
- які відповіді користувач уже дав;
- які дані ще відсутні;
- які припущення поки не підтверджені;
- які документи вже створені;
- які gates ще не пройдені;
- чи можна переходити до фінального результату.
```

У короткій розмові це не проблема. Якщо користувач просить переписати одне речення, моделі майже не потрібна складна памʼять процесу.

Але якщо задача складається з багатьох кроків, без явного стану модель починає губитися. Вона може забути, що вже було підтверджено. Може вдруге поставити те саме питання. Може вважати припущення підтвердженим фактом. Може перейти до генерації документа, хоча обовʼязкові дані ще не зібрані.

`State` в Ordo — це явна памʼять процесу.

![Nebu — ідея: State як памʼять процесу](../assets/mascots/64x64/Nebu_idea_64x64.png)

Не памʼять моделі “десь у контексті”, а структурований обʼєкт, який показує:

```text
що вже відомо;
що ще невідомо;
що підтверджено;
що тільки запропоновано;
що заблоковано;
який наступний дозволений крок.
```

Іншими словами, State відповідає на питання:

```text
Де ми зараз у процесі?
```

---

## 5.2. Чим State відрізняється від Context

На перший погляд `context` і `state` можуть здатися схожими. Обидва містять дані. Але їхня роль різна.

`Context` — це те, з чим модель працює.

Наприклад:

```text
вхідний текст;
source row;
документ користувача;
історичний приклад;
JSON payload;
витяг із playbook-а.
```

`State` — це те, що модель уже вирішила або зафіксувала в процесі виконання.

Наприклад:

```text
обраний path;
поточний node;
відповіді користувача;
підтверджені контракти;
відкриті питання;
статуси документів;
результати gates.
```

Можна сказати так:

```text
Context — це матеріал.
State — це поточне положення процесу.
```

Або ще простіше:

```text
Context відповідає на питання: “З чим ми працюємо?”
State відповідає на питання: “Що ми вже зробили і що дозволено далі?”
```

![Nebu — подумати: Context проти State](../assets/mascots/64x64/Nebu_thinking_64x64.png)

---

## 5.3. Простий приклад State

Уявімо невеликий процес: модель має допомогти користувачу підготувати відповідь клієнту про інцидент.

Перший вузол питає тип звернення:

```text
1. incident
2. change_request
```

Користувач відповідає:

```text
incident
```

Модель має не просто перейти до наступного питання. Вона має оновити стан:

```yaml
state:
  request_type: incident
  current_node: N2_INCIDENT_SEVERITY
  completed_nodes:
    - N1_REQUEST_TYPE
```

Далі модель питає критичність. Користувач відповідає:

```text
high
```

State оновлюється:

```yaml
state:
  request_type: incident
  severity: high
  current_node: N3_INCIDENT_AREA
  completed_nodes:
    - N1_REQUEST_TYPE
    - N2_INCIDENT_SEVERITY
```

Тепер модель знає не просто окрему відповідь. Вона знає шлях, яким іде процес.

Це важливо, бо наступні питання, outputs і gates залежать від уже зібраного стану.

---

## 5.4. STATE.SCHEMA

У простих задачах State можна вести вільно. Але в Ordo краще заздалегідь описувати схему стану.

Для цього використовується `STATE.SCHEMA`.

Приклад:

```yaml
state_schema:
  current_node:
    type: string
    required: true

  request_type:
    type: enum
    values:
      - incident
      - change_request
      - unknown
    required: false

  severity:
    type: enum
    values:
      - high
      - normal
      - unknown
    required: false

  terminal_path:
    type: string
    required: false

  open_questions:
    type: list
    required: true
    default: []

  assumptions:
    type: list
    required: true
    default: []

  gates:
    type: object
    required: true
    default: {}
```

Схема стану потрібна для трьох речей.

По-перше, вона допомагає моделі не вигадувати випадкові ключі.

Погано:

```yaml
state:
  type_of_problem: incident
  problem_kind: incident
  incidentType: incident
```

Добре:

```yaml
state:
  request_type: incident
```

По-друге, схема показує, які дані вже можуть бути у процесі.

По-третє, вона дозволяє gates перевіряти стан не за здогадками, а за конкретними полями.

---

## 5.5. State як захист від повторних питань

Без State модель може повторити питання, на яке користувач уже відповів.

Наприклад:

```text
Користувач: Це incident.
Модель: Добре. А який тип звернення — incident чи change_request?
```

Це створює відчуття, що модель не веде процес, а просто реагує на останнє повідомлення.

У Ordo після кожної відповіді має бути `STATE.UPDATE`.

Наприклад:

```json
{
  "op": "STATE.UPDATE",
  "path": "request_type",
  "value": "incident",
  "source": "USER_ANSWER.N1"
}
```

Після цього gate або node selection може сказати:

```text
request_type already set → do not ask N1 again
```

Тобто State не тільки зберігає інформацію. Він керує тим, які питання ще дозволені.

---

## 5.6. State як захист від передчасного результату

Одна з найважливіших функцій State — не дати моделі створити фінальний результат занадто рано.

Наприклад, для складного аналітичного пакета можуть бути такі поля:

```yaml
state:
  path_selected: false
  source_contract_confirmed: false
  alias_confirmed: false
  display_names_confirmed: false
  values_contract_confirmed: false
  qa_scope_confirmed: false
  automation_status_confirmed: false
  document_approvals:
    passport: pending
    jira: pending
    qa_package: pending
    automation_spec: pending
```

Поки ці поля не перейшли в потрібний стан, модель не має права створювати фінальний архів.

![Nebu — увага: State блокує передчасний фінал](../assets/mascots/64x64/Nebu_attention_64x64.png)

Gate може виглядати так:

```json
{
  "op": "GATE.CHECK",
  "id": "G_FINAL_ARCHIVE_ALLOWED",
  "method": "human",
  "trust_class": "human_decision",
  "assert": "state.path_selected == true && state.source_contract_confirmed == true && state.document_approvals.passport == 'approved'",
  "on_fail": "BLOCK_FINAL_ARCHIVE"
}
```

У звичайному prompt-і таке правило можна написати текстом. Але модель може його пропустити.

В Ordo це має бути частиною виконуваного стану.

---

## 5.7. State і статуси

State часто містить статуси. Але статуси мають бути чітко визначені.

Наприклад:

```yaml
state:
  package_status: draft
  automation_status: ready_for_first_run
  validation_status: passed_with_notes
```

Якщо статуси не мають семантики, модель може трактувати їх довільно.

Тому State має працювати разом із `STATUS.SEMANTICS`.

Наприклад:

```yaml
status_semantics:
  draft:
    meaning: "робота ще не фіналізована"
    final_handoff_allowed: false

  confirmed:
    meaning: "явно підтверджено користувачем або evidence"
    can_be_used_as_contract: true

  proposed:
    meaning: "запропоновано моделлю, але не підтверджено"
    can_be_used_as_contract: false

  blocked:
    meaning: "виконання зупинено через конкретну причину"
    next_action_required: true
```

Це дозволяє моделі не змішувати “запропоновано”, “погоджено”, “готово” і “заблоковано”.

---

## 5.8. Assumption ledger як частина State

Модель часто робить припущення.

Це нормально. Проблема починається тоді, коли припущення непомітно стає фактом.

Наприклад:

```text
Модель припустила, що подія має source = companyProfile / EDR.
Потім записала це в паспорт як confirmed.
```

Так робити не можна.

В Ordo припущення мають бути видимими:

```yaml
state:
  assumptions:
    - id: A1
      assumption: "source може бути companyProfile / EDR"
      evidence: "бізнесова назва схожа на EDR-фактографію"
      status: proposed
      required_confirmation: representative_source_row_or_analyst_confirmation
      final_package_allowed: false
```

Така форма не забороняє моделі думати. Вона забороняє їй видавати здогадку за підтверджений контракт.

`ASSUMPTION.LEDGER` — одна з найважливіших конструкцій для довіри до AI-процесу.

---

## 5.9. State і open questions

У складних задачах частина даних часто відсутня.

Погана модель заповнює їх сама.

Хороша Ordo-програма фіксує open questions:

```yaml
state:
  open_questions:
    - id: Q1
      question: "Який точний alias події використовуємо?"
      blocks:
        - final_package_generation

    - id: Q2
      question: "Який фактичний контракт HistoryEvent.item.values?"
      blocks:
        - passport_finalization
        - qa_automation_spec
```

Open question — це не слабкість. Це ознака чесного процесу.

Якщо даних не вистачає, Ordo має показати, чого саме бракує, а не вигадати відповідь.

---

## 5.10. State і traceability

State також допомагає пояснити, звідки взялося кожне рішення.

Наприклад:

```yaml
state:
  path:
    value: Path 1 candidate
    source: USER_ANSWER.N1
    confidence: medium
    reason: "користувач вказав, що зміна виникає у внутрішньому Mongo source row"
```

Або:

```yaml
state:
  values_contract:
    status: confirmed
    source: HISTORY_EVENT_EXAMPLE
    keys:
      - old#value
      - new#value
```

Це важливо для перевірки. Коли користувач питає “чому ти так вирішив?”, модель має не вигадувати пояснення заднім числом, а показати trace зі State.

---

## 5.11. State у compiled IR

У Semantic JSON IR State зазвичай представлений через операції:

```json
{
  "op": "STATE.INIT",
  "id": "ST1",
  "schema": "history_event_intake_state",
  "defaults": {
    "current_node": "N1",
    "path": "unknown",
    "open_questions": [],
    "assumptions": [],
    "gates": {}
  }
}
```

Після відповіді користувача:

```json
{
  "op": "STATE.UPDATE",
  "id": "STU1",
  "set": {
    "request_type": "incident",
    "current_node": "N2_INCIDENT_SEVERITY"
  },
  "source_ref": "USER_ANSWER.N1"
}
```

Після gate:

```json
{
  "op": "STATE.UPDATE",
  "id": "STU2",
  "set": {
    "gates.G1.status": "passed"
  },
  "source_ref": "GATE.G1"
}
```

Така форма зручна для runtime, тому що кожна зміна стану має джерело.

---

## 5.12. Типові помилки зі State

### Помилка 1. Не вести State явно

Модель просто відповідає на кожне повідомлення, не фіксуючи, що вже відомо.

Наслідок: повторні питання, втрата контексту, передчасні висновки.

### Помилка 2. Змішувати Context і State

Наприклад, зберігати весь source row у State.

Краще:

```yaml
context:
  representative_source_row: "..."

state:
  source_row_contract:
    status: confirmed
    evidence_ref: representative_source_row
```

### Помилка 3. Не розрізняти proposed і confirmed

Якщо модель запропонувала alias, це ще не confirmed alias.

State має показувати:

```yaml
alias:
  value: LU_CHANGE_CAPITAL
  status: proposed
```

а не:

```yaml
alias: LU_CHANGE_CAPITAL
```

### Помилка 4. Не зберігати blockers

Якщо виконання заблоковано, причина має бути в State:

```yaml
blockers:
  - id: B1
    reason: "source row contract not confirmed"
    blocks: final_archive
```

### Помилка 5. Не очищати припущення перед фіналом

Перед фінальним результатом assumption ledger має бути або порожній, або містити тільки non-blocking notes.

Якщо mandatory contract досі proposed, фінальний пакет не можна створювати.

---

## 5.13. Практичний шаблон State для Ordo-процесу

Для багатьох Ordo-процесів можна починати з такої базової схеми:

```yaml
state:
  current_node: START
  completed_nodes: []
  selected_path: unknown

  answers: {}

  contracts:
    required: []
    confirmed: []
    proposed: []
    missing: []

  assumptions: []
  open_questions: []
  blockers: []

  outputs:
    selected: []
    generated: []
    approved: []

  gates: {}

  handoff:
    status: draft
    allowed: false
```

Це не універсальний закон. Але це хороший стартовий шаблон.

Він змушує модель думати процесно:

```text
де ми;
що вже зібрано;
що підтверджено;
що заблоковано;
що можна створювати;
чи дозволений handoff.
```

---

## 5.14. Короткий підсумок розділу

`State` — це памʼять процесу в Ordo.

Він потрібен, щоб модель:

```text
- не повторювала питання;
- не перескакувала кроки;
- не видавала припущення за підтвердження;
- не створювала фінальний результат занадто рано;
- могла пояснити, звідки взялося рішення;
- розуміла, які gates пройдені;
- бачила open questions і blockers.
```

`Context` — це матеріал, із яким працює модель.

`State` — це поточне положення процесу.

Без State Ordo перетворюється назад на довгий prompt. Зі State Ordo стає керованим процесом.

---

## Міні-вправа

Візьміть будь-який процес, де модель має поставити кілька питань перед результатом.

Наприклад:

```text
Підготувати Jira-задачу за описом користувача.
```

Спробуйте описати State:

```yaml
state:
  current_node: START
  task_type: unknown
  business_goal: missing
  acceptance_criteria: missing
  out_of_scope: missing
  assumptions: []
  open_questions: []
  blockers: []
  handoff:
    status: draft
    allowed: false
```

Потім дайте відповідь на питання:

```text
1. Які поля мають бути confirmed перед фінальною задачею?
2. Які поля можуть бути proposed?
3. Які open questions блокують handoff?
4. Який gate не дозволить створити фінальний документ занадто рано?
```

---

<!-- REVIEWED: chapter 05; Nebu markers checked -->
