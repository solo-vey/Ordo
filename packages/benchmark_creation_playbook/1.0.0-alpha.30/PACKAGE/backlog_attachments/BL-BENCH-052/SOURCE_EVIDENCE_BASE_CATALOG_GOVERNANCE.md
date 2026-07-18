# ORDO — Структура і правила ведення каталогу доказової бази

Версія: 1.0  
Статус: нормативний transfer-документ

## 1. Призначення доказової бази

Доказова база зберігає:

- definitions benchmark;
- task classes і test cases;
- реалізації playbook різних representation types;
- зовнішні RUN results;
- оцінки;
- RCA;
- validation methodology;
- compilation rules;
- manifests і checksums;
- історію виправлень;
- поточну порівняльну таблицю.

Її мета — забезпечити відтворюваність, порівнюваність і неможливість підміни результатів.

---

# 2. Базова структура

```text
ORDO_EMPIRICAL_EVIDENCE_BASE_<version>/
├── PLAYBOOK_REPRESENTATION_TYPES.md
├── EVALUATION_METHODOLOGY.md
├── EVALUATION_METHODOLOGY_CASE_TEMPLATE.md
├── EVALUATION_METHODOLOGY_MANIFEST.json
├── GOVERNANCE/
│   ├── PLAYBOOK_COMPILATION_RULES.md
│   ├── EVIDENCE_BASE_CATALOG_GOVERNANCE.md
│   └── PACKAGE_VALIDATION_METHODOLOGY.md
├── 01_task_classes/
│   └── <TASK_CLASS_ID>/
│       └── <CASE_ID>/
│           ├── EVALUATION_METHODOLOGY_CASE.md
│           ├── 01_case_definition/
│           ├── 02_implementations/
│           ├── 03_launch_prompts/
│           ├── 04_runs/
│           ├── 05_analysis/
│           ├── 06_manifests/
│           └── README.md
└── manifests/
```

Існуючі каталоги можна не перейменовувати ретроспективно, але нові кейси бажано вести за цією схемою.

---

# 3. Кореневі нормативні файли

## `PLAYBOOK_REPRESENTATION_TYPES.md`

Містить визначення:

- YAML;
- Structured Instructions;
- Mixed Accumulated Instructions;
- Domain Adapted All-in-One.

Оновлюється, коли змінюються правила representation type.

## `EVALUATION_METHODOLOGY.md`

Єдині правила оцінювання:

- Process;
- Documents;
- Final;
- score caps;
- terminal-route interpretation;
- правила N/A.

Не змінювати заднім числом без version bump і migration note.

## `EVALUATION_METHODOLOGY_CASE_TEMPLATE.md`

Шаблон case-specific evaluation policy.

## `EVALUATION_METHODOLOGY_MANIFEST.json`

Версії й checksums нормативних evaluation-файлів.

## `GOVERNANCE/`

Містить process-level правила, які застосовуються до всіх case/package.

---

# 4. Рівень task class

Шлях:

```text
01_task_classes/<TASK_CLASS_ID>/
```

Task class об’єднує кейси з однаковим типом ризику або процесної складності.

README task class має описувати:

- class intent;
- shared risk profile;
- case inclusion criteria;
- expected route patterns;
- shared evaluation constraints.

---

# 5. Рівень test case

Шлях:

```text
01_task_classes/<TASK_CLASS_ID>/<CASE_ID>/
```

Обов’язковий `README.md` повинен містити:

- case ID і назву;
- бізнес-проблему;
- benchmark intent;
- source of truth;
- перелік representation types;
- перелік RUN;
- статус кожного варіанта;
- посилання на scorecard;
- known limitations;
- останній update.

---

# 6. `01_case_definition/`

Зберігає immutable або versioned definition кейсу:

- case passport;
- authoritative fixtures;
- RUN definitions;
- expected route class;
- evaluator-only ground truth;
- source/input constraints;
- benchmark boundaries;
- case-level manifests.

Evaluator-only файли мають бути чітко позначені й не потрапляти у model-visible package.

Не змінювати fixture після RUN без нової case version.

---

# 7. `02_implementations/`

Структура:

```text
02_implementations/
├── yaml/
├── structured_instructions/
├── mixed_accumulated_instructions/
└── domain_adapted_all_in_one/
```

У кожному representation-каталозі зберігати:

- release ZIP;
- SHA-256 ZIP;
- extracted release candidate, якщо потрібно;
- compilation rules;
- package validation methodology;
- green-light report;
- release manifest;
- status note;
- deprecation note;
- previous versions, якщо потрібна історія.

