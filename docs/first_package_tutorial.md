# First Package Tutorial: створюємо перший Ordo-пакет з нуля

Цей tutorial показує мінімальний практичний шлях від порожньої папки до перевіреного Ordo-пакета.

Мета: створити пакет, який можна:

- перевірити через `ordo lint`;
- скомпілювати в Semantic JSON IR через `ordo compile`;
- перевірити тестами через `ordo test`;
- оцінити coverage через `ordo coverage`;
- прогнати через мінімальний runtime через `ordo run`;
- пройти як guided intake через `ordo intake`;
- запакувати через `ordo package`.

> Важливо: `ordo-cli v0.1.0` ще не є AI-runtime. Це перший toolchain для структурування, перевірки, компіляції та мінімального runtime-рівня Ordo-пакета.

---

## 1. Передумови

Потрібен Python 3.10+.

Перейдіть у папку `cli` і встановіть CLI у editable-режимі:

```bash
cd cli
python -m pip install -e .
ordo --version
```

Очікувано:

```text
ordo-cli 0.1.0
```

Якщо ви не встановлюєте пакет, команди можна запускати так:

```bash
python -m ordo.cli --version
```

---

## 2. Створюємо новий пакет

З кореня workspace:

```bash
cd cli
ordo init ../packages/my_first_package
```

Або без встановлення:

```bash
cd cli
python -m ordo.cli init ../packages/my_first_package
```

Після цього зʼявиться структура:

```text
packages/my_first_package/
  README.md
  ordo.yml
  source/
    program.ordo.yaml
  tests/
    test_cases.yaml
  run_inputs/
    answers_success.yaml
    intake_success.yaml
  compiled/
  reports/
  runtime/
```

Головний файл пакета:

```text
packages/my_first_package/source/program.ordo.yaml
```

---

## 3. Мінімальна структура Ordo Source

Відкрийте `source/program.ordo.yaml`.

Мінімальна Ordo-програма має містити:

```text
ordo
intent
contract
state
nodes
gates
assertions
outputs
freeform
```

Для Ordo v0.12 особливо важливі поля:

```yaml
ordo:
  version: "0.12"
  package: my.first_package
  control_level: standard
  execution_mode: chat_internal
```

### Обовʼязково для gates

Кожен gate має мати `method` і `trust_class`:

```yaml
gates:
  - id: G_GOAL_PRESENT
    method: mechanical
    trust_class: deterministic
    condition: state.package_goal is not null
    on_fail: block
```

Gate без `method` — це помилка компіляції / лінтингу.

### Обовʼязково для assertions

Заборони описуються через `ASSERTION`:

```yaml
assertions:
  - id: A_NO_FINAL_WITHOUT_APPROVAL
    polarity: not
    condition: final_package_created_without_approval
    phase: [runtime, test]
    severity: block
    on_fail: STOP
```

CLI надалі може трактувати це як runtime-заборону і test expectation.

### Обовʼязково для nodes

Кожен node має мати контрольований fallback для незбігу відповіді:

```yaml
on_unmatched_input:
  action: CLARIFY.REQUEST
  strategy: rephrase_and_narrow
  max_attempts: 2
  on_exhausted:
    action: escalate_to_human
    reason: user input does not match this node
```

Це захищає guided intake від неконтрольованої імпровізації.

---

## 4. Перевіряємо пакет через lint

```bash
ordo lint ../packages/my_first_package
```

`lint` перевіряє базові правила Ordo v0.12:

- `ordo.version` дорівнює `0.12`;
- є `control_level`;
- є `execution_mode`;
- кожен gate має `method`;
- кожен gate має `trust_class`;
- кожен assertion має `polarity`, `phase`, `severity`;
- кожен node має `on_unmatched_input` або явний fallback;
- кожен include має `version`;
- кожен FREEFORM має `maturity`.

Після успішної перевірки створюється:

```text
reports/lint_report.json
```

---

## 5. Компілюємо Source у Semantic JSON IR

```bash
ordo compile ../packages/my_first_package
```

Компіляція створює:

```text
compiled/program.ir.json
reports/compile_report.json
```

Що робить compiler MVP:

- читає `source/program.ordo.yaml`;
- нормалізує пакет;
- розгортає локальні ID в namespaced ID;
- створює Semantic JSON IR;
- переносить `gate.method`, `trust_class`, `ASSERTION`, `execution_mode` в IR;
- формує compile report.

Приклад IR-операції:

```json
{
  "op": "GATE.DEF",
  "id": "my.first_package.G_GOAL_PRESENT",
  "source_local_id": "G_GOAL_PRESENT",
  "method": "mechanical",
  "trust_class": "deterministic"
}
```

---

## 6. Додаємо й запускаємо tests

Тести лежать тут:

```text
tests/test_cases.yaml
```

Приклад test case:

