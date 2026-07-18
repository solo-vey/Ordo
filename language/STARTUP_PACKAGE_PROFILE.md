# Startup Package Profile

**Milestone:** M66.0  
**Status:** schema/documentation convention  
**Top-level key:** `startup_package_profile`

## Definition

`startup_package_profile` is a top-level package/source convention that declares how a package should be started by different audiences and startup modes.

It is a package entry contract, not runtime execution logic.

## Suggested top-level structure

```yaml
startup_package_profile:
  profile_id: history_event_factory_startup_profile
  version: "0.1"
  package_id: history_event_guided_intake
  default_startup_mode: analyst_quick_start
  default_language: uk
  startup_root: ./

  startup_modes:
    - mode: analyst_quick_start
      audience: analyst
      entry_file: prompts/QUICK_START_PROMPT.md
      prompt_id: hp.package.quick_start.v1
      required: true
      visibility: visible_to_analyst

    - mode: analyst_runtime_mode
      audience: analyst
      entry_file: START_PROMPT_RUNTIME_MODE.md
      prompt_id: hp.runtime.start.v1
      required: true
      visibility: visible_to_analyst

    - mode: developer_maintenance
      audience: developer
      entry_file: START_PROMPT_DEVELOPER_MODE.md
      required: recommended
      visibility: developer

  entry_files:
    - path: README.md
      role: readme
      required: true
    - path: START_HERE_RUNTIME_MODE.md
      role: start_here
      required: true
    - path: START_PROMPT_RUNTIME_MODE.md
      role: hp.runtime.start.v1
      required: true

  readiness_gates:
    - check_id: startup_entry_files_exist
      severity: error
    - check_id: startup_prompt_refs_resolve
      severity: error
    - check_id: quick_start_discoverable_from_readme
      severity: warning
    - check_id: startup_manifest_coverage
      severity: warning

  authority_boundary:
    startup_files_may_override_gates: false
    startup_files_may_confirm_state: false
    startup_files_may_claim_validation_success: false
```

## Recommended fields

| Field | Meaning |
|---|---|
| `profile_id` | Stable startup profile identifier |
| `version` | Profile version |
| `package_id` | Package this profile describes |
| `default_startup_mode` | Recommended startup path |
| `default_language` | Default language for human-facing startup files |
| `startup_root` | Package-relative root for startup files |
| `startup_modes` | Supported startup paths |
| `entry_files` | Required/recommended start files |
| `readiness_gates` | Checks required before start-readiness is claimed |
| `authority_boundary` | Explicit limits on what startup files can do |

## Startup mode fields

| Field | Meaning |
|---|---|
| `mode` | Startup mode identifier |
| `audience` | Intended audience: analyst, developer, cli_operator, reviewer |
| `entry_file` | Package-relative entry file |
| `prompt_id` | Optional reference into `prompt_registry` |
| `required` | true / false / recommended / conditional |
| `visibility` | visible_to_analyst / developer / cli_operator / model_internal |
| `state_change_allowed` | Whether this startup mode may begin state mutation directly |
| `resume_supported` | Whether mode supports repair/resume |

## Required checks

For `standard` profile behavior, a startup package profile should check:

- profile exists where package requires guided startup;
- default startup mode exists;
- all required entry files exist;
- prompt IDs referenced by startup modes resolve in `prompt_registry`;
- quick-start prompt is discoverable from README or START_HERE when present;
- runtime start prompt is not confused with quick-start prompt;
- authority boundary is explicit;
- manifest/lockfile coverage is declared where package has manifest/lockfile;
- startup profile does not claim runtime validation success without evidence.

## Warning checks

- package has multiple start prompts but no default mode;
- analyst-facing package has no quick-start prompt;
- developer bundle has no developer start prompt;
- startup file exists but is not declared;
- declared startup mode is not mentioned in README/START_HERE;
- quick-start prompt is too long for copy-paste startup;
- startup file contains YAML/tool instructions even though it is analyst-facing and marked simple.

## Authority boundary

Startup profile entries may guide startup sequence and explain which file to use. They must not:

- bypass gates;
- change routing;
- silently mutate confirmed state;
- override `program_contract`;
- override prompt registry state-change policy;
- claim CLI/runtime validation passed without evidence;
- replace package validation or approval gates.

## Compatibility

`startup_package_profile` is compatible with M64 and M65 conventions. It may be adopted gradually by standard applied modules and package factories.
