# Spec 24 — Clean Package CLI Model

Status: `M67.4 aligned — M67.3 CLI implemented`

The Clean Package CLI Model defines the implemented minimal behavior of the `ordo clean-check` command. It connects the language-level package consistency conventions from M67.0 with a CLI-facing validation surface.

## Purpose

A package is clean when its declared source files, helper prompts, startup entries, manifest coverage, derived artifacts, and known deltas are mutually consistent enough for handoff or release review.

Clean does not mean business-complete. It means structurally consistent according to declared package conventions.

## Command contract

Canonical command:

```bash
ordo clean-check <package>
```

Supported options:

```bash
--profile light|standard|strict
--json
--fail-on-warning
```

Default profile: `standard`.

## Decision model

`clean-check` returns one of four status values:

| Status | Meaning |
|---|---|
| `passed` | no errors and no warnings under the selected profile |
| `passed_with_warnings` | no errors, but warnings exist |
| `blocked` | at least one blocking error exists |
| `not_applicable` | clean-check cannot apply because the target is not an Ordo package or lacks the minimum package identity |

When `--fail-on-warning` is set, `passed_with_warnings` should exit as a failure even if no blocking errors are present.

## Clean-check inputs

The command may inspect:

- package root path;
- package manifest such as `ordo.yml`;
- declared source YAML;
- package manifest/checksum files;
- prompt registry declarations;
- prompt manifest declarations;
- startup package profile declarations;
- artifact sync declarations;
- delta backlog declarations.

The command must not require a specific applied package.

## Minimum deterministic checks

Clean-check v1 should include deterministic file, YAML, reference, and checksum checks. It must not claim deterministic interpretation of human-language prompt safety.

Required check groups:

1. package identity and manifest parsing;
2. source YAML path and parseability;
3. declared manifest path existence;
4. declared checksum matching where checksums are available;
5. prompt registry reference resolution when prompt registry exists;
6. startup profile entry-file resolution when startup profile exists;
7. derived artifact freshness or explicit delta backlog coverage when artifact sync exists;
8. delta backlog blocker hygiene when delta backlog exists.

## Authority boundary

`clean-check` validates consistency. It does not:

- approve business content;
- approve human decisions;
- bypass gates;
- mutate confirmed state;
- choose branches;
- regenerate derived artifacts unless a separate explicit command is invoked;
- promote package-local conventions into runtime opcodes.

## Relationship to M67.0

M67.0 introduced language-level conventions for:

- `artifact_sync`;
- `delta_backlog`;
- `prompt_registry_packaging_checks`.

M67.2 defines the CLI-facing design for checking these conventions. It does not implement the command.

## Relationship to M67.3 and M67.4

M67.3 added a minimal implementation module and CLI entrypoint. M67.4 aligns the language-level `clean_package_gate` and derived artifact sync validation profile to that implemented CLI behavior. Package mutation remains out of scope.
