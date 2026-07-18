# 17. Interaction, Process Rail, and Conversation Semantics Model

Status: `M64.2 docs/schema convention`

M64.2 extends the program-level contract line with three related source-level conventions:

```text
interaction_model
process_rail
conversation_semantics
```

These conventions describe how a live Ordo process behaves when it is driven by AI, checked by CLI/helper tools, and approved by a human.

## 1. Boundary

M64.2 does not add opcodes, compiler behavior, or deterministic natural-language classification.

```text
Accepted in M64.2:
  schema/documentation convention
  value registries
  authoring guidance
  future lint/profile candidates

Not accepted in M64.2:
  runtime-core change
  new Semantic JSON IR object
  new opcode
  deterministic classifier
  FLOW.JOIN / SHARED.TAIL.REFERENCE implementation
```

## 2. Source model

A full-runtime package may declare:

```yaml
program_contract:
  control_level: standard
  execution_mode: full_runtime

interaction_model:
  human_role: content_decision_owner
  ai_role: guided_process_driver
  cli_role: deterministic_validator

process_rail:
  state_tracking: required
  allow_deviation: true
  require_resume_after_deviation: true
  backtracking: restricted

conversation_semantics:
  input_classes:
    - answer_current_node
    - clarification
    - deviation
    - backtrack_request
  unmatched_input_policy: clarify_before_state_change
```

## 3. Validation posture

M64.2 is documentation-first. Suggested future lint behavior:

- `allow_deviation: true` without resume policy: warning now, possible strict-profile error later.
- declared `input_classes` without `routing_rules`: warning now.
- `backtracking: restricted` without invalidation policy: warning now, possible strict-profile error later.
- raw tool output shown directly despite `summarize_before_user`: review finding, not compiler failure.

## 4. Relationship to M64.3

M64.3 may design profile/lint behavior for approval gates and required program-level checks. M64.2 intentionally stops before enforcement.
