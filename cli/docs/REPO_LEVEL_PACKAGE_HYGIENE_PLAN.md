# Repo-Level Package Hygiene Plan

Status: `M68.3 accepted design / implementation deferred to M68.4 candidate`

This document summarizes the repo-level hygiene line for `ordo clean-check` and points to the fuller design in `cli/docs/REPO_LEVEL_PACKAGE_HYGIENE_DESIGN.md`.

## Current decision

M68.3 selects this future integration direction:

```bash
ordo repo-check <repo> --clean
```

The alternative command shape remains backlog:

```bash
ordo clean-check <repo> --repo
```

## Why repo-check owns repo hygiene

`ordo clean-check <package>` is package-level. Repo hygiene is aggregation and policy over many roots, so it belongs with `repo-check`, which already performs repository-level checks.

## Required policy before enforcement

A repo-level clean implementation must have an explicit policy for:

- roots in scope;
- root roles;
- required vs optional vs delegated clean-check treatment;
- warning behavior;
- release-blocking behavior;
- evidence output path;
- applied-package opt-in boundaries.

## Default boundary

Applied packages are delegated by default. Repo hygiene must not silently validate or mutate them.

## Future implementation candidate

M68.4 may implement:

```bash
ordo repo-check <repo> --clean --profile standard --json --fail-on-warning --out reports/repo_clean_check.json
```

Only after preflight confirms it can be added without breaking existing `repo-check` behavior.

## M68.4 status

The optional integration step is implemented as `ordo repo-check <repo> --clean`. The implementation uses an explicit repo hygiene policy and delegates applied packages by default when no policy is present.
