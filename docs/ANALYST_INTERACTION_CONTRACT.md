# Analyst Interaction Contract

`analyst_interaction_contract` is an optional, executable source convention for
analyst-facing nodes. It makes the requested field meaning, response mode,
semantic sufficiency, retry route, draft confirmation, and side-question
behavior explicit.

```yaml
analyst_interaction_contract:
  version: "1.0"
  mode: strict
  side_question_policy: return_to_active_node
  interactions:
    - node: N_SCOPE
      field_meaning: Concise analyst-owned definition of the requested scope.
      response_mode: free_text # free_text | structured
      semantic_sufficiency:
        required: true
        min_length: 8 # or min_items / required_keys
      on_rejected_semantics: N_SCOPE_CLARIFY
      draft_confirmation:
        required: true
        confirmation_node: N_SCOPE_CONFIRM
  gate_failures:
    - gate: G_SCOPE_READY
      message: Scope information is incomplete.
      remedy: Provide the missing business owner and boundary.
      retry_node: N_SCOPE_CLARIFY
  route_labels:
    - from: N_SCOPE
      to: N_SCOPE_CONFIRM
      label: Review scope draft
```

The runtime does not infer meaning from text. It checks only declared,
deterministic criteria (`min_length`, `min_items`, and `required_keys`). A
rejected answer never changes business state; it routes to the declared retry
node. A required draft is also withheld until it is explicitly confirmed.

Use `ordo validate-analyst-interaction PACKAGE` to validate the contract.
Use `ordo explain-gate-failure PACKAGE --gate G_SCOPE_READY` to retrieve an
actionable message, remedy, and retry target for a failed gate.
Use `ordo route-side-question PACKAGE --active-node N_SCOPE --question "..."`
to record the supported non-mutating disposition: answer the side question and
resume the preserved active node.
