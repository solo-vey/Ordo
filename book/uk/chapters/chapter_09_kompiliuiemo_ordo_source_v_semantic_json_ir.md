# Розділ 9. Компілюємо Ordo Source в Semantic JSON IR

## 9.1. Навіщо взагалі щось компілювати

У попередньому розділі ми написали першу Ordo Source-програму. Вона була схожа на YAML: її можна прочитати очима, зрозуміти логіку, обговорити з аналітиком або розробником, виправити руками.

Це зручно для людини.

Але для моделі або майбутнього runtime цього не завжди достатньо. Людсько-читабельна форма може містити зручні назви, коментарі, різні стилі запису, скорочення й пояснення. Для виконання краще мати більш однозначну форму.

Саме тому Ordo вводить ідею компіляції.

![Nebu — ідея: компіляція як перехід до виконання](../assets/mascots/64x64/Nebu_idea_64x64.png)

Компіляція в Ordo — це не обовʼязково компіляція в машинний код, як у класичних мовах програмування. У першій практичній версії це радше перетворення людсько-читабельної Ordo Source-програми в структурований формат, який модель виконує стабільніше.

Найзручніший формат для цього на поточному етапі — Semantic JSON IR.

IR означає intermediate representation, тобто проміжне представлення.

Простіше:

```text
Ordo Source — форма для людини.
Semantic JSON IR — форма для виконання моделлю або runtime.
```

Ordo Source відповідає на питання:

```text
Як людині описати процес зрозуміло і контрольовано?
```

Semantic JSON IR відповідає на інше питання:

```text
Як подати цей процес моделі так, щоб вона бачила чіткі ops, порядок виконання, gates, state і handoff?
```

---

## 9.2. Що таке Semantic JSON IR

Semantic JSON IR — це список або дерево інструкцій, де кожна інструкція має явний `op`.

Наприклад:

```json
{
  "op": "INTENT.SET",
  "id": "I1",
  "goal": "summarize_text",
  "lang": "uk"
}
```

Така інструкція каже не просто “десь у тексті є мета”, а прямо:

```text
встановити intent програми;
id цієї інструкції — I1;
мета — summarize_text;
мова — українська.
```

Інший приклад:

```json
{
  "op": "GATE.CHECK",
  "id": "G1",
  "method": "self_verification",
  "trust_class": "model_judgment",
  "assert": "NO_UNSUPPORTED_FACTS",
  "source": "RESULT.summary",
  "on_fail": "REPAIR.REMOVE_UNSUPPORTED"
}
```

Тут уже видно контрольну точку:

```text
перевірити, що в результаті немає непідтверджених фактів;
перевіряти потрібно RESULT.summary;
якщо перевірка не пройдена — прибрати непідтверджене.
```

Це набагато точніше, ніж просто фраза в prompt-і:

```text
Не вигадуй фактів.
```

Фраза може загубитися. `GATE.CHECK` складніше проігнорувати, особливо якщо runtime або дисциплінована модель веде execution trace.

---

## 9.3. Чому саме JSON

Можна запитати: чому не YAML, не XML, не власний компактний синтаксис?

Причина проста: JSON добре підходить для поточних моделей і програмних інструментів.

Його переваги:

```text
- він структурований;
- його легко перевіряти програмно;
- його добре розуміють сучасні AI-моделі;
- його можна передавати між системами;
- його можна логувати;
- його можна валідовувати через schema;
- його можна виконувати покроково.
```

Ordo не привʼязана назавжди тільки до JSON. У майбутньому може зʼявитися компактний opcode format або навіть нативний model-internal формат.

Але для поточного етапу Semantic JSON IR — найкращий компроміс між зрозумілістю, суворістю і практичністю.

---

## 9.4. Ordo Source і IR на одному прикладі

Візьмемо просту Ordo Source-програму для підсумку тексту.

