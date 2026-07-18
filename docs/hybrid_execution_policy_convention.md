# Hybrid Execution Policy Convention

Status: `M64.2 documentation alignment`

M64.2 aligns `interaction_model`, `process_rail`, and `conversation_semantics` with the existing Hybrid Execution Model.

The stable principle remains:

```text
AI leads conversation.
CLI/helper tools perform deterministic checks.
Human owns content and approval decisions.
```

## Canonical relationship

```yaml
program_contract:
  execution_mode: full_runtime
  runtime_profile:
    ai_layer: guided_process_driver
    cli_layer: deterministic_validator
    human_layer: content_decision_owner

interaction_model:
  human_role: content_decision_owner
  ai_role: guided_process_driver
  cli_role: deterministic_validator

process_rail:
  state_tracking: required
  allow_deviation: true
  require_resume_after_deviation: true

conversation_semantics:
  unmatched_input_policy: clarify_before_state_change
```

## Boundary

M64.2 does not make these fields executable by themselves. A package may declare them to guide AI behavior, documentation, review, and future lint/profile checks.
