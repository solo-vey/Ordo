# Embedded Runtime CLI

Runtime packages generated with `ordo package --profile runtime` include a package-owned CLI entrypoint:

```text
cli_embedded/ordo
```

The embedded CLI is copied from the Developer Bundle CLI source at packaging time and wrapped so that only runtime commands are accepted.

Allowed runtime commands after M60.1:

```text
runtime-status
runtime-entry
next-step
check-gate
validate-state
intake
generate-output
validate-output
validate-artifacts
consistency
go-no-go
validate-cli-status
verify-session
render-runtime-view
verify-targets
```

Blocked command examples:

```bash
cli_embedded/ordo package .
cli_embedded/ordo init example
cli_embedded/ordo lock .
```

These fail because runtime packages are for execution, not authoring.

## Packaging behavior

When building a runtime package, `ordo package --profile runtime` creates:

```text
cli_embedded/ordo
cli_embedded/README.md
cli_embedded/ordo_pkg/ordo/...
```

and records the trust level in `ordo.runtime.json` and `reports/BUILD_MANIFEST.json`.

## M59.2 incremental submit evidence

The embedded CLI supports one-node runtime progression without editable source YAML:

```bash
cli_embedded/ordo intake . --submit <NODE_ID> --answer "<answer>" --state run_state.json
```

The command writes a submit report, a state snapshot, and a per-node evidence report under `runtime/evidence/`. The AI must show the evidence path and SHA-256 digest before asking the next runtime question. Direct reading of `compiled/program.ir.json` is not evidence for node transition.


## M60.1 runtime target view

Runtime packages include:

```text
compiled/program.ir.json
compiled/program.ordo.view
compiled/targets.manifest.json
```

The embedded CLI may verify and serve these targets:

```bash
cli_embedded/ordo verify-targets .
cli_embedded/ordo render-runtime-view . --format ordo-code --node <NODE_ID>
cli_embedded/ordo next-step . --format ordo-code
```

Authoring commands such as `compile` and `package` remain blocked in the embedded runtime CLI.
