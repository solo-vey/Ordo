# Розділ 27. Documentation Runtime

## Навіщо це потрібно

У попередньому розділі ми розібрали, чому формат `all-in-one` перестає бути головним, коли інструкція виростає до рівня великого playbook-а. Один великий файл зручно передати моделі, але незручно підтримувати, перевіряти, оновлювати й дебажити.

Проте одразу виникає нове питання: якщо ми розбили документацію на десятки окремих файлів, як модель має зрозуміти, які саме з них потрібні для поточного кроку?

Людина може відкрити зміст, переглянути назви, згадати контекст і вибрати потрібний розділ. Модель також може це зробити, але якщо залишити це тільки на її здогадку, ми знову повертаємося до проблеми звичайного prompt-а: вона може відкрити не той файл, пропустити важливу секцію або використати застарілу частину документа.

Саме для цього в Ordo потрібен `Documentation Runtime`.

`Documentation Runtime` — це мовний механізм, який керує тим, як Ordo-програма працює з великим набором документів: які документи існують, коли їх треба читати, які секції є source of truth, які документи допоміжні, а які не можна використовувати для прийняття рішень.

Інакше кажучи, це не просто “папка з інструкціями”. Це керований шар доступу до знань.

## Просте пояснення

Уявімо, що Ordo-програма — це кухар, а документація — це велика кулінарна бібліотека.

Якщо кухарю просто дати всю бібліотеку і сказати “готуй”, він може відкрити старий рецепт, переплутати десерт із основною стравою або використати примітку як обов’язкове правило.

Documentation Runtime працює як каталог і диспетчер:

```text
для цього кроку потрібні тільки ці документи;
цей документ є головним;
цей документ лише пояснює приклади;
цей файл застарів;
цей шаблон можна використовувати тільки після approval gate;
цей rendered artifact треба перевірити окремо.
```

Тобто Documentation Runtime не пише бізнесову логіку замість Domain Pack. Він відповідає за те, щоб модель брала правильні інструкції в правильний момент.

## Чим Documentation Runtime відрізняється від звичайної документації

Звичайна документація описує знання.

Documentation Runtime керує використанням знань.

Звичайна документація може сказати:

```text
У файлі 05_QA_PACKAGE описані правила QA.
```

Documentation Runtime має сказати точніше:

```text
NODE package_generation може читати 05_QA_PACKAGE_TEMPLATE.
Перед створенням QA-файлу потрібно перевірити G_QA_SCOPE_CONFIRMED.
Фінальний rendered QA-файл має пройти RENDER.VALIDATE.
Якщо fixture або source lookup не підтверджені, QA-файл не можна позначати як ready.
```

Це вже не просто опис. Це runtime-поведінка.

## Основні задачі Documentation Runtime

У Ordo Documentation Runtime має вирішувати кілька задач.

Перша задача — каталогізація документів.

Ordo має знати, які документи входять у пакет:

```text
README.md
execution contract
core binding
profile binding
domain pack
compiled IR
freeform ledger
validation report
source virtual docs
templates
examples
```

Друга задача — вибір потрібних документів для поточного вузла.

Модель не повинна щоразу перечитувати все. Для кожного `NODE` можна визначити набір документів, які дозволені або обов’язкові.

Третя задача — визначення source of truth.

Якщо є split-файли і all-in-one версія, потрібно явно знати, що редагувати треба split-файли, а all-in-one є зібраним артефактом. Інакше можна внести зміну не туди.

Четверта задача — контроль rendered artifacts.

Шаблон ще не означає, що фінальний файл правильний. Ordo має вміти відрізняти template від реально згенерованого документа.

П’ята задача — traceability.

Коли модель створила результат, має бути видно, на які документи вона спиралася.

## Ordo-конструкції

Для Documentation Runtime у мові потрібні такі конструкції:

