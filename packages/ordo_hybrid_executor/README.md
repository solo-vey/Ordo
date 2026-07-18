# ordo.hybrid_executor

`ordo.hybrid_executor` is a reference Ordo package for M28. It models execution of a ready Semantic JSON IR by AI Ordo Executor with Process Rail and deterministic helper checks.

## Scope

This package is not a full runtime implementation. It is a language/reference package that fixes the execution contract:

- AI Ordo Executor leads the conversation;
- Semantic JSON IR acts as Process Rail;
- CLI/helper tools validate mechanical parts;
- raw tool output is interpreted before it reaches the human;
- corrections and deviations require rail resume.


## Runtime Mode standard

Start this package with `START_PROMPT_RUNTIME_MODE.md`; the detailed runtime rules live in `START_HERE_RUNTIME_MODE.md`.

Runtime source-of-truth:

```text
ordo.yml = manifest / entrypoint
source/program.ordo.yaml = editable source of truth
compiled/program.ir.json = runtime source for guided execution
run_state.json = current execution state
generated artifacts = rendered output
```

The guided step order must come from `compiled/program.ir.json` when it is current. After editing `source/program.ordo.yaml`, run `ordo compile` before guided execution. CLI evidence should be recorded in `reports/CLI_VALIDATION_SUMMARY.md`.


## M59.1 Runtime CLI note

Runtime profile builds of this package include `cli_embedded/ordo`. Start Runtime Mode through the embedded CLI when available. If the embedded CLI cannot run, hard-stop; deterministic Runtime Mode is not enforced until CLI evidence exists.

## M59.3 Runtime verification note

Runtime profile packages now support `cli_embedded/ordo verify-session .`. Final approval requires the user to run this command and paste `session-chain: intact`. If the chain is broken or the compiled IR canary leaks, the runtime session is invalid and must restart through CLI.
