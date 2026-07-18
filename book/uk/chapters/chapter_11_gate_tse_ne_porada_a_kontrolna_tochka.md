# Розділ 11. Gate — це не порада, а контрольна точка

## 11.1. Навіщо Ordo потрібні Gates

У звичайній розмові з AI-моделлю правила часто звучать як рекомендації.

Наприклад:

```text
Не вигадуй фактів.
Не створюй фінальний документ, якщо бракує даних.
Перевір, що відповідь українською.
Не переходь до наступного кроку без підтвердження користувача.
```

Людина читає такі фрази і розуміє: це важливо. Але модель може сприйняти їх як загальні побажання. Вона може виконати їх, а може частково пропустити, особливо якщо завдання довге.

У Ordo такі правила мають бути не просто текстом, а контрольними точками виконання.

![Nebu — ідея: Gate як контрольна точка](../assets/mascots/64x64/Nebu_idea_64x64.png)

Саме для цього існує `Gate`.

Gate — це місце в процесі, де модель має зупинитися, перевірити умову і тільки після цього рухатися далі.

Якщо умова виконана — процес продовжується.

Якщо умова не виконана — процес не має мовчки рухатися далі. Він має або виправити результат, або поставити уточнювальне питання, або заблокувати наступний крок.

У цьому головна різниця між звичайною інструкцією і Ordo.

Звичайна інструкція каже:

```text
Було б добре перевірити це перед фіналом.
```

Ordo каже:

```text
Без цієї перевірки фінал заборонений.
```

## 11.2. Gate як світлофор

Найпростіша аналогія — світлофор.

Зелений сигнал означає: можна їхати.

Жовтий означає: потрібно бути уважним або підготуватися до зупинки.

Червоний означає: рух заборонений.

Gate працює схоже.

Наприклад, у процесі створення документа є gate:

```text
Чи всі обовʼязкові розділи заповнені?
```

Можливі результати:

```text
passed — усі розділи заповнені;
passed_with_notes — є незначні зауваження, але документ можна передати;
failed — бракує обовʼязкових частин;
blocked — без додаткових даних продовжувати не можна.
```

Якщо gate повернув `failed` або `blocked`, модель не має права робити вигляд, що все гаразд.

Вона має явно сказати:

```text
Поточний gate не пройдено.
Причина: бракує підтвердженого source contract.
Наступна дія: потрібно отримати representative source row або залишити пакет у draft status.
```

Це робить процес прозорим.

## 11.3. Gate у простому прикладі

Візьмемо дуже просте завдання:

```text
Підсумуй текст у максимум 3 пункти українською. Не додавай фактів, яких немає у вхідному тексті.
```

У prompt-формі це просто прохання.

В Ordo це набір кроків і gates.

```yaml
intent:
  goal: summarize_text

contract:
  output:
    format: bullet_list
    max_items: 3
    language: uk
  rules:
    - use_only_input_text
    - no_unsupported_facts

steps:
  - id: S1
    do: read_input_text
  - id: S2
    do: extract_supported_points
  - id: S3
    do: render_summary

gates:
  - id: G1
    method: mechanical
    trust_class: deterministic
    check: input_text_present
    on_fail: return_insufficient_data

  - id: G2
    method: self_verification
    trust_class: model_judgment
    check: no_unsupported_facts
    protocol:
      - list_claims
      - attach_source_span
      - classify_each_claim
    on_fail: remove_or_mark_unsupported

  - id: G3
    method: mechanical
    trust_class: deterministic
    check: max_3_items
    on_fail: compress_to_3_items

  - id: G4
    method: mechanical
    trust_class: deterministic
    check: output_language_uk
    on_fail: rewrite_in_ukrainian
```

Тут важливо не тільки те, що gates перелічені. Важливо, що для кожного gate є `on_fail`.

Тобто Ordo одразу описує, що робити, якщо перевірка не пройдена.

## 11.4. Gate має бути конкретним

Поганий gate звучить так:

```text
Перевір, що все добре.
```

Це занадто розмите. Модель може не знати, що саме означає “добре”.

Кращий gate:

```text
Перевір, що відповідь містить не більше 3 пунктів.
```

Ще кращий gate в Ordo-формі:

```json
{
  "op": "GATE.CHECK",
  "id": "G_MAX_3_ITEMS",
  "method": "mechanical",
  "trust_class": "deterministic",
  "assert": "ITEM_COUNT_LE",
  "source": "RESULT.summary",
  "params": {
    "max": 3
  },
  "on_fail": "REPAIR.COMPRESS_TO_LIMIT"
}
```

