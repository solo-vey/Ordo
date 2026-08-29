# Prompt Registry Values

Status: `M65.0 value registry / docs-lint-profile design`

This registry lists conventional values for `prompt_registry`, `prompt_refs`, manifest prompt entries, and future prompt consistency reports.

## Prompt types

| Value | Meaning |
|---|---|
| `package_bootstrap` | Tiny human-to-AI prompt for starting package use in a new chat. |
| `runtime_start` | Full runtime-mode start prompt. |
| `node_helper` | Prompt that helps the AI conduct a specific node. |
| `artifact_helper` | Prompt that helps generate or review a specific artifact/template. |
| `repair_helper` | Prompt that explains gate failure, missing data, or recovery path. |
| `validation_helper` | Prompt that helps interpret validation or lint results. |
| `human_explanation` | Prompt intended to explain package behavior to an analyst. |
| `model_execution` | Prompt intended to guide model execution discipline. |

## Audience values

| Value | Meaning |
|---|---|
| `human_to_ai` | Copy-paste prompt used by a human to start or steer the AI. |
| `ai_runtime` | Guidance used by the AI during package execution. |
| `developer` | Developer-facing prompt or instruction. |
| `analyst` | Analyst-facing explanation or artifact helper. |
| `cli_operator` | Operator-facing helper for running validation/runtime commands. |

## Required values

| Value | Meaning |
|---|---|
| `true` | Required for package completeness. |
| `false` | Optional. |
| `recommended` | Recommended for package quality; missing value should warn. |
| `conditional` | Required only under declared condition/profile. |

## Lifecycle values

| Value | Meaning |
|---|---|
| `draft` | Prompt is experimental or under review. |
| `stable` | Prompt is accepted for the current package version. |
| `deprecated` | Prompt remains for compatibility but should not be used by new refs. |

## Visibility values

| Value | Meaning |
|---|---|
| `visible_to_analyst` | May be shown directly to the analyst. |
| `model_internal` | Intended for model execution guidance; do not show by default. |
| `expose_on_request` | Can be shown when the analyst asks for prompt details. |

## Prompt ref `use` values

| Value | Meaning |
|---|---|
| `before_question` | Helps introduce the node before asking the main question. |
| `during_clarification` | Helps answer clarification without changing state. |
| `after_answer` | Helps summarize and confirm the result after a user answer. |
| `on_gate_fail` | Helps explain blocker and repair path. |
| `on_backtrack` | Helps explain invalidation/review consequences. |
| `artifact_generation` | Helps generate an artifact from confirmed state. |
| `validation_review` | Helps interpret validation result or finding. |

## Validation policy values

| Value | Meaning |
|---|---|
| `required_file_only` | Validate that referenced prompt path exists. |
| `required_file_and_readme_reference` | Validate path and README/START_HERE reference. |
| `resolve_node_and_file` | Validate path and attached node id. |
| `resolve_artifact_and_file` | Validate path and attached artifact/template id. |
| `manifest_checksum_required` | Validate path, manifest entry, and checksum. |
| `authority_safe_text_review` | Human/lint review that prompt does not override gates/state. |

## Conventional checks

| Check id | Target | Intent |
|---|---|---|
| `prompt_registry_present` | `prompt_registry` | Package declares prompt registry when prompt files are part of the package contract. |
| `prompt_ids_unique` | `prompt_registry.prompts` | Prompt ids are stable and unique. |
| `prompt_paths_exist` | `prompt_registry.prompts[*].path` | Each declared prompt path exists in the package. |
| `prompt_refs_resolve` | `nodes[*].prompt_refs` and other refs | Each prompt ref points to a registry entry. |
| `node_prompt_refs_target_existing_nodes` | `attached_to.node_id` | Node helper prompts attach only to existing nodes. |
| `prompt_visibility_declared` | `prompt_registry.prompts[*].visibility` | Visibility is explicit or inherited by rule. |
| `prompt_language_declared_or_inherited` | `language`, `default_language` | Prompt language is explicit or inherited. |
| `prompt_authority_safe` | prompt text / metadata | Helper prompt does not override gates, routing, state, or validation authority. |
| `state_change_policy_consistent` | `state_change_allowed` + ref use | Non-state-changing prompts are not used as state-changing instructions. |
| `quick_start_discoverable` | README / START_HERE | Bootstrap prompt is linked from user-facing entry points. |
| `prompt_manifest_coverage` | `MANIFEST.json` | Prompt files are listed and, where required, hashed. |

## Finding fields

```yaml
severity: warning
check: prompt_refs_resolve
target: nodes.B5_N3.prompt_refs[0]
message: prompt_id 'B5_N3_comparison_rule_helper' is referenced but not declared in prompt_registry
owner_action: add registry entry, remove reference, or mark inherited package prompt
```

## Authority rule

Prompt registry values are lint/review conventions. They do not override program contracts, gates, transitions, state requirements, runtime evidence, or human approval ownership.

## M65.3 lint profile values

| Value | Meaning |
|---|---|
| `light` | Early draft profile; blocks only basic structural failures. |
| `standard` | Normal package acceptance profile. |
| `strict` | Release/publication profile with stronger manifest, discoverability, and stale-ref checks. |

## M65.3 lint severity values

| Value | Meaning |
|---|---|
| `error` | Blocks approval under the selected profile. |
| `warning` | Requires reviewer attention or accepted rationale; may block under `strict`. |
| `info` | Non-blocking observation. |

## M65.3 prompt registry approval decisions

| Value | Meaning |
|---|---|
| `approved` | No blocking findings. |
| `approved_with_warnings` | Warnings remain but are accepted. |
| `blocked` | Blocking findings remain. |
| `not_applicable` | Prompt registry validation does not apply to the package. |
