# DD-ORDO-M54-001 — Runtime Guided Intake Entry Protocol

## Decision

Guided-intake packages may declare a `START_HERE_RUNTIME_MODE.md` entrypoint. AI Ordo Developer/Executor sessions must load the package as a runtime workspace and derive the first step from compiled IR.

## Rationale

Previous failures came from model memory overriding runtime order. A deterministic entry command makes the runtime state explicit before the first user question.

## Consequences

- `ordo runtime-entry` becomes the standard startup guard.
- Missing or empty runtime start files fail with `ORDO-RUNTIME-007`.
- The first guided question is derived from compiled IR.
- Package-specific path guards can be documented without rewriting the whole language.
