# CLI Package Profiles

`ordo package` supports three build profiles:

```bash
ordo package <package> --profile dev --out <zip>
ordo package <package> --profile runtime --out <zip>
ordo package <package> --profile evidence --out <zip>
```

## `dev`

Full source package for editing, audit, and recompilation. Includes editable source and tests.

## `runtime`

Clean execution package. It includes compiled IR, runtime start files, templates, and build evidence. It excludes source YAML, tests, run inputs, domain notes, generated outputs, release zips, and state snapshots.

Before creating a runtime package, the CLI checks:

```text
compiled/program.ir.json exists
IR is not stale relative to source/program.ordo.yaml
output_templates/ exists
START_HERE_RUNTIME_MODE.md exists
CLI status is truthful
```

## `evidence`

Validation and provenance reports only. It excludes editable source files.

## Generated evidence

The command writes:

```text
reports/package_report.json
reports/BUILD_MANIFEST.json
reports/SHA256SUMS.txt
ordo.runtime.json     # runtime profile only
```

## Important

`compile` is not equivalent to package validity. Runtime packaging should happen after validation steps such as `lint`, `compile`, `test`, `coverage`, `validate-output`, `consistency`, and `go-no-go` have produced evidence.


## M59.1 runtime profile addition

Runtime profile packages include `cli_embedded/ordo`. The embedded CLI is runtime-only and blocks authoring/package/release commands.

## `prompt_only`

A lightweight model-instruction package compiled from canonical Ordo Source. It contains `MODEL_INSTRUCTIONS.md`, `PROMPT_COMPILATION_MANIFEST.json`, build evidence, and checksums. It excludes source, tests, runtime state, and templates. The manifest must explicitly list guarantees retained and lost and must never claim equivalence to engine runtime.
