# Prompt Registry Validation Profile — History Event Factory

Status: `M65.1 planned-validation-profile`

## Hard checks

| Check | Expected result |
|---|---|
| `prompt_registry_present` | top-level registry exists before prompt files become part of package contract |
| `prompt_ids_unique` | no duplicate `prompt_id` |
| `required_prompt_paths_exist` | every required prompt path exists |
| `node_prompt_refs_resolve` | every node `prompt_ref` points to a registry entry |
| `node_prompt_refs_target_existing_nodes` | every node helper attaches to a current node id or declared compatibility alias |
| `quick_start_discoverable` | README or START_HERE links to `prompts/hp.package.quick_start.v1.md` |
| `prompt_manifest_coverage` | every prompt file is in manifest/checksum list |
| `prompt_authority_safe` | prompt text does not override gates, routing, state, approvals, or validation evidence |
| `state_change_policy_consistent` | prompts with `state_change_allowed: false` are not used as state-changing instructions |
| `runtime_start_protocol_not_weakened` | prompt files do not weaken the embedded CLI / Runtime Mode protocol |

## Warning checks

| Check | Meaning |
|---|---|
| `complex_node_without_helper_prompt` | major conversational nodes lack helper prompts |
| `prompt_file_unreferenced` | prompt file exists but no registry/ref uses it |
| `duplicated_prompt_content` | many node prompts duplicate the same text |
| `stable_prompt_references_deprecated_target` | stable prompt references a deprecated node/artifact id |
| `legacy_proposal_node_alias_unresolved` | proposed APF ids such as `B5_N3` are used without current mapping |

## Suggested finding format

```yaml
severity: error
check: node_prompt_refs_resolve
target: nodes.N_PATH_SELECT.prompt_refs[0]
message: prompt_id hp.source_type.clarification.v1 is referenced but not declared in prompt_registry
owner_action: add registry entry, remove prompt_ref, or mark prompt inherited from package-level registry
```

## Readiness statuses

```text
passed
passed_with_warnings
blocked
not_applicable
```

`passed_with_warnings` is allowed only if missing prompts are recommended, not required, and runtime/start protocol remains safe.
