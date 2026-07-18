# Appendix C. Verified Program Examples

Each example is taken from a canonical package that passes the current package linter. Long sources are excerpted to keep the appendix readable; the complete source remains in the package path shown for each example.

## Guided intake

Canonical source: `packages/history_event_guided_intake/source/program.ordo.yaml`

The excerpt demonstrates program metadata, graph or node declarations, contracts, and package-specific governance.

```yaml
ordo:
  version: '0.12'
  package: history_event.guided_intake
  control_level: standard
  execution_mode: chat_internal
includes:
- library: ordo.validation.contract_first
  version: ^0.2.0
  as: contract_first
- library: ordo.qa.release_validation
  version: ^0.1.0
  as: qa_release
intent:
  id: INTENT_HISTORY_EVENT_GUIDED_INTAKE
  description: Керовано зібрати мінімальний контракт для створення нового History Event package без передчасної генерації
    фінального архіву.
contract:
  id: CONTRACT_HISTORY_EVENT_GUIDED_INTAKE
  required:
  - event_goal
  - selected_path
  - event_alias
  - display_name_uk
  - display_name_en
  - source_field
  - value_semantics
  - qa_scope
  - test_coverage_level
  - test_strategy_contract
  - approval_received
state:
  id: STATE_HISTORY_EVENT_GUIDED_INTAKE
  schema:
    event_goal: null
    selected_path: null
    event_alias: null
    display_name_uk: null
    display_name_en: null
    source_field: null
    value_semantics: []
    qa_scope: []
    approval_received: false
    output_allowed: false
    final_package_created: false
    test_coverage_level: null
    test_strategy_contract: []
    manual_qa_coverage: []
    functional_test_coverage: []
    unit_test_coverage: []
    test_documentation_requirement: null
    test_propagation_required: true
graph_contract:
  entry_node: N_EVENT_GOAL
  external_terminal_targets:
  - G_APPROVAL_CONFIRMED
  - STOP_NEEDS_APPROVAL
nodes:
- id: N_EVENT_GOAL
  question: Яку бізнесову зміну має відображати нова історична подія?
  answer_type: free_text
  on_answer:
    update_state:
      event_goal: $answer
    next: N_PATH_SELECT
  on_unmatched_input:
    action: CLARIFY.REQUEST
    strategy: rephrase_and_narrow
    max_attempts: 2
    on_exhausted:
      action: escalate_to_human
      reason: event goal remains unclear
- id: N_PATH_SELECT
  question: 'Питання: оберіть Ordo path для цієї History Event.


    Варіанти:

    A — зміна у source row / ChangeRecord flow, далі без додаткових legacy A-subpath уточнень

    B — derived або агрегований стан

    C — зовнішній ExternalHistoryEvent

    D — інший або нестандартний шлях


    Відповідайте: A, B, C або D. Якщо вибрано A, runtime переходить одразу в A-flow: source row contract → event identity
    contract → business fields contract → ChangeRecord contract → trigger/no-op → normalization → HistoryEvent output → payload/display/time/entity/delta/test/artifact
    coverage.'
  answer_type: enum
  allowed_answers:
  - A
  - B
  - C
  - D
  on_answer:
    A:
      update_state:
        selected_path: A
      next: N_EVENT_ALIAS
    B:
      update_state:
        selected_path: B
      next: N_EVENT_ALIAS
    C:
      update_state:
        selected_path: C
      next: N_EVENT_ALIAS
    D:
      update_state:
        selected_path: D
      next: N_EVENT_ALIAS
  on_unmatched_input:
    action: CLARIFY.REQUEST
    strategy: show_allowed_answers
    max_attempts: 2
    on_exhausted:
      action: escalate_to_human
      reason: path selection did not match allowed paths
  prompt_refs:
  - prompt_id: hp.source_type.clarification.v1
    use: during_clarification
- id: N_EVENT_ALIAS
  question: Який технічний alias події?
  answer_type: free_text
  on_answer:
    update_state:
      event_alias: $answer
    next: N_DISPLAY_NAME_UK
  on_unmatched_input:
    action: CLARIFY.REQUEST
    strategy: rephrase_and_narrow
    max_attempts: 2
    on_exhausted:
      action: escalate_to_human
      reason: event alias remains unclear
- id: N_DISPLAY_NAME_UK
  question: Яка українська назва події для користувача?
  answer_type: free_text
  on_answer:
    update_state:
      display_name_uk: $answer
    next: N_DISPLAY_NAME_EN
  on_unmatched_input:
    action: CLARIFY.REQUEST
    strategy: rephrase_and_narrow
    max_attempts: 2
    on_exhausted:
      action: escalate_to_human
      reason: Ukrainian display name remains unclear
  prompt_refs:
  - prompt_id: hp.localization.bilingual_texts.v1
    use: before_question
- id: N_DISPLAY_NAME_EN
  question: Яка англійська назва події для технічної документації?
  answer_type: free_text
  on_answer:
    update_state:
      display_name_en: $answer
    next: N_SOURCE_FIELD
  on_unmatched_input:
    action: CLARIFY.REQUEST
    strategy: rephrase_and_narrow
    max_attempts: 2
    on_exhausted:
      action: escalate_to_human
      reason: English display name remains unclear
  prompt_refs:
  - prompt_id: hp.localization.bilingual_texts.v1
    use: before_question
- id: N_SOURCE_FIELD
  question: 'Питання: підтвердіть source field або набір полів для бізнесової зміни.


    Варіанти формату відповіді:

    1. одне поле, наприклад item.status

    2. група вкладених полів, наприклад item.capital.value + item.capital.currency
```

