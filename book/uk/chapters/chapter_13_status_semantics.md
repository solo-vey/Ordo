# Розділ 13. Status semantics

## Навіщо це потрібно

У звичайній розмові зі штучним інтелектом статус часто виглядає як дрібниця.

Модель може написати:

```text
готово
зроблено
можна передавати
виглядає коректно
потрібне уточнення
```

На перший погляд, усе зрозуміло. Але для керованого процесу цього недостатньо.

Проблема в тому, що такі слова не завжди мають чітке значення. Для однієї людини “готово” означає “чернетку можна прочитати”. Для іншої — “файл можна передавати розробнику”. Для третьої — “усі перевірки пройдено, ризиків немає”.

Для Ordo така нечіткість небезпечна. Якщо статус не має формальної семантики, модель може передчасно завершити процес, перескочити approval gate, видати чернетку як фінальний результат або назвати результат “готовим” без доказів.

Тому в Ordo потрібна окрема частина мови:

```text
STATUS.SEMANTICS
```

Вона визначає, що саме означає кожний статус, хто може його встановити, які gate-и мають бути пройдені перед цим і які дії дозволені після нього.

## Просте пояснення

Статус — це не просто етикетка.

![Nebu — ідея: статус як контрольована позиція процесу](../assets/mascots/64x64/Nebu_idea_64x64.png)

У Ordo статус — це контрольована позиція процесу.

Наприклад:

```text
needs_input
ready_for_analysis
analysis_in_progress
needs_approval
approved_for_generation
ready_for_handoff
blocked
```

Кожний статус має відповідати на кілька питань:

```text
1. Що вже відбулося?
2. Що ще не відбулося?
3. Хто має право перевести процес у цей статус?
4. Які дії тепер дозволені?
5. Які дії тепер заборонені?
6. Який наступний легальний статус?
```

Без цього статуси стають декоративними словами. З цим — вони стають частиною виконання.

## Чому статуси важливі саме для AI-моделі

Людина часто розуміє статус із контексту. Якщо аналітик каже “можна”, інша людина може уточнити, що саме можна: продовжити аналіз, створити файл, віддати в QA чи передати розробнику.

AI-модель так не працює надійно. Вона може взяти слово “можна” занадто широко.

Наприклад, користувач каже:

```text
Так, варіант підходить.
```

Модель може помилково вирішити:

```text
Користувач затвердив фінальну генерацію архіву.
```

А насправді користувач міг мати на увазі тільки:

```text
Мені підходить ідея, але ще не фінальний документ.
```

`STATUS.SEMANTICS` потрібен, щоб такі переходи не відбувалися автоматично.

## Ordo-конструкція

У Ordo статус можна описати так:

```yaml
status_semantics:
  - status: "needs_input"
    meaning: "процес очікує дані або рішення від користувача"
    allowed_actions:
      - "ask_question"
      - "summarize_current_state"
    forbidden_actions:
      - "generate_final_package"
      - "mark_as_ready_for_handoff"
    next_allowed_statuses:
      - "ready_for_analysis"
      - "blocked"

  - status: "ready_for_handoff"
    meaning: "результат пройшов mandatory gates і може бути переданий далі"
    requires_gates:
      - "G_CONTRACT_CONFIRMED"
      - "G_OUTPUT_VALIDATED"
      - "G_SELF_CHECK_PASSED"
    allowed_actions:
      - "handoff_result"
    forbidden_actions:
      - "change_contract_without_reapproval"
```

У compiled IR це може перетворитися на операції:

```json
[
  {
    "op": "STATUS.DEF",
    "id": "S_NEEDS_INPUT",
    "status": "needs_input",
    "meaning": "process waits for user input or decision"
  },
  {
    "op": "STATUS.ALLOW",
    "status": "needs_input",
    "actions": ["ask_question", "summarize_current_state"]
  },
  {
    "op": "STATUS.FORBID",
    "status": "needs_input",
    "actions": ["generate_final_package", "mark_as_ready_for_handoff"]
  },
  {
    "op": "STATUS.REQUIRE.GATES",
    "status": "ready_for_handoff",
    "gates": ["G_CONTRACT_CONFIRMED", "G_OUTPUT_VALIDATED", "G_SELF_CHECK_PASSED"]
  }
]
```

