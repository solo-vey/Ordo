# VERIFIED_DOCUMENT_CODE_IMPLEMENTATION v1.1

Advanced reusable Vibe pattern for implementing a **verified domain document/specification** in an accessible codebase.

This is intentionally a separate, more complete pattern than the library's smaller `IMPLEMENTATION_CHANGE`. The two are not composed in v1.1.

## Use when
Use after an upstream process has produced a verified immutable document identity and the playbook must ground that document in a repository, decide ownership/autonomy, expose the implementation contract, perform a bounded local change when safe, verify the exact resulting revision, and return a result/receipt.

## Generic core
`verified document → code source → repository grounding/profile → implementation obligations → repository scope → implementation change contract → mandatory informational presentation → exact 3-way scope/autonomy branch → plan/edit → tests → documentation → revision-bound verification → bounded repair or result packaging → completion`

## Required domain extensions
Bind domain/repository knowledge through: `document_to_requirements_adapter`, `repository_architecture_adapter`, `repository_scope_policy`, `autonomy_policy`, `test_obligation_policy`, `verification_adapter`, `implementation_contract_presentation_adapter`, `verification_recovery_policy`, and `result_packaging_policy`.

## Three-way implementation decision
`implementation_branch_gate` is **not a binary gate**. It must deterministically return exactly one of:
- `NO_LOCAL_CHANGE` — verified document creates no local mutation obligation;
- `HANDOFF_REQUIRED` — shared/architectural/external/unresolved ownership;
- `LOCAL_SAFE` — bounded local ownership and autonomy contract permit mutation.

Unknown/missing/multiple outcomes fail closed. A compiler/projection must preserve all three routes and must not lower this decision to PASS/FAIL.

## Implementation contract presentation
The derived implementation change contract is presented before any local mutation. This presentation is informational and does **not** become an approval gate unless the host playbook explicitly adds a separate authority contract.

## Verification freshness and bounded recovery
Every persisted code/test/documentation mutation advances `implementation_revision_identity` and invalidates older `local_verification_evidence`. Verification PASS is valid only for the current revision.

On failure: diagnose → increment recovery attempt → deterministic recovery-budget gate. The default maximum is 2 repair cycles (host may configure 0–5). `RETRY` returns to planning; exhausted/unsafe repair fails closed as `IMPLEMENTATION_VERIFICATION_BLOCKED`.

## Important invariants
- Never implement requirements not traceable to the verified input document.
- Never mutate before repository grounding, scope/autonomy decision, and implementation-contract presentation.
- Shared/architectural/unresolved ownership is a handoff, not automatic edit.
- Every implemented obligation needs test/assertion or executable verification coverage.
- Stale or unavailable verification is never PASS.
- Recovery is bounded.
- Package only persisted changed files; in-place source may bypass archive creation.

## Relation to IMPLEMENTATION_CHANGE
Treat `IMPLEMENTATION_CHANGE` as the simplified library pattern and this pattern as the advanced verified-document-to-code lifecycle. v1.1 intentionally makes no nested-composition claim.

## v1.2 compiler-hardening note

This revision preserves the prior process semantics and adds a mandatory compiler-valid lowering/preflight contract. See `COMPILATION_CONTRACT.md`.
