# Template — Applied Project Output Template Catalog

## Role

Defines how the factory captures output templates for a generated applied Ordo project.

## Required fields per output artifact

```text
artifact_id
filename_pattern
artifact_role
terminal_paths
required_sections
data_sources
validation_checks
owner_review_status
future_runtime_profile_inclusion
free_dialogue_source_fields
self_hosted_reuse_status
```

## Required coverage rule

Every output artifact named in `output_artifact_catalog` must have one template entry in `output_template_catalog`, unless it is explicitly marked `deferred` for M61.1.

## Allowed owner review statuses

```text
proposed-template
accepted-template
needs-owner-review
deferred
```

## M61.1 note

Templates are collected immediately, but only `source/program.ordo.yaml` is produced as the first release output.


## M61.5 note

When a template is discovered through free dialogue, its source must be traceable to structured extraction fields:

```text
free_dialogue_raw_notes → candidate_outputs / candidate_templates → approved decision-tree terminal path → output_template_catalog
```

<!-- APF alpha.21 full-validation contract coverage appendix -->

## APF alpha.21 full-validation contract coverage appendix

This appendix records confirmed contract fields for deterministic artifact coverage validation. It is a technical release-readiness section and does not change the user-facing APF process logic.

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
