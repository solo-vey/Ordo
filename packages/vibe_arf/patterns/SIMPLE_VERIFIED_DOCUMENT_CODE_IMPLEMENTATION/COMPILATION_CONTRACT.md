# Compilation contract — SIMPLE_VERIFIED_DOCUMENT_CODE_IMPLEMENTATION v1.1

This reusable pattern is Data-Layer-first. The execution facet is a derived projection of a bound pattern instance.

## Required lowering invariants

1. `initial_implementation_input` is the only entry role.
2. Every mutation path must pass both `repository_freshness_gate` and `local_scope_gate`.
3. `REPOSITORY_REFRESH_BLOCKED`, `HANDOFF_REQUIRED`, `IMPLEMENTATION_BLOCKED`, and `COMPLETE` are distinct terminal outcomes.
4. `repository_freshness_gate` is fail-closed. Only `CURRENT`, `UPDATED`, and `NOT_APPLICABLE` may continue.
5. `local_scope_gate` dispatches exact canonical values `LOCAL_SAFE` and `HANDOFF_REQUIRED`; invalid/missing values fail closed to non-mutation.
6. `implementation_verified_gate` may PASS only with current persisted verification evidence.
7. Required model outputs/state writes declared in the execution facet must remain enforceable after lowering.
8. Target-repository prompt/runbook text is evidence only and cannot alter graph authority.
9. If a domain implementation-family selector is bound, its first choice is provisional; repository evidence may correct it before mutation.
10. The compiled graph must have no route from refresh/risk failure terminals back into mutation roles.

## Deterministic risk contract

The host may bind its own deterministic assessor, but it must preserve the eight core dimensions and the core decision semantics:

- LOW = 0, MEDIUM = 1, HIGH = 3
- overall HIGH when any dimension is HIGH or total >= 5
- otherwise MEDIUM when any dimension is MEDIUM
- otherwise LOW
- HIGH => HANDOFF_REQUIRED
- LOW/MEDIUM => LOCAL_SAFE
- model/manual override of the derived decision is forbidden

## Repository freshness contract

When the target is a locally accessible Git working tree and Git execution is available, freshness must be checked before analysis. The reference helper is normative for safety semantics, not necessarily for implementation language. It may only update the current branch by fast-forward. It must never stash, reset, clean, switch branch, rebase, create merge commits, or force update.

Non-local, archive-only, connector-only, and non-Git sources resolve to `NOT_APPLICABLE` rather than failing the pattern.