## Applied Project Factory

Canonical source: `packages/ordo_applied_project_factory/source/program.ordo.yaml`

The excerpt demonstrates program metadata, graph or node declarations, contracts, and package-specific governance.

```yaml
ordo:
  version: '0.12'
  package: ordo.applied_project_factory
  control_level: standard
  execution_mode: chat_internal
  package_version: 0.1.0-rc.1
  language_package_version: 0.12.0-preview-rc1
module:
  id: ordo.applied_project_factory
  version: 0.1.0-rc.1
  versioning_scope: module_local
  language_compatibility: ordo >= 0.12.0-preview-rc1, M62 line closure compatible
  parent_language_package_version: 0.12.0-preview-rc1
  inclusion_model: language_package_includes_module_at_explicit_module_version
  release_channel: release_candidate
  previous_internal_labels:
  - M61.1
  - M61.2
  - M61.3
  - M61.4
  - M61.5
  - M61.6
  whole_tree_integration_review:
    version: 0.1.0-alpha.20
    status: closed_human_review
    source_version: 0.1.0-alpha.19
    scope:
    - startup_branches_integration
    - shared_output_template_joins
    - shared_validation_handoff_joins
    - terminal_deferred_unfinished_gates
    - orphans_dead_ends_duplication_scan
    human_review_blocks:
      startup_branches_integration: approved
      shared_output_template_joins: approved
      shared_validation_handoff_joins: approved
      terminal_deferred_unfinished_gates: approved
      orphans_dead_ends_duplication: approved_human_review
    real_structural_scan_required: true
    real_structural_scan_status: passed
  full_validation_fix:
    version: 0.1.0-alpha.21
    source_version: 0.1.0-alpha.20
    scope:
    - manifest_version_alignment
    - test_coverage_backfill
    - contract_artifact_marker_backfill
    - full_validation_state_fixture
    - artifact_consistency_report
    process_logic_changed: false
    status: applied_scoped_technical_fix
  m62_release_candidate_adaptation:
    version: 0.1.0-rc.1
    source_version: 0.1.0-alpha.21
    parent_language_line: M62 line closure
    status: applied
    scope:
    - adopt current M62 language package as parent base
    - preserve APF alpha.21 process logic
    - sync module packaging/docs to standard applied module layer
    - validate with M62 parent CLI available commands
    - keep future IR candidates FLOW.JOIN and SHARED.TAIL.REFERENCE as documented
      candidates, not runtime core changes
    process_logic_changed: false
includes:
- library: ordo.process_rail.core
  version: ^0.1.0
  as: process_rail
- library: ordo.project_authoring.validation
  version: ^0.1.0
  as: project_validation
- library: ordo.output_template.contracts
  version: ^0.1.0
  as: template_contracts
interaction_model:
  human_role: pm_or_analyst_without_ordo_yaml_knowledge
  ai_role: ai_ordo_project_factory_developer
  proactive_ai_behavior: required
  raw_tool_output_policy: ai_interprets_before_user
  yaml_visibility_policy: hidden_from_pm_by_default
intent:
  id: INTENT_APPLIED_PROJECT_FACTORY
  description: 'Допомогти PM/аналітику створити новий прикладний Ordo-проєкт будь-якого
    типу без написання YAML напряму; AI обирає режим, у free-dialogue накопичує raw
    notes, структурує їх у candidate nodes/gates/outputs/templates, формує draft tree,
    проводить depth-first review і генерує source/program.ordo.yaml. APF v0.1.0-alpha.13
    фіксує user-facing формат показу процесу під час design/review, щоб режим traversal,
    branch selection, node review decision і validation gate не змішувалися. APF v0.1.0-alpha.14
    додає четвертий режим старту — коригування існуючого процесу — з batch та targeted
    improvement subflows. APF v0.1.0-alpha.16 adds progressive branch-1 authoring,
    input policy, terminal output binding, and template/mock-example verification
    before YAML generation. APF v0.1.0-alpha.17 treats manual-tree authoring as an
    adapter into the progressive review path rather than a separate downstream process.
    APF v0.1.0-alpha.18 closes the shared terminal output/template subflow as a reusable
    block across all startup branches: terminal points explicitly choose an output
    policy; new artifacts are described by free-form artifact intent rather than fixed
    type lists; the runtime shows available terminal state fields, derives an output
    recipe with direct-insert vs generated sections, and uses file-first review packages
    for document-like artifacts. Template/mock/mapping review is simplified to four
    user decisions: confirm, revise, defer, or remove artifact. Deferred templates
    are recorded as unfinished and cannot be used by final gates until completed or
    removed. APF v0.1.0-alpha.19 closes the shared validation/handoff tail as the
    reusable final path for all startup branches and shared subflows: source YAML
    generation approval, minimal validation, full-validation decision, validation
    result review, scoped correction loop, final unfinished-items gate, handoff package
    generation, and final handoff. Validation failure UX is simplified: failed checks
    show a short issue list and route either into correction mode or a blocked/deferred
    state; details live inside correction mode. Skipped full validation for alpha
    is recorded as a limitation, never as passed. Handoff package generation is file-first
    and blocked by failed minimal validation or active unfinished artifacts/templates.
    APF v0.1.0-alpha.20 closes the whole-tree integration review after the branch
    and shared-tail closures: all four startup branches join the shared output/template
    subflow and shared validation/handoff tail; terminal/deferred/unfinished gates
    are aligned; legacy unreachable nodes are explicitly marked as deprecated compatibility
    nodes rather than active orphans; structural scan results are recorded in the
    alpha.20 validation report.'
  purpose: ' APF v0.1.0-alpha.12 separates unreviewed sibling branches from not-selected
    control actions and blocked control actions; review state must show which alternatives
    were intentionally not selected and which actions are blocked until readiness
    conditions are met.'
contract:
  id: CONTRACT_APPLIED_PROJECT_FACTORY
  required:
  - factory_authoring_mode
  - applied_project_goal
  - applied_process_type
  - runtime_human_role
  - runtime_ai_role
  - runtime_entry_point
  - decision_tree_blueprint
  - state_schema_blueprint
  - output_artifact_catalog
  - output_template_catalog
  - validation_gate_catalog
  - first_release_output_scope
  - approval_to_generate_source_yaml
  - domain_model_notes
  - open_questions
  - draft_tree_review_status
  - basic_test_case_catalog
  - domain_input_sources
  - domain_output_template_sources
  - approved_decision_tree
  - tree_review_depth_first_complete
  - free_dialogue_raw_notes
  - free_dialogue_structured_notes
  - candidate_decision_nodes
  - candidate_gates
  - candidate_outputs
  - candidate_templates
  - free_dialogue_draft_tree_ready
  - stabilized_tree_branch
  - self_hosted_authoring_loop_status
  - focused_svg_policy
  - graph_rendering_policy_status
  - language_improvement_proposals_status
  - module_versioning_policy
  - graph_annotation_overlay_policy
  - auto_svg_generation_policy
  - user_facing_node_description_policy
  - user_facing_extraction_policy
  - process_feedback_policy
  - process_feedback_policy_status
  - node_review_display_contract
  - node_review_display_policy_status
  - confirmed_review_path
  - current_review_branch
  - unreviewed_sibling_branches
  - deferred_return_points
  - current_node_review_record
  - node_review_control_gate_status
  - node_decision_gate_policy
  - current_node_review_decision
  - node_review_ordo_layer_visibility
  - incremental_yaml_update_policy
  - incremental_yaml_validation_profile
  - incremental_yaml_validation_status
  - last_incremental_yaml_patch_summary
  - full_project_validation_policy
  - full_project_validation_status
```

