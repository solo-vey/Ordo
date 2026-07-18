# ordo.project_builder

`ordo.project_builder` — перший Ordo package для створення нових Ordo-проєктів через діалог PM з AI Ordo Developer.

PM не пише YAML напряму. PM описує домен, задачу, процес і очікувані результати. AI Ordo Developer уточнює, радить, проектує Process Rail, оновлює YAML, запускає deterministic helper checks і компілює проєкт у Semantic JSON IR.

## Основний loop

```text
PM message
  ↓
AI Ordo Developer interprets intent
  ↓
Project draft YAML update
  ↓
CLI helper: lint / compile / test / coverage
  ↓
AI explains project state in human language
  ↓
next PM decision
```

## Scope M27

Цей package є conceptual MVP. Він фіксує authoring flow і gates, але не є повним no-code IDE для Ordo.

## M46 contract/artifact validation loop

For pre-release Developer work, the canonical validation route is now:

```text
lint → compile → coverage → validate-state → generate-output → validate-artifacts → consistency → go-no-go
```

Meaning:

- `compile` checks source and contract/artifact references;
- `coverage` checks that confirmed contracts have artifact mappings;
- `validate-state` checks current Process Rail readiness;
- `generate-output` renders artifacts;
- `validate-artifacts` checks that confirmed contract values reached the rendered files;
- `consistency` checks that rendered artifacts agree with each other;
- `go-no-go` returns the final deterministic readiness decision.

`go-no-go` does not replace AI Ordo Developer. It is deterministic evidence that the Developer must interpret before giving a PM-facing decision.

## M53 runtime source-of-truth workflow

This package is the canonical Developer example for treating an Ordo project as a runtime, not as a loose folder of Markdown/YAML files.

Source-of-truth chain:

```text
ordo.yml → source/program.ordo.yaml → compiled/program.ir.json → run_state.json → generated_outputs/
```

Recommended Developer pipeline:

```bash
ordo runtime-status .
ordo lint .
ordo compile .
ordo test .
ordo coverage .
ordo validate-state . --answers run_inputs/authoring_success.yaml
ordo next-step . --answers run_inputs/authoring_success.yaml
ordo check-gate . G_PM_APPROVES_AUTHORING_CONTRACT --answers run_inputs/authoring_success.yaml
```

`next-step` and `check-gate` must use the current compiled IR. If `source/program.ordo.yaml` is newer than `compiled/program.ir.json`, the helper must block with `ORDO-RUNTIME-004` instead of guessing the next step.

Do not claim `executed_cli_passed` in handoff reports unless these commands were actually run and the report includes evidence.


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

## M56 package build profiles

Ordo subject packages now distinguish three build profiles:

```bash
ordo package <package> --profile dev --out <zip>
ordo package <package> --profile runtime --out <zip>
ordo package <package> --profile evidence --out <zip>
```

- `dev` is the full editable package with source YAML, tests, run inputs, templates, reports, and development material.
- `runtime` is the clean guided-execution package. It uses `compiled/program.ir.json` as the primary runtime source and excludes `source/`, `tests/`, `run_inputs/`, `domain/`, generated outputs, state snapshots, and release zips.
- `evidence` contains validation/provenance/hash reports only.

Runtime packaging creates `ordo.runtime.json`, `reports/BUILD_MANIFEST.json`, and `reports/SHA256SUMS.txt`. The runtime package records the source YAML hash even though editable YAML is not included.

## M57 Runtime Checkpoint Discipline

Runtime Mode now enforces a checkpoint layer: one node, one contract, and one decision at a time. Helper reports expose `checkpoint_table`, `earliest_incomplete_node`, `open_required_fields`, and `forward_allowed`. `next-step` prioritizes the earliest incomplete node, and `generate-output` is blocked while checkpoint gaps remain. Detailed rules live in `language/RUNTIME_CHECKPOINTS.md` and package `START_HERE_RUNTIME_MODE.md`; minimal runtime prompts stay minimal.



## M59.1 Runtime CLI note

Runtime profile builds of this package include `cli_embedded/ordo`. Start Runtime Mode through the embedded CLI when available. If the embedded CLI cannot run, hard-stop; deterministic Runtime Mode is not enforced until CLI evidence exists.

## M59.3 Runtime verification note

Runtime profile packages now support `cli_embedded/ordo verify-session .`. Final approval requires the user to run this command and paste `session-chain: intact`. If the chain is broken or the compiled IR canary leaks, the runtime session is invalid and must restart through CLI.