```yaml
test_cases:
  - id: TC_GOAL_PRESENT_GATE
    fixture:
      state:
        package_goal: "Підготувати документ"
    expected:
      gates:
        - id: G_GOAL_PRESENT
          method: mechanical
          trust_class: deterministic
          status: passed
```

Запуск:

```bash
ordo test ../packages/my_first_package
```

`ordo test` у v0.1.0 є статичним test runner-ом. Він перевіряє, що expected behavior узгоджений із Source:

- expected node існує;
- expected gate існує;
- expected `method` збігається із gate у Source;
- expected `trust_class` збігається із gate у Source;
- expected assertion існує;
- assertion з test expectation має `phase: test`;
- `CLARIFY.REQUEST` відповідає `on_unmatched_input`.

Звіт:

```text
reports/test_report.json
```

---

## 7. Генеруємо coverage report

```bash
ordo coverage ../packages/my_first_package
```

Coverage report показує, які частини пакета покриті тестами:

- gates;
- assertions;
- nodes;
- gate methods;
- trust classes;
- execution modes;
- FREEFORM blocks.

Звіт:

```text
reports/coverage_report.json
```

---

## 8. Запускаємо runtime через `ordo run`

`ordo run` використовує готовий файл відповідей:

```bash
ordo run ../packages/my_first_package --answers ../packages/my_first_package/run_inputs/answers_success.yaml
```

Це не AI-виконання. Це мінімальний helper-runner, який:

- створює початковий state;
- застосовує answers до nodes;
- створює state snapshots;
- виконує mechanical gates;
- не підміняє `human` / `self_verification` gates;
- блокує output, якщо gates не пройдені;
- створює trace log.

Результати:

```text
runtime/trace_log.json
runtime/state_snapshots/
reports/run_report.json
```

---

## 9. Проходимо guided intake

Guided intake проходить nodes послідовно.

Non-interactive режим:

```bash
ordo intake ../packages/my_first_package \
  --answers ../packages/my_first_package/run_inputs/intake_success.yaml \
  --non-interactive
```

Interactive режим:

```bash
ordo intake ../packages/my_first_package
```

У guided intake runner:

- ставить питання з `NODE`;
- приймає відповіді;
- перевіряє `allowed_answers`;
- створює `CLARIFY.REQUEST` для unmatched input;
- оновлює state;
- виконує доступні gates;
- блокує output, якщо потрібні gates не пройдені.

Результати:

```text
runtime/intake_trace_log.json
reports/intake_report.json
```

---

## 10. Запаковуємо пакет

```bash
ordo package ../packages/my_first_package
```

Команда створює release-архів пакета у `dist/` або в стандартній вихідній папці, залежно від поточної реалізації CLI.

Перед handoff бажано виконати повний цикл:

```bash
ordo lint ../packages/my_first_package
ordo compile ../packages/my_first_package
ordo test ../packages/my_first_package
ordo coverage ../packages/my_first_package
ordo run ../packages/my_first_package --answers ../packages/my_first_package/run_inputs/answers_success.yaml
ordo intake ../packages/my_first_package --answers ../packages/my_first_package/run_inputs/intake_success.yaml --non-interactive
ordo package ../packages/my_first_package
```

---

## 11. Типові помилки першого пакета

### Gate без `method`

Погано:

```yaml
gates:
  - id: G_GOAL_PRESENT
    condition: state.package_goal is not null
```

Добре:

```yaml
gates:
  - id: G_GOAL_PRESENT
    method: mechanical
    trust_class: deterministic
    condition: state.package_goal is not null
```

### Немає `on_unmatched_input`

Погано:

```yaml
nodes:
  - id: N_GOAL
    question: "Яка мета?"
```

Добре:

```yaml
nodes:
  - id: N_GOAL
    question: "Яка мета?"
    on_unmatched_input:
      action: CLARIFY.REQUEST
      strategy: rephrase_and_narrow
      max_attempts: 2
      on_exhausted:
        action: escalate_to_human
```

### Human gate очікується як mechanical

Погано:

```yaml
expected:
  gates:
    - id: G_APPROVAL_CONFIRMED
      method: mechanical
```

Добре:

```yaml
expected:
  gates:
    - id: G_APPROVAL_CONFIRMED
      method: human
      trust_class: human_decision
```

### FREEFORM без maturity

Погано:

```yaml
freeform:
  - id: FF_NOTES
    content: "Додаткові пояснення"
```

Добре:

```yaml
freeform:
  - id: FF_NOTES
    role: domain_explanation
    maturity: stable
    incident_count: 0
    incident_threshold: 3
    content: "Додаткові пояснення"
```

---

## 12. Що робити далі

Після першого пакета спробуйте:

1. додати ще один node;
2. додати mechanical gate для нового state-поля;
3. додати assertion із `phase: [runtime, test]`;
4. додати test case;
5. запустити `lint → compile → test → coverage`;
6. перевірити, як зміниться `compiled/program.ir.json`.

Цей цикл і є базовим способом розробки Ordo-пакетів.
