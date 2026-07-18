# Ordo v0.12 Lint Rules

## Errors

| Code | Rule |
|---|---|
| `E_GATE_METHOD_REQUIRED` | Gate has no `method`. |
| `E_GATE_TRUST_CLASS_REQUIRED` | Gate has no `trust_class`. |
| `E_GATE_METHOD_TRUST_MISMATCH` | `method` and `trust_class` are incompatible. |
| `E_EXECUTION_MODE_REQUIRED` | Program or trace has no `execution_mode`. |
| `E_CONTROL_LEVEL_REQUIRED` | Program has no `control_level`. |
| `E_STRICT_TEST_COVERAGE_REQUIRED` | `strict` program lacks required test coverage. |
| `E_UNRESOLVED_LOCAL_ID` | Compiled IR contains local ID where namespaced ID is required. |
| `E_INCLUDE_VERSION_REQUIRED` | Library/Profile/Domain Pack include lacks version. |
| `E_UNRESOLVED_LAYER_CONFLICT` | Layer conflict exists without explicit override. |
| `E_NODE_UNMATCHED_INPUT_UNHANDLED` | Node with constrained answers lacks `on_unmatched_input`. |

## Warnings

| Code | Rule |
|---|---|
| `W_SELF_VERIFICATION_NO_PROTOCOL` | `self_verification` gate lacks evidence protocol. |
| `W_SELF_CONSISTENCY_LOW_RUNS` | `self_consistency` gate has fewer than 3 runs. |
| `W_CHAT_INTERNAL_NO_AUDIT` | Critical `chat_internal` program lacks end-of-run audit. |
| `W_FREEFORM_FORMALIZATION_RECOMMENDED` | FREEFORM incident threshold exceeded. |
| `W_LIGHT_TOO_MANY_GATES` | `light` program may need `standard` control level. |
| `W_STRICT_FREEFORM_UNCOVERED` | `strict` program has uncovered FREEFORM blocks. |
