# Appendix F. Practical YAML and Schema Reference

This appendix is generated from the current machine-readable schemas. It explains field types, enumerations, required fields, and descriptions without treating prose as a substitute for validation.

## F.1 Reading field types

- **enum**: choose only one of the listed values.
- **reference/id**: the referenced object must exist and satisfy provenance rules.
- **path**: the path must stay inside the allowed package or output root.
- **free text**: human-readable guidance; it must not be used as an implicit deterministic condition.
- **object/array**: validate nested members against the referenced schema.

## F.2 Ordo ANTIPATTERN.DEF

Canonical schema: `language/schemas/antipattern_def.schema.json`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `schema_version` | unspecified | yes |  |
| `id` | string | yes |  |
| `name` | string | yes |  |
| `summary` | string | yes |  |
| `severity` | unspecified; enum | yes | `info`, `warning`, `error`, `critical` |
| `enforcement` | unspecified; enum | yes | `advisory`, `blocking` |
| `scope` | array | yes |  |
| `symptoms` | array | yes |  |
| `detection` | object | yes |  |
| `recovery` | object | yes |  |
| `remediation` | object | yes |  |
| `evidence` | object | yes |  |
| `tags` | array | no |  |
| `version` | string | no |  |
| `status` | unspecified; enum | no | `draft`, `active`, `deprecated` |
| `classification_level` | unspecified; enum | no | `fundamental`, `subpattern`, `detector_case` |
| `fundamental_id` | string | no |  |
| `generalization_note` | string | no |  |

## F.3 Ordo anti-pattern evidence reference

Canonical schema: `language/schemas/antipattern_evidence_ref.schema.json`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `schema_version` | unspecified | yes |  |
| `evidence_type` | unspecified | yes |  |
| `evidence_id` | string | yes |  |
| `hook_id` | string | yes |  |
| `source_id` | string | yes |  |
| `gate_id` | string / null | no |  |
| `context_type` | unspecified; enum | yes | `conversation`, `process_trace`, `repository_state`, `package_state`, `evidence_state`, `runtime_state` |
| `decision` | unspecified; enum | yes | `allow`, `allow_with_advisory`, `block`, `inconclusive` |
| `finding_ids` | array | yes |  |
| `report_digest` | string | yes |  |
| `recorded_at` | string | yes |  |

## F.4 Ordo ANTIPATTERN.FINDING

Canonical schema: `language/schemas/antipattern_finding.schema.json`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `schema_version` | unspecified | yes |  |
| `finding_type` | unspecified | yes |  |
| `finding_id` | string | yes |  |
| `rule_id` | string | yes |  |
| `antipattern_id` | string | yes |  |
| `matched` | boolean | yes |  |
| `severity` | unspecified; enum | yes | `info`, `warning`, `error`, `critical` |
| `enforcement` | unspecified; enum | yes | `advisory`, `blocking` |
| `decision` | unspecified; enum | yes | `allow`, `allow_with_advisory`, `block`, `inconclusive` |
| `message` | string | yes |  |
| `evidence` | array | yes |  |
| `recovery` | object | yes |  |
| `remediation` | object | yes |  |
| `source` | object | yes |  |
| `timestamps` | object | yes |  |
| `resolution` | object | no |  |

## F.5 Ordo anti-pattern gate report

Canonical schema: `language/schemas/antipattern_gate_report.schema.json`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `schema_version` | unspecified | yes |  |
| `report_type` | unspecified | yes |  |
| `decision` | unspecified; enum | yes | `allow`, `allow_with_advisory`, `block`, `inconclusive` |
| `summary` | object | yes |  |
| `blocking_finding_ids` | array | yes |  |
| `advisory_finding_ids` | array | yes |  |
| `findings` | array | yes |  |
| `gate_id` | string | yes |  |
| `context_type` | unspecified; enum | yes | `conversation`, `process_trace`, `repository_state`, `package_state`, `evidence_state`, `runtime_state` |
| `source_id` | string | yes |  |
| `enabled_antipatterns` | array | no |  |
| `runtime_error` | string | no |  |
| `inconclusive_escalated_to_block` | boolean | no |  |

