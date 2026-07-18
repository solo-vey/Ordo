# First Ordo Package

Перший мінімальний Ordo v0.12 package.

## Runtime Mode

Use `START_PROMPT_RUNTIME_MODE.md` as the minimal prompt. It points to `START_HERE_RUNTIME_MODE.md`, which contains the full runtime loading, CLI truthfulness, fallback, gate, and artifact validation rules.

Guided execution order comes from `compiled/program.ir.json` after `ordo compile`; `source/program.ordo.yaml` remains the editable source of truth.

## Команди

```bash
ordo lint .
ordo compile .
ordo test .
ordo coverage .
ordo package .
```


## M2 — Static Test Runner

Додано команду `ordo test`, яка перевіряє `tests/test_cases.yaml` без запуску AI-моделі.

Поточний test runner перевіряє:

- чи expected `node` існує у Source;
- чи expected `gates` посилаються на реальні gates;
- чи expected `method` / `trust_class` збігаються з gate definition;
- чи expected `assertions` мають правильну `EXPECT.NOT` / `EXPECT.MUST` projection;
- чи assertion з expected test projection має `phase: test`;
- чи expected clarify behavior має `on_unmatched_input` у відповідному node.

Це ще не runtime і не модельний executor. Це M2-рівень: static behavior validation.


## M3 — Run

```bash
ordo run . --answers run_inputs/answers_success.yaml
ordo run . --answers run_inputs/answers_blocked.yaml
```

Runner створює `runtime/trace_log.json`, `runtime/state_snapshots/` і `reports/run_report.json`.


## M4 guided intake

```bash
ordo intake . --answers run_inputs/intake_success.yaml --non-interactive
```


## M59.1 Runtime CLI note

Runtime profile builds of this package include `cli_embedded/ordo`. Start Runtime Mode through the embedded CLI when available. If the embedded CLI cannot run, hard-stop; deterministic Runtime Mode is not enforced until CLI evidence exists.
