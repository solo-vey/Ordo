# 09. Execution Modes

## Purpose

`execution_mode` tells the reader, model, compiler and runner how much of the execution is enforceable.

## Modes

```yaml
execution_mode: full_runtime | chat_internal | freeform_only
```

### full_runtime

A runner/code orchestrator owns state transitions, node transitions, gate invocation and mechanical checks.

### chat_internal

The model operates in a chat session but may use session-local files/scripts to perform mechanical checks. The check itself may be deterministic, but the invocation point is not fully enforced without an external runner.

### freeform_only

The model follows Ordo discipline through instructions only. This has the weakest guarantee and should not be presented as equivalent to runtime enforcement.

## Runtime context and source of truth

`state.schema` is reserved for business/domain state. Runtime control data such
as `run_id`, active node, closed-node history, session checkpoints and source
digests MUST be stored under the versioned `runtime_context` envelope, not in
business state.

For resumable execution, `runtime/live_session_state.json` MUST bind its
`runtime_context` to the selected `execution_mode`, canonical YAML digest (when
included) and compiled IR digest. A missing, legacy or mismatched binding is a
blocking condition: a helper MUST NOT silently resume it or treat the cached
session as another semantic source.

Mode selection is explicit:

- `full_runtime` and `chat_internal` use the current compiled IR for deterministic helpers.
- `freeform_only` is non-runtime authoring mode and has no implicit executable fallback.

## Required documentation rule

Every Ordo program and every execution trace MUST declare `execution_mode`.