## Hybrid Executor

Canonical source: `packages/ordo_hybrid_executor/source/program.ordo.yaml`

The excerpt demonstrates program metadata, graph or node declarations, contracts, and package-specific governance.

```yaml
ordo:
  version: '0.12'
  package: ordo.hybrid_executor
  control_level: standard
  execution_mode: chat_internal
includes:
- library: ordo.process_rail.core
  version: ^0.1.0
  as: process_rail
- library: ordo.hybrid_execution.helpers
  version: ^0.1.0
  as: hybrid_helpers
interaction_model:
  human_role: user
  ai_role: ordo_executor
  proactive_ai_behavior: required
  raw_tool_output_policy: ai_interprets_before_user
process_rail:
  rail_id: ORDO_HYBRID_EXECUTION_RAIL
  purpose: Виконати готовий Semantic JSON IR через AI Ordo Executor без перетворення
    CLI на головний діалоговий runtime.
  state_tracking: required
  allow_deviation: true
  require_resume_after_deviation: true
  backtracking: enabled
hybrid_execution:
  ai_role: ordo_executor
  semantic_ir_role: process_rail
  cli_role: deterministic_helper
  raw_tool_output_policy: ai_interprets_before_user
  allow_deviation: true
  require_resume_after_deviation: true
  backtracking: enabled
conversation_semantics:
  on_unmatched_input:
    strategy: classify_and_route
    allowed_classes:
    - answer_current_question
    - answer_future_question
    - correction_previous_answer
    - clarification_request
    - domain_context
    - approval
    - refusal
    - out_of_scope
    require_state_validation: true
intent:
  id: INTENT_HYBRID_EXECUTION
  description: Допомогти AI Ordo Executor виконати готовий Semantic JSON IR, тримаючись
    Process Rail і використовуючи CLI/helper checks лише для детермінованих частин.
contract:
  id: CONTRACT_HYBRID_EXECUTION
  required:
  - semantic_ir_loaded
  - current_rail_node
  - rail_state_validated
  - human_input_classified
  - helper_result_interpreted
  - resume_after_deviation
  - output_allowed_by_gate
state:
  id: STATE_HYBRID_EXECUTION
  schema:
    semantic_ir_loaded: false
    current_rail_node: null
    completed_nodes: []
    invalidated_nodes: []
    human_input_classified: null
    rail_state_validated: false
    helper_result_interpreted: false
    deviation_detected: false
    resume_after_deviation: false
    output_allowed_by_gate: false
    human_visible_summary: null
graph_contract:
  entry_node: N_LOAD_IR
  allowed_cycle_regions:
  - id: CR_EXECUTION_LOOP
    nodes:
    - N_CLASSIFY_INPUT
    - N_VALIDATE_STATE
    - N_INTERPRET_HELPER
    - N_HANDLE_DEVIATION
    - N_OUTPUT_GATE
    - N_NEXT_MOVE
nodes:
- id: N_LOAD_IR
  question: Завантажити готовий Semantic JSON IR і визначити стартовий Process Rail
    node.
  answer_type: system_action
  on_answer:
    update_state:
      semantic_ir_loaded: true
    next: N_CLASSIFY_INPUT
  on_unmatched_input:
    action: CLARIFY.REQUEST
    strategy: explain_that_execution_needs_compiled_ir
    max_attempts: 1
    on_exhausted:
      action: block_execution
      reason: semantic json ir is missing
- id: N_CLASSIFY_INPUT
  question: Класифікувати повідомлення людини відносно поточного Process Rail node.
  answer_type: ai_classification
  on_answer:
    update_state:
      human_input_classified: $answer.class
    next: N_VALIDATE_STATE
  on_unmatched_input:
    action: CLARIFY.REQUEST
    strategy: classify_or_ask_for_clarification
    max_attempts: 2
    on_exhausted:
      action: keep_current_node
      reason: input class remains unclear
- id: N_VALIDATE_STATE
  question: Викликати deterministic helper для перевірки запропонованого стану.
  answer_type: tool_result
  on_answer:
    update_state:
      rail_state_validated: true
    next: N_INTERPRET_HELPER
  on_unmatched_input:
    action: CLARIFY.REQUEST
    strategy: retry_or_explain_validation_problem
    max_attempts: 1
    on_exhausted:
      action: block_next_step
      reason: state validation unavailable
- id: N_INTERPRET_HELPER
  question: Перетворити helper result у людське пояснення без raw technical dump.
  answer_type: ai_explanation
  on_answer:
    update_state:
      helper_result_interpreted: true
      human_visible_summary: $answer
    next: N_HANDLE_DEVIATION
  on_unmatched_input:
    action: CLARIFY.REQUEST
    strategy: produce_plain_language_summary
    max_attempts: 1
    on_exhausted:
      action: block_handoff
      reason: helper result was not interpreted
- id: N_HANDLE_DEVIATION
  question: Якщо є correction/deviation, виконати rail resume або backtracking.
  answer_type: ai_process_decision
  on_answer:
    update_state:
      resume_after_deviation: true
    next: N_OUTPUT_GATE
  on_unmatched_input:
    action: CLARIFY.REQUEST
    strategy: ask_whether_user_changes_previous_decision
    max_attempts: 1
    on_exhausted:
      action: continue_without_deviation
      reason: no confirmed deviation
- id: N_OUTPUT_GATE
  question: Перевірити, чи дозволено генерувати output на поточному стані.
  answer_type: gate_check
  on_answer:
    update_state:
      output_allowed_by_gate: $answer.allowed
    next: N_NEXT_MOVE
  on_unmatched_input:
    action: CLARIFY.REQUEST
    strategy: explain_output_gate
    max_attempts: 1
    on_exhausted:
      action: block_output
      reason: output gate unresolved
- id: N_NEXT_MOVE
  terminal: true
  question: 'Обрати наступний conversational move: питання, пояснення, повернення
    назад або output.'
  answer_type: ai_decision
  on_answer:
    update_state:
      current_rail_node: $answer.next_node
```

