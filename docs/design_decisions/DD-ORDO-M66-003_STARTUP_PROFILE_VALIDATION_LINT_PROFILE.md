# DD-ORDO-M66-003 — Startup Profile Validation / Lint Profile

**Milestone:** M66.2  
**Status:** accepted design convention

## Decision

Adopt a standard `startup_profile_validation` convention for packages that declare `startup_package_profile`.

The convention defines profile levels, severity levels, readiness decisions, and canonical check IDs for startup readiness.

## Rationale

M66.0 introduced the package startup standard. M66.1 applied it to History Event Factory. M66.2 adds the validation vocabulary needed to check whether startup surfaces are discoverable, resolved, manifest-covered, and authority-safe.

## Consequences

- Package startup can be reviewed consistently.
- Startup prompts remain guidance, not runtime authority.
- Future CLI/linter implementation has a stable conceptual contract.

## Non-decisions

This decision does not implement CLI enforcement, compiler behavior, or deterministic prompt-safety classification.
