# Розділ 4. Intent, Contract, Context

У попередніх розділах ми говорили про Ordo як про мову керування поведінкою моделі. Тепер починаємо розбирати її базові будівельні блоки.

Перші три поняття, з яких варто починати майже будь-яку Ordo-програму, — це:

```text
Intent
Contract
Context
```

Їх легко переплутати, бо у звичайному prompt-і вони часто змішані в одному реченні. Але для Ordo важливо розділяти їх.

Коротко:

```text
Intent  — що ми хочемо зробити.
Contract — яким має бути правильний результат і які правила не можна порушити.
Context — з чим саме модель працює: вхідні дані, джерела, попередні рішення, документи.
```

Ці три речі створюють стартову рамку. Якщо вони не розділені, модель часто починає виконувати завдання занадто вільно. Якщо вони визначені чітко, модель має менше простору для випадкових припущень.

---

## 4.1. Чому ці три поняття важливі

Уявімо простий запит:

```text
Підготуй короткий звіт по цьому тексту.
```

На вигляд усе зрозуміло. Але якщо придивитися, тут багато невизначеного.

Що означає “короткий”?

Це 3 речення? 5 пунктів? Одна сторінка?

Що означає “звіт”?

Це підсумок? Аналітична записка? Таблиця? Рекомендації?

Чи можна моделі додавати власні висновки?

Чи має вона посилатися тільки на текст?

Чи потрібно показати відкриті питання?

Чи треба писати українською?

У звичайному prompt-і ці питання часто не проговорені. Модель сама добудовує відсутні частини. Іноді це зручно. Але якщо процес критичний, така свобода небезпечна.

Ordo пропонує почати з трьох уточнень:

```yaml
intent:
  goal: create_short_report

contract:
  output:
    format: bullet_report
    max_items: 5
    language: uk
  rules:
    - use_only_input_text
    - mark_missing_information

context:
  input_text: "$USER_INPUT.text"
```

Тепер завдання вже набагато чіткіше.

Модель не просто “готує звіт”. Вона створює короткий звіт у визначеному форматі, за визначеними правилами, на основі конкретного вхідного тексту.

---

## 4.2. Intent: намір або мета

`Intent` відповідає на питання:

```text
Що ми хочемо досягти?
```

Це не повний опис результату і не набір правил. Це головна мета.

Приклади intent-ів:

```yaml
intent:
  goal: summarize_text
```

```yaml
intent:
  goal: classify_user_request
```

```yaml
intent:
  goal: create_jira_task
```

```yaml
intent:
  goal: guide_analyst_through_history_event_intake
```

```yaml
intent:
  goal: generate_qa_package
```

Добрий `intent` має бути достатньо коротким. Якщо він перетворюється на великий абзац із правилами, значить частина змісту має переїхати в `contract`, `context`, `state`, `path` або `gates`.

Погано:

```yaml
intent:
  goal: "Створи повний пакет, але не вигадуй значення, перевір source row, зроби QA, automation, validation, не забудь approvals і не створюй архів якщо щось не підтверджено"
```

Чому погано?

Бо це вже не intent. Це змішання мети, правил, gates, outputs і hard stops.

Краще:

```yaml
intent:
  goal: create_history_event_analysis_package
```

А решту рознести:

```yaml
contract:
  final_result:
    type: compact_analysis_package
    required_outputs: 11

rules:
  - contract_first
  - no_final_archive_before_confirmed_contracts

gates:
  - path_selected
  - mandatory_contracts_confirmed
  - pre_archive_approvals_passed
```

`Intent` — це компас, а не карта.

Він показує напрям, але не описує всі дороги й перевірки.

---

## 4.3. Типові помилки з Intent

### Помилка 1. Робити intent занадто широким

Наприклад:

```yaml
intent:
  goal: help_user
```

Це майже нічого не означає. Допомогти можна сотнями способів. Модель мусить сама здогадуватися, що саме робити.

Краще:

```yaml
intent:
  goal: classify_support_request_and_select_output_documents
```

Тут уже зрозуміло, що треба не просто “допомогти”, а класифікувати звернення і вибрати документи.

### Помилка 2. Вкладати в intent правила

Наприклад:

