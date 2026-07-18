# Розділ 31. Guided intake як Ordo-програма

## Навіщо це потрібно

У багатьох реальних процесах модель не повинна одразу створювати фінальний результат. Їй спочатку потрібно зібрати дані, уточнити контекст, пройти дерево рішень, перевірити gates і тільки після цього перейти до створення документа, архіву, звіту або іншого artifact.

Такий режим роботи називається `guided intake`.

Простими словами, guided intake — це кероване опитування користувача, у якому модель не імпровізує порядок питань, а рухається за визначеною Ordo-програмою.

Це особливо важливо для складних playbook-ів, де неправильне перше питання може зламати весь процес. Наприклад, якщо модель надто рано питає про назву події, хоча спочатку треба визначити path, або якщо вона починає генерувати фінальний пакет до підтвердження контракту.

У звичайному prompt-підході guided intake часто виглядає так:

```text
Постав мені кілька питань, щоб зібрати інформацію.
```

Але цього недостатньо. Модель може:

- поставити питання не в тому порядку;
- пропустити обов’язкове питання;
- сплутати попередню відповідь із підтвердженим фактом;
- перейти до результату занадто рано;
- не зафіксувати, який path був обраний;
- не пояснити, чому одні варіанти відкинуті, а інші прийняті.

В Ordo guided intake — це не просто “розмова”. Це повноцінна Ordo-програма.

---

## Просте пояснення

Guided intake можна уявити як форму, яка заповнюється не на одній сторінці, а через діалог.

Але важлива різниця в тому, що ця “форма” має логіку:

```text
якщо відповідь така → йдемо сюди;
якщо бракує даних → ставимо питання;
якщо gate не пройдений → зупиняємося;
якщо contract підтверджений → переходимо до наступного етапу;
якщо користувач змінив рішення → оновлюємо state і повертаємося до потрібного вузла.
```

Тобто guided intake — це поєднання:

```text
ENTRY → NODE → STATE → QUESTION → ANSWER → GATE → PATH → NEXT NODE
```

Модель у такому процесі має не просто “бути корисною”. Вона має виконувати роль керованого оператора процесу.

---

## Чим guided intake відрізняється від звичайного діалогу

Звичайний діалог може бути вільним. Користувач щось каже, модель відповідає, потім тема змінюється, потім модель щось уточнює.

Guided intake має іншу природу.

У ньому кожне питання має призначення:

```text
питання збирає конкретне поле state;
питання прив’язане до конкретного NODE;
відповідь має бути класифікована;
після відповіді виконується state update;
потім перевіряється gate;
потім визначається наступний NODE.
```

Наприклад, якщо Ordo-програма створює нову історичну подію, то питання:

```text
Який alias події?
```

не є просто розмовним питанням. Це операція збору контрактного поля:

```yaml
node:
  id: "N_COLLECT_ALIAS"
  asks_for: "event.alias"
  required: true
  next_if_answered: "N_COLLECT_SOURCE_FIELD"
```

---

## Базові елементи guided intake

Для guided intake потрібні такі елементи Ordo:

```text
ENTRY.DEF
NODE.DEF
QUESTION.DEF
ANSWER.REGISTRY
STATE.SCHEMA
STATE.UPDATE
PATH.SELECT
GATE.REPORT
NEXT.NODE
STATUS.SEMANTICS
```

### `ENTRY.DEF`

Визначає, з чого починається процес.

```yaml
entry:
  id: "history_event_intake"
  purpose: "guided intake for a new History Event"
  start_node: "N_CLASSIFY_INPUT"
```

### `NODE.DEF`

Описує один вузол діалогу.

```yaml
node:
  id: "N_CLASSIFY_INPUT"
  type: "decision"
  purpose: "understand what kind of event request this is"
  allowed_next:
    - "N_PATH_A1"
    - "N_PATH_A2"
    - "N_PATH_A4"
    - "N_NEED_MORE_CONTEXT"
```

### `QUESTION.DEF`

Описує, яке питання можна поставити користувачу.

```yaml
question:
  id: "Q_SOURCE_FIELD"
  node: "N_COLLECT_SOURCE_FIELD"
  text: "Яке source field змінюється?"
  writes_to: "state.contract.source_field"
  required: true
```

