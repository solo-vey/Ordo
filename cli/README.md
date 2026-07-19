# Ordo CLI

`ordo` is the deterministic helper layer for Ordo Process Rail packages.

It validates and compiles package structure, checks state and gates, generates helper reports, and supports package-local output generation. It is not the main conversational runtime; AI Ordo Developer and AI Ordo Executor interpret the results for humans.

Run all commands below from the repository root.

## Install

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ./cli
```

Python 3.10 or newer is required.

## Canonical examples

```bash
python tools/run_golden_examples.py --all
```

The full walkthrough is in [`../docs/QUICKSTART.md`](../docs/QUICKSTART.md). The machine-readable source of truth is [`../examples/golden_examples.json`](../examples/golden_examples.json).

## Core package commands

```bash
ordo lint packages/ordo_project_builder
ordo compile packages/ordo_project_builder
ordo test packages/ordo_project_builder
ordo coverage packages/ordo_project_builder
ordo validate-state packages/ordo_project_builder --answers packages/ordo_project_builder/run_inputs/authoring_success.yaml
ordo next-step packages/ordo_project_builder --answers packages/ordo_project_builder/run_inputs/authoring_success.yaml
```

## Command surface

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

Commands removed by the lean cleanup are not part of the current CLI surface: registry-site, dashboard, global publication catalog, release-promotion, and global template-registry commands.

## Artifact validation

`ordo validate-artifacts` checks rendered Markdown, JSON, and YAML artifacts against confirmed contract values and writes `reports/artifact_validation_report.json`.

`ordo consistency` generates `reports/CONSISTENCY_CHECK_REPORT.json` and checks whether generated artifacts agree on confirmed contract fields.

`ordo go-no-go` runs the final deterministic helper pipeline and writes `reports/GO_NO_GO_REPORT.json`. It returns exit code `0` only for `go`.

```bash
ordo go-no-go packages/history_event_guided_intake   --answers packages/history_event_guided_intake/run_inputs/intake_success.yaml
```

## Repository hygiene scopes

Use development scope in an installed working tree:

```bash
ordo repo-check . --clean --profile standard --hygiene-scope development
```

Use release scope only against an isolated clean candidate tree:

```bash
mkdir -p /tmp/ordo-release-candidate
git archive --format=tar HEAD | tar -xf - -C /tmp/ordo-release-candidate
ordo repo-check /tmp/ordo-release-candidate --clean --profile strict --hygiene-scope release --fail-on-warning
```

Development scope reports local Python cache and install metadata without blocking unless Git tracks it. Release scope strictly forbids that metadata in the candidate tree.

## Runtime checkpoints

Runtime Mode enforces one node, one contract, and one decision at a time. Helper reports expose `checkpoint_table`, `earliest_incomplete_node`, `open_required_fields`, and `forward_allowed`. `next-step` prioritizes the earliest incomplete node, and `generate-output` is blocked while checkpoint gaps remain.

See [`../language/RUNTIME_CHECKPOINTS.md`](../language/RUNTIME_CHECKPOINTS.md) and package-local `START_HERE_RUNTIME_MODE.md` files.

## Incremental intake

Use one-node submit mode when the runtime is collecting answers interactively:

```bash
ordo intake packages/history_event_guided_intake --submit N_EVENT_GOAL --answer "Capital change"
ordo intake packages/history_event_guided_intake --submit N_PATH_SELECT --answer A   --state packages/history_event_guided_intake/reports/intake_submit_report.json
```

Each submit produces `reports/intake_submit_report.json`, a state snapshot, and `runtime/evidence/*_evidence.json` with SHA-256 digest metadata.

## Session verification

```bash
ordo verify-session packages/history_event_guided_intake
```

The command prints `session-chain: intact` for an intact chain. Broken chains report the failing sequence. Canary leaks report that raw IR was read.

## Runtime target views

`compile` emits:

```text
compiled/program.ir.json
compiled/program.ordo.view
compiled/targets.manifest.json
```

Runtime helpers:

```bash
ordo render-runtime-view packages/history_event_guided_intake --format ordo-code --node N_PATH_SELECT
ordo next-step packages/history_event_guided_intake --format ordo-code
ordo verify-targets packages/history_event_guided_intake
```

`verify-targets` checks that every target matches the manifest and that AI-facing targets derive from the current IR hash without leaking the canary.

## Runtime packaging modes

```bash
ordo package packages/history_event_guided_intake --profile runtime --runtime-view json
ordo package packages/history_event_guided_intake --profile runtime --runtime-view ordo-code
ordo package packages/history_event_guided_intake --profile runtime --runtime-view json,ordo-code
```

## Session trace proof

```bash
ordo intake packages/history_event_guided_intake --submit N_EVENT_GOAL --answer-file tmp_answer.yaml
ordo verify-session packages/history_event_guided_intake
```

`intake --submit` appends an Ordo-code-like proof step to `runtime/session.ordo.trace` and links that step from per-node evidence. `verify-session` validates the target set, hash-chain snapshots, session trace, and canary scan together.

## Full regression suite in constrained tool environments

```bash
python cli/scripts/run_full_suite_partitioned.py
```

The launcher runs each `cli/tests/test_*.py` file in an isolated subprocess and writes `reports/FULL_TEST_SUITE_PARTITIONED_REPORT.json`.


## Documentation map

See [`../docs/README.md`](../docs/README.md) for the canonical documentation routes.