## F.6 Ordo Anti-pattern Severity and Enforcement Policy

Canonical schema: `language/schemas/antipattern_policy.schema.json`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `schema_version` | unspecified | yes |  |
| `policy_version` | string | yes |  |
| `severity_order` | array | yes |  |
| `decision_matrix` | object | yes |  |
| `critical_must_block` | unspecified | no |  |
| `error_default_enforcement` | unspecified; enum | no | `advisory`, `blocking` |
| `warning_default_enforcement` | unspecified | no |  |
| `info_default_enforcement` | unspecified | no |  |

## F.7 Ordo anti-pattern wiring hook

Canonical schema: `language/schemas/antipattern_wiring_hook.schema.json`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `schema_version` | unspecified | yes |  |
| `hook_id` | string | yes |  |
| `phase` | unspecified; enum | yes | `before_node_execution`, `after_state_update_before_transition`, `before_repository_mutation`, `before_package_finalization`, `before_final_status_claim` |
| `adapter` | object | yes |  |
| `context_type` | unspecified; enum | yes | `conversation`, `process_trace`, `repository_state`, `package_state`, `evidence_state`, `runtime_state` |
| `source_id` | string | yes | Stable node, transition, gate, package, evidence, or repository mutation identifier. |
| `input` | object | yes |  |
| `output` | object | yes |  |
| `decision_policy` | object | yes |  |
| `routing` | object | yes |  |
| `enabled_antipattern_overrides` | array | no |  |

## F.8 ARF Control Model Contract

Canonical schema: `language/schemas/arf_control_model_contract.schema.json`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `schema_version` | unspecified | yes |  |
| `contract_id` | string | yes |  |
| `default_control_profile` | unspecified | yes |  |
| `decision_model` | unspecified | yes |  |
| `default_role` | unspecified | yes |  |
| `undefined_action` | unspecified | yes |  |
| `modes` | object | yes |  |
| `mode_switching` | object | yes |  |
| `ambiguity_policy` | object | yes |  |
| `transition_policy` | object | yes |  |
| `node_contract_profiles` | object | yes |  |

## F.9 ARF Node Contract Profiles

Canonical schema: `language/schemas/arf_node_contract.schema.json`

This schema does not expose top-level `properties`; inspect its composition (`allOf`, `oneOf`, or referenced definitions) with the validator.

## F.10 Artifact Requirement Schema

Canonical schema: `language/schemas/artifact_requirement_schema.yaml`

This schema does not expose top-level `properties`; inspect its composition (`allOf`, `oneOf`, or referenced definitions) with the validator.

## F.11 Artifact Schema

Canonical schema: `language/schemas/artifact_schema.yaml`

This schema does not expose top-level `properties`; inspect its composition (`allOf`, `oneOf`, or referenced definitions) with the validator.

## F.12 Assertion Schema

Canonical schema: `language/schemas/assertion_schema.yaml`

This schema does not expose top-level `properties`; inspect its composition (`allOf`, `oneOf`, or referenced definitions) with the validator.

## F.13 Ordo Capability Maturity

Canonical schema: `language/schemas/capability_maturity.schema.json`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `specification` | unspecified | yes |  |
| `schema_support` | unspecified | yes |  |
| `toolchain_support` | unspecified | yes |  |
| `runtime_enforcement` | unspecified | yes |  |
| `model_benchmark` | unspecified | yes |  |
| `production_recommendation` | unspecified | yes |  |

## F.14 Ci Release Clean Gate Policy Schema

Canonical schema: `language/schemas/ci_release_clean_gate_policy_schema.yaml`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `ci_release_clean_gates` | object | yes |  |

## F.15 Ordo Clean Package Gate Schema

Canonical schema: `language/schemas/clean_package_gate_schema.yaml`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `clean_package_gate` | object | yes |  |