Тут видно:

- що саме перевіряється;
- де перевіряється;
- який параметр;
- що робити при помилці.

Це вже не побажання. Це контрольна точка.


## 11.4.1. Gate має показувати спосіб перевірки

У Ordo v0.12 gate більше не може виглядати однаково для всіх типів перевірок.

Є велика різниця між перевіркою, яку може виконати код, і перевіркою, яка потребує семантичного судження моделі або рішення людини.

Наприклад:

```text
порахувати, що в списку не більше 3 пунктів
```

це механічна перевірка.

А ось:

```text
визначити, чи всі факти мають достатню підтримку в джерелах
```

це вже не проста арифметика. Це семантична оцінка. Вона може бути добре структурованою, але не має такої самої сили, як перевірка кодом.

Тому кожен gate має явно мати два поля:

```yaml
method: mechanical | self_verification | self_consistency | human
trust_class: deterministic | model_judgment | repeated_model_judgment | human_decision
```

`method` показує, як саме виконується перевірка.

`trust_class` показує, якому класу довіри належить результат цієї перевірки.

Наприклад:

```json
{
  "op": "GATE.CHECK",
  "id": "G_MAX_3_ITEMS",
  "method": "mechanical",
  "trust_class": "deterministic",
  "assert": "ITEM_COUNT_LE",
  "source": "RESULT.summary",
  "params": {
    "max": 3
  },
  "on_fail": "REPAIR.COMPRESS_TO_LIMIT"
}
```

А для семантичної перевірки:

```json
{
  "op": "GATE.CHECK",
  "id": "G_NO_UNSUPPORTED_FACTS",
  "method": "self_verification",
  "trust_class": "model_judgment",
  "assert": "NO_UNSUPPORTED_FACTS",
  "protocol": [
    "list_claims",
    "attach_source_span",
    "classify_each_claim"
  ],
  "on_fail": "REPAIR_OR_ESCALATE"
}
```

У першому випадку runtime або скрипт може порахувати кількість пунктів. У другому випадку модель виконує structured verification, але це все одно залишається model judgment.

Це не робить другий gate непотрібним. Навпаки, він дуже корисний. Але Ordo має чесно показувати, що це інший клас довіри.

Відсутність `method` у gate має бути помилкою компіляції, а не мовчазним припущенням.

```text
ERROR: gate.method is required
```

## 11.5. Gate може зупиняти процес

Не кожен gate має автоматичний repair.

Іноді модель може сама виправити проблему. Наприклад, якщо відповідь вийшла занадто довгою, модель може стиснути її.

Але іноді модель не має права сама виправляти ситуацію.

Наприклад:

```text
Чи підтверджений контракт HistoryEvent.item.values?
```

Якщо контракт не підтверджений, модель не повинна вигадувати його.

Правильна дія:

```text
BLOCK_AND_REQUEST_CONFIRMATION
```

Приклад:

```json
{
  "op": "GATE.CHECK",
  "id": "G_HISTORY_EVENT_VALUES_CONFIRMED",
  "method": "human",
  "trust_class": "human_decision",
  "assert": "MANDATORY_CONTRACT_CONFIRMED",
  "target": "HistoryEvent.item.values",
  "on_fail": "BLOCK_AND_REQUEST_CONFIRMATION"
}
```

Це дуже важливо.

Ordo не повинна заохочувати модель “дотягувати” відповідь до красивого фіналу, якщо ключові дані відсутні.

![Nebu — увага: hard stop сильніший за бажання завершити відповідь](../assets/mascots/64x64/Nebu_attention_64x64.png)

У багатьох реальних процесах правильна відповідь моделі — не фінальний документ, а чесне повідомлення:

```text
Продовжувати не можна, бо не підтверджений обов'язковий контракт.
```

## 11.6. Gate і hard stop

Деякі gates є мʼякими. Вони дозволяють repair.

Наприклад:

```text
output_language_uk
```

Якщо відповідь не українською, модель може переписати її українською.

Але є gates, які є hard stop.

Hard stop означає: не можна продовжувати без зовнішнього підтвердження, нових даних або явного рішення користувача.

Приклади hard stop:

```text
- final archive before confirmed contracts;
- proposed contract used as confirmed;
- missing approval for mandatory document;
- unresolved source row contract;
- automation-ready without runner evidence;
- rendered QA artifact failed validation.
```

У Ordo hard stop має бути описаний явно.

```yaml
hard_stop_conditions:
  - unresolved_mandatory_contract
  - proposed_contract_used_as_confirmed
  - final_archive_without_approvals
  - rendered_artifact_validation_failed
```

