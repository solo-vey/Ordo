# CLI Clean Check Command Design

Status: `M67.3 implemented-minimal / CLI command available`

`clean-check` is the CLI command for checking whether an Ordo package is clean enough for handoff, release, or runtime execution review.

M67.3 implements the minimal deterministic v1 command without changing runtime, compiler, IR, opcodes, or applied packages.

## Command shape

```bash
ordo clean-check <package>
ordo clean-check <package> --profile light
ordo clean-check <package> --profile standard
ordo clean-check <package> --profile strict
ordo clean-check <package> --json
ordo clean-check <package> --fail-on-warning
```

`<package>` is a filesystem path to a package root. The command should not require the package to be a specific applied module.

## Profiles

| Profile | Intended use | Blocking behavior |
|---|---|---|
| `light` | authoring and draft package review | blocks parse failures and missing required root/package files |
| `standard` | normal package handoff | blocks unresolved declared files, checksum mismatches, missing prompt/startup entries, and unbacklogged stale derived artifacts |
| `strict` | release or stable handoff | blocks standard errors plus warnings that remain unresolved or unwaived |

Default profile: `standard`.

## Output contract

Human-readable output should summarize the package status, profile, errors, warnings, and key checks.

JSON output must be deterministic and must use this top-level shape:

```json
{
  "status": "passed",
  "profile": "standard",
  "package_root": "path/to/package",
  "checks": [],
  "warnings": [],
  "errors": [],
  "summary": {
    "error_count": 0,
    "warning_count": 0,
    "check_count": 0
  }
}
```

Allowed status values:

- `passed`
- `passed_with_warnings`
- `blocked`
- `not_applicable`

## Minimum v1 checks

The M67.3 implementation is deliberately small and deterministic.

| Check ID | Scope | Failure severity |
|---|---|---|
| `package_root_exists` | package path exists and is a directory | error |
| `package_manifest_present` | `ordo.yml` exists when package layout requires it | error |
| `package_manifest_parse` | `ordo.yml` parses as YAML | error |
| `source_yaml_declared` | package manifest declares source YAML path, when supported | error |
| `source_yaml_exists` | declared source YAML exists | error |
| `source_yaml_parse` | declared source YAML parses as YAML | error |
| `declared_manifest_paths_exist` | declared manifest paths exist | error |
| `declared_manifest_checksums_match` | declared checksums match current file contents | error in standard/strict, warning in light |
| `prompt_registry_refs_resolve_when_present` | prompt refs resolve when `prompt_registry` is present | error |
| `startup_profile_entries_exist_when_present` | startup entry files exist when `startup_package_profile` is present | error |
| `derived_artifacts_current_or_backlogged_when_declared` | derived artifacts are current or explicitly listed in `delta_backlog` | error in standard/strict, warning in light |
| `delta_backlog_blockers_not_expired_when_declared` | blockers are not expired or unowned | error in strict, warning in standard |

## Non-goals for v1

`clean-check` v1 must not:

- regenerate runtime artifacts;
- regenerate lockfiles;
- rebuild embedded CLI bundles;
- mutate package source YAML;
- mutate package manifests;
- make natural-language authority decisions deterministically;
- apply package-specific business logic;
- change runtime, compiler, IR, or opcode behavior.

## Relationship to existing commands

`clean-check` is not a replacement for:

- `lint`;
- `compile`;
- `test`;
- `coverage`;
- `runtime-status`;
- `repo-check`;
- `package`.

It is a package consistency gate that can call or reuse lower-level checks in future implementation.

## Implementation boundary

M67.3 implements minimal support in `cli/ordo/clean_check.py` and wires the command in `cli/ordo/cli.py`. It does not regenerate runtime artifacts, lockfiles, compiled IR, or embedded CLI bundles. It does not mutate package source YAML.

## M67.4 language gate alignment

M67.4 aligns this implemented command with the language-level `clean_package_gate` and `derived_artifact_sync_validation_profile` conventions. The CLI report is the executable evidence surface; language docs define gate interpretation and schema conventions.

See:

- `../../language/CLEAN_PACKAGE_GATE.md`
- `../../language/DERIVED_ARTIFACT_SYNC_VALIDATION_PROFILE.md`
- `../../language/spec/25_CLEAN_PACKAGE_GATE_MODEL.md`



## M68.0 hardening plan

M68.0 does not change this command contract. It adds the hardening plan and fixture matrix that should guide the next implementation milestones.

See:

- `CLEAN_CHECK_HARDENING_PLAN.md`
- `CLEAN_CHECK_FIXTURE_MATRIX.md`
- `REPO_LEVEL_PACKAGE_HYGIENE_PLAN.md`

## M68.1 fixture-backed validation

M68.1 adds a real fixture suite under `cli/tests/fixtures/clean_check/` and a
targeted test module `cli/tests/test_clean_check_fixtures.py`. These tests exercise
`ordo clean-check` across clean, blocked, warning, profile-sensitive, JSON, output-file,
and fail-on-warning scenarios without touching applied packages.



## M68.2 output and exit-code hardening

M68.2 hardens the report contract without changing the command shape. The report now includes:

- `schema_version`: currently `ordo.clean_check.report.v1`;
- `profile_requested`: the caller-provided profile string after normalization;
- `profile`: the effective profile used by the checker;
- `fail_on_warning`: whether warnings are treated as non-zero exit for this run;
- `exit_code`: the exact process exit code the CLI should return;
- expanded `summary` counters: `passed_count`, `failed_count`, and `not_applicable_count`;
- `exit_policy`: the status-to-exit-code mapping for the current run.

The CLI still accepts only `light`, `standard`, and `strict` through argparse. Programmatic callers of `run_clean_check()` that pass an unsupported profile receive a warning finding and the effective profile falls back to `standard`.

Exit-code behavior remains:

| Status | `--fail-on-warning` | Exit code |
|---|---:|---:|
| `passed` | false/true | 0 |
| `passed_with_warnings` | false | 0 |
| `passed_with_warnings` | true | 1 |
| `blocked` | false/true | 1 |