## F.16 Contract Schema

Canonical schema: `language/schemas/contract_schema.yaml`

This schema does not expose top-level `properties`; inspect its composition (`allOf`, `oneOf`, or referenced definitions) with the validator.

## F.17 Ordo Conversation Scope Guard Source Declaration

Canonical schema: `language/schemas/conversation_scope_guard_source.schema.json`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `supported` | boolean | yes |  |
| `enabled` | boolean | yes |  |
| `mode` | unspecified; enum | no | `advisory`, `guided_redirect`, `strict_redirect`, `locked_process` |
| `state_change_on_out_of_scope` | unspecified | no |  |
| `scope` | object / array / string | no |  |
| `out_of_scope_behavior` | object / string | no |  |
| `escalation` | object | no |  |
| `trace` | object | no |  |

## F.18 Conversation Semantics Schema

Canonical schema: `language/schemas/conversation_semantics_schema.yaml`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `input_classes` | array | no |  |
| `routing_rules` | object | no |  |
| `unmatched_input_policy` | string; enum | no | `clarify_before_state_change`, `reject`, `log_and_continue`, `route_to_human_review` |
| `clarification_policy` | string | no |  |
| `resume_policy` | string | no |  |

## F.19 Coverage Rule Schema

Canonical schema: `language/schemas/coverage_rule_schema.yaml`

This schema does not expose top-level `properties`; inspect its composition (`allOf`, `oneOf`, or referenced definitions) with the validator.

## F.20 Ordo CSG Package Binding

Canonical schema: `language/schemas/csg_package_binding.schema.json`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `supported` | boolean | yes |  |
| `enabled` | boolean | yes |  |
| `decision_status` | unspecified; enum | yes | `confirmed_enabled`, `confirmed_not_required` |
| `contract` | string | no |  |
| `policy` | string | no |  |
| `tests` | string | no |  |
| `trace_events` | string | no |  |

## F.21 Ordo Delta Backlog Schema

Canonical schema: `language/schemas/delta_backlog_schema.yaml`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `delta_backlog` | object | yes |  |

## F.22 Ordo Derived Artifact Sync Schema

Canonical schema: `language/schemas/derived_artifact_sync_schema.yaml`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `artifact_sync` | object | yes |  |

## F.23 Ordo Derived Artifact Sync Validation Profile Schema

Canonical schema: `language/schemas/derived_artifact_sync_validation_profile_schema.yaml`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `derived_artifact_sync_validation_profile` | object | yes |  |

## F.24 Ordo DETECT.RULE

Canonical schema: `language/schemas/detect_rule.schema.json`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `schema_version` | unspecified | yes |  |
| `id` | string | yes |  |
| `antipattern_id` | string | yes |  |
| `name` | string | yes |  |
| `description` | string | yes |  |
| `input_contract` | object | yes |  |
| `condition` | object | yes |  |
| `output_contract` | object | yes |  |
| `evaluation` | object | yes |  |
| `version` | string | no |  |
| `status` | unspecified; enum | no | `draft`, `active`, `deprecated` |
| `tags` | array | no |  |

## F.25 Ordo Deviation Classification Record

Canonical schema: `language/schemas/deviation_classification.schema.json`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `op` | unspecified | yes |  |
| `message_ref` | string | yes |  |
| `active_node_ref` | string / null | yes |  |
| `active_question_ref` | string / null | no |  |
| `classification` | unspecified; enum | yes | `answer_to_active_question`, `clarification`, `correction`, `backtrack_request`, `requirement_change`, `pause_request`, `resume_request`, `exit_request`, `process_meta_question`, `related_context`, `unrelated_topic`, `unsafe_or_emergency_message`, `unclassifiable_input` |
| `confidence` | unspecified; enum | no | `confirmed`, `high`, `medium`, `low`, `unknown` |
| `matched_scope_evidence` | array | no |  |
| `classification_reason` | string | no |  |
| `state_mutation_allowed` | boolean | yes |  |
| `action` | unspecified; enum | yes | `accept_answer`, `clarify_active_step`, `apply_correction`, `backtrack`, `reopen_contract`, `pause_process`, `resume_process`, `exit_process`, `answer_process_meta`, `register_related_context`, `redirect`, `bypass_for_safety`, `request_classification_clarification` |
| `trace_required` | boolean | no |  |