```yaml
intent:
  goal: summarize_text_without_adding_facts_and_return_3_bullets_in_ukrainian
```

Це працює для маленьких задач, але погано масштабується.

Краще:

```yaml
intent:
  goal: summarize_text

contract:
  output:
    format: bullet_list
    max_items: 3
    language: uk
  rules:
    - no_unsupported_facts
```

### Помилка 3. Плутати intent і output

Наприклад:

```yaml
intent:
  goal: README.md
```

`README.md` — це output, а не intent.

Краще:

```yaml
intent:
  goal: explain_package_usage

outputs:
  - id: README
    file: README.md
```

Intent каже, навіщо створюється результат. Output каже, що саме буде створено.

---

## 4.4. Contract: що вважається правильним результатом

`Contract` відповідає на питання:

```text
Яким має бути результат, щоб ми могли вважати його правильним?
```

Це одне з найважливіших понять Ordo.

Звичайний prompt часто описує бажання користувача. Contract описує межі допустимого результату.

Наприклад, prompt:

```text
Підсумуй текст.
```

Contract:

```yaml
contract:
  output:
    format: bullet_list
    max_items: 3
    language: uk
  rules:
    - use_only_input_text
    - do_not_add_external_facts
    - if_input_is_insufficient_return_insufficient_data_status
```

Тут модель уже знає:

```text
- формат результату;
- максимальну кількість пунктів;
- мову;
- джерело фактів;
- що робити, якщо даних недостатньо.
```

Contract перетворює “зроби добре” на “зроби ось так і не порушуй ось ці правила”.

---

## 4.5. Contract не обов’язково має бути вигаданим з нуля

У реальних проєктах contract часто вже існує.

Наприклад:

```text
- існуючий формат JSON;
- API contract;
- database schema;
- шаблон документа;
- приклад реального HistoryEvent;
- існуючий ChangeRecord;
- корпоративний стандарт Jira-задачі;
- вимоги QA runner-а.
```

У такому випадку модель не має придумувати “кращий” contract. Вона має знайти і використати існуючий.

Це один із головних принципів Ordo:

```text
Спочатку перевірити, чи contract уже існує.
Тільки якщо його немає — запропонувати новий як proposed_contract.
```

Приклад:

```yaml
contract_resolution:
  search_order:
    - current_playbook_rules
    - factual_examples
    - source_row
    - code_contract
    - analyst_confirmation
  if_found: use_exactly
  if_not_found: propose_contract_with_confirmation_required
```

Це дуже важливо для AI-моделей, бо вони часто вміють створити логічний contract, але не завжди знають, що в конкретному проєкті вже існує інший.

---

## 4.6. Contract і “confirmed”

![Nebu — важливо: статус контракту](../assets/mascots/64x64/Nebu_attention_64x64.png)

Не кожен contract одразу confirmed.

У Ordo варто розрізняти:

```text
missing — контракту немає;
candidate — є можливий варіант;
proposed — модель запропонувала варіант;
requires_confirmation — потрібне підтвердження;
confirmed — контракт підтверджений;
blocked — без контракту не можна рухатися далі.
```

Наприклад:

```yaml
history_event_values_contract:
  status: proposed
  proposed_shape: flat_keys
  proposed_keys:
    - old#value
    - new#value
  evidence_source: analogy_with_existing_profile_events
  final_package_allowed: false
```

Тут модель може показати пропозицію, але не має права вважати її підтвердженою.

Після підтвердження аналітиком:

```yaml
history_event_values_contract:
  status: confirmed
  shape: flat_keys
  keys:
    - old#value
    - new#value
  evidence_source: analyst_confirmation
  final_package_allowed: true
```

Це здається бюрократією, але саме такі дрібні статуси захищають складні процеси від тихих помилок.

---

## 4.7. Contract може містити не тільки output

Часто contract помилково сприймають тільки як формат фінального результату. Насправді він може описувати різні речі.

Наприклад:

```yaml
contract:
  input:
    required:
      - source_row
      - event_alias
      - display_names

  output:
    type: compact_analysis_package
    files_count: 11

  rules:
    - no_invented_contracts
    - no_final_archive_before_approvals

  status_semantics:
    ready_for_first_run:
      runner_policy: execute

  forbidden:
    - nested_values_without_confirmation
    - delta_field_with_item_prefix
```

