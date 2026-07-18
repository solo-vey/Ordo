# Процес ведення benchmark evidence package, валідації запусків і фіксації Playbook

## 1. Призначення документа

Цей документ описує повний робочий процес ведення доказового пакета для benchmark-тестування різних способів подання одного й того самого процесу моделі.

Документ призначений для перенесення правил у Playbook, який керує:

- структурою benchmark evidence base;
- збереженням тестових класів і test case;
- збереженням підтверджених версій Playbook;
- прийманням та аудитом результатів запусків;
- оцінюванням якості проходження процесу;
- оцінюванням створених документів;
- формуванням загальної оцінки;
- веденням порівняльної таблиці;
- відокремленням робочих, історичних, невалідних та підтверджених доказів.

Головний принцип:

> До canonical evidence package потрапляє лише те, що було окремо перевірено і явно підтверджено користувачем.

Автоматичне створення, наявність файлу або успішне завершення validator не означає автоматичного включення результату до доказової бази.

---

## 2. Загальна структура benchmark evidence base

На верхньому рівні benchmark evidence base має таку логічну структуру:

```text
benchmark_evidence_base/
├── governance/
├── task_classes/
├── manifests/
└── comparative_analysis/
```

Основна ієрархія тестів:

```text
task class
  → test case
    → Playbook variant
      → approved Playbook package
      → launch prompts
      → confirmed run results
      → audits
```

### 2.1. Перший рівень — клас задач

Клас задач групує test case за характером процесу.

Приклади:

```text
TC01_COMPLEX_MULTI_STEP_PROCESS
TC02_INTERRELATED_ARTIFACT_SET
TC03_RECURRING_REGULATED_HIGH_COST_OMISSION
```

Кожен клас задач може містити декілька окремих test case.

### 2.2. Другий рівень — конкретний test case

Кожен test case має власний каталог.

Приклад:

```text
TC03_RECURRING_REGULATED_HIGH_COST_OMISSION/
└── EX02_DATABASE_CHANGE_DOCUMENT_CRITICAL_ARTIFACT_SET/
```

У каталозі test case зберігається вся інформація, необхідна для незалежного відтворення тесту:

```text
01_problem_inputs/
02_implementations/
03_test_cases/
04_runs/
05_comparative_analysis/
README.md
```

### 2.3. Третій рівень — тип реалізації Playbook

У поточному benchmark використовуються чотири варіанти:

```text
yaml_playbook/
structured_instructions/
mixed_accumulated_instructions/
domain_adapted_all_in_one/
```

Їхній зміст:

1. `yaml_playbook`  
   Формальний YAML Playbook із явними кроками, переходами, gates, contracts і validators.

2. `structured_instructions`  
   Структуровані покрокові інструкції, створені на основі процесу.

3. `mixed_accumulated_instructions`  
   Накопичені інструкції без повністю детермінованої покрокової моделі.

4. `domain_adapted_all_in_one`  
   Варіант, у якому файл «все в одному» від аналітика адаптовано шляхом зміни доменної моделі.

---

## 3. Структура конкретного test case

Рекомендована canonical структура:

```text
<TEST_CASE>/
├── 01_problem_inputs/
│   ├── source_materials/
│   ├── parameters/
│   ├── templates/
│   ├── document_quality_criteria/
│   ├── validation_rules/
│   └── reference_examples/
│
├── 02_implementations/
│   ├── yaml_playbook/
│   │   ├── approved_packages/
│   │   ├── launch_prompts/
│   │   ├── version_history/
│   │   └── APPROVED_BASELINE.md
│   ├── structured_instructions/
│   │   ├── approved_packages/
│   │   ├── launch_prompts/
│   │   ├── version_history/
│   │   └── APPROVED_BASELINE.md
│   ├── mixed_accumulated_instructions/
│   │   ├── approved_packages/
│   │   ├── launch_prompts/
│   │   ├── version_history/
│   │   └── APPROVED_BASELINE.md
│   └── domain_adapted_all_in_one/
│       ├── approved_packages/
│       ├── launch_prompts/
│       ├── version_history/
│       └── APPROVED_BASELINE.md
│
├── 03_test_cases/
│   ├── SCENARIO_CATALOG.md
│   ├── SCORING_CONTRACT.md
│   ├── RUN_01_INPUT/
│   ├── RUN_02_INPUT/
│   ├── RUN_03_INPUT/
│   ├── RUN_04_INPUT/
│   └── RUN_05_INPUT/
│
├── 04_runs/
│   ├── yaml_playbook/
│   │   ├── confirmed_runs/
│   │   ├── rejected_runs/
│   │   └── audits/
│   ├── structured_instructions/
│   │   ├── confirmed_runs/
│   │   ├── rejected_runs/
│   │   └── audits/
│   ├── mixed_accumulated_instructions/
│   │   ├── confirmed_runs/
│   │   ├── rejected_runs/
│   │   └── audits/
│   └── domain_adapted_all_in_one/
│       ├── confirmed_runs/
│       ├── rejected_runs/
│       └── audits/
│
├── 05_comparative_analysis/
│   ├── CURRENT_COMPARATIVE_SCOREBOARD.md
│   ├── SCORE_LEDGER.json
│   ├── audit_reports/
│   └── conclusions/
│
├── FILE_MANIFEST_SHA256.json
├── SHA256SUMS.txt
└── README.md
```

