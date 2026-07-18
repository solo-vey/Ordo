# Ordo Capability Catalog

The machine-readable registry is `capability_catalog.yaml`.

## Conversation Scope Guard

- Contract: `ORDO-CAP-CSG-001`
- Source construct: `conversation_scope_guard`
- Core default: disabled
- Status: language-integrated optional specification
- Opcodes: `CONVERSATION.SCOPE.DEF`, `DEVIATION.CLASSIFY`, `DEVIATION.HANDLE`, `DEVIATION.ESCALATE`, `STATE.PROTECT`, `PROCESS.PAUSE`, `PROCESS.RESUME`, `PROCESS.EXIT`
- Trace events: `conversation.deviation.detected`, `conversation.deviation.classified`, `conversation.redirect.emitted`, `conversation.escalation.changed`, `conversation.scope_guard.bypassed_for_control_intent`, `conversation.scope_guard.bypassed_for_safety`, `process.pause.requested`, `process.paused`, `process.resume.requested`, `process.resumed`, `process.exit.requested`, `process.exited`
