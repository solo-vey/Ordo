# 27. Repo-Level Package Hygiene Model

Status: `M68.3 accepted design / no runtime semantics`

This chapter defines the language-adjacent repository hygiene model used to aggregate package clean-check evidence across a repository.

Repo-level hygiene is not an opcode, not runtime behavior, and not compiler behavior. It is a CLI/release-gate convention layered above `ordo clean-check`.

## Relationship to clean package gate

The clean package gate answers whether one package is clean.

The repo-level hygiene model answers whether a repository release scope is clean enough to hand off.

```text
package root -> ordo clean-check -> package clean result
repo policy + package clean results -> repo hygiene result
```

## Policy-first enforcement

Repo hygiene must be policy-first. The repository must declare which roots are in scope and how each root is treated.

Without policy, an implementation should avoid broad enforcement and should report `not_applicable` or require explicit flags.

## Root treatment

Roots may be:

- `required`;
- `optional`;
- `delegated`;
- `ignored`;
- `not_applicable`.

The default for concrete applied packages is `delegated`.

## Result vocabulary

Repo hygiene uses the same top-level status vocabulary as clean-check:

```text
passed
passed_with_warnings
blocked
not_applicable
```

This keeps CI/release handling consistent across package and repo levels.

## Evidence requirements

A repo hygiene report must include:

- schema version;
- repo root;
- profile;
- fail-on-warning policy;
- per-root results;
- delegated roots;
- warnings;
- errors;
- summary counts;
- exit code.

## Non-goals

Repo hygiene must not:

- introduce IR or opcode semantics;
- mutate package files;
- regenerate runtime/lock/generated artifacts;
- replace package-local ownership;
- auto-apply language standards to applied packages.

## Implementation note

The preferred future CLI integration is:

```bash
ordo repo-check <repo> --clean
```

because repository aggregation belongs with repository checks rather than with the package-only `clean-check` command.