## F.26 Execution Trace Schema

Canonical schema: `language/schemas/execution_trace_schema.yaml`

This schema does not expose top-level `properties`; inspect its composition (`allOf`, `oneOf`, or referenced definitions) with the validator.

## F.27 Flow Join Schema

Canonical schema: `language/schemas/flow_join_schema.yaml`

This schema does not expose top-level `properties`; inspect its composition (`allOf`, `oneOf`, or referenced definitions) with the validator.

## F.28 Freeform Schema

Canonical schema: `language/schemas/freeform_schema.yaml`

This schema does not expose top-level `properties`; inspect its composition (`allOf`, `oneOf`, or referenced definitions) with the validator.

## F.29 Gate Schema

Canonical schema: `language/schemas/gate_schema.yaml`

This schema does not expose top-level `properties`; inspect its composition (`allOf`, `oneOf`, or referenced definitions) with the validator.

## F.30 Go No Go Schema

Canonical schema: `language/schemas/go_no_go_schema.yaml`

This schema does not expose top-level `properties`; inspect its composition (`allOf`, `oneOf`, or referenced definitions) with the validator.

## F.31 Improvement Record Schema

Canonical schema: `language/schemas/improvement_record_schema.yaml`

This schema does not expose top-level `properties`; inspect its composition (`allOf`, `oneOf`, or referenced definitions) with the validator.

## F.32 Interaction Model Schema

Canonical schema: `language/schemas/interaction_model_schema.yaml`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `human_role` | string | no |  |
| `ai_role` | string | no |  |
| `cli_role` | string | no |  |
| `raw_tool_output_policy` | string; enum | no | `summarize_before_user`, `show_on_request`, `show_full`, `never_show_raw` |
| `decision_authority` | object | no |  |
| `review_points` | array | no |  |

## F.33 Library Include Schema

Canonical schema: `language/schemas/library_include_schema.yaml`

This schema does not expose top-level `properties`; inspect its composition (`allOf`, `oneOf`, or referenced definitions) with the validator.

## F.34 Migration Ambiguity.Schema

Canonical schema: `language/schemas/migration_ambiguity.schema.json`

This schema does not expose top-level `properties`; inspect its composition (`allOf`, `oneOf`, or referenced definitions) with the validator.

## F.35 Migration Clause Inventory.Schema

Canonical schema: `language/schemas/migration_clause_inventory.schema.json`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `schema_version` | unspecified | yes |  |
| `source_ref` | string | yes |  |
| `clauses` | array | yes |  |

## F.36 Migration Dependency Graph.Schema

Canonical schema: `language/schemas/migration_dependency_graph.schema.json`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `schema_version` | unspecified | yes |  |
| `graph_id` | string | yes |  |
| `nodes` | array | yes |  |
| `edges` | array | yes |  |

## F.37 Migration Loss Finding.Schema

Canonical schema: `language/schemas/migration_loss_finding.schema.json`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `schema_version` | unspecified | yes |  |
| `finding_id` | string | yes |  |
| `clause_id` | string | yes |  |
| `loss_type` | unspecified; enum | yes | `unmapped_clause`, `partial_coverage`, `mandatory_strength_downgrade`, `authorization_boundary_loss`, `decision_semantic_loss`, `evidence_requirement_loss`, `unsupported_exclusion`, `unit_merge_without_equivalence`, `construct_mapping_missing` |
| `severity` | unspecified; enum | yes | `warning`, `error`, `critical` |
| `message` | string | yes |  |
| `blocking` | boolean | yes |  |
| `mapped_unit_ids` | array | no |  |

## F.38 Migration Ordo Mapping.Schema