Тобто contract може включати:

```text
- input contract;
- output contract;
- field contract;
- status contract;
- naming contract;
- evidence contract;
- approval contract;
- forbidden forms.
```

У складних Ordo-програмах contract — це не один маленький блок, а цілий шар правил.

---

## 4.8. Context: з чим модель працює

`Context` відповідає на питання:

```text
Які дані, документи, приклади або правила модель має використати зараз?
```

Context — це не мета і не результат. Це матеріал для роботи.

Приклади context:

```yaml
context:
  user_request: "$USER_INPUT.message"
  source_text: "$USER_INPUT.text"
```

```yaml
context:
  documentation:
    - START_HERE_ORDO.md
    - 00_ORDO_EXECUTION_CONTRACT.md
    - 07_HISTORY_EVENT_PLAYBOOK_COMPILED_IR.json
```

```yaml
context:
  source_row:
    type: companyProfile
    sub_type: EDR
    dms_id: "..."
```

```yaml
context:
  examples:
    - factual_history_event_example
    - changerecord_example
```

Context може бути коротким або дуже великим. Але Ordo вимагає не просто “мати контекст”, а правильно його вибирати.

Для великих playbook-ів це особливо важливо.

Не треба щоразу змушувати модель тримати весь playbook у голові. Краще:

```text
DOC.SPLIT → DOC.CATALOG → DOC.SELECT
```

Тобто:

```text
розбити документацію;
створити каталог;
вибрати потрібні розділи для поточного кроку.
```

---

## 4.9. Чому context має бути обмеженим

![Nebu — подумати: обмежений контекст](../assets/mascots/64x64/Nebu_thinking_64x64.png)

Може здатися, що чим більше контексту, тим краще. Але це не завжди так.

Якщо модель бачить занадто багато документів одночасно, вона може:

```text
- використати неактуальне правило;
- змішати різні гілки процесу;
- взяти приклад за contract;
- застосувати правило з іншого path;
- пропустити поточний gate;
- витратити увагу на нерелевантні секції.
```

Тому Ordo вводить ідею focused context.

Для кожного кроку треба вибирати тільки те, що потрібно саме зараз.

Наприклад, якщо модель перебуває на старті guided intake, їй не потрібні повні QA templates. Їй потрібні:

```text
- entry definition;
- decision tree;
- правила першого питання;
- заборона питати alias/source row завчасно.
```

Якщо модель генерує QA package, тоді їй потрібні:

```text
- QA template;
- manual QA gates;
- rendered artifact validation;
- automation status rules;
- runner preflight, якщо застосовно.
```

Це дисципліна контексту.

---

## 4.10. Intent, Contract і Context на одному прикладі

Візьмемо завдання:

```text
Створи Jira-задачу для нової історичної події.
```

У prompt-підході модель може одразу написати задачу. Але в Ordo ми спочатку розділяємо.

### Intent

```yaml
intent:
  goal: create_jira_task_for_history_event
```

### Contract

```yaml
contract:
  output:
    file: "02_JIRA_TASK_<ALIAS>.md"
    format: jira_description
    required_sections:
      - Summary
      - Context
      - Acceptance criteria
      - Event Creation Logic
      - Data Mapping
      - Technical Deliverables
      - Out of scope
      - QA reference data
      - Test coverage
  rules:
    - do_not_replace_passport
    - do_not_duplicate_full_qa_runbook
    - use_confirmed_contracts_only
```

### Context

```yaml
context:
  confirmed_alias: "$STATE.alias"
  path: "$STATE.path"
  passport_draft: "$ARTIFACTS.passport"
  confirmed_values_contract: "$STATE.history_event_values_contract"
  qa_scope: "$STATE.qa_scope"
```

Тепер модель розуміє:

```text
- що вона робить;
- яким має бути результат;
- з яких даних вона має його створити.
```

Без цього вона може створити красиву, але неправильну Jira-задачу.

---

## 4.11. Як ці поняття пов’язані з gates

Intent, Contract і Context самі по собі ще не гарантують виконання. Потрібні gates.

Наприклад:

