# M64.0 Program-Level Contract Decision

Status: `P0 accepted for next design line`

## Decision

The M64 intake package identifies a missing Ordo layer: the **program-level contract layer**.

This layer describes how the whole process behaves before any individual node, gate or output template is executed.

## Accepted as next design target

The following are accepted for M64.1/M64.2 design work:

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

interaction_model:
  roles:
    human: confirms_content_decisions
    ai: guided_process_driver
    cli: deterministic_validator
  raw_tool_output_policy: summarize_for_human

process_rail:
  state_tracking: required
  allow_deviation: true
  require_resume_after_deviation: true
  backtracking: restricted
  backtracking_policy:
    invalidates_dependent_state: true
    requires_review_before_continue: true

conversation_semantics:
  input_classes:
    - answer_current_node
    - clarification
    - deviation
    - backtrack_request
    - new_requirement
  unmatched_input_policy: clarify_before_state_change
  resume_policy: return_to_current_node_after_deviation

hybrid_execution_model:
  ai_layer: guided_process_driver
  cli_layer: deterministic_validator
  deterministic_commands:
    - compile
    - validate
  human_review_points:
    - approve_program_contract
    - approve_final_package
```

## Non-decision

M64.0 does not make these fields mandatory for every existing package. It only accepts them as the next language/package schema convention to design.

## Promotion ladder

```text
observed APF need
→ documented pattern
→ reusable package/profile convention
→ lint/check candidate
→ formal language construct
→ IR/runtime object only if execution requires it
```
