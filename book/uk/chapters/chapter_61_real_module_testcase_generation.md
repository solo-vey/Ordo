# Розділ 61. Real Module Testcase Generation

## Навіщо потрібен цей крок

Після M60.6 стало зрозуміло: dry-run baseline добре перевіряє wiring, але не дає достатньо різноманітних даних для калібрування оцінок. Наступний корисний крок — не одразу запускати великий model benchmark, а навчити PathWalk будувати тест-кейси з реального Ordo-модуля.

Ідея M60.7 така:

```text
реальний source/program.ordo.yaml
    ↓
реальне дерево / граф рішень
    ↓
terminal paths
    ↓
testcase artifacts
    ↓
контрольований noise
```

## Що є входом

Базовий вхід:

```text
source/program.ordo.yaml
```

Це source-level робота. PathWalk може читати source YAML для генерації тест-кейсів, бо це authoring/testing layer. Але під час enforced runtime виконання модель усе одно не повинна напряму читати `compiled/*`; вона має користуватися embedded CLI.

## Які типи шуму потрібні

M60.7 має генерувати не лише ідеальні happy path сценарії. Потрібні контрольовані варіанти плутанини моделі:

| Тип | Сенс |
|---|---|
| `clean_path` | правильне проходження гілки без шуму |
| `distraction` | стороннє питання під час intake |
| `backtrack` | повернення до попереднього вузла |
| `skip_ahead` | спроба відповісти на майбутній крок зарано |
| `invalid_branch` | відповідь, яка не дозволена поточною гілкою |
| `clarification_without_submit` | уточнення без submit-відповіді |
| `correction_backtrack` | виправлення раніше поданої відповіді |

## Які артефакти має давати генератор

Початковий контракт артефактів:

```text
REAL_MODULE_TESTCASE_PLAN.json
REAL_MODULE_GRAPH_SUMMARY.json
cases/<case_id>.json
cases/<case_id>.md
RAW_TESTCASE_MATRIX.csv
SUMMARY.json
SUMMARY.md
VALIDATION_REPORT.json
```

Це спочатку generation contract, а не model benchmark contract.

## Що не треба змішувати

M60.7 не має автоматично відкривати калібрування ваг. Генерація реалістичних тест-кейсів покращує матеріал для майбутніх benchmark-ів, але не замінює:

```text
real model/transcript evidence
nonzero variance
repeatability analysis
manual failure review
calibration decision artifact
```

## Що реалізовано в M60.7.1

M60.7.1 реалізує перший вузький зріз цієї лінії: PathWalk вже може прочитати реальний `source/program.ordo.yaml` і побудувати graph summary без запуску runtime та без читання `compiled/*`.

Команда:

```bash
PYTHONPATH=cli:. python3 -m utilities.ordo_pathwalk.cli real-module-graph \
  --source path/to/source/program.ordo.yaml \
  --out runs/real_module_graph \
  --force
```

Вихідні артефакти M60.7.1:

```text
REAL_MODULE_GRAPH_SUMMARY.json
REAL_MODULE_GRAPH_SUMMARY.md
VALIDATION_REPORT.json
```

Graph summary фіксує nodes, edges, branching nodes, unmatched handlers, gates, outputs, terminal/gate targets і unresolved targets. Це ще не генерація тест-кейсів: `testcase_generation_ready` навмисно лишається `false`, щоб не змішувати loader/summary з наступними етапами.


## Що реалізовано в M60.7.2

M60.7.2 додає наступний вузький зріз: terminal path enumeration. PathWalk бере вже створений `REAL_MODULE_GRAPH_SUMMARY.json` і будує перелік terminal paths.

Команда:

```bash
PYTHONPATH=cli:. python3 -m utilities.ordo_pathwalk.cli real-module-paths \
  --summary runs/real_module_graph/REAL_MODULE_GRAPH_SUMMARY.json \
  --out runs/real_module_paths \
  --force
```

Вихідні артефакти M60.7.2:

```text
REAL_MODULE_TERMINAL_PATHS.json
REAL_MODULE_TERMINAL_PATHS.md
VALIDATION_REPORT.json
```

Terminal paths містять branch signature, node sequence, answer sequence, terminal target, terminal type, state updates і outputs, які дозволені після terminal gate. Це вже достатня структурна база для майбутнього clean-path testcase generator, але самі test cases ще не створюються.

Тому readiness навмисно розділено:

```text
terminal_path_enumeration_ready = true/false
clean_path_case_generation_ready = true/false
noise_case_generation_ready = false
testcase_generation_ready = false
```

## Правильна послідовність

Безпечна послідовність така:

```text
M60.7.1 — source YAML loader і graph summary
M60.7.2 — terminal path enumeration ✅
M60.7.3 — clean testcase artifacts
M60.7.4 — noise testcase artifacts
M60.7.5 — fixture acceptance і packaging
```