Головне не конкретний синтаксис, а принцип: статус має бути виконуваним правилом, а не вільною фразою.

## Status lifecycle

Для Ordo-програми корисно описувати не тільки окремі статуси, а й життєвий цикл процесу.

Наприклад:

```text
created
→ needs_input
→ contract_ready
→ contract_confirmed
→ analysis_in_progress
→ needs_approval
→ approved_for_generation
→ generation_in_progress
→ validation_in_progress
→ ready_for_handoff
→ handed_off
```

Такий lifecycle показує, як процес має рухатися.

Важливо: модель не повинна сама вигадувати переходи між статусами.

Якщо дозволено тільки:

```text
needs_approval → approved_for_generation
```

то модель не може перейти напряму:

```text
needs_approval → ready_for_handoff
```

Навіть якщо їй здається, що “все вже зрозуміло”.

## Status transition

Перехід між статусами — це окрема дія.

У простому вигляді:

```yaml
status_transitions:
  - from: "needs_approval"
    to: "approved_for_generation"
    allowed_by:
      - "user_explicit_approval"
    requires:
      - "approval_scope_defined"
    on_missing_requirement: "STOP"
```

Це означає: модель не може просто сказати “схоже, затверджено”. Має бути явне підтвердження або інша дозволена умова.

У Ordo бажано розрізняти:

```text
model_can_set
user_must_set
runtime_can_set
external_system_can_set
```

Наприклад:

```yaml
status: "contract_confirmed"
can_be_set_by:
  - "user"
forbidden_for:
  - "model_without_explicit_approval"
```

Це особливо важливо для процесів, де модель має допомагати, але не має права приймати бізнес-рішення замість людини.

## Статуси і gates

Статус не має встановлюватися без gate-ів.

Погано:

```text
Модель: усе перевірено, статус ready_for_handoff.
```

Краще:

```yaml
set_status: "ready_for_handoff"
requires_gates:
  - "G_REQUIRED_FILES_PRESENT"
  - "G_NO_UNRESOLVED_PLACEHOLDERS"
  - "G_CONSISTENCY_CHECK_PASSED"
  - "G_HANDOFF_NOTE_PRESENT"
```

У цьому випадку статус — це не думка моделі. Це результат проходження контрольних точок.

Якщо хоча б один gate не пройдено, статус не може бути встановлений.

```text
G_CONSISTENCY_CHECK_PASSED = failed
→ ready_for_handoff заборонено
```

Саме так Ordo зменшує ризик передчасного “готово”.

## Статуси і ASSERT.NOT

Негативні перевірки також можуть бути прив’язані до статусів.

Наприклад:

```yaml
status: "ready_for_handoff"
assert_not:
  - "unresolved_placeholders_present"
  - "missing_validation_report"
  - "unconfirmed_assumption_present"
  - "freeform_without_binding"
```

Це означає, що процес не може назватися готовим, якщо в ньому залишилися заборонені умови.

Для фінального статусу часто важливі саме негативні перевірки:

```text
немає незаповнених місць
немає вигаданих рішень
немає невидимих припущень
немає неперевірених документів
немає непоясненого FREEFORM
```

## Статуси і користувацькі відповіді

![Nebu — увага: коротка відповідь діє тільки в межах поточного вузла](../assets/mascots/64x64/Nebu_attention_64x64.png)

Одна з найважливіших проблем у роботі з AI-моделями — інтерпретація коротких відповідей користувача.

Користувач може написати:

```text
так
ок
підходить
далі
можна
згоден
```

Без `STATUS.SEMANTICS` модель може трактувати це занадто широко.

