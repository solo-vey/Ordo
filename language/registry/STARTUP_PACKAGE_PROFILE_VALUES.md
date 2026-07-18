# Startup Package Profile Values

**Milestone:** M66.0

## Startup modes

| Value | Meaning |
|---|---|
| `analyst_quick_start` | Minimal copy-paste start for a human analyst |
| `analyst_runtime_mode` | Full guided runtime-mode entry |
| `developer_maintenance` | Developer/maintainer startup path |
| `cli_operator` | CLI/helper startup path |
| `review_only` | Read-only package review |
| `repair_resume` | Resume after failed or interrupted startup |

## Audiences

| Value | Meaning |
|---|---|
| `analyst` | Normal human analyst/user |
| `developer` | Package maintainer or author |
| `cli_operator` | Human or AI using CLI/helper tools |
| `reviewer` | Read-only reviewer |
| `ai_runtime` | AI execution layer |

## Entry file roles

| Value | Meaning |
|---|---|
| `readme` | General package overview |
| `start_here` | Minimal guided starting instructions |
| `hp.package.quick_start.v1` | Tiny copy-paste prompt |
| `hp.runtime.start.v1` | Full runtime-mode startup prompt |
| `developer_start_prompt` | Developer-maintainer prompt |
| `cli_start` | CLI startup instruction file |
| `validation_profile` | Start-readiness validation profile |
| `manifest` | File/package manifest |
| `lockfile` | Version/compiled/runtime expectation lockfile |

## Requiredness values

| Value | Meaning |
|---|---|
| `true` | Required |
| `false` | Not required |
| `recommended` | Recommended but not blocking in standard profile |
| `conditional` | Required only when declared condition applies |

## Visibility values

| Value | Meaning |
|---|---|
| `visible_to_analyst` | Safe and intended for normal analyst use |
| `developer` | Developer/maintainer material |
| `cli_operator` | CLI/operator material |
| `model_internal` | Model-facing support material |
| `expose_on_request` | Not primary surface, but may be shown if requested |

## Readiness decisions

| Value | Meaning |
|---|---|
| `start_ready` | Startup profile and required startup files are valid |
| `start_ready_with_warnings` | Start may proceed, but warnings should be reviewed |
| `blocked` | Startup should not proceed until errors are repaired |
| `not_applicable` | Startup profile does not apply to this package/profile |


## M66.2 startup validation profiles

| Value | Meaning |
|---|---|
| `light` | Draft/example startup validation profile. |
| `standard` | Default reusable-package startup validation profile. |
| `strict` | Stable or externally shared startup validation profile. |

## M66.2 startup validation severity values

| Value | Meaning |
|---|---|
| `error` | Blocking startup validation issue. |
| `warning` | Non-blocking issue requiring review. |
| `info` | Advisory startup validation note. |

## M66.2 conventional startup validation checks

- `startup_profile_present`
- `startup_profile_schema_valid`
- `startup_profile_id_unique`
- `startup_profile_version_declared`
- `default_startup_mode_declared`
- `default_startup_mode_defined`
- `startup_entry_files_declared`
- `required_entry_files_exist`
- `entry_file_roles_known`
- `entry_file_visibility_declared`
- `entry_file_audience_declared`
- `entry_file_paths_package_relative`
- `startup_prompt_refs_resolve`
- `startup_prompt_files_exist`
- `startup_prompts_manifest_covered`
- `quick_start_prompt_visible_to_analyst`
- `hp.runtime.start.v1_available_when_runtime_mode_declared`
- `startup_manifest_present_when_required`
- `startup_manifest_paths_resolve`
- `startup_manifest_checksums_match`
- `startup_manifest_covers_required_entries`
- `startup_authority_boundary_declared`
- `startup_text_does_not_bypass_gates`
- `startup_text_does_not_claim_validation_success`
- `startup_text_does_not_override_program_contract`
- `startup_text_does_not_modify_state_without_gate`
- `startup_readiness_gates_declared`
- `required_readiness_gates_passed`
- `repair_resume_entry_declared_when_repair_mode_supported`
- `developer_entry_declared_when_maintenance_mode_supported`