```yaml
ordo: "0.12-draft"
program: "minimal.summary.uk"

intent:
  goal: "summarize_text"
  language: "uk"

contract:
  input:
    text: required
  output:
    format: "bullet_list"
    max_items: 3
    language: "uk"
  rules:
    - id: R1
      rule: "use_only_input_text"
    - id: R2
      rule: "do_not_invent_facts"
    - id: R3
      rule: "if_input_insufficient_return_insufficient_data_status"

context:
  source:
    text: "$USER_INPUT.text"

state:
  status: "draft"
  unsupported_facts: []

path:
  id: "summarize_or_report_insufficient_input"
  steps:
    - id: S1
      do: "read_input_text"
    - id: S2
      do: "extract_supported_points"
    - id: S3
      do: "select_up_to_3_key_points"
    - id: S4
      do: "render_ukrainian_bullet_summary"

  gates:
    - id: G1
      method: "mechanical"
      trust_class: "deterministic"
      check: "input_text_present"
      on_fail: "return_insufficient_data"
    - id: G2
      method: "self_verification"
      trust_class: "model_judgment"
      check: "no_unsupported_facts"
      on_fail: "remove_or_mark_unsupported"
    - id: G3
      method: "mechanical"
      trust_class: "deterministic"
      check: "max_3_items"
      on_fail: "compress_to_3_items"
    - id: G4
      method: "mechanical"
      trust_class: "deterministic"
      check: "output_language_uk"
      on_fail: "rewrite_in_ukrainian"

result:
  primary: "summary"
  fallback: "insufficient_data_message"

handoff:
  include:
    - "status"
    - "result"
    - "gate_report"
```

Це нормально читається людиною.

Тепер подивимося на Semantic JSON IR для тієї ж програми.

```json
{
  "ir_version": "ordo-ir/0.12-draft",
  "program_id": "minimal.summary.uk",
  "mode": "model_execution",
  "ops": [
    {
      "op": "INTENT.SET",
      "id": "I1",
      "goal": "summarize_text",
      "lang": "uk"
    },
    {
      "op": "CONTRACT.DEF",
      "id": "C1",
      "input": {
        "text": "required"
      },
      "output": {
        "type": "bullet_list",
        "max_items": 3,
        "lang": "uk"
      }
    },
    {
      "op": "RULE.ADD",
      "id": "R1",
      "kind": "SOURCE_BOUND_ONLY"
    },
    {
      "op": "RULE.ADD",
      "id": "R2",
      "kind": "NO_UNSUPPORTED_FACTS"
    },
    {
      "op": "RULE.ADD",
      "id": "R3",
      "kind": "INSUFFICIENT_INPUT_FALLBACK"
    },
    {
      "op": "CONTEXT.LOAD",
      "id": "CTX1",
      "slot": "input.text",
      "from": "$USER_INPUT.text"
    },
    {
      "op": "STATE.INIT",
      "id": "ST1",
      "status": "draft",
      "unsupported_facts": []
    },
    {
      "op": "PATH.SELECT",
      "id": "P1",
      "path": "summarize_or_report_insufficient_input"
    },
    {
      "op": "STEP.RUN",
      "id": "S1",
      "fn": "READ_INPUT_TEXT",
      "in": ["CTX1"],
      "out": ["ST1.input_read"]
    },
    {
      "op": "GATE.CHECK",
      "id": "G1",
      "method": "mechanical",
      "trust_class": "deterministic",
      "assert": "INPUT_TEXT_PRESENT",
      "on_fail": "RESULT.INSUFFICIENT_DATA"
    },
    {
      "op": "STEP.RUN",
      "id": "S2",
      "fn": "EXTRACT_SUPPORTED_POINTS",
      "in": ["CTX1"],
      "out": ["ST1.supported_points"]
    },
    {
      "op": "STEP.RUN",
      "id": "S3",
      "fn": "SELECT_TOP_N",
      "params": {
        "n": 3
      },
      "in": ["ST1.supported_points"],
      "out": ["ST1.selected_points"]
    },
    {
      "op": "STEP.RUN",
      "id": "S4",
      "fn": "RENDER_BULLETS",
      "params": {
        "lang": "uk"
      },
      "in": ["ST1.selected_points"],
      "out": ["RESULT.summary"]
    },
    {
      "op": "GATE.CHECK",
      "id": "G2",
      "method": "self_verification",
      "trust_class": "model_judgment",
      "assert": "NO_UNSUPPORTED_FACTS",
      "source": "RESULT.summary",
      "on_fail": "REPAIR.REMOVE_UNSUPPORTED"
    },
    {
      "op": "GATE.CHECK",
      "id": "G3",
      "method": "mechanical",
      "trust_class": "deterministic",
      "assert": "ITEM_COUNT_LE",
      "params": {
        "max": 3
      },
      "source": "RESULT.summary",
      "on_fail": "REPAIR.COMPRESS"
    },
    {
      "op": "GATE.CHECK",
      "id": "G4",
      "method": "mechanical",
      "trust_class": "deterministic",
      "assert": "LANG_IS",
      "params": {
        "lang": "uk"
      },
      "source": "RESULT.summary",
      "on_fail": "REPAIR.REWRITE_LANG"
    },
    {
      "op": "HANDOFF.EMIT",
      "id": "H1",
      "include": [
        "status",
        "result",
        "gate_report"
      ]
    }
  ]
}
```

