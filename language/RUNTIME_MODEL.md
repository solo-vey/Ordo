# Ordo Runtime Model

Ordo packages have one source-of-truth chain:

```text
ordo.yml → source/program.ordo.yaml → compiled/program.ir.json → run_state.json → generated_outputs/
```

## Roles

- `ordo.yml` is the package manifest and entrypoint.
- `source/program.ordo.yaml` is the editable source of truth.
- `compiled/program.ir.json` is the runtime artifact used by deterministic helpers.
- `run_state.json` or a report embedding `state` is the current execution state.
- `generated_outputs/` contains rendered artifacts and model-assisted rendered files.

## Runtime freshness

Before guided execution, the runtime helper checks whether the source program is newer than the compiled IR.

If `source/program.ordo.yaml` is newer than `compiled/program.ir.json`, helper commands must block with:

```text
ORDO-RUNTIME-004 IR is stale. Run ordo compile before guided execution.
```

If compiled IR is missing, helper commands must not guess the next step. They must report `ORDO-RUNTIME-003` unless the command explicitly allows non-runtime fallback.

## Guided execution rule

When a current IR exists, AI Ordo Developer and AI Ordo Executor must use it as the runtime rail:

```text
read manifest → resolve source → check IR freshness → load IR → load state → next-step/check-gate
```

They must not invent the next step when `program.ir.json` and `run_state` can be checked deterministically.
