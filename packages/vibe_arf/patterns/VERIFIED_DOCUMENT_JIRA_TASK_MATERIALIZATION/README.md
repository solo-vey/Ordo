# VERIFIED_DOCUMENT_JIRA_TASK_MATERIALIZATION v1.0

Reusable pattern for projecting a **verified large document** into a compact Jira implementation task.

The generic core owns the process contract: request runtime testing context, derive the task projection contract, compose the Jira task, materialize it, validate it, and present only a validated artifact.

It deliberately does **not** own domain-specific Jira routing fields or domain-specific testing identifiers. Those belong to bindings/extensions. The test-context request is generic and may accept identifiers, fixtures, accounts, environments, scenarios, or equivalent implementation-test information.

Required Jira task semantics are intentionally stable: summary, implementation goal, supported source references, technical requirements, runtime testing context, and acceptance/verification expectations.

## v1.1 compiler-hardening note

This revision preserves the prior process semantics and adds a mandatory compiler-valid lowering/preflight contract. See `COMPILATION_CONTRACT.md`.
