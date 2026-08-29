> M64.2 note: hybrid execution is now aligned with `interaction_model`, `process_rail`, and `conversation_semantics` conventions. AI leads conversation, CLI/helper tools validate deterministic checks, and humans own content/approval decisions. No runtime-core behavior changes are introduced by M64.2.

# 13. Hybrid Execution Model

## 1. Purpose

Hybrid Execution Model defines how compiled Semantic JSON IR is used during live execution.

Ordo execution is led by an AI Ordo Executor. Semantic JSON IR provides the Process Rail. Deterministic helper tools validate mechanical parts of the process.

## 2. Execution loop

```text
human_input
  → ai_interpretation
  → rail_mapping
  → proposed_state_update
  → deterministic_helper_validation
  → ai_human_explanation
  → next_conversation_move
```

## 3. Required execution semantics

An Ordo execution profile should define:

```yaml
hybrid_execution:
  ai_role: ordo_executor
  semantic_ir_role: process_rail
  cli_role: deterministic_helper
  raw_tool_output_policy: ai_interprets_before_user
  allow_deviation: true
  require_resume_after_deviation: true
  backtracking: enabled
```

## 4. Input classification

The AI Ordo Executor classifies human input before updating state:

```yaml
allowed_input_classes:
  - answer_current_question
  - answer_future_question
  - correction_previous_answer
  - clarification_request
  - domain_context
  - approval
  - refusal
  - out_of_scope
```

## 5. Helper output policy

Tool output is machine feedback for the AI. It must not be exposed to the human as a raw dump unless explicitly requested.

## 6. Output gate

Final outputs can be generated only after the relevant gates pass or a human approval gate explicitly allows generation.
