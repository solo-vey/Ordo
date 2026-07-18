# DD-ORDO-M68-001: CLI clean-check hardening plan and fixture matrix

Status: accepted

Date: 2026-07-09

## Context

M67 introduced language-level clean package concepts and a minimal `ordo clean-check` CLI implementation. The command now exists, but it needs fixture-backed tests and output/exit-code hardening before broader repo-level enforcement can be trusted.

## Decision

Adopt M68.0 as a planning milestone before additional implementation. The next implementation must start with real synthetic fixtures and explicit expected results.

The M68 first wave should proceed in this order:

1. M68.0 — hardening plan and fixture matrix.
2. M68.1 — real fixture tests.
3. M68.2 — output and exit-code hardening.
4. M68.3 — repo-level hygiene design.
5. M68.4 — optional repo-check integration only if preflight confirms it is safe.

## Boundaries

M68.0 does not implement code. It does not mutate applied packages. It does not regenerate runtime artifacts, lockfiles, compiled IR, or embedded CLI bundles.

## Consequences

- M68 implementation becomes test-first.
- CLI behavior remains tied to the M67 command contract.
- Repo-level hygiene stays design-only until package-level clean-check is hardened.
- Applied-package changes remain delegated.