Canonical schema: `language/schemas/migration_ordo_mapping.schema.json`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `schema_version` | unspecified | yes |  |
| `mapping_id` | string | yes |  |
| `entries` | array | yes |  |

## F.39 Migration Traceability Matrix.Schema

Canonical schema: `language/schemas/migration_traceability_matrix.schema.json`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `schema_version` | unspecified | yes |  |
| `matrix_id` | string | yes |  |
| `source_ref` | string | yes |  |
| `rows` | array | yes |  |

## F.40 Node Schema

Canonical schema: `language/schemas/node_schema.yaml`

This schema does not expose top-level `properties`; inspect its composition (`allOf`, `oneOf`, or referenced definitions) with the validator.

## F.41 Process Instruction Migration Intake.Schema

Canonical schema: `language/schemas/process_instruction_migration_intake.schema.json`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `schema_version` | unspecified | yes |  |
| `intake_id` | string | yes |  |
| `source` | object | yes |  |
| `migration_goal` | string | yes |  |
| `preservation_contract` | object | yes |  |
| `decomposition_policy` | object | yes |  |
| `validation_policy` | object | yes |  |

## F.42 Ordo Process Instruction Migration Package

Canonical schema: `language/schemas/process_instruction_migration_package.schema.json`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `schema_version` | unspecified | yes |  |
| `package_id` | string | yes |  |
| `source` | object | yes |  |
| `intake` | object | yes |  |
| `clause_inventory` | object | yes |  |
| `ambiguities` | array | yes |  |
| `dependency_graph` | object | yes |  |
| `ordo_mapping` | object | yes |  |
| `traceability_matrix` | object | yes |  |
| `gate_report` | object | yes |  |
| `playbook` | object | yes |  |

## F.43 Process Rail Schema

Canonical schema: `language/schemas/process_rail_schema.yaml`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `rail_id` | string | no |  |
| `state_tracking` | string; enum | no | `required`, `recommended`, `none` |
| `allow_deviation` | boolean | no |  |
| `require_resume_after_deviation` | boolean | no |  |
| `resume_policy` | string | no |  |
| `backtracking` | string; enum | no | `disabled`, `restricted`, `enabled` |
| `backtracking_policy` | object | no |  |
| `skip_ahead_policy` | string | no |  |
| `stale_answer_policy` | string | no |  |

## F.44 Program Level Approval Gate Schema

Canonical schema: `language/schemas/program_level_approval_gate_schema.yaml`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `gate_id` | string | no | Stable local identifier for the program-level approval gate. |
| `applies_to` | array | no |  |
| `profile` | string; enum | no | `light`, `standard`, `strict` |
| `severity_policy` | object | no |  |
| `required_checks` | array | no |  |
| `approval_decision` | object | no |  |

## F.45 Program Level Contract Schema

Canonical schema: `language/schemas/program_level_contract_schema.yaml`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `program_id` | string | yes | Local stable program identifier. |
| `module_id` | string | yes | Canonical module/package identifier, for example ordo.applied_project_factory. |
| `version` | string | no | Module/package version. |
| `ordo_version` | string | no | Compatible Ordo language version or line. |
| `lifecycle` | string; enum | no | `draft`, `alpha`, `beta`, `release-candidate`, `stable`, `deprecated` |
| `control_level` | string; enum | no | `light`, `standard`, `strict` |
| `execution_mode` | string; enum | no | `full_runtime`, `chat_internal`, `freeform_only`, `dry_run`, `test` |
| `contract_profile` | string | no |  |
| `compatibility` | object | no |  |
| `runtime_profile` | object | no |  |
| `required_review_points` | array | no |  |
| `required_validation_commands` | array | no |  |

## F.46 Prompt Ref Schema

Canonical schema: `language/schemas/prompt_ref_schema.yaml`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `prompt_id` | string | no | Must resolve to prompt_registry.prompts[*].prompt_id. |
| `use` | string | no |  |
| `required_for_profile` | array | no |  |
| `state_change_allowed` | boolean | no | Optional local override must not contradict registry-level prompt metadata. |
| `notes` | string | no |  |

