# EXECUTION_TRACE Registry Values

## Status values
`created`, `running`, `paused`, `completed`, `failed`, `cancelled`, `interrupted`

## Capture levels
`minimal`, `standard`, `full`, `audit`

## Replay modes
`deterministic`, `re_evaluate`, `simulation`, `audit_only`

## Actor types
`analyst`, `user`, `model`, `runtime`, `system`, `service`

## Trace sources
`model_self_report`, `runtime_enforced`, `hybrid`

## Event types
`run_started`, `run_paused`, `run_resumed`, `run_completed`, `run_failed`, `run_cancelled`, `node_entered`, `node_exited`, `path_selected`, `phase_changed`, `question_asked`, `user_input`, `input_validated`, `input_rejected`, `field_assigned`, `field_cleared`, `action_started`, `action_completed`, `action_failed`, `external_call`, `decision_evaluated`, `decision_selected`, `branch_selected`, `gate_evaluated`, `gate_passed`, `gate_failed`, `gate_overridden`, `state_snapshot`, `state_changed`, `template_selected`, `artifact_generation_started`, `artifact_generated`, `artifact_updated`, `artifact_validation`, `warning_raised`, `error_raised`, `recovery_applied`, `approval_requested`, `approval_granted`, `approval_rejected`, `checkpoint_created`