## Project Builder

Canonical source: `packages/ordo_project_builder/source/program.ordo.yaml`

The excerpt demonstrates program metadata, graph or node declarations, contracts, and package-specific governance.

```yaml
ordo:
  version: '0.12'
  package: ordo.project_builder
  control_level: standard
  execution_mode: chat_internal
includes:
- library: ordo.process_rail.core
  version: ^0.1.0
  as: process_rail
- library: ordo.project_authoring.validation
  version: ^0.1.0
  as: project_validation
interaction_model:
  human_role: pm
  ai_role: ordo_developer
  proactive_ai_behavior: required
  raw_tool_output_policy: ai_interprets_before_user
process_rail:
  rail_id: ORDO_PROJECT_AUTHORING_RAIL
  purpose: Створити або модернізувати Ordo-проєкт через PM dialogue без вимоги, щоб PM писав Ordo YAML напряму.
  state_tracking: required
  allow_deviation: true
  require_resume_after_deviation: true
  backtracking: enabled
conversation_semantics:
  on_unmatched_input:
    strategy: classify_and_route
    allowed_classes:
    - answer_current_question
    - answer_future_question
    - correction_previous_answer
    - clarification_request
    - domain_context
    - design_suggestion_request
    - approval
    - refusal
    - out_of_scope
    require_state_validation: true
intent:
  id: INTENT_ORDO_PROJECT_BUILDER
  description: Допомогти PM створити новий Ordo-проєкт через діалог із AI Ordo Developer і отримати валідований Semantic JSON
    IR.
contract:
  id: CONTRACT_ORDO_PROJECT_BUILDER
  required:
  - project_goal
  - project_domain
  - human_roles
  - ai_roles
  - process_rail_goal
  - state_model_summary
  - intake_or_execution_mode
  - required_outputs
  - deterministic_helper_scope
  - approval_before_compile
state:
  id: STATE_ORDO_PROJECT_BUILDER
  schema:
    project_goal: null
    project_domain: null
    human_roles: []
    ai_roles: []
    process_rail_goal: null
    state_model_summary: null
    intake_or_execution_mode: null
    required_outputs: []
    deterministic_helper_scope: []
    yaml_project_created: false
    syntax_checked: false
    semantic_ir_compiled: false
    approval_before_compile: false
    pm_visible_summary: null
graph_contract:
  entry_node: N_PROJECT_GOAL
  external_terminal_targets:
  - G_APPROVAL_BEFORE_COMPILE
  - STOP_NEEDS_APPROVAL
nodes:
- id: N_PROJECT_GOAL
  question: Який Ordo-проєкт ви хочете створити і яку проблему він має вирішувати?
  answer_type: free_text
  on_answer:
    update_state:
      project_goal: $answer
    next: N_PROJECT_DOMAIN
  on_unmatched_input:
    action: CLARIFY.REQUEST
    strategy: ask_for_project_goal_in_plain_language
    max_attempts: 2
    on_exhausted:
      action: escalate_to_human
      reason: project goal remains unclear
- id: N_PROJECT_DOMAIN
  question: Яку доменну область або тип процесу має описувати цей Ordo-проєкт?
  answer_type: free_text
  on_answer:
    update_state:
      project_domain: $answer
    next: N_ROLES
  on_unmatched_input:
    action: CLARIFY.REQUEST
    strategy: ask_for_domain_examples
    max_attempts: 2
    on_exhausted:
      action: escalate_to_human
      reason: project domain remains unclear
- id: N_ROLES
  question: Хто буде людиною в цьому процесі і яку роль має виконувати ШІ?
  answer_type: free_text
  on_answer:
    update_state:
      human_roles: $answer.human_roles
      ai_roles: $answer.ai_roles
    next: N_PROCESS_RAIL_GOAL
  on_unmatched_input:
    action: CLARIFY.REQUEST
    strategy: ask_for_pm_user_ai_roles
    max_attempts: 2
    on_exhausted:
      action: escalate_to_human
      reason: roles remain unclear
- id: N_PROCESS_RAIL_GOAL
  question: 'Що саме Process Rail має утримувати: питання, рішення, gates, повернення назад, outputs або інше?'
  answer_type: free_text
  on_answer:
    update_state:
      process_rail_goal: $answer
    next: N_STATE_MODEL
  on_unmatched_input:
    action: CLARIFY.REQUEST
    strategy: show_process_rail_examples
    max_attempts: 2
    on_exhausted:
      action: escalate_to_human
      reason: process rail goal remains unclear
- id: N_STATE_MODEL
  question: Який мінімальний state треба вести, щоб процес не губився?
  answer_type: free_text
  on_answer:
    update_state:
      state_model_summary: $answer
    next: N_MODE_SELECT
  on_unmatched_input:
    action: CLARIFY.REQUEST
    strategy: ask_for_decisions_and_fields_to_track
    max_attempts: 2
    on_exhausted:
      action: escalate_to_human
      reason: state model remains unclear
- id: N_MODE_SELECT
  question: Це Ordo-проєкт для створення інших проєктів, для виконання готового процесу чи змішаний режим?
  answer_type: enum
  allowed_answers:
  - authoring
  - execution
  - mixed
  on_answer:
    authoring:
      update_state:
        intake_or_execution_mode: authoring
      next: N_REQUIRED_OUTPUTS
    execution:
      update_state:
        intake_or_execution_mode: execution
      next: N_REQUIRED_OUTPUTS
    mixed:
      update_state:
        intake_or_execution_mode: mixed
      next: N_REQUIRED_OUTPUTS
  on_unmatched_input:
    action: CLARIFY.REQUEST
    strategy: show_allowed_answers
    max_attempts: 2
    on_exhausted:
      action: escalate_to_human
      reason: mode selection did not match allowed modes
- id: N_REQUIRED_OUTPUTS
  question: Які output artifacts має створювати цей Ordo-проєкт?
  answer_type: list
  on_answer:
```
