# Chapter 51. Package Build Profiles: dev / runtime / evidence

M56 adds a standard division of an Ordo package into three profiles.

## Why this is needed

During development, one subject package may contain everything at once: source YAML, compiled IR, tests, run inputs, generated outputs, runtime snapshots, and reports. This is useful for a developer, but dangerous for guided runtime: the executor may accidentally inspect YAML or stale intermediate files instead of the current `compiled/program.ir.json`.

Three profiles are therefore introduced:

```text
dev      — complete source package for development and audit
runtime  — clean executable package for guided intake
evidence — compilation, validation, hash/provenance/status evidence
```

## Runtime profile

A runtime package must work without editable YAML:

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

It must not contain:

```text
source/program.ordo.yaml
tests/
run_inputs/
domain/
runtime/state_snapshots/
generated_outputs/
release/*.zip
```

The main rule is:

```text
Runtime package must not require source YAML for execution.
Runtime package must use compiled/program.ir.json as primary runtime source.
```

## CLI

Packaging is explicit:

```bash
ordo package <package> --profile dev --out <zip>
ordo package <package> --profile runtime --out <zip>
ordo package <package> --profile evidence --out <zip>
```

For the runtime profile, the CLI checks compiled IR availability, IR freshness relative to YAML, runtime start files, output templates, and CLI evidence.

## Evidence

Every build profile generates or uses:

```text
reports/BUILD_MANIFEST.json
reports/SHA256SUMS.txt
reports/package_report.json
```

The runtime profile also generates:

```text
ordo.runtime.json
```

This gives the executor a clean runtime package and the reviewer a separate evidence package.

The book PDF was not regenerated in M56.

## Standard package-profile errors

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