```text
DOC.CATALOG
DOC.DEF
DOC.ROLE
DOC.SOURCE_OF_TRUTH
DOC.SELECT
DOC.BIND
DOC.READ
DOC.RENDER
DOC.SPLIT
DOC.MERGE
DOC.VERSION
DOC.DEPRECATE
DOC.TRACE
RENDER.VALIDATE
```

Розглянемо їх простими словами.

`DOC.CATALOG` описує список документів у пакеті.

`DOC.DEF` описує конкретний документ.

`DOC.ROLE` вказує роль документа: contract, template, example, source, generated artifact, validation report.

`DOC.SOURCE_OF_TRUTH` визначає, який файл є головним для зміни певного правила.

`DOC.SELECT` каже, які документи потрібні для поточного вузла.

`DOC.BIND` прив’язує документ до node, gate, output або library.

`DOC.TRACE` фіксує, які документи були реально використані під час run.

`RENDER.VALIDATE` перевіряє не шаблон, а вже згенерований фінальний артефакт.

## Малий приклад

Припустимо, у нас є Ordo-програма для створення аналітичного пакета.

У Source-форматі Documentation Runtime може виглядати так:

```yaml
doc_catalog:
  id: "history_event_docs"

  documents:
    - id: "execution_contract"
      path: "00_ORDO_EXECUTION_CONTRACT.md"
      role: "contract"
      source_of_truth: true

    - id: "domain_pack"
      path: "04_HISTORY_EVENT_DOMAIN_PACK.md"
      role: "domain_rules"
      source_of_truth: true

    - id: "qa_template"
      path: "05_QA_PACKAGE_TEMPLATE.md"
      role: "template"

    - id: "qa_output"
      path: "05_QA_PACKAGE_<ALIAS>.md"
      role: "rendered_artifact"
      generated: true

doc_select:
  node: "generate_qa_package"
  required:
    - "execution_contract"
    - "domain_pack"
    - "qa_template"
  forbidden:
    - "deprecated_all_in_one"

render_validate:
  output: "qa_output"
  rules:
    - "must_not_contain_unresolved_placeholders"
    - "must_include_manual_test_table"
    - "must_match_confirmed_contract"
```

Тут важливо, що модель не просто “знає про документи”. Вона отримує правила, які документи брати, які не брати, і як перевіряти результат.

## Documentation Runtime і all-in-one

Documentation Runtime не забороняє all-in-one. Він просто змінює його роль.

All-in-one може бути:

```text
- зручним read-only snapshot;
- артефактом для передачі моделі;
- зібраним представленням split-документів;
- контрольним переглядом усього пакета.
```

Але він не повинен автоматично бути source of truth.

Якщо source of truth — секційні файли, Documentation Runtime має явно це сказати:

```yaml
source_of_truth:
  rules:
    - target: "playbook_logic"
      document: "source_virtual_docs/"
    - target: "rendered_snapshot"
      document: "999_ALL_IN_ONE.md"
      editable: false
```

Це захищає від дуже типової помилки: модель редагує великий all-in-one файл, а реальні секційні документи залишаються старими.

## Documentation Runtime і trace

Коли Ordo-програма працює з документами, trace має показувати:

```text
які документи були вибрані;
чому саме вони;
які документи були відхилені;
які секції використані;
які outputs були згенеровані на їх основі;
чи пройшли rendered artifacts перевірку.
```

Наприклад:

```yaml
trace_source: "model_self_report"
doc_trace:
  node: "generate_qa_package"

  selected:
    - id: "execution_contract"
      reason: "required for confirmed scope"
    - id: "domain_pack"
      reason: "required for domain rules"
    - id: "qa_template"
      reason: "required for output structure"

  rejected:
    - id: "deprecated_all_in_one"
      reason: "not source of truth for editing"

  rendered_outputs:
    - id: "qa_output"
      validation: "passed"
```

Такий trace особливо важливий у debug mode. Якщо результат неправильний, ми можемо побачити, чи проблема в логіці, чи модель просто взяла не той документ.

## Documentation Runtime і бібліотеки

