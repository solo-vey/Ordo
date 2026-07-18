# Розділ 30. Міграція playbook-а в Ordo

## Навіщо це потрібно

Коли ми зрозуміли, що старий markdown-playbook є базою знань, виникає наступне питання: як перетворити його на Ordo-програму?

Це не має бути механічне переписування тексту. Міграція playbook-а в Ordo — це процес, у якому ми поступово виділяємо з документа виконувану структуру:

```text
intent → contract → context → state → paths → nodes → gates → outputs → tests → coverage
```

Мета міграції не в тому, щоб зробити документ “красивішим”. Мета — зробити процес керованим, трасованим, тестованим і придатним для повторного виконання.

![Nebu — ідея: міграція перетворює знання на виконувану структуру](../assets/mascots/64x64/Nebu_idea_64x64.png)

---

## Просте пояснення

Міграція playbook-а в Ordo схожа на перетворення великої інструкції для людини на програму для керованого виконання моделлю.

Було:

```text
Прочитай інструкцію, зрозумій контекст, постав питання, не забудь перевірити пакет, якщо все готово — сформуй архів.
```

Стає:

```yaml
intent:
  id: "create_history_event_package"

contract:
  requires:
    - "alias_confirmed"
    - "source_field_confirmed"
    - "expected_values_confirmed"

nodes:
  - id: "N_SELECT_PATH"
  - id: "N_COLLECT_ALIAS"
  - id: "N_COLLECT_SOURCE_FIELD"

required_gates:
  - "G_CONTRACT_CONFIRMED"
  - "G_PRE_ARCHIVE_APPROVAL"
  - "G_RENDERED_ARTIFACT_VALIDATED"
```

Тобто Ordo робить приховану логіку playbook-а явною.

![Nebu — подумати: прихована логіка має стати явними вузлами, станом і gates](../assets/mascots/64x64/Nebu_thinking_64x64.png)

---

## Основні етапи міграції

Міграцію варто описувати як послідовність із десяти кроків.

```text
1. Inventory
2. Classification
3. Contract extraction
4. Decision tree extraction
5. State model extraction
6. Gate extraction
7. Output mapping
8. FREEFORM binding
9. Test layer creation
10. IR compilation and validation
```

---

## Крок 1. Inventory

Спочатку потрібно зрозуміти, що взагалі є в playbook-у.

Потрібно скласти каталог фрагментів:

```yaml
source_catalog:
  sections:
    - id: "S01_INTRO"
      type: "explanation"
    - id: "S02_DECISION_TREE"
      type: "decision_logic"
    - id: "S03_OUTPUT_PACKAGE"
      type: "output_rules"
    - id: "S04_QA"
      type: "qa_rules"
```

Цей крок потрібен, щоб не втратити частину знань під час міграції.

---

## Крок 2. Classification

Далі кожен фрагмент класифікується.

Мінімальні категорії:

```text
- rule
- node
- gate
- status
- output
- template
- example
- anti-pattern
- freeform note
- improvement note
```

Наприклад:

```yaml
fragment:
  id: "F_SELF_CHECK_BEFORE_ARCHIVE"
  original_type: "markdown paragraph"
  classified_as:
    - "gate"
    - "assert_not"
    - "test_candidate"
```

Це важливо, бо різні типи фрагментів перетворюються на різні Ordo-конструкції.

---

## Крок 3. Contract extraction

У будь-якому складному playbook-у є умови, без яких роботу не можна вважати визначеною.

Наприклад для History Event package такими умовами можуть бути:

```text
- підтверджений alias;
- підтверджений тип події;
- підтверджене source field;
- зрозумілі old/new values;
- зрозумілий path;
- підтверджені expected outputs;
- підтверджені QA expectations.
```

В Ordo це стає contract:

```yaml
contract:
  required_inputs:
    - "event_alias"
    - "source_field"
    - "path_type"
    - "expected_values"

  missing_input_behavior:
    action: "ask_next_required_question"
    final_output_allowed: false
```

Головне правило:

![Nebu — увага: без зібраного contract не можна переходити до фінального output](../assets/mascots/64x64/Nebu_attention_64x64.png)

```text
якщо contract не зібраний, playbook не має переходити до фінального output
```

---

## Крок 4. Decision tree extraction

Якщо в playbook-у є різні сценарії, вони мають бути винесені в decision tree.

Наприклад:

```yaml
paths:
  - id: "A1"
    name: "direct source field change"
    condition: "change detected in primary source row"

  - id: "A2"
    name: "related entity change"
    condition: "change belongs to entity linked through identification center"

  - id: "A4"
    name: "external history event"
    condition: "input is ExternalHistoryEvent candidate"
```

У debug mode Ordo має показувати не тільки selected path, а й rejected paths:

```yaml
path_explain:
  selected: "A1"
  rejected:
    - path: "A2"
      reason: "related entity was not confirmed"
    - path: "A4"
      reason: "no external event input"
```

---

## Крок 5. State model extraction

Markdown часто приховує state у тексті.

Наприклад:

```text
Коли аналітик підтвердив source field, можна переходити до values.
```

В Ordo це має стати state transition:

```yaml
state:
  source_field_confirmed: true
  next_node: "N_COLLECT_VALUES"
```

Потрібно визначити:

```text
- які поля state існують;
- хто може їх змінювати;
- які значення означають готовність;
- які значення блокують процес;
- які transitions дозволені;
- які transitions заборонені.
```

Без state model модель буде “памʼятати процес у голові”, а це ненадійно.

---

## Крок 6. Gate extraction

Gate — це місце, де процес має зупинитися або перевірити умову.

Під час міграції потрібно шукати фрази типу:

```text
- перед тим як;
- тільки після;
- обовʼязково перевірити;
- не можна створювати;
- має бути підтверджено;
- якщо не визначено — зупинитися;
- без цього не переходити далі.
```

Такі фрази майже завжди є кандидатами на `GATE.DEF` або `ASSERT.NOT`.

Приклад:

```yaml
- op: "GATE.DEF"
  id: "G_PRE_ARCHIVE_APPROVAL"
  type: "blocking"
  before: "OUTPUT.FINAL_ARCHIVE"
  condition: "user_approval == true"
```

---

## Крок 7. Output mapping

Далі потрібно визначити, що саме playbook має створювати.

Для простого процесу це може бути один документ. Для складного — пакет файлів.

Ordo має явно описувати output:

```yaml
outputs:
  - id: "O_ANALYTICAL_PACKAGE"
    kind: "file_set"
    required_files:
      - "README.md"
      - "SUMMARY.json"
      - "VALIDATION_REPORT.json"
      - "CONSISTENCY_CHECK_REPORT.json"
```

Також потрібно описати rendered validation:

```yaml
render_validate:
  required:
    - "all_required_files_present"
    - "no_unexpected_files"
    - "no_unresolved_placeholders"
    - "cross_file_consistency_passed"
```

Output без validation — слабке місце.

---

## Крок 8. FREEFORM binding

Після перших семи кроків частина playbook-а все одно залишиться неформалізованою.

Це нормально.

Але її потрібно оформити як controlled FREEFORM:

```yaml
freeform:
  id: "FF_DOMAIN_EDGE_CASES"
  type: "domain_notes"
  bound_to:
    - "PATH.A4"
    - "G_EXTERNAL_EVENT_NORMALIZED"
  reason: "edge cases are described as examples and not yet stable enough for full formalization"
```

Головне правило:

```text
FREEFORM має бути привʼязаний до конкретної частини виконання
```

---

## Крок 9. Test layer creation

Після міграції потрібно створити тестовий шар.

Мінімальний набір:

```text
- один happy-path test для кожного path;
- negative tests для заборонених дій;
- gate tests;
- no-op tests;
- rendered artifact validation tests;
- regression suite.
```

Приклад:

```yaml
test:
  id: "TC_A1_HAPPY_PATH"
  fixture:
    user_message: "створюємо подію зміни статусу"
  expected:
    path: "A1"
    gates:
      - id: "G_CONTRACT_CONFIRMED"
        status: "passed"
    output:
      package_created: true
```