---

## 4. Що має лежати у вхідних даних test case

Каталог `01_problem_inputs/` є джерелом істини для тесту.

Він повинен містити:

- опис задачі;
- вхідні документи;
- усі початкові параметри;
- test-specific значення;
- очікувані сценарії;
- шаблони документів;
- критерії якості документів;
- правила оцінювання;
- правила блокування;
- правила closure evidence;
- reference examples;
- пояснення очікуваних terminal states;
- обмеження щодо відсутніх authoritative inputs;
- правила заборони вигадування даних.

Не можна покладатися лише на знання, що залишилися у чаті. Усе, без чого зовнішня модель не зможе повторити benchmark, має бути фізично збережено в каталозі test case.

---

## 5. Правила збереження Playbook-версій

### 5.1. Playbook не стає canonical автоматично

Нова версія Playbook може бути:

- робочою;
- тестовою;
- candidate;
- rejected;
- approved.

До `approved_packages/` вона переноситься лише після явної команди користувача.

Приклад підтвердження:

> Підтверджуємо цю версію Playbook. Занеси її в каталог.

Лише після цього модель:

1. копіює ZIP Playbook у `approved_packages/`;
2. копіює нейтральний стартовий промпт у `launch_prompts/`;
3. оновлює `APPROVED_BASELINE.md`;
4. фіксує версію, SHA-256, дату та статус;
5. за потреби переносить попередню canonical версію до `version_history/`;
6. оновлює manifest і checksums.

### 5.2. Після п’ятого запуску

Після завершення RUN_01–RUN_05 для одного типу Playbook діє таке правило:

- якщо користувач уже сказав, що версію Playbook треба зафіксувати, вона переноситься до `approved_packages/`;
- якщо користувач цього не сказав, модель повинна окремо запитати:

> Чи підтверджуємо цю версію Playbook як canonical для цього типу?

Без позитивної відповіді Playbook не фіксується як approved.

### 5.3. Нейтральність стартового промпта

Стартовий промпт не повинен містити:

- опису того, що було покращено в новій версії;
- переліку нових validation gates;
- підказок, на які дефекти звертати увагу;
- пояснення, що саме перевіряється цим benchmark;
- натяків на очікуваний terminal state.

Причина: це створює чітинг і змінює поведінку моделі.

Стартовий промпт має лише:

- вказати пакет;
- описати загальну процедуру запуску;
- надати test input;
- вимагати виконати Playbook;
- вимагати повернути фактичний result package або terminal report.

Специфічні правила повинні міститися всередині Playbook, а не в launch prompt.

---

## 6. Процес приймання одного запуску

Користувач передає результати запусків по одному.

Приклад:

```text
RUN_01
RUN_02
RUN_03
RUN_04
RUN_05
```

Для кожного запуску використовується одна й та сама процедура.

### 6.1. Початковий статус

Після отримання файлу запуск має статус:

```text
RECEIVED_NOT_CONFIRMED
```

Його не можна одразу переносити до canonical evidence package.

### 6.2. Розпакування

Якщо результат надано у ZIP:

1. обчислити SHA-256 зовнішнього ZIP;
2. перевірити, що ZIP відкривається;
3. розпакувати в окремий audit workspace;
4. зберегти список файлів;
5. перевірити внутрішні manifests і checksums;
6. знайти execution report;
7. знайти state ledger;
8. знайти generated documents;
9. знайти validation reports;
10. знайти approval, invalidation і regeneration evidence.

Оцінювати запуск лише за execution summary заборонено.

Потрібно аналізувати фактичний вміст результату.

### 6.3. Результат без ZIP

Для деяких terminal states ZIP може бути відсутній коректно.

Наприклад:

- `T_SCENARIO_EXHAUSTED`;
- `T_INPUT_BLOCKED`;
- hard stop;
- rollback/no-change.

