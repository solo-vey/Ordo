# Ordo Trace Event Catalog

Canonical trace events introduced by optional capabilities. The machine-readable source is `trace_event_catalog.yaml`.

| Event | Capability | Status |
|---|---|---|
| `conversation.deviation.detected` | `conversation_scope_guard` | specified |
| `conversation.deviation.classified` | `conversation_scope_guard` | specified |
| `conversation.redirect.emitted` | `conversation_scope_guard` | specified |
| `conversation.escalation.changed` | `conversation_scope_guard` | specified |
| `conversation.scope_guard.bypassed_for_control_intent` | `conversation_scope_guard` | specified |
| `conversation.scope_guard.bypassed_for_safety` | `conversation_scope_guard` | specified |
| `process.pause.requested` | `conversation_scope_guard` | specified |
| `process.paused` | `conversation_scope_guard` | specified |
| `process.resume.requested` | `conversation_scope_guard` | specified |
| `process.resumed` | `conversation_scope_guard` | specified |
| `process.exit.requested` | `conversation_scope_guard` | specified |
| `process.exited` | `conversation_scope_guard` | specified |
| `runner.action.blocked` | `conversation_scope_guard` | runtime_enforced |
| `runner.csg.decision` | `conversation_scope_guard` | runtime_enforced |
