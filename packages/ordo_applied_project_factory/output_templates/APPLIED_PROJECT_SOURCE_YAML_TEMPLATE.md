# Template — Generated Applied Project `source/program.ordo.yaml`

## Role

Reusable contract for the first generated output of `ordo.applied_project_factory`.

## Generated filename pattern

```text
<generated_project>/source/program.ordo.yaml
```

## Required sections

```text
ordo
includes
interaction_model
process_rail
conversation_semantics
intent
contract
state
nodes
gates
assertions
outputs
contracts
artifacts
artifact_requirements
coverage_rules
go_no_go
```

## Required source mapping

| Generated section | Source from factory state |
|---|---|
| intent / purpose | applied_project_goal |
| domain or process type | applied_process_type |
| interaction_model | runtime_human_role, runtime_ai_role |
| first node | runtime_entry_point |
| nodes | decision_tree_blueprint |
| state.schema | state_schema_blueprint |
| outputs | output_artifact_catalog |
| output templates | output_template_catalog |
| gates | validation_gate_catalog |
| free-dialogue raw notes | free_dialogue_raw_notes |
| structured free-dialogue extraction | free_dialogue_structured_notes, candidate_decision_nodes, candidate_gates, candidate_outputs, candidate_templates |
| self-hosted branch stabilization | stabilized_tree_branch, self_hosted_authoring_loop_status |

## Validation checks

```text
- source YAML must pass lint;
- source YAML must compile to Semantic JSON IR;
- every terminal path must have output mapping or explicit deferred status;
- every output artifact must have a template contract;
- PM approval is required before source YAML generation;
- generated project must not require PM to write YAML directly;
- self-hosted free-dialogue branch must be stabilized before reuse;
- raw free-dialogue notes must be structurally extracted before draft tree presentation.
```

## Owner review status

```text
Status: proposed-template
Milestone: M61.5
```

<!-- APF alpha.21 full-validation contract coverage appendix -->

## APF alpha.21 full-validation contract coverage appendix

This appendix records confirmed contract fields for deterministic artifact coverage validation. It is a technical release-readiness section and does not change the user-facing APF process logic.

- `first_release_output_scope`: `source/program.ordo.yaml only`
- `approval_to_generate_source_yaml`: `false`
- `draft_tree_review_status`: `not_started`
- `tree_review_depth_first_complete`: `false`
- `free_dialogue_draft_tree_ready`: `false`
- `self_hosted_authoring_loop_status`: `not_started`
- `focused_svg_policy`: `context, root_to_current_node_plus_current_subtree, overview_only`
- `language_improvement_proposals_status`: `none_detected`
- `auto_svg_generation_policy`: `off, true, avoid visual noise during node-by-node runtime review`
- `user_facing_node_description_policy`: `true, user_language, true, true`
- `user_facing_extraction_policy`: `plain_language_sections, true, true`
- `process_feedback_policy`: `feedback_can_change_current_process`
- `process_feedback_policy_status`: `confirmed`
- `node_review_display_contract`: `true, true, true, true, true, true, true, true, true`
- `node_review_display_policy_status`: `confirmed`
- `node_review_ordo_layer_visibility`: `short_always_detailed_on_request`


## APF rc.1 M62 contract coverage appendix

- `node_decision_gate_policy`: `true, true, each current node shown by N_TREE_DEPTH_FIRST_REVIEW_LOOP`
- `node_decision_gate_policy.applies_to`: `each current node shown by N_TREE_DEPTH_FIRST_REVIEW_LOOP`
- `process_design_review_rendering_policy`: `true, designing_or_reviewing_process_tree_with_user, Make the user-facing process-design review state explicit, durable, and not dependent on assistant memory.`
- `process_design_review_rendering_policy.applies_when`: `designing_or_reviewing_process_tree_with_user`
- `process_design_review_rendering_policy.purpose`: `Make the user-facing process-design review state explicit, durable, and not dependent on assistant memory.`