У такому разі оцінюється terminal report.

Відсутність ZIP не є дефектом, якщо:

- terminal state відповідає сценарію;
- canonical документи не повинні були створюватися;
- модель не вигадала відсутні дані;
- є достатня evidence зупинки.

---

## 7. Три обов’язкові оцінки

Кожен запуск завжди отримує три числа:

```text
Process Quality / Document Quality / Final Quality
```

Українською:

1. якість проходження шляху;
2. якість створених документів;
3. загальна якість запуску.

### 7.1. Якість проходження шляху

Оцінюється за фактичною evidence:

- правильність маршруту;
- повнота виконаних кроків;
- відповідність terminal state;
- правильність переходів;
- виконання gates;
- робота approvals;
- робота invalidation;
- regeneration після виправлень;
- backtracking;
- rollback;
- збереження provenance;
- checksum integrity;
- заборона вигадування відсутніх inputs;
- коректне блокування;
- узгодженість state ledger і execution report;
- виявлення фактичних дефектів документів.

Важливо:

> Формальні 126/126 і PASS усіх validators не гарантують 100 за процес.

Якщо процес пропустив реальний дефект документа, процесна оцінка знижується, бо gates не виконали свою функцію.

### 7.2. Якість документів

Canonical документи:

1. Passport;
2. Jira;
3. Manual QA;
4. Automation.

Кожен документ має однакову вагу.

Формула:

```text
Document Quality =
(Passport + Jira + Manual QA + Automation) / 4
```

Implementation Prompt можна коментувати окремо, але він не входить у canonical document score.

### 7.3. Загальна якість

Формула:

```text
Final Quality =
(Process Quality + Document Quality) / 2
```

Використовується звичайне округлення до цілого.

Приклад:

```text
Process = 90
Documents = 81

Final = (90 + 81) / 2
      = 85.5
      = 86
```

---

## 8. Основні правила оцінювання документів

## 8.1. Passport

Passport не повинен дублювати повний Manual QA runbook.

Він повинен містити:

- функціональні сценарії;
- concrete atomic unit/provider tests;
- stable mapping;
- TC→MQA→AUTO traceability;
- status кожного сценарію;
- blockers;
- closure evidence;
- mapping rationale;
- authoritative references.

Розриви, які вважаються дефектами:

- generic UNIT entries;
- ID-only mapping без пояснення;
- blocked status без exact blocker;
- blocked status без closure evidence;
- статуси не збігаються між документами;
- scenario coverage не простежується.

Коректно blocked scenario не знижує оцінку, якщо:

- інформація дійсно відсутня;
- її не можна безпечно вивести;
- status стабільний;
- exact blocker зафіксований;
- closure evidence описане;
- усі документи узгоджені;
- модель нічого не вигадала.

## 8.2. Jira

Jira не зобов’язана дублювати unit tests.

Але кожен delivery item повинен самостійно описувати:

- target component або domain object;
- implementation action;
- конкретний implementation output;
- створюваний або заборонений side effect;
- measurable behavior;
- acceptance criteria;
- closure criteria;
- evidence-based Definition of Done.

Посилання на Passport, TC, Manual QA або Automation є додатковими.

Вони не можуть заміняти самостійний зміст delivery item.

Дефект:

```text
DEL-001: Implement according to Passport TC-001.
```

Прийнятний варіант:

```text
DEL-001: Implement processing-state change handling for
item.processingState, persisting exactly one change record and emitting
one processing-state-changed event while creating zero error records.
```

## 8.3. Manual QA

Manual QA має бути case-local і реально виконуваним.

Він повинен містити:

- конкретні команди;
- literal inputs;
- точні payload;
- executable assertions;
- expected exact values;
- cleanup;
- rollback;
- post-rollback verification;
- fail-closed поведінку.

Ключове правило:

> Команда, яка лише друкує count або value, не є assertion.

Неприйнятно:

```bash
mongosh ... countDocuments(...)
# assert count == 0
```

Прийнятно:

```bash
mongosh ... --eval '
const n = db.changes.countDocuments({...});
if (n !== 0) quit(1);
'
```

Zero-count і rollback assertions повинні завершуватися nonzero exit при mismatch.

Manual QA без complete case-local executable commands/assertions має максимальну оцінку 50.

## 8.4. Automation

Automation повинна мати:

- per-test runner structure;
- exact Passport↔Manual↔Automation correspondence;
- authoritative fixture reference;
- complete publish payload;
- complete process payload;
- case-local executable assertions;
- lifecycle checks;
- rollback semantics;
- exact cardinality;
- zero-side-effect checks.

Для duplicate/idempotency:

