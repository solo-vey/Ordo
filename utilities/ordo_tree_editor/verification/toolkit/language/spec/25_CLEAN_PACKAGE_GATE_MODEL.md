# Spec 25 — Clean Package Gate Model

Status: `M67.4 aligned to implemented CLI`

The Clean Package Gate Model connects the implemented `ordo clean-check` CLI command with language-level package handoff semantics.

## Source of truth

The CLI command is the executable evidence surface:

```bash
ordo clean-check <package>
```

The language model defines how to interpret the report, not how to mutate the package.

## Gate role

`clean_package_gate` is a handoff/release-readiness gate. It checks package consistency across:

- package root and `ordo.yml`;
- declared source YAML;
- declared manifest paths;
- checksums when available;
- prompt registry references;
- startup profile entry files;
- artifact sync declarations;
- delta backlog blockers.

## Implemented report shape

The M67.3 CLI returns a deterministic report shaped as:

```json
{
  "mode": "clean_package_check",
  "status": "passed",
  "profile": "standard",
  "package_root": "/path/to/package",
  "checks": [],
  "warnings": [],
  "errors": [],
  "summary": {
    "error_count": 0,
    "warning_count": 0,
    "check_count": 0
  },
  "exit_code": 0
}
```

## Gate interpretation

| Report status | Gate result |
|---|---|
| `passed` | `approved` |
| `passed_with_warnings` | `approved_with_warnings` |
| `blocked` | `blocked` |
| `not_applicable` | `not_applicable` |

The `exit_code` is CLI/CI evidence. The semantic gate decision is derived from `status` and selected policy.

## Required v1 check IDs

M67.4 treats the M67.3 v1 check IDs as the baseline clean package check set:

1. `package_root_exists`
2. `package_manifest_present`
3. `package_manifest_parse`
4. `source_yaml_declared`
5. `source_yaml_exists`
6. `source_yaml_parse`
7. `declared_manifest_paths_exist`
8. `declared_manifest_checksums_match`
9. `prompt_registry_refs_resolve_when_present`
10. `startup_profile_entries_exist_when_present`
11. `derived_artifacts_current_or_backlogged_when_declared`
12. `delta_backlog_blockers_not_expired_when_declared`

Some checks may return `not_applicable` when the corresponding convention is not present in the package.

## No mutation rule

The clean package gate is read-only. A future command may regenerate artifacts, refresh lockfiles, or update manifests, but it must be explicit and separate from `clean-check`.

## Scope boundary

This specification does not change runtime execution, compiler behavior, opcodes, IR semantics, package-local business logic, or applied package source YAML.