### `ANSWER.REGISTRY`

Фіксує відповіді користувача не як “текст у чаті”, а як значення state.

```yaml
answer:
  question_id: "Q_SOURCE_FIELD"
  raw_text: "status"
  normalized_value: "item.status"
  confidence: "confirmed"
```

### `STATE.UPDATE`

Показує, що саме змінилося після відповіді.

```yaml
state_update:
  field: "contract.source_field"
  before: null
  after: "item.status"
  source: "user_answer"
```

---

## Одне головне питання за раз

Для guided intake важливе правило:

```text
один NODE — одне головне питання
```

Це не означає, що модель ніколи не може поставити уточнення. Але головний рух процесу має бути контрольований.

Погано:

```text
Який alias, source field, old value, new value, display name, path і QA сценарії?
```

Таке питання перевантажує користувача і змішує кілька state transitions.

Добре:

```text
Поточний крок: потрібно визначити alias події.
Який alias використовуємо?
```

Після відповіді модель оновлює state і переходить до наступного вузла.

---

## Поточний статус має бути видимим

Guided intake має постійно знати, де він знаходиться.

Мінімальний службовий статус може виглядати так:

```yaml
intake_status:
  current_entry: "history_event_intake"
  current_node: "N_COLLECT_ALIAS"
  selected_path: "A1"
  confirmed:
    - "event_type"
    - "source_row"
  pending:
    - "alias"
    - "source_field"
    - "old_new_values"
  blocked_by:
    - "G_CONTRACT_COMPLETE"
```

У звичайному режимі модель не обов’язково показує весь цей status користувачу повністю. Але в debug mode він має бути доступний.

---

## Path selection у guided intake

Одна з головних функцій guided intake — правильно обрати path.

Наприклад:

```text
A1 — зміна поля в основній source row;
A2 — зміна поля у пов’язаній сутності;
A4 — зовнішній ExternalHistoryEvent;
A5 — no-op або expected-no-change сценарій.
```

Модель не повинна просто здогадуватися. Вона має виконати `PATH.SELECT`.

```yaml
trace_source: "model_self_report"
path_selection:
  candidate_paths:
    - id: "A1"
      condition: "direct source field change"
    - id: "A2"
      condition: "related entity through identification center"
    - id: "A4"
      condition: "external history event input"

  selected:
    id: "A1"
    reason: "user confirmed direct field change in source row"

  rejected:
    - id: "A2"
      reason: "no related entity context confirmed"
    - id: "A4"
      reason: "input is not ExternalHistoryEvent"
```

Це особливо важливо, бо помилка в path на початку часто призводить до неправильного пакета в кінці.

---

## Gates у guided intake

Guided intake не має бути нескінченним опитуванням. Він має контрольні точки.

Наприклад:

```text
G_PATH_CONFIRMED
G_CONTRACT_COMPLETE
G_SOURCE_ROW_CONFIRMED
G_VALUES_CONFIRMED
G_QA_SCOPE_CONFIRMED
G_PRE_PACKAGE_APPROVAL
```

Gate не просто “нагадує”. Він блокує перехід далі.

```yaml
gate:
  id: "G_CONTRACT_COMPLETE"
  method: mechanical
  trust_class: deterministic
  type: "blocking"
  requires:
    - "contract.alias"
    - "contract.source_field"
    - "contract.values"
    - "contract.source_row"
  on_fail:
    action: "ask_missing_question"
```

Якщо контракт неповний, модель не має права переходити до генерації фінального output.

---

## Як guided intake працює з уточненнями користувача

Користувач може змінити рішення.

Наприклад:

```text
вернись до попереднього кроку
змінюю рішення на 3
```

Ordo має не ігнорувати це, а виконати контрольований state correction.

```yaml
state_correction:
  reason: "user changed previous decision"
  affected_field: "selected_option"
  before: "2"
  after: "3"
  rollback_to_node: "N_CONFIRM_OPTION"
  recheck_gates:
    - "G_PATH_CONFIRMED"
    - "G_CONTRACT_COMPLETE"
```