```text
publish_1
→ process_1
→ assertions_1
→ publish_2
→ process_2
→ assertions_2
```

Обидва cycles повинні використовувати:

- той самий authoritative business payload;
- ту саму dedup identity;
- той самий changeId, якщо це dedup key;
- той самий documentId;
- той самий recordKey;
- той самий fieldPath;
- ті самі oldValue і newValue;
- той самий ruleId.

Після другого циклу мають бути:

- exact final cardinality;
- explicit no-second-record assertion;
- explicit no-second-event assertion.

Automation без per-test runner structure або exact correspondence має максимальну оцінку 50.

---

## 9. Процедура представлення аудиту користувачу

Після перевірки одного запуску модель повинна показати:

```text
RUN_N — <Playbook type/version>

Process Quality: NN
Document Quality: NN
Final Quality: NN
```

Далі коротко:

- що виконано добре;
- які дефекти знайдено;
- оцінка Passport;
- оцінка Jira;
- оцінка Manual QA;
- оцінка Automation;
- формула document score;
- формула final score.

Після цього обов’язково повідомити:

> Запуск ще не занесено до evidence package. Очікую підтвердження.

---

## 10. Підтвердження або відхилення запуску

### 10.1. Підтвердження

Користувач говорить:

> Підтверджуємо цей запуск.

Тоді модель:

1. копіює original result ZIP або terminal report;
2. копіює audit report;
3. створює metadata;
4. фіксує три оцінки;
5. фіксує SHA-256;
6. переносить у:

```text
04_runs/<variant>/confirmed_runs/RUN_N/
```

7. оновлює run registry;
8. оновлює comparative scoreboard;
9. оновлює manifests і checksums;
10. відповідає:

> Я заніс RUN_N у відповідний каталог evidence package.

### 10.2. Відхилення

Якщо користувач говорить, що запуск не підтверджується:

- він не потрапляє у `confirmed_runs/`;
- за потреби переноситься до `rejected_runs/`;
- обов’язково зберігається причина відхилення;
- він не враховується в canonical comparative score.

### 10.3. Виправлений повторний запуск

Якщо той самий RUN повторено:

- попередній результат не перезаписується мовчки;
- новий результат отримує revision;
- приклад:

```text
RUN_01/revision_01/
RUN_01/revision_02/
```

Canonical revision визначається окремим підтвердженням користувача.

---

## 11. Оновлення порівняльної таблиці

Порівняльна таблиця має рядки:

```text
RUN_01
RUN_02
RUN_03
RUN_04
RUN_05
```

Колонки:

```text
YAML playbook
Structured instructions
Mixed accumulated instructions
Domain-adapted all-in-one
```

Кожна клітинка:

```text
Process / Documents / Final
```

Приклад:

```text
90 / 81 / 86
```

Якщо підтвердженого запуску немає:

```text
—
```

У таблицю не можна вносити:

- непідтверджений запуск;
- rejected run;
- noncanonical run;
- оцінку лише зі слів execution summary;
- результат, який не був розпакований і перевірений;
- старий run після оголошення його невалідним.

Після очищення старих запусків відповідні клітинки повинні бути прочерками.

---

## 12. Видалення невалідних запусків

Користувач може оголосити всю попередню серію невалідною.

Тоді модель повинна:

1. видалити її з canonical `confirmed_runs/`;
2. прибрати її з comparative scoreboard;
3. прибрати з canonical averages;
4. не використовувати її у висновках;
5. за потреби перенести до quarantine/archive;
6. не видаляти інші варіанти, яких команда не стосувалася.

Приклад:

Було оголошено невалідними попередні запуски:

- YAML playbook;
- structured instructions;
- mixed accumulated instructions.

Після цього їхні клітинки у comparative table мають бути `—`.

П’ять підтверджених `domain_adapted_all_in_one` залишаються, якщо користувач не наказав їх прибрати.

---

## 13. Робочий стан і canonical evidence package

Потрібно розрізняти:

### Working workspace

Містить:

- розпаковані ZIP;
- тимчасові аудити;
- candidate Playbook;
- непідтверджені runs;
- debug artifacts;
- проміжні scripts.

### Canonical evidence package

Містить лише:

- підтверджені inputs;
- approved Playbook packages;
- canonical neutral launch prompts;
- підтверджені runs;
- accepted audits;
- canonical score ledger;
- manifests і checksums.

Непідтверджений файл не можна переносити з working workspace до canonical evidence package.

---

## 14. Versioning evidence base

Evidence base має версію:

```text
v1.6
v1.7
v1.8
...
```

Під час синхронізації:

