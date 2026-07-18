# Runtime Package Standard

A runtime package is the execution-safe form of an Ordo subject package.

Runtime package rule:

```text
Runtime package must not require source YAML for execution.
Runtime package must use compiled/program.ir.json as primary runtime source.
```

The editable source of truth remains `source/program.ordo.yaml` in the `dev` profile, but it is intentionally excluded from the `runtime` profile. The runtime profile carries `source_yaml_sha256` in `ordo.runtime.json` so reviewers can trace which source produced the compiled IR without giving the runtime executor a second competing process definition.

## `ordo.runtime.json`

```json
{
  "package_id": "",
  "package_version": "",
  "profile": "runtime",
  "runtime_source": "compiled/program.ir.json",
  "templates": "output_templates/",
  "source_yaml_included": false,
  "source_yaml_sha256": "",
  "compiled_ir_sha256": "",
  "compiler_version": "",
  "cli_validation_status": "executed_cli_passed"
}
```

## Runtime execution rule

A runtime executor should load:

```text
START_HERE_RUNTIME_MODE.md → ordo.runtime.json → compiled/program.ir.json → run_state
```

It should not use missing or excluded source YAML to choose the next question when a current compiled IR exists.


## M59.1 update — CLI-in-package hard-stop

A runtime package must carry `cli_embedded/ordo`. Runtime execution must use the embedded CLI outputs as the enforceable runtime interface. If the embedded CLI cannot run, the session must hard-stop and may continue only after explicit user approval in nondeterministic fallback mode with `DETERMINISM_NOT_ENFORCED` in every generated artifact.

`ordo.runtime.json` records:

```json
{
  "embedded_cli_included": true,
  "embedded_cli_path": "cli_embedded/ordo",
  "trust_level": "level_1_cli_in_package_hard_stop"
}
```

## M59.3 update — session-chain verification

Runtime packages must support:

```bash
cli_embedded/ordo verify-session <package>
```

The expected successful terminal line is:

```text
session-chain: intact
```

The runtime package must also include start-file rules that prohibit direct AI reading of `compiled/*` and require user-run verification before final approval.

## M60.3 update — multi-target runtime package

Runtime packages are now multi-target packages. The canonical machine target is still:

```text
compiled/program.ir.json
```

Additional target metadata is stored in:

```text
compiled/targets.manifest.json
```

The mutable runtime proof program is initialized as:

```text
runtime/session.ordo.trace
```

If the package is built with `--runtime-view ordo-code` or `--runtime-view json,ordo-code`, it also includes:

```text
compiled/program.ordo.view
```

If the package is built with `--runtime-view json`, `compiled/program.ordo.view` must be excluded to avoid stale AI-facing projections.

`ordo.runtime.json` records:

```json
{
  "runtime_view": "ordo-code",
  "canonical_target": "json-ir",
  "targets": ["json-ir", "ordo-code-view", "session-trace"],
  "runtime_view_behavior": {
    "default_next_step_format": "ordo-code",
    "allowed_cli_formats": ["ordo-code"]
  }
}
```

The embedded CLI may verify and render targets, but must not regenerate them inside a runtime package.
