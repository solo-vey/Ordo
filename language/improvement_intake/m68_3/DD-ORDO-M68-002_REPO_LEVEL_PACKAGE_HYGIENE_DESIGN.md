# DD-ORDO-M68-002 — Repo-Level Package Hygiene Design

Status: `accepted`

Date: 2026-07-10

## Context

M67 introduced `ordo clean-check` as a package-level clean gate. M68.0 planned hardening, M68.1 added fixture tests, and M68.2 stabilized output and exit-code behavior.

The next design question is whether clean-check should scale to the whole repository.

## Decision

Repo-level clean aggregation should be designed as a `repo-check --clean` extension, not as a broadening of package-level `clean-check`.

The preferred future command is:

```bash
ordo repo-check <repo> --clean
```

The implementation is deferred. M68.3 only defines the policy model, aggregation behavior, evidence shape, and scope guard.

## Rationale

`clean-check` is intentionally package-scoped. Repository hygiene requires discovery, scope policy, delegation, and aggregation. These belong with repo-level checks.

## Scope boundary

Applied packages are delegated by default. They must not be checked or modified unless an explicit repo policy opts them in.

## Consequences

Future M68.4 implementation must:

- preserve existing `repo-check` behavior;
- call clean-check logic programmatically;
- use synthetic repo fixtures for tests;
- keep applied packages out of default enforcement;
- produce stable JSON evidence.