## F.47 Ordo Prompt Registry Packaging Checks Schema

Canonical schema: `language/schemas/prompt_registry_packaging_checks_schema.yaml`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `prompt_registry_packaging_checks` | object | yes |  |

## F.48 Prompt Registry Schema

Canonical schema: `language/schemas/prompt_registry_schema.yaml`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `registry_id` | string | no | Stable identifier for the package prompt registry. |
| `version` | string | no | Registry version local to the package. |
| `default_language` | string | no | Default BCP-47-like or package-local language code for prompt files. |
| `prompt_root` | string | no | Package-relative prompt root folder, for example prompts/. |
| `prompts` | array | no |  |

## F.49 Prompt Registry Validation Profile Schema

Canonical schema: `language/schemas/prompt_registry_validation_profile_schema.yaml`

This schema does not expose top-level `properties`; inspect its composition (`allOf`, `oneOf`, or referenced definitions) with the validator.

## F.50 Release Clean Gate Provenance Schema

Canonical schema: `language/schemas/release_clean_gate_provenance_schema.yaml`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `schema_version` | unspecified | yes |  |
| `gate_id` | string | yes |  |
| `gate_class` | unspecified | yes |  |
| `repository` | string | yes |  |
| `revision` | string | yes |  |
| `ref` | string | yes |  |
| `run_id` | string | yes |  |
| `profile` | unspecified | yes |  |
| `fail_on_warning` | unspecified | yes |  |
| `linkage` | object | yes |  |

## F.51 Rendered Artifact Assertion Schema

Canonical schema: `language/schemas/rendered_artifact_assertion_schema.yaml`

This schema does not expose top-level `properties`; inspect its composition (`allOf`, `oneOf`, or referenced definitions) with the validator.

## F.52 Rendering Template Schema

Canonical schema: `language/schemas/rendering_template_schema.yaml`

This schema does not expose top-level `properties`; inspect its composition (`allOf`, `oneOf`, or referenced definitions) with the validator.

## F.53 Ordo Conversation Scope Guard Strictness and Escalation Policy

Canonical schema: `language/schemas/scope_guard_policy.schema.json`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `mode` | unspecified; enum | yes | `advisory`, `guided_redirect`, `strict_redirect`, `locked_process` |
| `resolved_policy` | object | yes |  |
| `escalation` | object | yes |  |

## F.54 Semantic Json Ir Schema

Canonical schema: `language/schemas/semantic_json_ir_schema.yaml`

This schema does not expose top-level `properties`; inspect its composition (`allOf`, `oneOf`, or referenced definitions) with the validator.

## F.55 Shared Tail Reference Schema

Canonical schema: `language/schemas/shared_tail_reference_schema.yaml`

This schema does not expose top-level `properties`; inspect its composition (`allOf`, `oneOf`, or referenced definitions) with the validator.

## F.56 Startup Package Profile Schema

Canonical schema: `language/schemas/startup_package_profile_schema.yaml`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `startup_package_profile` | object | yes |  |

## F.57 Startup Profile Validation Profile Schema Convention

Canonical schema: `language/schemas/startup_profile_validation_profile_schema.yaml`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `startup_profile_validation` | object | yes |  |

## F.58 Ordo Conversation Scope Guard State Protection

Canonical schema: `language/schemas/state_protection.schema.json`

| Field | Type | Required | Allowed values / description |
|---|---|---:|---|
| `trigger_classification` | array | yes |  |
| `protected_state` | array | yes |  |
| `allowed_mutations` | array | yes |  |
| `rollback_on_violation` | unspecified | yes |  |
| `blocking` | unspecified | yes |  |

## F.59 Trace Schema

Canonical schema: `language/schemas/trace_schema.yaml`

This schema does not expose top-level `properties`; inspect its composition (`allOf`, `oneOf`, or referenced definitions) with the validator.
