# Conversation Semantics Schema Convention

Status: `M64.2 accepted-docs-schema-convention`

M64.2 documents `conversation_semantics` as a policy contract for classifying human input during AI-guided execution.

This is **not** a deterministic natural-language classifier. It declares the input classes the AI/runtime policy should recognize, the routing rules expected by the package, and the policy for unmatched input.

```text
conversation_semantics
  → names expected input classes
  → declares routing rules for those classes
  → declares unmatched-input policy
  → declares clarification policy
  → declares resume policy after deviations
```

## Canonical source shape

```yaml
conversation_semantics:
  input_classes:
    - answer_current_node
    - clarification
    - deviation
    - backtrack_request
    - new_requirement
  routing_rules:
    answer_current_node: evaluate_current_node_gate
    clarification: answer_without_state_change
    deviation: answer_then_resume
    backtrack_request: apply_backtracking_policy
    new_requirement: capture_and_route_to_change_review
  unmatched_input_policy: clarify_before_state_change
  clarification_policy: do_not_advance_node
  resume_policy: return_to_current_node_after_deviation
```

## Attribute semantics

### `input_classes`

- Type: `list[enum or convention string]`
- Required: recommended.
- Core allowed values:
  - `answer_current_node`: user answers the current node/question.
  - `clarification`: user asks for explanation without intending to change state.
  - `deviation`: user moves temporarily away from the current path.
  - `backtrack_request`: user asks to return to an earlier decision/node.
  - `new_requirement`: user introduces a new requirement or scope change.
  - `approval`: user explicitly approves the current proposal/artifact/gate.
  - `refusal`: user rejects the current proposal or refuses a path.
  - `out_of_scope`: input does not belong to the declared process.
- Validation behavior: package-local classes are allowed only when `routing_rules` describes them.

### `routing_rules`

- Type: `map[input_class -> routing_action]`
- Required: recommended.
- Common routing actions:
  - `evaluate_current_node_gate`: interpret input as an answer and evaluate the active gate.
  - `answer_without_state_change`: respond but do not advance or mutate state.
  - `answer_then_resume`: handle deviation, then return to resume policy.
  - `apply_backtracking_policy`: reopen a previous decision under process rail rules.
  - `capture_and_route_to_change_review`: capture new requirement and route to change review.
  - `ask_clarification`: ask the user what they intended.
  - `reject_as_out_of_scope`: explain that input is outside the process.
- Validation behavior: every declared class should have a routing rule or inherit a documented default.

### `unmatched_input_policy`

- Type: `enum`
- Required: recommended.
- Allowed values:
  - `clarify_before_state_change`: ask for clarification before changing state.
  - `reject`: reject input as not usable for the current node.
  - `log_and_continue`: record the input but do not change route/state.
  - `route_to_human_review`: ask human owner how to treat it.
- Runtime meaning: prevents accidental state mutation from ambiguous text.

### `clarification_policy`

- Type: `enum or convention string`
- Required: optional.
- Known values:
  - `do_not_advance_node`: clarification answers must not move to the next node.
  - `may_update_explanation_only`: AI may update explanation text but not state.
  - `ask_if_user_intends_answer`: ask whether the clarification is also an answer.

### `resume_policy`

- Type: `enum or convention string`
- Required: recommended when deviations are allowed.
- Known values mirror `process_rail.resume_policy`:
  - `return_to_current_node_after_deviation`
  - `return_to_last_unresolved_question`
  - `ask_user_where_to_resume`
  - `resume_at_declared_checkpoint`

## Typical mistakes

- Adding an input class without a routing rule.
- Treating clarification as answer to the current node.
- Treating unmatched text as state-changing input.
- Letting AI “silently decide” whether a new requirement changes the process.
