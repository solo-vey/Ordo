# First Ordo Package

The first minimal Ordo v0.12 package.

## Runtime Mode

Use `START_PROMPT_RUNTIME_MODE.md` as the minimal prompt. It points to `START_HERE_RUNTIME_MODE.md`, which contains the full runtime loading, CLI truthfulness, fallback, gate, and artifact validation rules.

Guided execution order comes from `compiled/program.ir.json` after `ordo compile`; `source/program.ordo.yaml` remains the editable source of truth.

## Commands

```bash
ordo lint .
ordo compile .
ordo test .
ordo coverage .
ordo package .
```


## M2 — Static Test Runner

The `ordo test` command validates `tests/test_cases.yaml` without running an AI model.

The current test runner verifies:

- the expected `node` exists in the Source;
- expected `gates` refer to actual gates;
- expected `method` and `trust_class` match the gate definition;
- expected `assertions` have the correct `EXPECT.NOT` or `EXPECT.MUST` projection;
- an assertion with an expected test projection has `phase: test`;
- expected clarify behavior has `on_unmatched_input` in the relevant node.

This is not yet a runtime or a model executor. It is M2-level static behavior validation.


## M3 — Run

```bash
ordo run . --answers run_inputs/answers_success.yaml
ordo run . --answers run_inputs/answers_blocked.yaml
```

The runner creates `runtime/trace_log.json`, `runtime/state_snapshots/`, and `reports/run_report.json`.


## M4 guided intake

```bash
ordo intake . --answers run_inputs/intake_success.yaml --non-interactive
```


## M59.1 Runtime CLI note

Runtime profile builds of this package include `cli_embedded/ordo`. Start Runtime Mode through the embedded CLI when available. If the embedded CLI cannot run, hard-stop; deterministic Runtime Mode is not enforced until CLI evidence exists.
