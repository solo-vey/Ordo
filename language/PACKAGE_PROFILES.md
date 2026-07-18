# Ordo Package Build Profiles

Ordo subject packages use explicit build profiles so development material is not mixed with runtime execution material.

## Profiles

### `dev`

The `dev` profile is the full editable source package for development, audit, and recompilation. It may contain:

```text
README.md
START_HERE_RUNTIME_MODE.md
START_PROMPT_RUNTIME_MODE.md
ordo.yml
ordo.lock.json
source/program.ordo.yaml
compiled/program.ir.json
run_inputs/
tests/
output_templates/
domain/
runtime/
generated_outputs/
reports/
PACKAGING_PROFILES.md
```

### `runtime`

The `runtime` profile is a clean executable package for guided intake in chat or another runner. It must use `compiled/program.ir.json` as the primary runtime source and must not require editable YAML source.

Allowed runtime contents:

```text
README.md
START_HERE_RUNTIME_MODE.md
START_PROMPT_RUNTIME_MODE.md
ordo.runtime.json
compiled/program.ir.json
output_templates/
reports/CLI_VALIDATION_SUMMARY.md
reports/BUILD_MANIFEST.json
reports/SHA256SUMS.txt
```

Runtime packages must not include:

```text
source/program.ordo.yaml
tests/
run_inputs/
domain/
runtime/state_snapshots/
generated_outputs/
release/*.zip
```

### `evidence`

The `evidence` profile contains validation and provenance proof only. It is used for audit/release review and must not contain editable source files.

Typical evidence contents:

```text
reports/CLI_VALIDATION_SUMMARY.md
reports/BUILD_MANIFEST.json
reports/SHA256SUMS.txt
reports/coverage_report.json
reports/lint_report.json
reports/compile_report.json
reports/test_report.json
reports/output_validation_report.json
reports/release_validation_report.json
reports/release_provenance.json
reports/PACKAGE_PROFILE_SUMMARY.md
```

## Validation errors

```text
ORDO-PACKAGE-001 unknown package profile
ORDO-PACKAGE-002 runtime profile includes source YAML
ORDO-PACKAGE-003 runtime profile missing compiled IR
ORDO-PACKAGE-004 runtime profile missing output templates
ORDO-PACKAGE-005 runtime profile missing START_HERE_RUNTIME_MODE.md
ORDO-PACKAGE-006 runtime profile missing ordo.runtime.json
ORDO-PACKAGE-007 runtime profile missing BUILD_MANIFEST.json
ORDO-PACKAGE-008 runtime profile missing SHA256SUMS.txt
ORDO-PACKAGE-009 evidence profile includes editable source files
ORDO-PACKAGE-010 package claims executed_cli_passed without CLI evidence
```


## M59.1 update — embedded runtime CLI

Runtime profile packages now include `cli_embedded/`:

```text
cli_embedded/ordo
cli_embedded/README.md
cli_embedded/ordo_pkg/ordo/...
```

The embedded entrypoint exposes runtime commands only and blocks authoring/release/package commands. A runtime package without a runnable CLI is not considered an enforced Runtime Mode package.

Additional validation error:

```text
ORDO-PACKAGE-011 runtime profile missing embedded runtime CLI
```

## M59.3 update — verify-session in runtime profile

Runtime profile packages include `verify-session` in the embedded CLI allowlist. The runtime manifest remains backward-compatible with:

```json
"trust_level": "level_1_cli_in_package_hard_stop"
```

and adds the detailed Level 1 capability marker:

```json
"trust_level_detail": "level_1_cli_in_package_hard_stop_hash_chain_human_verify"
```

Runtime profile validation must preserve `cli_embedded/ordo`, `compiled/program.ir.json`, `START_HERE_RUNTIME_MODE.md`, `ordo.runtime.json`, and the profile reports needed for independent verification.

## M60.3 update — runtime view modes and target manifest

Runtime packages now support explicit AI-facing runtime view modes:

```bash
ordo package <package> --profile runtime --runtime-view json
ordo package <package> --profile runtime --runtime-view ordo-code
ordo package <package> --profile runtime --runtime-view json,ordo-code
```

`json-ir` is always included as the canonical target. `ordo-code-view` is included only when the selected runtime view requires it. `session-trace` is initialized as a mutable runtime proof target.

M60.3 runtime packages include:

```text
compiled/program.ir.json
compiled/targets.manifest.json
runtime/session.ordo.trace
```

and include this file only when the view supports it:

```text
compiled/program.ordo.view
```

`ordo.runtime.json` must record `runtime_view`, `canonical_target`, `targets`, and `runtime_view_behavior` so embedded CLI can decide whether `next-step --format auto` should emit JSON-only output or a code-like current contract fragment.