Це дозволяє не повертатися в технічне болото transcript replay matrix, а рухатися до більш цінного рівня: реальні дерева рішень і реальні сценарії плутанини.

## Що реалізовано в M60.7.3

M60.7.3 додає перший власне testcase-artifact зріз: clean-path test cases. PathWalk бере `REAL_MODULE_TERMINAL_PATHS.json` і створює один чистий тест-кейс на кожен terminal path.

Команда:

```bash
PYTHONPATH=cli:. python3 -m utilities.ordo_pathwalk.cli real-module-clean-cases \
  --paths runs/real_module_paths/REAL_MODULE_TERMINAL_PATHS.json \
  --out runs/real_module_clean_cases \
  --force
```

Вихідні артефакти M60.7.3:

```text
cases/<case_id>.json
cases/<case_id>.md
RAW_TESTCASE_MATRIX.csv
SUMMARY.json
SUMMARY.md
VALIDATION_REPORT.json
```

Clean-path case описує найкоротшу правильну послідовність відповідей для конкретного terminal path:

```text
path_id
branch_signature
answer_steps
expected_terminal
expected_outputs
expected_state_updates
```

Це ще не runtime execution і не noise generation. Тому readiness лишається розділеним:

```text
clean_path_cases_ready = true/false
runtime_execution_ready = false
noise_case_generation_ready = false
```

M60.7.3 важливий тим, що вперше перетворює реальний Ordo source graph на матеріальні testcase artifacts, але не повертається до transcript-replay benchmark orchestration.

## Оновлена послідовність після M60.7.3

```text
M60.7.1 — source YAML loader і graph summary ✅
M60.7.2 — terminal path enumeration ✅
M60.7.3 — clean testcase artifacts ✅
M60.7.4 — noise testcase artifacts
M60.7.5 — fixture acceptance і packaging
```


## Що реалізовано в M60.7.4

M60.7.4 додає перші noise testcase artifacts, але все ще не запускає runtime і не відкриває benchmark/scoring/calibration гілку.

Перші підтримані noise patterns:

| Pattern | Сенс |
|---|---|
| `distraction` | користувач вставляє стороннє питання перед валідною відповіддю |
| `invalid_branch` | користувач дає недозволену відповідь для поточного вузла, після чого сценарій має продовжитись валідною відповіддю |

Команда:

```bash
PYTHONPATH=cli:. python3 -m utilities.ordo_pathwalk.cli real-module-noise-cases \
  --paths runs/real_module_paths/REAL_MODULE_TERMINAL_PATHS.json \
  --out runs/real_module_noise_cases \
  --pattern distraction \
  --pattern invalid_branch \
  --force
```

Вихідні артефакти M60.7.4:

```text
cases/<case_id>.json
cases/<case_id>.md
RAW_NOISE_TESTCASE_MATRIX.csv
SUMMARY.json
SUMMARY.md
VALIDATION_REPORT.json
```

Важлива межа: `runtime_execution_ready`, `scoring_ready` і `calibration_ready` залишаються `false`. M60.7.4 генерує тільки source-level testcase artifacts. Це зроблено навмисно, щоб не повернутися в технічну гілку runtime-harness/watchdog, яку ми зафіксували як blocked у M60.6.5 / M60.6.4.1.


## Що реалізовано в M60.7.5

M60.7.5 розширює artifact-only noise testcase generation до контрольованого набору з чотирьох patterns:

```text
distraction
invalid_branch
clarification_without_submit
skip_ahead
```

Це свідомо обмежений slice. Ми не продовжуємо нескінченне додавання малих variants у цій гілці. Складніші conversational recovery patterns, наприклад `backtrack` і `correction_backtrack`, зафіксовані як future improvements і не блокують поточний milestone.

Важлива межа лишається незмінною: runtime execution, scoring, calibration і benchmark orchestration не відкриваються в M60.7.5.


## M60.7 line closure

M60.7 закривається на стабільній межі M60.7.5. Це означає, що поточна корисна artifact-only лінія вже є завершеною:

```text
source/program.ordo.yaml
    ↓
REAL_MODULE_GRAPH_SUMMARY
    ↓
REAL_MODULE_TERMINAL_PATHS
    ↓
clean-path testcase artifacts
    ↓
bounded noise testcase artifacts
```

Поточний підтриманий набір noise patterns:

```text
distraction
invalid_branch
clarification_without_submit
skip_ahead
```

Складніші conversational recovery patterns — `backtrack` і `correction_backtrack` — не додаються в цій лінії автоматично. Вони зафіксовані як future improvements, щоб не перетворювати M60.7 на нескінченний блок дрібних покращень.

Runtime execution, scoring і benchmark orchestration також лишаються окремими майбутніми milestones.
