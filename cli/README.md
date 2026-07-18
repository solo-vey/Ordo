# Ordo CLI

`ordo` is the deterministic helper layer for Ordo Process Rail packages.

It validates and compiles package structure, checks state/gates, generates helper reports, and supports package-local output generation. It is not the main conversational runtime; AI Ordo Developer / AI Ordo Executor interpret the results for humans.

## Install

```bash
python -m pip install -e .
```

## Core commands

```text
init
lint
compile
test
coverage
run
intake
validate-state
check-gate
next-step
diff-state
explain-validation
generate-output
validate-output
validate-artifacts
consistency
go-no-go
lock
validate-lock
check-conflicts
validate-release
build-provenance
validate-provenance
diff-release
generate-release-notes
render-runtime-view
verify-targets
verify-session
repo-check
package
```

Removed in M43 lean cleanup: registry-site, dashboard, global publication catalog, release-promotion and global template-registry commands.

## Example

```bash
ordo lint ../packages/ordo_project_builder
ordo compile ../packages/ordo_project_builder
ordo test ../packages/ordo_project_builder
ordo coverage ../packages/ordo_project_builder
ordo validate-state ../packages/ordo_project_builder --answers ../packages/ordo_project_builder/run_inputs/authoring_success.yaml
ordo next-step ../packages/ordo_project_builder --answers ../packages/ordo_project_builder/run_inputs/authoring_success.yaml
```

### `ordo validate-artifacts`

Checks rendered Markdown/JSON/YAML artifacts against confirmed contract values and writes `reports/artifact_validation_report.json`.

### `ordo consistency`

Generates `reports/CONSISTENCY_CHECK_REPORT.json` and checks whether generated artifacts agree on confirmed contract fields.

### `ordo go-no-go`

Runs the final deterministic helper pipeline and writes `reports/GO_NO_GO_REPORT.json`. It returns exit code `0` only for `go`.

```bash
ordo go-no-go ../packages/history_event_guided_intake \
  --answers ../packages/history_event_guided_intake/run_inputs/intake_success.yaml
```

### `ordo repo-check` hygiene scopes

Use development scope in an installed working tree:

```bash
ordo repo-check .. --clean --profile standard --hygiene-scope development
```

Use release scope only against an isolated clean candidate tree:

```bash
git archive --format=tar HEAD | tar -xf - -C /tmp/ordo-release-candidate
ordo repo-check /tmp/ordo-release-candidate --clean --profile strict --hygiene-scope release --fail-on-warning
```

Development scope reports local Python cache/install metadata without blocking unless Git tracks it. Release scope strictly forbids that metadata in the candidate tree.


- `RUNTIME_ENTRY.md` — `ordo runtime-entry` startup guard for AI Runtime Mode.

## M57 Runtime Checkpoint Discipline

Runtime Mode now enforces a checkpoint layer: one node, one contract, and one decision at a time. Helper reports expose `checkpoint_table`, `earliest_incomplete_node`, `open_required_fields`, and `forward_allowed`. `next-step` prioritizes the earliest incomplete node, and `generate-output` is blocked while checkpoint gaps remain. Detailed rules live in `language/RUNTIME_CHECKPOINTS.md` and package `START_HERE_RUNTIME_MODE.md`; minimal runtime prompts stay minimal.

## M59.2 incremental intake

Use one-node submit mode when the runtime is collecting answers interactively:

```bash
ordo intake ../packages/history_event_guided_intake --submit N_EVENT_GOAL --answer "Зміна капіталу"
ordo intake ../packages/history_event_guided_intake --submit N_PATH_SELECT --answer A --state ../packages/history_event_guided_intake/reports/intake_submit_report.json
```

Each submit produces `reports/intake_submit_report.json`, a state snapshot, and `runtime/evidence/*_evidence.json` with SHA-256 digest metadata.


## M59.3 verify-session

Use `verify-session` to check the tamper-evident runtime session chain:

```bash
ordo verify-session <package>
```

The command prints one terminal line for human verification:

```text
session-chain: intact
```

Broken chains produce `session-chain: broken at seq N`. Canary leaks produce `session-chain: CANARY LEAK — raw IR was read`.

## M60.1 multi-target runtime views

`compile` now emits a horizontal target set:

```text
compiled/program.ir.json       # canonical machine target
compiled/program.ordo.view     # AI-facing ordo-code target
compiled/targets.manifest.json # target hash/derivation manifest
```

Runtime helpers:

```bash
ordo render-runtime-view ../packages/history_event_guided_intake --format ordo-code --node N_PATH_SELECT
ordo next-step ../packages/history_event_guided_intake --format ordo-code
ordo verify-targets ../packages/history_event_guided_intake
```

`verify-targets` checks that every target matches the manifest and that AI-facing targets are derived from the current IR hash without leaking the canary.

## M60.3 runtime packaging modes

Runtime packages now have explicit AI-facing view modes while keeping JSON IR canonical:

```bash
ordo package <package> --profile runtime --runtime-view json
ordo package <package> --profile runtime --runtime-view ordo-code
ordo package <package> --profile runtime --runtime-view json,ordo-code
```

`json` mode packages `compiled/program.ir.json`, `compiled/targets.manifest.json`, and `runtime/session.ordo.trace`, but intentionally excludes `compiled/program.ordo.view`. `ordo-code` mode packages the Ordo-code projection and makes `next-step --format auto` print the current contract fragment.

## M60.2 session trace proof

`intake --submit` appends an Ordo-code-like proof step to `runtime/session.ordo.trace` and links that step from the per-node evidence report. `verify-session` validates target-set, hash-chain snapshots, session trace, and canary scan together.

```bash
ordo intake <package> --submit <NODE_ID> --answer-file tmp_answer.yaml
ordo verify-session <package>
```

## Full regression suite in constrained tool environments

Use the partitioned launcher when one interactive tool call cannot remain open for the whole suite:

```bash
python scripts/run_full_suite_partitioned.py
```

It runs every `tests/test_*.py` file in an isolated subprocess and writes `../reports/FULL_TEST_SUITE_PARTITIONED_REPORT.json`. Do not classify an interrupted tool call as a hanging test until the suspected file and test have been run separately. See `docs/FULL_TEST_SUITE_EXECUTION_PROTOCOL.md`.
