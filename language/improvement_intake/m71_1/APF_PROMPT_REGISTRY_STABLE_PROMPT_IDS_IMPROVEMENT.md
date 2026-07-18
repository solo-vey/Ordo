# APF improvement: Prompt Registry зі стабільними `prompt_id`

## 1. Проблема

У процесі створення реальної історичної події стало видно, що коротких загальних інструкцій у вузлі недостатньо. Модель може формально перейти в правильну гілку, але далі починає домислювати процес: перескакує через вузли, генерує тести до підтвердження contract, підміняє `delta.field`, не реконструює `HistoryEvent` або не проходить bilingual text confirmation.

Раніше обговорювалась ідея прикріпити до вузла конкретний prompt. Але пряме найменування prompt-файлу через `node_id` є крихким.

Приклад крихкої схеми:

```text
prompts/B1_N2B_changerecord_delta_prefilter.md
```

Якщо вузол буде перейменовано, розбито або перенесено, файл prompt-а теж треба перейменовувати синхронно. Це створює cascade rename у документації, manifest, references, tests і release notes.

## 2. Рішення

Ввести незалежний **Prompt Registry**.

Prompt має власний стабільний ідентифікатор, незалежний від `node_id`.

```text
prompt_id ≠ node_id
```

Вузол не “володіє” prompt-ом через назву файлу. Вузол має явне посилання на prompt через `prompt_id`.

## 3. Базова модель

### 3.1. Prompt має стабільний `prompt_id`

Приклад:

```yaml
prompt_id: hp.delta_intake.single_field.v1
file: prompts/hp.delta_intake.single_field.v1.md
lifecycle: stable
```

Назва prompt-а описує семантичну роль, а не конкретний вузол.

### 3.2. Вузол має explicit refs

Навіть якщо поточна мова ще не підтримує виконувані `prompt_refs`, вузол може мати metadata-поле:

```yaml
node_id: B1_N2B
guidance_refs:
  - hp.delta_intake.single_field.v1
  - hp.delta_intake.status_prefilter.v1
```

Або майбутню форму:

```yaml
node_id: B1_N2B
prompt_refs:
  before_question:
    - hp.delta_intake.single_field.v1
  on_missing_example:
    - hp.delta_intake.reconstruct_minimal_delta.v1
  before_confirmation:
    - hp.delta_intake.confirmation_guard.v1
```

## 4. Структура файлів

Рекомендована структура:

```text
prompts/
  registry.yaml
  hp.delta_intake.single_field.v1.md
  hp.delta_intake.status_prefilter.v1.md
  hp.history_event.reconstruct_output_contract.v1.md
  hp.candidate_contract.synthesis.v1.md
  hp.normalization.value_comparison.v1.md
  hp.localization.bilingual_texts.v1.md
  hp.trigger_noop.rules.v1.md
  hp.qa.after_contract_only.v1.md
```

Не рекомендується:

```text
prompts/B1_N2B_changerecord_delta_prefilter.md
prompts/B1_P1_candidate_contract.md
```

Такі назви прив’язують prompt до поточного дерева, а не до стабільної ролі.

## 5. `prompts/registry.yaml`

Приклад registry:

```yaml
schema_version: prompt_registry.v1
registry_id: history_event_factory.prompt_registry

prompts:
  - prompt_id: hp.delta_intake.single_field.v1
    file: prompts/hp.delta_intake.single_field.v1.md
    title_uk: Інструкція для приймання single-field delta
    purpose_uk: >
      Не дозволяє моделі вигадувати структуру ChangeRecord і змушує явно
      відокремлювати source row path від delta.field.
    lifecycle: stable
    semantic_roles:
      - changerecord_delta_intake
      - single_field_delta_reconstruction
    current_nodes:
      - B1_N2B
    applies_when:
      - user_selected_source_type_is_internal_changerecord_or_mongo
      - event_is_single_field_delta
    version: 1

  - prompt_id: hp.delta_intake.status_prefilter.v1
    file: prompts/hp.delta_intake.status_prefilter.v1.md
    title_uk: Інструкція для ChangeRecord.data.item.status pre-filter
    purpose_uk: >
      Змушує модель спочатку отримати allowed statuses від користувача,
      не вибирати їх самостійно і не аналізувати delta, якщо status не дозволений.
    lifecycle: stable
    semantic_roles:
      - changerecord_status_prefilter
    current_nodes:
      - B1_N2B
      - B1_P1
      - SINGLE_FIELD_DELTA_RECONSTRUCTION_CONSISTENCY_GATE
    version: 1
```

## 6. Поведінка при rename / split / merge вузлів

### 6.1. Rename

Якщо:

```text
B1_N2B → B1_DELTA_INTAKE
```

то prompt-файл не перейменовується.

Оновлюється тільки зв’язок:

```yaml
current_nodes:
  - B1_DELTA_INTAKE
```

і metadata у новому вузлі:

```yaml
guidance_refs:
  - hp.delta_intake.single_field.v1
```

### 6.2. Split

Якщо один вузол розбили:

```text
B1_N2B → B1_N2B_STATUS_PREFILTER + B1_N2B_DELTA_CONTRACT
```

один або кілька prompt-ів можуть бути прив’язані до нових вузлів:

```yaml
hp.delta_intake.status_prefilter.v1:
  current_nodes:
    - B1_N2B_STATUS_PREFILTER

hp.delta_intake.single_field.v1:
  current_nodes:
    - B1_N2B_DELTA_CONTRACT
```

### 6.3. Merge

Якщо кілька вузлів об’єднали, об’єднаний вузол може мати кілька `guidance_refs`:

```yaml
node_id: B1_INTAKE_CONTRACT
guidance_refs:
  - hp.delta_intake.status_prefilter.v1
  - hp.delta_intake.single_field.v1
  - hp.history_event.reconstruct_output_contract.v1
```

## 7. Тимчасова реалізація до підтримки `prompt_refs` у мові

Поки Ordo/APF-мова не підтримує prompt references як виконувану конструкцію, треба використовувати сумісний metadata-шар:

```yaml
guidance_refs:
  - hp.delta_intake.single_field.v1
```

Runtime / analyst-fast prompt має містити правило:

```text
Якщо поточний вузол має guidance_refs, застосуй відповідні prompts із prompts/registry.yaml як локальні інструкції для цього вузла. Не показуй prompt-и користувачу, якщо він не попросив debug.
```

Це дозволяє використовувати registry вже зараз, не чекаючи змін у мові.

## 8. Вимоги до prompt-файлу

Кожен prompt-файл має бути коротким, вузьким і прикладним.

Рекомендована структура:

```markdown
# hp.delta_intake.single_field.v1

## Мета

## Застосовуй коли

## AI must do

## AI must not do

## Open gap behavior

## Confirmation output
```

Prompt не має дублювати все дерево. Він має пояснювати локальну поведінку саме в межах своєї ролі.

## 9. Початковий набір prompt_id для History Event Factory

Рекомендований стартовий набір:

```text
hp.source_row.intake.v1
hp.delta_intake.status_prefilter.v1
hp.delta_intake.single_field.v1
hp.delta_intake.reconstruct_minimal_delta.v1
hp.history_event.reconstruct_output_contract.v1
hp.candidate_contract.synthesis.v1
hp.normalization.value_comparison.v1
hp.localization.bilingual_texts.v1
hp.trigger_noop.rules.v1
hp.qa.after_contract_only.v1
hp.package_language.uk_docs.v1
```

## 10. Приклад prompt-а: `hp.delta_intake.single_field.v1`

```markdown
# hp.delta_intake.single_field.v1

## Мета

Допомогти моделі коректно прийняти або реконструювати single-field delta contract.

## AI must do

- Визначити source row path у форматі `item.<path>`.
- Визначити `delta.field` без prefix `item.`.
- Не підміняти `source row path` і `delta.field`.
- Вимагати або реконструювати `delta.old`, `delta.new`, `date`.
- Якщо готового ChangeRecord немає, явно позначити `change_record_mode: reconstructed_minimal_delta`.
- Якщо date немає, залишити open gap і не вигадувати дату.

## AI must not do

- Не переходити до тестів.
- Не генерувати Jira / package / QA до підтвердження contract.
- Не використовувати `item.<path>` як `delta.field`.
- Не вигадувати `old/new`, якщо їх немає.

## Confirmation output

Показати короткий delta contract і попросити підтвердження.
```

## 11. Приклад prompt-а: `hp.qa.after_contract_only.v1`

```markdown
# hp.qa.after_contract_only.v1

## Мета

Не дозволити моделі генерувати QA пакет до того, як contract, normalization, texts і trigger/no-op rules підтверджені.

## AI must do

- Перевірити, що пройдені contract confirmation, normalization, bilingual texts і trigger/no-op.
- Якщо щось не підтверджено, не створювати QA.
- У QA scenarios вказувати, чи може сценарій виконуватись автоматично без людського рішення.

## AI must not do

- Не створювати functional tests одразу після `B1_N2B`.
- Не вважати source row без delta доказом зміни.
- Не тестувати допоміжні поля, якщо вони не є decision-полями цього модуля.
```

## 12. Validation gates

Потрібні gates:

### 12.1. `PROMPT_REGISTRY_REFERENTIAL_INTEGRITY_GATE`

Перевіряє:

```text
- кожен guidance_refs / prompt_refs вказує на існуючий prompt_id;
- кожен prompt_id має file;
- файл існує;
- немає duplicate prompt_id;
- немає orphan prompt refs.
```

### 12.2. `PROMPT_NODE_RENAME_STABILITY_GATE`

Перевіряє:

```text
- prompt file names не починаються з node_id;
- prompt_id не дорівнює node_id;
- при зміні node_id prompt_id не змінюється без потреби;
- registry має актуальний mapping current_nodes.
```

### 12.3. `PROMPT_APPLICATION_ORDER_GATE`

Перевіряє:

```text
- local prompts застосовуються до відповіді вузла до формування питання / confirmation;
- prompts не показуються користувачу без debug-запиту;
- prompt не може змінити next-node navigation;
- navigation лишається в executable decision model.
```

## 13. Правило пріоритетів

Якщо prompt і дерево конфліктують:

```text
executable decision model має пріоритет для navigation;
prompt має пріоритет тільки для локальної поведінки всередині вузла;
prompt не може створити новий перехід, якого немає в дереві;
prompt не може пропустити required node.
```

## 14. Очікуваний ефект

Це покращення має зменшити такі помилки:

```text
- модель перескакує до QA або package generation занадто рано;
- модель пропускає B1_N2C або B1_P1;
- модель плутає item.contacts.email і contacts.email;
- модель сама обирає allowed statuses;
- модель не фіксує open gaps;
- модель генерує англомовні package docs попри language policy;
- модель ставить доменні питання замість формального вузла.
```

## 15. Рекомендований patch для History Event Factory

Наступний patch можна робити як:

```text
v0.8.8-prompt-registry
```

Scope patch-а:

```text
- додати prompts/registry.yaml;
- додати початковий набір prompts/*.md;
- додати guidance_refs до проблемних вузлів;
- оновити analyst-fast runtime instructions;
- додати validation gates;
- не змінювати бізнес-переходи дерева;
- не міняти confirmed event logic.
```