Це дуже важливо. У складних процесах користувач часто уточнює або змінює попередні рішення. Якщо guided intake не підтримує контрольоване повернення назад, state швидко стає недостовірним.

---

## Guided intake і debug mode

У debug mode guided intake має показувати:

```text
- поточний NODE;
- чому поставлено саме це питання;
- яке поле state воно заповнює;
- які paths ще не визначені;
- які gates блокують перехід;
- які відповіді вже підтверджені;
- які рішення були змінені користувачем;
- чому модель не переходить до фінального output.
```

Приклад debug-фрагмента:

```yaml
debug:
  current_node: "N_COLLECT_SOURCE_FIELD"
  question_reason: "contract.source_field is required for Path A1"
  writes_to: "state.contract.source_field"
  blocked_gates:
    - "G_CONTRACT_COMPLETE"
  next_after_answer:
    - "N_COLLECT_VALUES"
```

---

## Guided intake і improvement loop

Guided intake є одним із головних місць, де виникають покращення.

Користувач може сказати:

```text
це питання треба було поставити раніше
```

або:

```text
тут потрібно не питати alias, а спочатку визначити source row
```

Ordo має створити improvement record:

```yaml
improvement_record:
  type: "intake_order_problem"
  affected_unit:
    kind: "node"
    id: "N_COLLECT_ALIAS"
  proposed_patch:
    - "move N_COLLECT_SOURCE_ROW before N_COLLECT_ALIAS"
  suggested_test:
    id: "TC_SOURCE_ROW_BEFORE_ALIAS"
```

Так guided intake поступово стає кращим не через хаотичне переписування інструкцій, а через керований цикл покращення.

---

## Guided intake як compiled IR

У compiled IR guided intake може виглядати як набір op-кодів:

```json
[
  {
    "op": "ENTRY.DEF",
    "id": "history_event_intake",
    "start_node": "N_CLASSIFY_INPUT"
  },
  {
    "op": "NODE.DEF",
    "id": "N_COLLECT_ALIAS",
    "node_type": "question",
    "writes_to": "contract.alias"
  },
  {
    "op": "QUESTION.DEF",
    "id": "Q_ALIAS",
    "text": "Який alias події?",
    "required": true
  },
  {
    "op": "GATE.DEF",
    "id": "G_CONTRACT_COMPLETE",
    "type": "blocking"
  },
  {
    "op": "STATE.UPDATE",
    "from": "Q_ALIAS",
    "to": "contract.alias"
  }
]
```

Це означає, що guided intake можна не тільки описати словами, а й виконувати як structured program.

---

## Типові помилки

### Помилка 1. Перетворити guided intake на звичайний список питань

Список питань не є guided intake, якщо немає state, gates і path logic.

### Помилка 2. Питати все одразу

Коли модель питає десять речей одночасно, вона втрачає контроль над state.

### Помилка 3. Не фіксувати, що підтверджено

Якщо модель не розділяє “користувач згадав” і “користувач підтвердив”, вона може створити неправильний contract.

### Помилка 4. Не підтримувати повернення назад

Користувачі часто змінюють рішення. Ordo має вміти коректно оновити state.

### Помилка 5. Дозволити фінальний output до gates

Guided intake має блокувати передчасну генерацію artifact.

---

## Міні-вправа

Візьміть простий процес:

```text
Підготувати відповідь клієнту на скаргу.
```

Спробуйте визначити:

```text
1. Який ENTRY запускає процес?
2. Які 3–5 NODE потрібні?
3. Яке перше питання має поставити модель?
4. Які поля state потрібно зібрати?
5. Який gate має бути перед фінальним текстом?
6. Що робити, якщо користувач змінив тон відповіді з “офіційний” на “дружній”?
```

---

## Короткий підсумок

Guided intake — це не просто діалог із моделлю. Це Ordo-програма, яка керує збором інформації, path selection, state updates, gates і переходами між вузлами.

Його головна цінність у тому, що складний процес не перетворюється на хаотичне листування. Модель знає, де вона знаходиться, що вже підтверджено, що ще потрібно зібрати і чому вона не має права рухатися далі.

У великих playbook-ах guided intake є мостом між людською розмовою і формальним виконанням Ordo.
