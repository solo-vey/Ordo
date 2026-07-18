# Chapter 48. Runtime Source of Truth and CLI Honesty

After contract → artifact coverage and two-tier rendering appeared, Ordo gained another important layer: the runtime source of truth.

The idea is simple: an Ordo package cannot be executed as a random collection of files. It must be loaded as a consistent runtime:

```text
ordo.yml → source/program.ordo.yaml → compiled/program.ir.json → run_state.json → generated_outputs/
```

`ordo.yml` is the package entry point. `source/program.ordo.yaml` is the editable source of truth. `compiled/program.ir.json` is the runtime artifact from which helper commands obtain the Process Rail, nodes, gates, and outputs. `run_state.json`, or a report with embedded `state`, describes the current execution state. Generated artifacts are the rendering result.

## Why this is needed

Without this rule, AI Ordo Developer may accidentally conduct guided intake “from memory”: start with the wrong question, skip a gate, or use stale instructions after YAML changes.

M53 closes this class of errors. If YAML is newer than compiled IR, a runtime helper must block execution and request recompilation.

```text
ORDO-RUNTIME-004: IR is stale. Run ordo compile before guided execution.
```

## Standard Developer workflow

```text
runtime-status
lint
compile
test
coverage
validate-state
check-gate / next-step
generate-output
validate-output
validate-artifacts
consistency
go-no-go
package
```

Importantly, `compile` does not mean the final package is valid. It only creates Semantic JSON IR. Final readiness is determined after `validate-artifacts`, `consistency`, and `go-no-go`.

## CLI honesty

Ordo also introduces a truthfulness rule: the model must not write “CLI validation passed” if the CLI was not actually run.

Allowed statuses are:

```text
executed_cli_passed
executed_cli_failed
logical_self_check_only
not_run_cli_unavailable
not_run_user_skipped
```

This separates real verification from a logical assumption. If the CLI is unavailable, that is not itself an error, but it must be stated honestly.

## What this provides

M53 brings the Developer Bundle closer to a real runtime package: AI works flexibly, but every critical transition is checked deterministically.
