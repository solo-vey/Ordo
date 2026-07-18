# Improvement Prompt: Add Program-Level Metadata, Interaction Semantics, and Approval Gates to the Base APF Process

## Purpose

Improve the base APF / Ordo process that is used to create applied playbook or factory packages, so that program-level configuration is explicitly designed, reviewed with the human analyst, validated, and preserved in every generated package.

This improvement is about the **base process and package framework**, not about any specific domain process such as HistoryEvent, ChangeRecord, Mongo/EDR, ExternalHistoryEvent, or data-block comparison.

## Problem Observed

During creation of a new applied factory/playbook, the process focused heavily on:

- decision-tree nodes;
- gates;
- transitions;
- templates;
- package outputs;
- compiled/runtime artifacts.

However, important **program-level and conversation-level configuration** was not explicitly surfaced to the analyst before final package creation.

These settings affect how the package works in practice:

- what runtime profile the package expects;
- whether the process is strict or flexible;
- how AI should interpret analyst input;
- whether state tracking is required;
- how deviations and backtracking are handled;
- which checks must be deterministic CLI/runtime checks rather than AI statements;
- how human review points are enforced.

Without an explicit approval gate, the package can look complete while still lacking a confirmed top-level execution policy.

## Required Improvement

The base APF process must include a mandatory stage for designing, reviewing, validating, and confirming program-level metadata and interaction semantics before final package assembly.

Add a program-level contract layer covering at least:

1. `PROGRAM.DEF` / top-level program metadata.
2. `INTERACTION.MODEL`.
3. `PROCESS_RAIL.DEF` / `process_rail`.
4. `CONVERSATION.SEMANTICS`.
5. `HYBRID_EXECUTION.MODEL`.
6. Deterministic validation requirements.
7. Human review and approval points.

## New Required Process Stage

Add a mandatory stage before final package generation:

```text
PROGRAM_LEVEL_CONTRACT_REVIEW
```

or equivalent naming:

```text
PROCESS_LEVEL_CONTRACT_APPROVAL
```

This stage must be executed after the main tree/process design is stable and before runtime compilation, package composition checks, and final archive assembly.

Suggested placement:

```text
process tree / templates / output rules confirmed
→ PROGRAM_LEVEL_CONTRACT_REVIEW
→ PROGRAM_LEVEL_CONTRACT_APPROVAL_GATE
→ runtime compilation gate
→ package composition gate
→ final archive assembly
```

## Required Analyst Review

The AI must present a concise summary of the proposed program-level configuration to the analyst and ask for confirmation or changes.

The analyst must be shown, at minimum:

```text
Program identity:
- program_id
- module_id
- version
- ordo_version

Runtime profile:
- control_level: light | standard | strict
- execution_mode: full_runtime | chat_internal | freeform_only
- package profile: source-authoring | compiled-runtime | hybrid | handoff

Interaction model:
- human responsibility
- AI responsibility
- CLI/helper responsibility
- raw tool output policy

Process rail:
- state tracking
- deviation policy
- resume policy
- backtracking policy

Conversation semantics:
- answer_current_node
- clarification
- deviation
- backtrack_request
- new_requirement
- unmatched input policy

Hybrid execution:
- deterministic commands that must be run, not simulated
- human review points
- runtime/CLI evidence required

Final package startup behavior:
- START_PROMPT policy
- README startup section policy
- analyst start guide policy
```

The AI must not hide these decisions inside YAML only. The analyst should see a human-readable summary before approval.

## Required YAML / Source Model Fields

The generated source YAML or adapted Ordo source must include explicit program-level fields.

Minimum fields:

```yaml
program_id: <stable program id>
module_id: <package/module id>
ordo_version: "0.12"
version: <module version>
control_level: standard
execution_mode: full_runtime
compatibility:
  runtime: <policy>
  cli: <policy>
  schema: <policy>
```

Interaction model:

```yaml
interaction_model:
  id: interaction_model
  roles:
    human: confirms_content_decisions
    ai: guided_process_driver
    cli: deterministic_validator
  raw_tool_output_policy: summarize_for_human
  human_responsibility:
    - confirm contract decisions
    - approve templates
    - approve final package profile
  ai_responsibility:
    - guide one node at a time
    - summarize decisions
    - propose next step
  cli_responsibility:
    - compile
    - validate
    - verify targets
    - check package composition
```

Process rail:

```yaml
process_rail:
  rail_id: guided_intake_rail
  state_tracking: required
  allow_deviation: true
  require_resume_after_deviation: true
  backtracking: restricted
  backtracking_policy:
    invalidates_dependent_state: true
    requires_review_before_continue: true
```

Conversation semantics:

```yaml
conversation_semantics:
  input_classes:
    - answer_current_node
    - clarification
    - deviation
    - backtrack_request
    - new_requirement
  routing_rules:
    answer_current_node: evaluate_current_node_answer
    clarification: answer_without_state_change
    deviation: handle_deviation_then_resume
    backtrack_request: invoke_backtracking_policy
    new_requirement: log_for_review_before_state_change
  unmatched_input_policy: clarify_before_state_change
  resume_policy: return_to_current_node_after_deviation
```

Hybrid execution model:

```yaml
hybrid_execution_model:
  id: hybrid_execution
  ai_layer: guided_process_driver
  cli_layer: deterministic_validator
  deterministic_commands:
    - compile
    - validate
    - verify-targets
    - render-graphs
    - package-composition-check
  human_review_points:
    - approve_program_contract
    - approve_branch_contract
    - approve_templates
    - approve_runtime_profile
    - approve_final_package
```

## New Required Gate

Add a mandatory gate:

```text
PROGRAM_LEVEL_CONTRACT_APPROVAL_GATE
```

The gate passes only if:

- `program_id` is set.
- `ordo_version` is set.
- `control_level` is one of `light`, `standard`, `strict`.
- `execution_mode` is one of `full_runtime`, `chat_internal`, `freeform_only`.
- `module_id` and package version are set or explicitly marked as pending draft values.
- compatibility policy is present.
- interaction roles are defined.
- human responsibility, AI responsibility, and CLI responsibility are defined.
- raw tool output policy is defined.
- process rail state tracking policy is defined.
- deviation and resume policies are defined if deviation is allowed.
- backtracking policy is defined if backtracking is enabled or restricted.
- conversation input classes and routing rules are defined.
- unmatched input policy is defined.
- hybrid execution deterministic commands are listed.
- human review points are listed.
- analyst has reviewed and approved or corrected the proposed settings.

The gate blocks if:

- the package claims `full_runtime` but compiled/runtime gates are absent;
- `strict` control level is selected but important decisions lack gates;
- deviation is allowed without resume policy;
- backtracking is enabled/restricted without invalidation policy;
- AI is allowed to make human content decisions without confirmation;
- CLI checks are described but can be satisfied by AI claims instead of real evidence;
- package startup prompts and README startup instructions are not defined.

## Validation Requirements

The base process must include deterministic validation for this layer.

Validation should check:

```text
program metadata completeness
allowed enum values
execution mode/profile consistency
control level/gate consistency
interaction role completeness
process rail completeness
conversation semantics completeness
hybrid execution deterministic commands present
human review points present
startup prompt/readme policies present
```

If validation fails, the final archive must not be assembled.

## Required AI Behavior

When building a new applied package, the AI must:

1. Detect whether program-level metadata is already available.
2. If missing or incomplete, propose default settings.
3. Present a human-readable summary to the analyst.
4. Ask for confirmation or corrections.
5. Update the source YAML / runtime model accordingly.
6. Run or request deterministic validation.
7. Record the approved program-level contract in package reports and README.
8. Prevent final package assembly until the gate passes.

The AI must not silently choose values such as `control_level`, `execution_mode`, or `backtracking` without review.

## Required Package Outputs

Every full generated package should include, either as files or clearly marked sections:

```text
program_contract summary
runtime profile summary
interaction model summary
process rail summary
conversation semantics summary
hybrid execution summary
validation result for program-level contract
START_PROMPT / START_HERE instructions
README startup instructions
```

## Acceptance Criteria

This improvement is complete when a generated full package contains:

- source YAML with program-level metadata;
- compiled/runtime representation preserving those settings;
- human-readable program contract summary;
- `PROGRAM_LEVEL_CONTRACT_APPROVAL_GATE` in the process model;
- validation report covering program-level settings;
- README section explaining startup behavior;
- start prompt for future model sessions;
- no final archive assembly before the program-level contract is confirmed.

## Out of Scope

This improvement does not define domain-specific paths, HistoryEvent mappings, ChangeRecord handling, external fact handling, or data-block comparison logic.

It only defines how the base APF process must handle top-level program identity, runtime profile, interaction semantics, rail policy, and hybrid execution configuration.