Ordo має вимагати, щоб коротка відповідь користувача інтерпретувалась тільки в межах поточного node або поточного gate.

Наприклад, якщо поточне питання було:

```text
Обрати варіант A, B або C?
```

і користувач відповів:

```text
A
```

це не означає:

```text
користувач затвердив фінальний пакет
```

Це означає тільки:

```text
користувач обрав варіант A у поточному node
```

Тому в Ordo статус повинен бути пов’язаний з current node, current gate і current question.

## Приклад: guided intake

Уявімо, що модель проводить guided intake нової історичної події.

Можливі статуси:

```yaml
statuses:
  - "intake_started"
  - "path_selected"
  - "event_alias_confirmed"
  - "source_row_confirmed"
  - "values_confirmed"
  - "qa_scope_confirmed"
  - "package_ready_for_generation"
  - "package_generated"
  - "package_validated"
  - "package_ready_for_handoff"
```

Для кожного статусу можна задати allowed transitions:

```yaml
transitions:
  - from: "intake_started"
    to: "path_selected"
    requires: ["path_decision_answered"]

  - from: "path_selected"
    to: "event_alias_confirmed"
    requires: ["alias_confirmed_by_user"]

  - from: "package_generated"
    to: "package_validated"
    requires: ["self_check_executed", "validation_report_created"]

  - from: "package_validated"
    to: "package_ready_for_handoff"
    requires: ["no_blocking_validation_errors"]
```

Тепер модель не просто “йде за розмовою”. Вона рухається через контрольовану карту статусів.

## Приклад: документ

Для підготовки документа статуси можуть бути такими:

```text
draft_requested
structure_confirmed
content_drafted
content_reviewed
rendered_artifact_created
rendered_artifact_validated
ready_to_share
```

У цьому випадку важливо не плутати:

```text
content_drafted
```

і

```text
ready_to_share
```

Звичайна модель може написати “готово” після створення тексту. Але для Ordo текст ще не готовий, якщо не пройдено перевірку фінального артефакту.

Наприклад:

```yaml
status: "ready_to_share"
requires:
  - "content_reviewed"
  - "rendered_artifact_created"
  - "rendered_artifact_validated"
  - "download_link_available"
```

Це особливо важливо для PDF, DOCX, презентацій, архівів і пакетів документів.

## Чернетка, фінал і handoff

Одна з головних причин вводити статуси — розвести три різні стани:

```text
draft
final
handoff_ready
```

Це не одне й те саме.

`draft` означає:

```text
текст або структура створені, але ще можуть бути неповними
```

`final` означає:

```text
зміст вважається завершеним у межах поточного contract
```

`handoff_ready` означає:

```text
результат не тільки завершений, а й перевірений, упакований і готовий до передачі
```

У Ordo не можна підміняти один статус іншим.

Наприклад:

```text
final_content != handoff_ready_package
```

Фінальний текст може бути готовим, але файл ще не перевірений. Або пакет може бути сформований, але validation report показує помилки. У таких випадках статус `handoff_ready` недозволений.

## Status report

Ordo-процес має вміти показати статус не тільки словом, а й коротким звітом.

Наприклад:

```yaml
status_report:
  current_status: "needs_approval"
  current_node: "N_APPROVE_PACKAGE_SCOPE"
  completed_gates:
    - "G_PATH_SELECTED"
    - "G_ALIAS_CONFIRMED"
  pending_gates:
    - "G_PACKAGE_SCOPE_APPROVED"
  blocked_actions:
    - "generate_final_archive"
  next_allowed_actions:
    - "ask_package_scope_approval"
```

Такий звіт корисний і для користувача, і для runtime, і для наступної моделі, яка може підхопити процес.

Він також зменшує ризик втрати контексту в довгих діалогах.

## Статуси і trace

![Nebu — подумати: статус має залишати слід](../assets/mascots/64x64/Nebu_thinking_64x64.png)