На перший погляд JSON довший. Але він краще підходить для виконання.

У ньому чітко видно:

```text
- порядок операцій;
- що є intent;
- що є contract;
- які rules додано;
- звідки береться context;
- який state ініціалізується;
- які steps виконуються;
- які gates перевіряються;
- що передається у handoff.
```

---

## 9.5. Що саме робить компілятор

У простому вигляді компілятор Ordo робить кілька речей.

По-перше, він знаходить основні блоки Ordo Source:

```text
intent
contract
context
state
path
steps
gates
result
handoff
```

По-друге, він перетворює їх у явні operations:

```text
INTENT.SET
CONTRACT.DEF
CONTEXT.LOAD
STATE.INIT
PATH.SELECT
STEP.RUN
GATE.CHECK
HANDOFF.EMIT
```

По-третє, він нормалізує назви.

Наприклад, у source може бути:

```yaml
check: "no_unsupported_facts"
```

А в IR це стає:

```json
{
  "assert": "NO_UNSUPPORTED_FACTS"
}
```

По-четверте, компілятор може виявити частини, які не вдалося безпечно формалізувати.

Наприклад:

```text
Зберегти тон доброзичливий, але не надто офіційний, як у наших попередніх листах клієнтам.
```

Це можна частково формалізувати як `tone: polite`, але фраза “як у наших попередніх листах” вимагає контексту або стилістичного прикладу. Якщо такого формального представлення ще немає, компілятор може винести це в `FREEFORM.ADD`.

```json
{
  "op": "FREEFORM.ADD",
  "id": "F1",
  "role": "style_guidance",
  "binding": "CONTRACT.C1",
  "text": "Зберегти тон доброзичливий, але не надто офіційний, як у наших попередніх листах клієнтам.",
  "compile_status": "not_structured",
  "reason": "style reference requires examples or domain-specific style profile"
}
```

Це чесніше, ніж удавати, що все повністю формалізовано.

---

## 9.6. Компіляція не має спотворювати сенс

![Nebu — увага: компіляція не має спотворювати сенс](../assets/mascots/64x64/Nebu_attention_64x64.png)

Головне правило компіляції:

```text
краще залишити частину в controlled FREEFORM,
ніж перетворити її на неправильну структуровану інструкцію.
```

Наприклад, користувач пише:

```text
Не роби документ сухим. Він має бути зрозумілий аналітику, але не втрачати технічну точність.
```

Можна формалізувати частину:

```yaml
style:
  audience: analyst
  readability: high
  technical_accuracy: required
```

Але фразу “не сухим” важко точно формалізувати без стилістичного профілю. Її можна залишити як controlled FREEFORM:

```json
{
  "op": "FREEFORM.ADD",
  "id": "F_STYLE_1",
  "role": "style_guidance",
  "binding": "OUTPUT.DEF",
  "text": "Документ не має бути сухим. Він має бути зрозумілий аналітику, але не втрачати технічну точність.",
  "compile_status": "partially_structured",
  "structured_parts": [
    "audience=analyst",
    "readability=high",
    "technical_accuracy=required"
  ],
  "reason": "stylistic nuance is better preserved as controlled freeform"
}
```

Це і є чесна компіляція.

Ordo не намагається насильно стиснути весь людський сенс у маленький набір op-кодів.

---

## 9.7. Source map: як не втратити звʼязок із людським текстом