Рекомендована versioned структура:

```text
<representation>/
├── releases/
│   └── <version>/
├── compiler/
├── validation/
├── deprecated/
└── STATUS.md
```

## Правило релізу

Implementation не вважається ready, доки:

- release validator PASS;
- clean extraction PASS;
- exact launch prompt preflight PASS;
- semantic parity PASS;
- green-light evidence збережено.

---

# 8. `03_launch_prompts/`

Зберігає exact prompt, який отримувала зовнішня модель.

Структура:

```text
03_launch_prompts/
└── <representation>/
    └── <version>/
        ├── RUN_01.md
        ├── RUN_02.md
        ├── ...
        ├── PROMPTS.zip
        └── PROMPTS.zip.sha256
```

Launch prompt і package є version-locked pair.

Не можна:

- тестувати package одним prompt, а зберігати інший;
- перезаписувати prompt після RUN;
- використовувати prompt старої версії без explicit compatibility record.

---

# 9. `04_runs/`

Зберігає лише фактичні зовнішні результати.

Структура:

```text
04_runs/
└── <representation>/
    └── <version>/
        └── RUN_XX/
            ├── ORIGINAL_RETURNED_PACKAGE.zip
            ├── ORIGINAL_RETURNED_PACKAGE.zip.sha256
            ├── INTEGRITY_REPORT.md
            ├── EXTRACTION_MANIFEST.json
            └── STATUS.md
```

## Незмінність

Оригінальний повернений ZIP не редагувати.

Якщо треба виправити:

- не змінювати RUN package;
- створити новий RUN або нову package version;
- analysis може пояснювати дефект, але не переписувати evidence.

## Що фіксувати

- filename;
- отриману дату;
- SHA-256;
- ZIP integrity;
- internal checksum status;
- terminal route;
- artifact presence;
- approval/receipt presence;
- package assembly defects;
- evaluator restrictions.

---

# 10. `05_analysis/`

Структура:

```text
05_analysis/
├── <representation>/
│   ├── <version>/
│   │   ├── RUN_01_ANALYSIS.md
│   │   ├── RUN_02_ANALYSIS.md
│   │   ├── AGGREGATE_ANALYSIS.md
│   │   └── RCA/
└── CURRENT_COMPARATIVE_SCORECARD.md
```

## RUN analysis

Повинен містити:

- scope;
- integrity findings;
- Process score;
- Passport score;
- Jira score;
- Manual QA score;
- Automation score;
- Documents score;
- Final score;
- score-cap application;
- terminal-route interpretation;
- strong points;
- defects;
- whether defect belongs to process, model, validator, compiler or package assembly.

## Aggregate analysis

Містить:

- результати RUN_01–RUN_05;
- mean;
- pattern analysis;
- representation-level conclusion;
- comparison with other variants;
- known defects.

## RCA

Створюється, коли:

- результат неочікувано низький;
- local validation PASS, а external preflight FAIL;
- validator дав false PASS/false FAIL;
- documents materially differ from YAML semantics;
- terminal route unexpected.

RCA не змінює score автоматично; score змінюється лише за рішенням evaluation process.

---

# 11. `CURRENT_COMPARATIVE_SCORECARD.md`

Є current view, а не єдиний source of truth.

Має містити:

- representation;
- exact version;
- RUN_01–RUN_05 Final;
- average;
- completion status;
- important footnote.

Не змішувати результати різних версій під одним рядком.

Якщо результати version видалено за рішенням користувача:

- прибрати рядок;
- прибрати aggregate analysis;
- прибрати/архівувати corresponding run results згідно з рішенням;
- зафіксувати removal note.

---

# 12. `06_manifests/`

Зберігає:

- case evidence manifest;
- file inventory;
- SHA-256 inventory;
- version map;
- source-to-artifact map;
- package-to-prompt pairing;
- run-to-analysis pairing;
- deprecation/removal ledger.

Рекомендований `CASE_EVIDENCE_MANIFEST.json`:

```json
{
  "case_id": "...",
  "case_version": "...",
  "representations": [
    {
      "type": "structured_instructions",
      "version": "alpha_1_3_0",
      "package": "...",
      "package_sha256": "...",
      "launch_prompts": "...",
      "runs": {
        "RUN_01": {
          "evidence": "...",
          "sha256": "...",
          "analysis": "...",
          "final_score": 95
        }
      }
    }
  ]
}
```

---

# 13. Naming conventions

Використовувати стабільні IDs:

- `TCxx_...`;
- `EXxx_...`;
- `RUN_01` ... `RUN_05`;
- representation slug;
- exact semantic version.