Статуси повинні залишати слід.

Недостатньо просто мати поточний статус. Потрібна історія переходів:

```yaml
trace_source: "model_self_report"
status_trace:
  - from: "needs_input"
    to: "contract_ready"
    reason: "all mandatory intake fields collected"
    evidence: ["E_INPUT_FIELDS_COMPLETE"]

  - from: "contract_ready"
    to: "contract_confirmed"
    reason: "user explicitly approved contract"
    evidence: ["E_USER_APPROVAL_2026_07_05"]
```

Це дає відповідь на питання:

```text
чому процес зараз у цьому статусі?
хто або що його сюди перевело?
які докази цього переходу?
```

Для Ordo це дуже важливо, бо без trace статус знову перетворюється на заяву моделі.

## Типові помилки

### Помилка 1. Використовувати розмиті статуси

Погано:

```text
ok
ready
done
almost_done
good
```

Краще:

```text
contract_confirmed
content_drafted
validation_passed
ready_for_handoff
```

Статус має описувати конкретний стан процесу.

### Помилка 2. Не розділяти approval і execution

Погано:

```text
approved
```

Незрозуміло, що саме затверджено: ідея, структура, contract, генерація, фінальний файл?

Краще:

```text
contract_approved
package_scope_approved
generation_approved
handoff_approved
```

### Помилка 3. Дозволяти моделі самій ставити фінальні статуси

Погано:

```yaml
status: "ready_for_handoff"
can_be_set_by: ["model"]
```

Краще:

```yaml
status: "ready_for_handoff"
can_be_set_by: ["runtime"]
requires_gates:
  - "G_SELF_CHECK_PASSED"
  - "G_RENDERED_ARTIFACT_VALIDATED"
  - "G_NO_BLOCKING_ERRORS"
```

Або, якщо runtime немає:

```yaml
can_be_set_by: ["model_after_required_trace"]
```

але тільки з обов’язковим gate report.

### Помилка 4. Не описувати allowed transitions

Погано:

```text
status може бути будь-яким із переліку
```

Краще:

```yaml
from: "needs_approval"
to: "approved_for_generation"
requires: ["explicit_user_approval"]
```

Статуси без переходів — це словник. Статуси з переходами — це процес.

### Помилка 5. Плутати статус і результат

```text
status = ready_for_handoff
```

не є самим handoff. Це тільки дозвіл на handoff.

Так само:

```text
status = validation_passed
```

не є validation report. Це результат проходження validation gate, який має мати evidence.

## Міні-вправа

Візьміть будь-який процес, який ви часто доручаєте AI-моделі.

Наприклад:

```text
Підготувати задачу для Jira.
```

Спробуйте описати статуси:

```text
request_received
problem_context_collected
acceptance_criteria_drafted
qa_scope_drafted
pm_level_review_needed
ready_for_jira_copy
```

Потім для кожного статусу дайте відповідь:

```text
1. Що означає цей статус?
2. Хто може його встановити?
3. Які gate-и потрібні перед ним?
4. Які дії дозволені після нього?
5. Які дії заборонені після нього?
6. Який наступний статус дозволений?
```

Після цього ви побачите, що навіть простий процес стає набагато контрольованішим.

## Короткий підсумок

`STATUS.SEMANTICS` визначає, що саме означають статуси в Ordo-програмі.

Статус у Ordo — це не просто слово “готово” або “зроблено”. Це формальний стан процесу з правилами, дозволеними діями, заборонами, переходами, gate-ами і evidence.

Добре описані статуси захищають процес від передчасного завершення, неправильного трактування коротких відповідей користувача, прихованих переходів і змішування чернетки з фінальним handoff.

Якщо `Gate` відповідає на питання “чи можна пройти далі?”, то `STATUS.SEMANTICS` відповідає на питання “де саме ми зараз у процесі і що нам дозволено робити далі?”.

<!-- REVIEWED: chapter 13; Nebu markers checked -->
