# Process Rail Schema Convention

Status: `M64.2 accepted-docs-schema-convention`

M64.2 documents `process_rail` as a source-level convention for keeping a conversational AI-guided process on track.

It is **not** a new runtime opcode and does not make conversation handling fully deterministic. It declares the package policy for deviations, resume behavior, backtracking, and state invalidation.

```text
process_rail
  → tracks whether state is required
  → declares deviation policy
  → declares resume policy
  → declares backtracking policy
  → declares what happens to dependent state after changes
```

## Canonical source shape

```yaml
process_rail:
  rail_id: default_runtime_rail
  state_tracking: required
  allow_deviation: true
  require_resume_after_deviation: true
  resume_policy: return_to_current_node_after_deviation
  backtracking: restricted
  backtracking_policy:
    invalidates_dependent_state: true
    requires_review_before_continue: true
  skip_ahead_policy: block_until_required_state_ready
  stale_answer_policy: require_reconfirmation
```

## Attribute semantics

### `rail_id`

- Type: `string`
- Required: optional.
- Meaning: local identifier for the rail policy.
- Validation behavior: should be stable if referenced by docs, tests, or reports.

### `state_tracking`

- Type: `enum`
- Required: recommended.
- Allowed values:
  - `required`: the process depends on explicit state tracking.
  - `recommended`: state should be tracked but not every path requires it.
  - `none`: no explicit state tracking claim is made.
- Runtime meaning: affects whether answers can safely change state or must remain freeform notes.

### `allow_deviation`

- Type: `boolean`
- Required: recommended.
- Meaning: whether users may ask side questions or leave the current path without failing the process.
- Validation behavior: if `true`, a resume policy should be declared.

### `require_resume_after_deviation`

- Type: `boolean`
- Required: recommended when `allow_deviation: true`.
- Meaning: after a side path, the AI must return the user to the active node or declared resume point.

### `resume_policy`

- Type: `enum or convention string`
- Required: recommended when deviations are allowed.
- Known values:
  - `return_to_current_node_after_deviation`: return to the interrupted node.
  - `return_to_last_unresolved_question`: return to the last unanswered required question.
  - `ask_user_where_to_resume`: ask the user to choose resume point.
  - `resume_at_declared_checkpoint`: resume at an explicit checkpoint.
- Validation behavior: unknown values should be documented in package policy docs.

### `backtracking`

- Type: `enum`
- Required: recommended.
- Allowed values:
  - `disabled`: user cannot move backward through the process.
  - `restricted`: user can move backward under explicit policy and review.
  - `enabled`: user may move backward freely, subject to state consistency.
- Runtime meaning: controls whether prior decisions can be reopened.

### `backtracking_policy`

- Type: `map`
- Required: recommended when `backtracking` is `restricted` or `enabled`.
- Useful fields:
  - `invalidates_dependent_state` (`boolean`): changing an earlier answer invalidates downstream dependent state.
  - `requires_review_before_continue` (`boolean`): downstream state must be reviewed before continuing.
  - `preserve_artifacts_until_reconfirmed` (`boolean`): artifacts stay visible but are not considered current until reconfirmed.

### `skip_ahead_policy`

- Type: `enum or convention string`
- Required: optional.
- Known values:
  - `block_until_required_state_ready`: do not allow future-node answers until required state exists.
  - `capture_as_future_context`: store the input as future context without changing current node.
  - `ask_clarification`: ask whether the user wants to skip ahead.

### `stale_answer_policy`

- Type: `enum or convention string`
- Required: optional.
- Known values:
  - `require_reconfirmation`: ask the user to reconfirm stale answers.
  - `invalidate_and_reask`: invalidate stale answer and ask again.
  - `keep_with_warning`: keep answer but mark warning.

## Typical mistakes

- `allow_deviation: true` without a resume policy.
- `backtracking: enabled` without invalidation rules.
- Treating a side question as an answer to the active node.
- Treating a future-node answer as current state without confirmation.