- попередня версія зберігається незмінною;
- створюється нова версія;
- формується sync report;
- вказується, що додано, видалено або оголошено noncanonical;
- оновлюється SHA-256 manifest.

Не можна тихо змінювати вже опублікований evidence ZIP.

---

## 15. Manifest і контроль цілісності

Canonical evidence package повинен містити:

```text
MANIFEST.json
FILE_MANIFEST_SHA256.json
SHA256SUMS.txt
SYNC_REPORT_<DATE>.md
```

Для кожного підтвердженого run metadata має містити:

```json
{
  "run_id": "RUN_01",
  "variant": "yaml_playbook",
  "playbook_version": "Alpha 1.16.4",
  "status": "confirmed",
  "process_score": 90,
  "document_score": 81,
  "final_score": 86,
  "result_sha256": "...",
  "audit_sha256": "...",
  "confirmed_by_user": true
}
```

---

## 16. Правила поведінки моделі

Модель повинна:

- перевіряти фактичні файли;
- не покладатися на execution summary;
- не переносити результат без підтвердження;
- не переносити Playbook без підтвердження;
- після RUN_05 запитати про фіксацію Playbook, якщо користувач ще не сказав;
- давати рівно три основні оцінки;
- оновлювати таблицю лише після підтвердження;
- ставити прочерки там, де canonical runs відсутні;
- не вигадувати відсутні authoritative inputs;
- коректно визнавати blocked terminal states;
- не додавати change hints у стартовий промпт;
- зберігати історію без змішування з canonical results;
- повідомляти точний каталог, куди занесено підтверджений артефакт.

Модель не повинна:

- вважати validator PASS достатнім доказом якості;
- оцінювати ZIP лише за назвою;
- автоматично підтверджувати власний результат;
- перезаписувати попередній canonical run;
- змішувати різні Playbook versions в одній серії без явного маркування;
- переносити development runs до canonical benchmark table;
- приховувати, що файл відсутній або не був перевірений.

---

## 17. Повний цикл для одного типу Playbook

```text
1. Користувач передає Playbook candidate.
2. Playbook зберігається у working workspace.
3. Користувач запускає RUN_01.
4. Модель розпаковує й аудіює RUN_01.
5. Модель показує Process / Documents / Final.
6. Користувач підтверджує або відхиляє RUN_01.
7. Підтверджений RUN_01 переноситься до evidence package.
8. Повторити для RUN_02.
9. Повторити для RUN_03.
10. Повторити для RUN_04.
11. Повторити для RUN_05.
12. Після RUN_05 перевірити, чи підтверджено Playbook.
13. Якщо ні — окремо запитати користувача.
14. Після підтвердження перенести Playbook до approved_packages.
15. Оновити comparative scoreboard.
16. Оновити manifests і SHA-256.
17. Створити нову versioned evidence base.
```

---

## 18. Критерій завершення серії

Серія для одного Playbook variant завершена лише тоді, коли:

- розглянуто всі п’ять RUN;
- кожен має явний статус confirmed або rejected;
- усі confirmed results фізично лежать у evidence package;
- усі оцінки внесено в score ledger;
- comparative table оновлена;
- Playbook version або підтверджена, або явно залишена candidate;
- neutral launch prompt збережений;
- manifest і SHA-256 оновлені;
- сформовано sync report.

---

## 19. Поточний контекст benchmark

У поточному test case є чотири варіанти.

На момент формування цього документа:

- старі runs для `yaml_playbook` оголошено невалідними;
- старі runs для `structured_instructions` оголошено невалідними;
- старі runs для `mixed_accumulated_instructions` оголошено невалідними;
- їхні canonical run sections повинні бути порожніми;
- п’ять runs `domain_adapted_all_in_one` залишаються збереженими;
- нові YAML runs передаються й аудіюються по одному;
- RUN_01 Alpha 1.16.4 вже був розглянутий, але на момент цього документа ще не підтверджений для перенесення;
- оцінка непідтвердженого RUN_01:
  - process: 90;
  - documents: 81;
  - final: 86.

Ця інформація є статусним контекстом, а не автоматичною командою включити RUN_01 до canonical evidence package.

---

## 20. Підсумковий принцип

Benchmark evidence package — це не просто каталог файлів.

Це керована система доказів, у якій кожен canonical артефакт має:

- походження;
- версію;
- SHA-256;
- audit;
- оцінку;
- статус;
- явне підтвердження користувача;
- визначене місце у структурі.

Головне правило:

> Спочатку фактичний аудит, потім оцінка, потім явне підтвердження користувача, і лише після цього — включення до canonical evidence package.
