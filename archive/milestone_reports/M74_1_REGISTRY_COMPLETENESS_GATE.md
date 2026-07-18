# M74.1 — Registry and Toolchain Completeness Gate

M74.1 establishes machine-readable registries for source constructs, capabilities, and trace events, and connects them to the existing opcode registry.

Blocking diagnostics:

```text
SOURCE_CONSTRUCT_NOT_IN_REGISTRY
CAPABILITY_SOURCE_CONSTRUCT_NOT_IN_REGISTRY
OPCODE_NOT_IN_REGISTRY
TRACE_EVENT_NOT_IN_REGISTRY
CSG_MODE_INVALID
CSG_MODE_REQUIRED
CSG_STATE_MUTATION_FORBIDDEN
```

Conversation Scope Guard now has minimal linter and compiler support:

```text
conversation_scope_guard Source block
→ deterministic field validation
→ CONVERSATION.SCOPE.DEF Semantic JSON IR op
→ opcode and capability registry checks
```

This does not implement semantic classification or runtime state-protection enforcement. CSG toolchain maturity becomes `partial`, not `integrated`.
