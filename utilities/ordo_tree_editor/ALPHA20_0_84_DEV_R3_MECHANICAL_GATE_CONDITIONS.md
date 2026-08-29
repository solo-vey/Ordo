# alpha.20.0.84-dev — generic mechanical gate condition evaluator

Runtime now evaluates a safe, fail-closed subset of declarative mechanical gate
`condition:` expressions instead of requiring every deterministic gate to use a
validator file or `required_inputs`.

Supported generic clauses include:
- `state.path is one of A, B`
- `state.path is not one of A, B`
- `state.path is not empty` / `is empty`
- `state.path == VALUE` / `!= VALUE` / `equals VALUE`
- `state.path is true` / `is false`
- top-level `and` / `or`

No Python `eval` is used. Unsupported syntax and missing state remain UNRESOLVED.

Exact regression: JSON_VALIDATION_WORKING_PLAYBOOK_V3_FAIL_FAST — all seven
mechanical gates can evaluate their declared conditions after package-tool state
commits.