Не використовувати `final`, `latest`, `new2` як єдині version identifiers.

Допустимо мати зручний current alias, але canonical artifact має exact version.

---

# 14. Checksum rules

- кожен release ZIP має зовнішній `.sha256`;
- кожен returned RUN ZIP має зовнішній `.sha256`;
- internal `SHA256SUMS.txt` не повинен рекурсивно хешувати сам себе;
- checksums генеруються після фінального складання;
- після будь-якої зміни checksums перегенеровуються;
- checksum mismatch фіксується як evidence defect, а не мовчки виправляється.

---

# 15. Validation methodology lifecycle

`PACKAGE_VALIDATION_METHODOLOGY.md` — накопичуваний нормативний файл.

Після кожного нового external blocker або false-positive:

1. описати defect;
2. додати release-blocking check;
3. додати positive/negative fixture;
4. оновити validator;
5. перевірити пакет у clean extraction;
6. зафіксувати зміну у release notes.

Особливо обов’язкові:

- exact-path checks;
- exact launch-prompt commands;
- External Model Preflight Simulation;
- first-generation-gate sufficiency;
- Driver validator execution;
- receipt authenticity;
- stdout/stderr/return code capture;
- package reference resolution;
- checksum self-reference check.

---

# 16. Порядок додавання нової implementation version

1. Створити versioned implementation directory.
2. Додати/оновити compilation rules.
3. Побудувати package.
4. Запустити до п’яти validation/fix cycles.
5. Зберегти cycle log.
6. На green light:
   - release ZIP;
   - external SHA;
   - manifest;
   - green-light report;
   - exact launch prompts.
7. Додати representation/version у case README і manifest.
8. Лише після цього запускати RUN.

Стара version не видаляється автоматично. Вона позначається:

- active;
- superseded;
- deprecated;
- on hold;
- invalidated.

---

# 17. Порядок додавання RUN result

1. Зберегти оригінальний ZIP без змін.
2. Обчислити external SHA.
3. Перевірити ZIP integrity.
4. Перевірити internal checksums.
5. Зафіксувати terminal route.
6. Провести evaluation за case methodology.
7. Створити RUN analysis.
8. Оновити aggregate analysis.
9. Оновити scorecard.
10. Оновити case evidence manifest.

Не переносити score з іншої version.

---

# 18. Видалення або виключення результатів

Коли користувач просить прибрати results:

- чітко визначити, чи видаляються:
  - scores;
  - analysis;
  - runs;
  - implementation;
  - усі згадки;
- створити `REMOVAL_NOTE.md`;
- оновити scorecard;
- оновити manifest;
- не залишати dangling links;
- якщо implementation треба лишити, явно зазначити: package retained, results removed.

---

# 19. Evidence bundle для передачі

Періодично створюється transfer ZIP.

Він повинен містити:

- README;
- root governance;
- case definitions;
- active implementation packages;
- launch prompts;
- original RUN evidence;
- analyses;
- scorecards;
- manifests;
- checksums;
- open issues;
- on-hold work;
- deprecation/removal notes.

Перед видачею transfer ZIP:

- перевірити file inventory;
- перевірити checksums;
- перевірити, що всі заявлені файли реально включені;
- перевірити відсутність stale links;
- перевірити, що current scorecard відповідає included analyses.

---

# 20. Межі model-visible / evaluator-only

У package і evidence base треба чітко розрізняти:

- model-visible analyst instructions;
- runtime inputs;
- Driver-visible contracts;
- evaluator-only ground truth;
- compiler/provenance metadata;
- historical benchmark results.

Зовнішня execution model не повинна бачити:

- evaluator-only expected outputs;
- scores попередніх RUN;
- hidden YAML provenance для Mixed Accumulated;
- generation methodology, якщо формат вимагає origin hiding;
- answer keys.

---

# 21. Поточний status tracking

У кожному representation каталозі бажано мати `STATUS.md`:

```text
Representation:
Current active version:
Status:
Green light:
External RUNs:
Known defects:
On hold:
Superseded versions:
Next action:
```

У case README — зведений status.

---

# 22. Мінімальні acceptance criteria для доказової бази

Доказова база придатна до передачі, якщо:

- структура зрозуміла без контексту чату;
- є README;
- нормативні правила включені;
- active versions однозначні;
- package/prompt pairs однозначні;
- original evidence не змінено;
- усі scores мають analysis;
- scorecard не містить orphan rows;
- checksums валідні;
- manifests відповідають filesystem;
- on-hold і removed work зафіксовано;
- немає тверджень про файли, яких немає в архіві.
