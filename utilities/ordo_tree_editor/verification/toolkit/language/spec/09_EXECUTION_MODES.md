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

## Required documentation rule

Every Ordo program and every execution trace MUST declare `execution_mode`.