Якщо спрацьовує hard stop, модель має перейти не до результату, а до статусу `blocked` або `requires_confirmation`.

## 11.7. Gate перед результатом і gate всередині процесу

Gates бувають різних типів.

Перший тип — локальні gates. Вони перевіряють конкретний крок.

Наприклад:

```text
Чи відповідь користувача входить у allowed answers цього NODE?
```

Другий тип — contract gates. Вони перевіряють, чи можна вважати певний контракт підтвердженим.

Наприклад:

```text
Чи підтверджені source field paths?
```

Третій тип — output gates. Вони перевіряють готовий результат.

Наприклад:

```text
Чи всі 11 файлів compact package присутні?
```

Четвертий тип — handoff gates. Вони перевіряють, чи можна передавати результат у роботу.

Наприклад:

```text
Чи пройдені approval gates для passport, Jira, QA package і automation spec?
```

У складній Ordo-програмі всі ці gates можуть співіснувати.

Важливо не змішувати їх.

Локальний gate не замінює фінальний self-check.

А фінальний self-check не замінює contract confirmation у середині процесу.

## 11.8. Gate має мати evidence

Gate без доказу легко перетворюється на декоративну фразу.

![Nebu — подумати: Gate має мати evidence](../assets/mascots/64x64/Nebu_thinking_64x64.png)

Погано:

```json
{
  "gate": "contracts_confirmed",
  "status": "passed"
}
```

Чому погано?

Бо незрозуміло, звідки взято `passed`.

Краще:

```json
{
  "op": "GATE.CHECK",
  "id": "G_SOURCE_ROW_CONTRACT",
  "method": "human",
  "trust_class": "human_decision",
  "assert": "SOURCE_ROW_CONTRACT_CONFIRMED",
  "status": "passed",
  "evidence": {
    "source": "representative_source_row",
    "fields_confirmed": [
      "type",
      "sub_type",
      "source",
      "root_id",
      "dms_id",
      "item.target_field"
    ]
  }
}
```

Тут видно, чому gate пройдено.

У простих задачах evidence може бути мінімальним. У складних задачах evidence стає обов'язковою частиною довіри до результату.

Після v0.12 evidence треба читати разом із `method`. Якщо `method: mechanical`, evidence може бути машинним результатом перевірки. Якщо `method: self_verification`, evidence показує, як модель обґрунтувала свій висновок. Якщо `method: human`, evidence має показувати, яке саме підтвердження або рішення людини було отримано.

## 11.9. Gate не має бути захований у FREEFORM

Ordo дозволяє `FREEFORM`, але важливі gates не можна ховати у вільний текст.

Погано:

```json
{
  "op": "FREEFORM.ADD",
  "role": "important_note",
  "text": "Не створювати фінальний пакет, якщо не підтверджені контракти."
}
```

Це не просто примітка. Це правило зупинки.

Його треба оформити як gate:

```json
{
  "op": "GATE.CHECK",
  "id": "G_NO_FINAL_PACKAGE_BEFORE_CONTRACTS",
  "method": "mechanical",
  "trust_class": "deterministic",
  "assert": "ALL_MANDATORY_CONTRACTS_CONFIRMED",
  "on_fail": "BLOCK_FINAL_PACKAGE"
}
```

А у `FREEFORM` можна залишити пояснення:

```json
{
  "op": "FREEFORM.ADD",
  "role": "rationale",
  "binding": "GATE.G_NO_FINAL_PACKAGE_BEFORE_CONTRACTS",
  "text": "Цей gate потрібен, щоб модель не перетворювала proposed або candidate contracts на confirmed без підтвердження."
}
```

Так Ordo зберігає і контроль, і людське пояснення.

## 11.10. Gate і repair action

Не кожне порушення має закінчуватися блокуванням.

Іноді правильніше дати моделі шанс виправити результат.

Наприклад:

```json
{
  "op": "GATE.CHECK",
  "id": "G_OUTPUT_LANGUAGE",
  "method": "mechanical",
  "trust_class": "deterministic",
  "assert": "LANG_IS",
  "params": {
    "lang": "uk"
  },
  "source": "RESULT.primary",
  "on_fail": "REPAIR.REWRITE_IN_LANGUAGE"
}
```

Або:

```json
{
  "op": "GATE.CHECK",
  "id": "G_MAX_ITEMS",
  "method": "mechanical",
  "trust_class": "deterministic",
  "assert": "ITEM_COUNT_LE",
  "params": {
    "max": 3
  },
  "source": "RESULT.summary",
  "on_fail": "REPAIR.COMPRESS"
}
```

