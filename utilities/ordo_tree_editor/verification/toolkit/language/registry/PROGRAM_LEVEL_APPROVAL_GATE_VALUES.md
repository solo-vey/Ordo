# Program-level Approval Gate Values

Status: `M64.3 value registry / docs-lint-profile design`

This registry lists conventional values for `program_level_approval_gate` and future lint/profile reports.

## Profiles

| Value | Meaning |
|---|---|
| `light` | Advisory checks for drafts, examples, and exploratory packages. |
| `standard` | Default checks for reusable process packages and standard applied modules. |
| `strict` | Hardened checks for release-candidate/stable or validator-backed guided processes. |

## Severity values

| Value | Meaning |
|---|---|
| `error` | Blocks approval under the selected profile. |
| `warning` | Must remain visible for review but does not necessarily block approval. |
| `info` | Non-blocking contextual note. |

## Approval decisions

| Value | Meaning |
|---|---|
| `approved` | Checks passed with no blocking findings. |
| `approved_with_warnings` | No errors, but warnings remain visible. |
| `blocked` | At least one profile-blocking error exists. |
| `not_applicable` | Gate does not apply to this package/artifact. |

## Conventional checks

| Check id | Target | Intent |
|---|---|---|
| `program_contract_identity_present` | `program_contract` | `program_id` and required identity fields exist. |
| `module_id_present_for_reusable_package` | `program_contract` | reusable packages declare `module_id`. |
| `runtime_profile_declared` | `program_contract` | human/AI/CLI layers are declared. |
| `required_review_points_declared` | `program_contract` | package review/approval points are listed. |
| `required_validation_commands_declared` | `program_contract` | expected validation commands/checks are listed when CLI role is claimed. |
| `interaction_roles_consistent` | `interaction_model` | human/AI/CLI roles do not contradict runtime profile. |
| `human_final_approval_declared` | `interaction_model` | final release/package decision belongs to human or shared authority. |
| `raw_tool_output_policy_safe` | `interaction_model` | raw tool output policy is compatible with analyst-facing execution. |
| `process_rail_resume_policy_consistent` | `process_rail` | deviations/backtracking have resume policy. |
| `backtracking_invalidation_policy_present` | `process_rail` | backtracking declares downstream invalidation/review behavior. |
| `conversation_input_classes_routed` | `conversation_semantics` | every declared input class has a routing rule or documented default. |
| `unmatched_input_policy_safe` | `conversation_semantics` | unmatched input cannot silently change state. |
| `profile_local_values_documented` | all M64 blocks | package-local enum/convention values are explained. |

## Conventional finding fields

```yaml
severity: warning
check: conversation_input_classes_routed
target: conversation_semantics.routing_rules
message: input class 'approval' is declared but no routing action is defined
owner_action: add routing rule, remove input class, or document inherited default
```

## Decision defaults

```text
any error      → blocked
no errors + warnings → approved_with_warnings
no findings or only info → approved
explicit out-of-scope → not_applicable
```

## Authority rule

Values in this registry are lint/review conventions. They do not override program-level contracts, gates, state requirements, runtime evidence, or human approval ownership.