Тестування — це те, що відрізняє Ordo-міграцію від простого переписування документа.

---

## Крок 10. IR compilation and validation

Останній крок — скомпілювати Ordo Source в Semantic JSON IR і перевірити, що всі важливі частини playbook-а мають відображення.

Потрібно отримати:

```text
- compiled IR;
- traceability report;
- validation report;
- consistency check report;
- coverage report;
- freeform coverage report;
- regression suite summary.
```

Якщо частина playbook-а не покрита, це не завжди помилка. Але це має бути видно.

Наприклад:

```yaml
migration_report:
  structured_core: "72%"
  controlled_freeform: "28%"
  uncovered_fragments: 0
  blocking_gates_defined: 14
  tests_defined: 18
  status: "passed_with_notes"
```

---

## Мінімальний результат міграції

Після міграції має бути не один великий файл, а набір повʼязаних артефактів.

Наприклад:

```text
START_HERE_ORDO.md
ORDO_EXECUTION_CONTRACT.md
ORDO_CORE_BINDING.md
ORDO_PROFILE_BINDINGS.md
DOMAIN_PACK.md
PLAYBOOK_ORDO_SOURCE.md
PLAYBOOK_COMPILED_IR.json
FREEFORM_LEDGER.md
FREEFORM_COVERAGE.md
VALIDATION_REPORT.json
CONSISTENCY_CHECK_REPORT.json
```

Це не просто “більше файлів”. Це різні runtime views одного процесу.

---

## Як зрозуміти, що міграція успішна

Міграція успішна, якщо можна відповісти “так” на такі питання:

```text
1. Чи зрозуміло, з якого entry починати?
2. Чи є contract?
3. Чи є state model?
4. Чи є decision paths?
5. Чи є blocking gates?
6. Чи є outputs?
7. Чи є rendered validation?
8. Чи зрозуміло, що залишилось у FREEFORM?
9. Чи є tests?
10. Чи можна пояснити, чому run пішов певним шляхом?
```

Якщо відповідь “ні” хоча б на кілька пунктів, playbook ще не став повноцінною Ordo-програмою.

---

## Типові помилки

### Помилка 1. Починати з IR

Не треба одразу писати JSON IR руками.

Спочатку потрібно зрозуміти contract, paths, state і gates. IR — це compiled representation, а не перший документ, з якого варто починати роботу.

---

### Помилка 2. Не зберегти звʼязок зі старим playbook-ом

Якщо після міграції неможливо сказати, звідки взялося правило, це проблема.

Потрібна traceability matrix.

---

### Помилка 3. Формалізувати приклади як правила

Приклад показує можливу ситуацію. Rule визначає обовʼязкову поведінку.

Це різні речі.

---

### Помилка 4. Не виділити blocking gates

Якщо gate не blocking, модель може піти далі навіть після failed condition.

Для критичних процесів це неприпустимо.

---

### Помилка 5. Не додати improvement loop

Після першої міграції playbook не стане ідеальним.

Потрібно одразу мати механізм збору проблем і покращень.

---

## Міні-вправа

Візьміть один розділ старого playbook-а і спробуйте зробити міні-міграцію.

Заповніть таблицю:

```text
Фрагмент | Тип | Ordo object | Gate? | Test needed? | FREEFORM?
```

Наприклад:

```text
“Не створювати архів без self-check”
→ anti-pattern / gate candidate
→ ASSERT.NOT + GATE.DEF
→ так
→ так
→ ні
```

Це простий спосіб побачити, як текст починає перетворюватися на Ordo-програму.

---

## Короткий підсумок

Міграція playbook-а в Ordo — це не переписування документа іншими словами.

Це виділення виконуваної структури:

```text
knowledge → rules → state → paths → gates → outputs → tests → IR
```

Головна думка розділу:

```text
Ordo-міграція успішна тоді, коли playbook можна не тільки прочитати, а й виконати, пояснити, перевірити і покращити
```


---