Коли Ordo Source компілюється в IR, важливо не втратити звʼязок із першоджерелом.

Для цього потрібен source map.

![Nebu — подумати: source map зберігає звʼязок із людським текстом](../assets/mascots/64x64/Nebu_thinking_64x64.png)

Source map відповідає на питання:

```text
з якої частини людської інструкції виникла ця IR-операція?
```

Наприклад:

```json
{
  "op": "GATE.CHECK",
  "id": "G2",
  "method": "self_verification",
  "trust_class": "model_judgment",
  "assert": "NO_UNSUPPORTED_FACTS",
  "source_ref": "source.contract.rules.R2"
}
```

Це означає, що gate `G2` походить із правила `R2` у source-програмі.

У складних playbook-ах це дуже важливо. Якщо модель виконує gate, аналітик має бачити, звідки це правило взялося.

У майбутньому source map може дозволяти такі речі:

```text
- показати користувачу, які частини інструкції були використані;
- знайти, чому модель поставила саме це питання;
- перевірити, чи не зникло правило під час компіляції;
- оновити source і перегенерувати IR;
- порівняти різні версії playbook-а.
```

Без source map compiled IR може стати “чорною скринькою”. Ordo має уникати цього.

---

## 9.8. Execution trace: що модель реально виконала

Source map показує, звідки взялася інструкція.

Execution trace показує, що реально було виконано.

Наприклад:

```json
{
  "trace": [
    {
      "op_id": "I1",
      "status": "passed",
      "note": "Intent set to summarize_text"
    },
    {
      "op_id": "CTX1",
      "status": "passed",
      "note": "Input text loaded"
    },
    {
      "op_id": "G1",
      "status": "passed",
      "note": "Input text is present"
    },
    {
      "op_id": "G2",
      "status": "passed",
      "note": "No unsupported facts detected"
    }
  ]
}
```

Для простого summary це може здаватися зайвим. Але для великого процесу trace дуже корисний.

Наприклад, якщо модель не створила фінальний архів, trace має показати чому:

```json
{
  "op_id": "G_CONTRACTS_CONFIRMED",
  "status": "failed",
  "reason": "history_event_values_keys has status proposed",
  "action": "BLOCK_FINAL_ARCHIVE"
}
```

Це набагато краще, ніж загальна відповідь:

```text
Поки не вистачає даних.
```

Ordo має робити причину зупинки видимою.

---

## 9.9. IR не обовʼязково має бути зручним для людини

Важливий момент: Ordo Source і Semantic JSON IR мають різні цілі.

Ordo Source має бути зрозумілим людині.

IR має бути зручним для виконання.

Тому не треба вимагати, щоб IR був красивим для читання. Він може бути довшим, сухішим, формальнішим.

Це нормально.

У майбутньому може існувати ще компактніший формат:

```json
[
  ["I", "summarize_text", "uk"],
  ["C", {"out": {"type": "bullets", "max": 3, "lang": "uk"}}],
  ["G", "NO_UNSUPPORTED_FACTS", "summary", "REPAIR.REMOVE_UNSUPPORTED"],
  ["H", ["status", "result", "gate_report"]]
]
```

Це майже не зручно для людини, але може бути зручно для runtime або моделі, спеціально навченої на Ordo.

Поточний Semantic JSON IR — проміжний практичний формат. Він ще достатньо читабельний, але вже достатньо структурований.

---

## 9.10. Що має бути в хорошому IR

Хороший Ordo IR має відповідати кільком правилам.

### 1. Кожна операція має мати `op`

Погано:

```json
{
  "goal": "summarize_text"
}
```

Краще:

```json
{
  "op": "INTENT.SET",
  "goal": "summarize_text"
}
```

`op` показує, що саме треба зробити.

### 2. Кожна важлива операція має мати `id`

```json
{
  "op": "GATE.CHECK",
  "id": "G_NO_UNSUPPORTED_FACTS",
  "method": "self_verification",
  "trust_class": "model_judgment"
}
```

Без `id` важко робити trace, source map і validation report.

### 3. Gates мають бути явними

Погано:

```json
{
  "rules": ["do not invent facts"]
}
```

Краще:

