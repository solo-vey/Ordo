# Program-level Approval Profile

Status: `M64.3 accepted-docs-lint-profile-design`

This document defines the profile behavior for the program-level approval gate.

Profiles are review/lint modes. They do not change runtime semantics.

```text
light    → advisory checks for early/draft packages
standard → expected checks for standard applied modules and reusable process packages
strict   → hardened checks for release-candidate/stable packages or deterministic validator-backed workflows
```

## Profile selection

A package can select a profile in one of three ways:

1. `program_level_approval_gate.profile` if the M64.3 block is present;
2. `program_contract.control_level` as a fallback;
3. reviewer/tool default, usually `standard`, if neither is declared.

Recommended fallback mapping:

| Source value | Approval profile |
|---|---|
| `control_level: light` | `light` |
| `control_level: standard` | `standard` |
| `control_level: strict` | `strict` |
| missing control level | `standard` for reusable packages, `light` for examples |

## Light profile

Use for early drafts, examples, exploratory packages, and documents that are not yet release candidates.

### Expected behavior

- Missing M64 blocks usually produce warnings, not errors.
- Legacy packages are not blocked simply because they do not yet declare all M64 conventions.
- Warnings should still identify what is missing before the package can move toward standard or strict mode.

### Typical light checks

```text
program_contract_identity_present: warning if missing
runtime_profile_declared: warning if missing
interaction_roles_consistent: warning if inconsistent
process_rail_resume_policy_consistent: warning if deviations are enabled without resume policy
conversation_input_classes_routed: warning if routing rules are incomplete
```

## Standard profile

Use for standard applied modules, reusable process packages, and release-candidate documentation packages.

### Expected behavior

- `program_contract` identity and runtime profile are required.
- Human final approval must be declared for release/package handoff decisions.
- If AI and CLI roles are declared, their authority must be consistent with validation/review points.
- If deviation/backtracking is allowed, resume/invalidation policy must be declared.
- Declared conversation input classes must have routing rules or documented defaults.

### Typical standard checks

```text
program_contract_identity_present: error if missing
module_id_present_for_reusable_package: error if missing
runtime_profile_declared: error if missing
human_final_approval_declared: error if missing for release/stable packages
required_validation_commands_declared: warning if incomplete
interaction_roles_consistent: error if contradictory
process_rail_resume_policy_consistent: warning or error depending on deviation policy
conversation_input_classes_routed: warning if incomplete
unmatched_input_policy_safe: error if ambiguous state-changing default exists
```

## Strict profile

Use for stable packages, high-control guided processes, AI-runtime-facing packages, and packages that claim deterministic validator-backed behavior.

### Expected behavior

- All top-level M64 blocks are expected unless a documented exception exists.
- Missing routing rules, missing resume policy, or unsafe decision authority are blocking errors.
- Raw tool output policy must be compatible with human-facing execution.
- Every declared review point should be mapped to a gate/check/report artifact or explicit human approval point.
- Package-local enum values require documentation.

### Typical strict checks

```text
program_contract_identity_present: error
runtime_profile_declared: error
required_review_points_declared: error
required_validation_commands_declared: error
interaction_roles_consistent: error
human_final_approval_declared: error
raw_tool_output_policy_safe: error
process_rail_resume_policy_consistent: error
backtracking_invalidation_policy_present: error when backtracking is enabled/restricted
conversation_input_classes_routed: error
unmatched_input_policy_safe: error
profile_local_values_documented: error or warning by owner policy
```

## Non-goals

M64.3 approval profiles do not:

- execute the package;
- classify natural language deterministically;
- mutate state;
- replace `go-no-go` or artifact validation;
- add CLI commands;
- promote any M64.1/M64.2 block into runtime-core semantics.

## Reviewer rule

When a finding depends on package intent, do not silently downgrade it. Mark it as `needs_owner_review` or keep it as a warning/error under the selected profile.
