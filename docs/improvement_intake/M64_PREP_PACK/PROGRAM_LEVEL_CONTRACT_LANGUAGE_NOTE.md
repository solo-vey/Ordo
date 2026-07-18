# Program-Level Contract Language Note

Status: `P0 language candidate`

## Problem

A process can have a correct tree, gates, templates and runtime artifacts, but still lack an approved top-level execution policy.

Examples of missing decisions:

```text
which runtime profile is expected
whether the process is strict or flexible
how analyst input is classified
what happens after deviations
whether backtracking invalidates dependent state
which checks require CLI evidence
where human approval is mandatory
how future chats should start the package
```

## Proposed language/package model

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

## Gate

Add a package/process gate:

```text
PROGRAM_LEVEL_CONTRACT_REVIEW
PROGRAM_LEVEL_CONTRACT_APPROVAL_GATE
```

The gate must be human-visible, not only YAML-visible.

## Blocking conditions

The gate blocks if:

```text
- full_runtime is claimed but runtime/compile gates are absent;
- strict control level lacks gates for important decisions;
- deviation is allowed without resume policy;
- backtracking is enabled/restricted without invalidation policy;
- AI is allowed to make human content decisions without confirmation;
- CLI checks can be satisfied by AI claims instead of real evidence;
- startup prompt and README startup instructions are missing.
```
