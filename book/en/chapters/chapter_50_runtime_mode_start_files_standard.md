# Chapter 50. Runtime Mode Start Files Standard

After M55, detailed runtime rules no longer need to be inserted into a large prompt every time.

Every runtime-ready Ordo package has two start files:

```text
START_HERE_RUNTIME_MODE.md
START_PROMPT_RUNTIME_MODE.md
```

`START_HERE_RUNTIME_MODE.md` contains the full protocol: how to read `ordo.yml`, how to check source/IR, how to work with `run_state`, how not to conduct guided intake “from memory,” how to record CLI status, how not to bypass gates, and how to run artifact validation.

`START_PROMPT_RUNTIME_MODE.md` is minimal. It only tells the AI to read `START_HERE_RUNTIME_MODE.md` and begin the runtime loading protocol.

The source-of-truth chain remains:

```text
ordo.yml = manifest / entrypoint
source/program.ordo.yaml = editable source of truth
compiled/program.ir.json = runtime source for guided execution
run_state.json = current execution state
generated artifacts = rendered output
```

The book PDF is not regenerated at this step.