```yaml
gates:
  - id: G_INTENT_DEFINED
    assert: intent.goal is not empty

  - id: G_CONTRACT_CONFIRMED
    assert: mandatory_contracts.status == confirmed

  - id: G_CONTEXT_AVAILABLE
    assert: required_context_items are present
```

Якщо context відсутній, модель не має вигадувати дані.

Якщо contract не confirmed, модель не має створювати final package.

Якщо intent неясний, модель має поставити уточнення.

У Ordo gates перетворюють “було б добре” на контроль виконання.

---

## 4.12. Малий шаблон для старту будь-якої Ordo-програми

![Nebu — ідея: стартовий шаблон](../assets/mascots/64x64/Nebu_idea_64x64.png)

Коли ви проектуєте нову Ordo-програму, можна почати з такого мінімального шаблону:

```yaml
ordo: "0.12-draft"
program: "example.program"

intent:
  goal: "<що потрібно зробити>"

contract:
  input:
    required: []
  output:
    type: "<тип результату>"
  rules: []
  forbidden: []

context:
  sources: []
  user_input: "$USER_INPUT"

state:
  status: draft
  assumptions: []
  open_questions: []

gates:
  - id: G_INTENT_DEFINED
    check: intent_defined
  - id: G_CONTRACT_AVAILABLE
    check: mandatory_contract_available
  - id: G_CONTEXT_AVAILABLE
    check: required_context_available
```

Це ще не повна програма. Але це хороший старт.

---

## 4.13. Типові помилки

### Помилка 1. Починати з output без intent

Погано:

```yaml
outputs:
  - README.md
  - SUMMARY.json
```

Краще спочатку:

```yaml
intent:
  goal: explain_and_validate_package
```

Output без intent не пояснює, навіщо створюється артефакт.

### Помилка 2. Писати rules у context

Погано:

```yaml
context:
  note: "Не вигадувати фактів"
```

Краще:

```yaml
contract:
  rules:
    - no_unsupported_facts
```

Або як gate:

```yaml
gates:
  - id: G_NO_UNSUPPORTED_FACTS
    check: no_unsupported_facts
```

### Помилка 3. Класти джерело даних у contract

Погано:

```yaml
contract:
  source_text: "$USER_INPUT.text"
```

Краще:

```yaml
context:
  source_text: "$USER_INPUT.text"
```

Contract описує правила результату, а context — матеріал, з яким працює модель.

### Помилка 4. Не позначати статус контракту

Погано:

```yaml
contract:
  values:
    - old#value
    - new#value
```

Краще:

```yaml
contract:
  values:
    status: confirmed
    keys:
      - old#value
      - new#value
    evidence_source: factual_history_event_example
```

Якщо status не вказаний, модель може сприйняти candidate як confirmed.

---

## 4.14. Короткий підсумок розділу

`Intent`, `Contract` і `Context` — це перші три опори Ordo.

```text
Intent — що ми хочемо зробити.
Contract — яким має бути правильний результат і які правила не можна порушити.
Context — з якими даними, джерелами й документами модель працює.
```

Вони мають бути розділені.

Якщо intent занадто широкий, модель не знає, що саме робити.

Якщо contract нечіткий, модель може створити красивий, але неправильний результат.

Якщо context не обмежений, модель може застосувати не ті правила.

Добра Ordo-програма починається не з великого тексту, а з чіткої відповіді на три питання:

```text
1. Яка мета?
2. Який контракт правильного результату?
3. Який контекст потрібен саме зараз?
```

---

## Міні-вправа

Візьміть будь-який свій prompt і перепишіть його у три блоки.

Наприклад, prompt:

```text
Підготуй короткий лист клієнту про те, що інцидент ще аналізується, але ми вже працюємо над ним.
```

Спробуйте заповнити:

```yaml
intent:
  goal: "..."

contract:
  output:
    type: "..."
    tone: "..."
    language: "..."
  rules:
    - "..."

context:
  incident_summary: "..."
  known_facts: []
  unknown_facts: []
```

Після цього перевірте:

```text
- чи intent не містить зайвих правил;
- чи contract описує результат;
- чи context містить тільки дані й джерела;
- чи є щось, що треба винести в gate.
```

---