Repair action має бути безпечним.

Якщо модель може виправити проблему без нових даних і без порушення контракту, repair дозволений.

Якщо для виправлення потрібне нове знання або підтвердження людини, repair не дозволений. Тоді потрібен `BLOCK` або `REQUEST_CONFIRMATION`.

## 11.11. Gate і користувач

Gate не має робити процес незручним для користувача.

Погано, якщо модель після кожної дрібниці каже:

```text
Потрібне підтвердження. Потрібне підтвердження. Потрібне підтвердження.
```

Ordo має відрізняти:

```text
- що модель може безпечно зробити сама;
- що можна позначити як assumption;
- що можна залишити як open question;
- що потребує explicit approval;
- що є hard stop.
```

Наприклад, для чернетки документа можна залишити placeholder.

Але для фінального контракту не можна мовчки залишити припущення.

Тому gate має знати контекст:

```yaml
mode:
  draft: allow_placeholders
  final: require_confirmed_contracts
```

Це дозволяє Ordo бути не тільки суворою, а й практичною.

## 11.12. Gate report

Після важливого етапу Ordo-програма має вміти показати gate report.

Gate report — це короткий звіт про те, які перевірки пройдено, які ні, і що це означає.

Приклад:

```json
{
  "trace_source": "hybrid",
  "gate_report": [
    {
      "id": "G_PATH_SELECTED",
      "method": "mechanical",
      "trust_class": "deterministic",
      "status": "passed",
      "evidence": "terminal_path = Path 1 candidate"
    },
    {
      "id": "G_SOURCE_ROW_CONFIRMED",
      "method": "human",
      "trust_class": "human_decision",
      "status": "failed",
      "reason": "representative source row not provided",
      "next_action": "request source row or keep package in draft mode"
    },
    {
      "id": "G_NO_FINAL_PACKAGE",
      "method": "mechanical",
      "trust_class": "deterministic",
      "status": "blocked",
      "reason": "mandatory contracts unresolved"
    }
  ]
}
```

Для користувача це дуже корисно. Він бачить не просто “модель не може продовжити”, а чому саме.

Для розробника або runtime це ще корисніше, бо gate report можна перевіряти автоматично.

## 11.13. Типові помилки з gates

Перша помилка — писати gates як загальні побажання.

```text
Перевірити якість.
```

Краще:

```text
Перевірити, що кожен executable TC має source lookup, action, ChangeRecord lookup, history processing, event assertion, rollback і post-rollback verification.
```

Друга помилка — не описувати `on_fail`.

Якщо gate не пройдено, модель має знати, що робити.

Третя помилка — ховати hard stop у FREEFORM.

Четверта помилка — дозволяти моделі самій вирішувати, що gate passed, без evidence.

Пʼята помилка — мати gate у шаблоні, але не перевіряти фінальний rendered artifact.

Шоста помилка — не розрізняти `failed`, `blocked` і `requires_confirmation`.

Сьома помилка — не вказувати `method` і створювати враження, що semantic self-check має таку саму силу, як механічна перевірка кодом.

Ці помилки роблять Ordo-програму схожою на звичайний довгий prompt. А мета Ordo — якраз уникнути цього.

## 11.14. Короткий підсумок розділу

Gate — це контрольна точка виконання.

Він має відповідати на питання:

```text
Чи можна рухатися далі?
```

Добрий gate має:

```text
- чітку умову;
- method;
- trust_class;
- джерело перевірки;
- статус;
- evidence;
- on_fail поведінку;
- зрозумілий вплив на наступний крок.
```

Gate може:

```text
- дозволити рух далі;
- запустити repair;
- попросити підтвердження;
- заблокувати фінальний результат;
- створити gate report.
```

Головний принцип:

```text
Gate — це не порада.
Gate — це точка, де Ordo-програма вирішує, чи має модель право продовжувати.
```

## Міні-вправа

Візьміть будь-який свій процес і знайдіть у ньому три місця, де модель не має права рухатися далі без перевірки.

Для кожного місця запишіть:

```text
1. Що перевіряємо?
2. Де це перевіряємо?
3. Який статус можливий?
4. Який `method` потрібен: mechanical, self_verification, self_consistency чи human?
5. Який `trust_class` має результат перевірки?
6. Що робити, якщо перевірка не пройдена?
7. Чи може модель виправити це сама, чи потрібне підтвердження людини?
```

Після цього спробуйте записати один gate у JSON-формі.

---

<!-- REVIEWED: chapter 11; v0.12 gate.method/trust_class applied; Nebu markers checked -->