Після появи Ordo Libraries Documentation Runtime стає ще важливішим.

Бібліотека може підключати власні документи:

```text
- опис exported gates;
- шаблони;
- приклади;
- правила сумісності;
- changelog;
- tests;
- coverage report.
```

Ordo має знати, що ці документи належать не основному playbook-у, а бібліотеці.

Наприклад:

```yaml
library_docs:
  library: "ordo.validation.contract_first"
  version: "0.1"

  documents:
    - id: "contract_gates"
      path: "docs/gates.md"
      role: "library_rule_reference"

    - id: "contract_tests"
      path: "tests/contract_first_tests.yaml"
      role: "test_suite"
```

Якщо проблема виникла через правило з бібліотеки, `DOC.TRACE` і `IMPROVEMENT.RECORD` мають показати саме це.

## Documentation Runtime і FREEFORM

FREEFORM часто містить пояснення, приклади або винятки. Documentation Runtime має допомагати не втратити контроль над такими блоками.

Для кожного FREEFORM-блоку бажано знати:

```text
у якому документі він лежить;
до якого node/gate/rule прив’язаний;
чи є він normative, example або note;
чи дозволено моделі приймати рішення на його основі;
чи є для нього coverage.
```

Наприклад:

```yaml
freeform_doc_binding:
  freeform_id: "FF_EDGE_CASES"
  document: "04_HISTORY_EVENT_DOMAIN_PACK.md"
  section: "Edge cases"
  binding:
    node: "select_path"
    role: "controlled_explanation"
  decision_allowed: true
```

Без такого binding модель може сприйняти будь-який приклад як правило або будь-яку примітку як дозвіл на дію.

## Типові помилки

Перша помилка — вважати, що список файлів уже є runtime-ом.

Список файлів — це тільки каталог. Runtime починається тоді, коли є правила вибору, ролі, gates і trace.

Друга помилка — не визначити source of truth.

Якщо є два документи з подібним змістом, модель має знати, який з них головний.

Третя помилка — перевіряти шаблон замість фінального документа.

Шаблон може бути правильним, але згенерований artifact може містити порожні секції, незамінені placeholders або дані не з підтвердженого contract.

Четверта помилка — дозволяти моделі самій вирішувати, які документи “мабуть релевантні”.

Для простого питання це нормально. Для production playbook-а — ні. Там має бути `DOC.SELECT`.

П’ята помилка — не трасувати використані документи.

Без `DOC.TRACE` після помилки буде незрозуміло, чи проблема в правилі, чи в неправильному документі.

## Міні-вправа

Візьміть будь-який великий набір інструкцій, з яким ви працювали.

Спробуйте відповісти на питання:

```text
1. Які документи входять у пакет?
2. Який документ є source of truth?
3. Які документи є лише прикладами?
4. Які документи є шаблонами?
5. Які документи є rendered artifacts?
6. Для якого кроку потрібен який документ?
7. Які документи не можна використовувати для прийняття рішень?
8. Як перевірити, що фінальний документ відповідає шаблону і contract?
9. Як у trace побачити, які документи були використані?
```

Якщо на ці питання немає чіткої відповіді, у вас ще немає Documentation Runtime. У вас є просто папка з документами.

## Короткий підсумок

Documentation Runtime — це шар Ordo, який керує роботою з великим набором документів.

Він визначає:

```text
- які документи існують;
- яку роль має кожен документ;
- який документ є source of truth;
- які документи потрібні для конкретного node;
- які документи заборонені або застарілі;
- як перевіряти rendered artifacts;
- як трасувати використання документації;
- як пов’язувати документи з libraries, FREEFORM і improvement records.
```

Головна ідея проста:

```text
великий playbook має бути не просто прочитаним,
а виконаним через керований documentation runtime.
```

Без Documentation Runtime модель працює з документацією як із великою купою тексту.

З Documentation Runtime документація стає частиною виконуваної Ordo-програми.


---