```json
{
  "op": "GATE.CHECK",
  "method": "self_verification",
  "trust_class": "model_judgment",
  "assert": "NO_UNSUPPORTED_FACTS",
  "on_fail": "REPAIR.REMOVE_UNSUPPORTED"
}
```

### 4. State має бути явним

Якщо модель має памʼятати відповідь користувача, це має бути в state.

```json
{
  "op": "STATE.UPDATE",
  "key": "request_type",
  "value": "incident"
}
```

### 5. Handoff має бути описаний

Модель має знати, що саме повертати користувачу.

```json
{
  "op": "HANDOFF.EMIT",
  "include": ["status", "result", "gate_report"]
}
```

---

## 9.11. Типові помилки при компіляції

### Помилка 1. Залишити важливий gate у звичайному тексті

Якщо правило блокує фінальний результат, воно має бути `GATE.CHECK`, а не просто реченням.

### Помилка 2. Перетворити доменне пояснення на універсальне правило

Наприклад, `HistoryEvent.item.values` — це доменний контракт, а не правило Ordo Core.

### Помилка 3. Втратити статуси

Якщо в source є `candidate`, `confirmed`, `blocked`, `ready_for_first_run`, IR має зберегти різницю між ними.

### Помилка 4. Не винести неформалізоване в FREEFORM

Якщо частина інструкції не може бути безпечно структурована, її не можна просто загубити.

### Помилка 5. Не зробити source map

Без source map важко довести, що IR справді відповідає source-програмі.

### Помилка 6. Зробити IR занадто людським

IR не має бути есе. Якщо в ньому забагато вільного тексту, модель знову працюватиме з prompt-ом, а не з execution contract.

---

## 9.12. Як це виглядає в реальному playbook-у

У простому прикладі IR може містити 10–20 операцій.

У реальному playbook-у їх може бути десятки або сотні.

Наприклад, Ordo-native History Event Playbook має такі групи ops:

```text
PROGRAM.DEF
PROFILE.USE
DOMAIN_PACK.LOAD
ENTRY.DEF
NODE.DEF
ANSWER.REGISTRY
STATE.SCHEMA
OUTPUT.DEF
TEMPLATE.BIND
GATE.DEF
APPROVAL.REQUIRE
DOC.SPLIT
DOC.CATALOG
DOC.SELECT
RENDER.VALIDATE
FREEFORM.ADD
HANDOFF.DEF
```

Це не означає, що модель має виводити всі ці ops користувачу. Користувачу достатньо бачити поточний вузол, вибрані документи, оновлення стану і наступне питання.

Але всередині процес має бути керованим.

---

## 9.13. Короткий підсумок розділу

Ordo Source потрібен для людей.

Semantic JSON IR потрібен для виконання.

Компіляція Ordo Source в IR робить процес більш явним:

```text
- intent стає INTENT.SET;
- contract стає CONTRACT.DEF;
- context стає CONTEXT.LOAD;
- state стає STATE.INIT / STATE.UPDATE;
- steps стають STEP.RUN;
- gates стають GATE.CHECK;
- result і handoff стають HANDOFF.EMIT.
```

Хороший IR має:

```text
- явні op;
- стабільні id;
- gates;
- state;
- source map;
- execution trace;
- controlled FREEFORM для того, що не можна безпечно формалізувати.
```

Головна думка:

```text
компіляція не повинна робити інструкцію красивішою;
вона має робити її виконуванішою.
```

---

## Міні-вправа

Візьміть просту Ordo Source-програму:

```yaml
intent:
  goal: write_customer_reply

contract:
  output:
    type: email
    language: uk
  rules:
    - polite_tone
    - no_specific_deadline
    - acknowledge_request

context:
  customer_message: "$USER_INPUT.message"

result:
  primary: customer_reply
```

Спробуйте вручну перетворити її на Semantic JSON IR.

Мінімально вам потрібні ops:

```text
INTENT.SET
CONTRACT.DEF
RULE.ADD
CONTEXT.LOAD
STATE.INIT
STEP.RUN
GATE.CHECK
HANDOFF.EMIT
```

Окремо подумайте: яке правило має бути `GATE.CHECK`, а яке може лишитися як style guidance?
