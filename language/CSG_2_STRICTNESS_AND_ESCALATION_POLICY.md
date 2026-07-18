# CSG-2 — Strictness and Escalation Policy

**Status:** normative integration artifact  
**Parent contract:** `ORDO-CAP-CSG-001`

## 1. Rule

When `Conversation Scope Guard` is enabled, its strictness mode and escalation policy MUST be explicit and mechanically resolvable.

Canonical operations:

```text
DEVIATION.HANDLE
DEVIATION.ESCALATE
```

A mode name alone is insufficient unless its behavior resolves to canonical policy fields.

## 2. Canonical strictness modes

```text
advisory
guided_redirect
strict_redirect
locked_process
```

### `advisory`

May answer an unrelated question briefly, then MUST return to the active process.

### `guided_redirect`

MUST NOT develop the unrelated topic. It acknowledges the message, explains the active process boundary, and returns to the active question.

### `strict_redirect`

MUST NOT answer or develop the unrelated topic. It emits a scope notice and repeats the active question.

### `locked_process`

Accepts only active answers and declared process-control intents. Other input is redirected or escalated.

## 3. Canonical resolved policy

```yaml
strictness_policy:
  mode: "guided_redirect"
  answer_external_question: false
  acknowledge_message: true
  explain_scope_boundary: true
  repeat_active_question: true
  preserve_state: true
  allowed_external_answer_scope: "none"
```

Compiler/runtime MUST resolve every mode to these fields before execution.

## 4. Mode matrix

| Field | advisory | guided_redirect | strict_redirect | locked_process |
|---|---:|---:|---:|---:|
| answer external question | brief | no | no | no |
| acknowledge unrelated message | yes | yes | optional | no |
| explain scope boundary | optional | yes | yes | yes |
| repeat active question | yes | yes | yes | yes |
| preserve state | yes | yes | yes | yes |
| accept related context | yes | yes | yes | only if declared |
| accept process-control intents | yes | yes | yes | yes |

No mode may disable state preservation for `unrelated_topic`.

## 5. Escalation scope

Default counter scope:

```yaml
counter_scope: "active_node"
```

Allowed scopes:

```text
active_node
deviation_session
process_run
```

`process_run` MUST be explicitly selected and SHOULD produce a diagnostic because unrelated messages far apart in a long run may otherwise be treated as repeated deviations.

Default reset rules:

```yaml
reset_on:
  - "valid_process_answer"
  - "node_transition"
  - "process_resume"
```

## 6. Canonical escalation levels

```yaml
levels:
  1:
    action: "gentle_redirect"
  2:
    action: "explicit_scope_reminder"
  3:
    action: "offer_pause_or_exit"
  4:
    action: "suspend_until_process_choice"
```

Level progression MUST be monotonic within the active counter scope.

The runtime MUST NOT skip a level unless the policy explicitly defines `jump_conditions`.

## 7. Controlled suspension

`suspend_until_process_choice` is not process completion.

It MUST set:

```yaml
status: "awaiting_process_choice"
normal_node_execution: false
state_preserved: true
allowed_choices:
  - "return_to_active_step"
  - "pause_process"
  - "exit_process"
```

The runtime MUST NOT mark the process `completed`.

## 8. Counter behavior

A deviation counter increments only for:

```text
unrelated_topic
```

By default it MUST NOT increment for:

```text
clarification
correction
backtrack_request
requirement_change
pause_request
resume_request
exit_request
process_meta_question
related_context
unsafe_or_emergency_message
unclassifiable_input
```

`unclassifiable_input` may have a separate ambiguity counter but MUST NOT silently increase the unrelated-topic escalation level.

## 9. Response-action contract

Canonical escalation actions:

```text
gentle_redirect
explicit_scope_reminder
offer_pause_or_exit
suspend_until_process_choice
```

Every action MUST resolve to a response contract.

Example:

```yaml
response_action:
  id: "offer_pause_or_exit"
  required_parts:
    - "repeated_deviation_notice"
    - "active_step_reference"
    - "return_option"
    - "pause_option"
    - "exit_option"
```

A response action MUST NOT mutate business state.

## 10. Overrides

A playbook MAY override mode behavior or escalation levels only explicitly.

```yaml
strictness_override:
  target: "guided_redirect"
  field: "acknowledge_message"
  value: false
  reason: "regulated intake requires minimal redirect text"
```

Forbidden overrides:

```text
allow unrelated_topic to confirm state
allow unrelated_topic to change path
allow unrelated_topic to complete node
block safety bypass
remove all pause/exit escape behavior from locked_process
mark controlled suspension as completed
```

## 11. Diagnostics

```text
CSG201_UNKNOWN_MODE
CSG202_MODE_NOT_RESOLVED
CSG203_UNSAFE_STATE_POLICY
CSG204_INVALID_COUNTER_SCOPE
CSG205_PROCESS_RUN_COUNTER_WARNING
CSG206_INVALID_ESCALATION_ACTION
CSG207_ESCALATION_LEVEL_GAP
CSG208_ILLEGAL_LEVEL_SKIP
CSG209_SUSPENSION_MARKED_COMPLETE
CSG210_LOCKED_PROCESS_WITHOUT_ESCAPE
CSG211_NON_DEVIATION_INCREMENTED_COUNTER
CSG212_RESPONSE_ACTION_MUTATES_BUSINESS_STATE
```

Blocking diagnostics:

```text
CSG201
CSG203
CSG206
CSG207
CSG209
CSG210
CSG212
```

## 12. Trace events

Required events:

```text
conversation.redirect.emitted
conversation.escalation.changed
conversation.scope_guard.suspended
```

Example:

```yaml
event_type: "conversation.escalation.changed"
node_id: "N_CONFIRM_SOURCE_FIELD"
counter_scope: "active_node"
previous_level: 2
new_level: 3
trigger_classification: "unrelated_topic"
action: "offer_pause_or_exit"
state_changed: false
```

## 13. Minimum regression set

Required cases:

```text
advisory brief answer then redirect
guided redirect without external answer
strict redirect
locked process control-intent acceptance
first unrelated message
second unrelated message
third unrelated message
fourth unrelated message
counter reset after valid answer
counter reset after node transition
counter reset after resume
non-deviation does not increment counter
controlled suspension preserves state
controlled suspension is not completion
locked process retains pause/exit escape
```

## 14. Conformance

CSG-2 conforms when:

- mode resolves to canonical behavior fields;
- unrelated-topic handling preserves state;
- escalation counter scope is explicit;
- reset behavior is explicit;
- level progression is deterministic;
- controlled suspension is non-terminal;
- process-control intents do not increment the deviation counter;
- forbidden overrides are rejected;
- trace records escalation changes.
