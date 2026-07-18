# Startup Profile Validation / Lint Profile

**Milestone:** M66.2  
**Status:** docs/schema/lint-profile design  
**Scope:** validation convention for `startup_package_profile` blocks in Ordo packages.

## Purpose

M66.2 defines how a package-local `startup_package_profile` should be checked before a package is presented as start-ready.

It is a **lint/validation profile convention**, not a runtime feature. It does not add CLI commands, opcodes, compiler behavior, or runtime state transitions.

## Validation object

A package may declare a startup validation profile as a top-level package/source object:

```yaml
startup_profile_validation:
  profile: standard
  applies_to:
    - startup_package_profile
    - prompt_registry
    - package_manifest
  readiness_decision:
    allowed_values:
      - start_ready
      - start_ready_with_warnings
      - blocked
      - not_applicable
```

## Profiles

| Profile | Intended use | Blocking behavior |
|---|---|---|
| `light` | Draft packages, examples, early package planning | Only missing profile, broken default mode, and missing required entry files block. |
| `standard` | Reusable applied modules and analyst-facing packages | Blocks unresolved required files, prompt IDs, unsafe authority claims, and missing required readiness gates. |
| `strict` | Stable, externally shared, or automation-adjacent packages | Standard checks plus manifest/checksum coverage, stale entry warnings, and package-level evidence expectations. |

## Severity levels

| Severity | Meaning |
|---|---|
| `error` | Startup should be blocked until repaired. |
| `warning` | Startup may proceed with explicit warning/review. |
| `info` | Non-blocking advisory note. |

## Readiness decisions

| Decision | Meaning |
|---|---|
| `start_ready` | No blocking errors and no unresolved startup warnings. |
| `start_ready_with_warnings` | No blocking errors, but warnings remain. |
| `blocked` | At least one blocking error exists. |
| `not_applicable` | Startup validation does not apply to this package/profile. |

## Core check families

### Profile presence and shape

- `startup_profile_present`
- `startup_profile_schema_valid`
- `startup_profile_id_unique`
- `startup_profile_version_declared`
- `default_startup_mode_declared`
- `default_startup_mode_defined`

### Entry file resolution

- `startup_entry_files_declared`
- `required_entry_files_exist`
- `entry_file_roles_known`
- `entry_file_visibility_declared`
- `entry_file_audience_declared`
- `entry_file_paths_package_relative`

### Prompt registry linkage

- `startup_prompt_refs_resolve`
- `startup_prompt_files_exist`
- `startup_prompts_manifest_covered`
- `quick_start_prompt_visible_to_analyst`
- `hp.runtime.start.v1_available_when_runtime_mode_declared`

### Manifest and checksum coverage

- `startup_manifest_present_when_required`
- `startup_manifest_paths_resolve`
- `startup_manifest_checksums_match`
- `startup_manifest_covers_required_entries`

### Authority safety

- `startup_authority_boundary_declared`
- `startup_text_does_not_bypass_gates`
- `startup_text_does_not_claim_validation_success`
- `startup_text_does_not_override_program_contract`
- `startup_text_does_not_modify_state_without_gate`

### Readiness gates

- `startup_readiness_gates_declared`
- `required_readiness_gates_passed`
- `repair_resume_entry_declared_when_repair_mode_supported`
- `developer_entry_declared_when_maintenance_mode_supported`

## Default decision logic

```text
if any error:
  readiness_decision = blocked
elif any warning:
  readiness_decision = start_ready_with_warnings
elif profile not applicable:
  readiness_decision = not_applicable
else:
  readiness_decision = start_ready
```

## Non-goals

M66.2 does not:

- introduce a CLI command;
- change compiler behavior;
- change runtime behavior;
- add Ordo opcodes;
- regenerate compiled IR;
- assert deterministic natural-language classification of startup prompt safety.

## Human ownership rule

A startup profile can make startup discoverable and checkable. It cannot replace human review, final approval, or package-specific go/no-go gates.
