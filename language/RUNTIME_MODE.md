# Runtime Mode

Runtime Mode is the standard way to operate an Ordo subject package with an AI Developer/Executor.

The detailed instruction belongs inside the package in `START_HERE_RUNTIME_MODE.md`. The user-facing prompt should be minimal and should only ask the AI to read that file and begin runtime loading.

## Source-of-truth chain

```text
ordo.yml → source/program.ordo.yaml → compiled/program.ir.json → run_state.json → generated artifacts
```

`source/program.ordo.yaml` is editable source of truth. `compiled/program.ir.json` is the primary runtime source for guided execution when it exists and is fresh. The AI must not invent question order when the IR is current.

## Standard runtime flow

```text
read START_HERE_RUNTIME_MODE.md
→ read ordo.yml
→ resolve source YAML
→ resolve compiled IR
→ check freshness
→ load IR
→ initialize/load run_state
→ next-step/check-gate/validate-state
→ render
→ validate-output/validate-artifacts
→ consistency
→ go-no-go
```

`compile` alone is not final package validation.

## M57 Runtime Checkpoint Discipline

Runtime Mode now enforces a checkpoint layer: one node, one contract, and one decision at a time. Helper reports expose `checkpoint_table`, `earliest_incomplete_node`, `open_required_fields`, and `forward_allowed`. `next-step` prioritizes the earliest incomplete node, and `generate-output` is blocked while checkpoint gaps remain. Detailed rules live in `language/RUNTIME_CHECKPOINTS.md` and package `START_HERE_RUNTIME_MODE.md`; minimal runtime prompts stay minimal.



## M59.1 CLI-enforced runtime mode

Runtime Mode is enforceable only when a CLI can run. Runtime packages therefore include `cli_embedded/ordo`. If the embedded CLI cannot run, the AI/runner must stop and report that Ordo determinism is not enforced. Silent continuation with `not_run_cli_unavailable` is no longer acceptable.
