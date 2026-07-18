# 30. Production Repo Hygiene Policy Model

M70.0 defines a repository-root classification model above package-level clean-check.

## Principle

Release criticality and package clean-check compatibility are independent properties.

A root can be release-critical while its current clean-check treatment remains `not_applicable`.

## Root classification fields

```yaml
root_id: stable identifier
path: repository-relative path
role: semantic repository role
release_critical: true | false | scope_dependent
clean_check_compatible: true | false
current_treatment: required | optional | delegated | ignored | not_applicable
future_checker: checker or contract required before enforcement
```

## Safety invariant

A production policy must not declare a root `required` merely because it is important. It must first have a compatible checker and fixture evidence.

## Current baseline

- `language/`: release-critical, not package-clean compatible.
- `cli/`: release-critical, not package-clean compatible.
- canonical CLI example package: optional and package-clean compatible.
- `packages/`: delegated by default.
- docs/book/utilities: separate repo-level contracts required.
- generated/report areas: ignored by package clean-check and governed by existing repo checks.

## M74.2 scope isolation

Repository hygiene now distinguishes two evidence scopes:

```text
development
release
```

`development` evaluates source hygiene in an installed or actively tested worktree. Generated Python metadata is blocking only when Git reports it as tracked. Local untracked `__pycache__`, `.pyc`, and `.egg-info` artifacts remain visible in the report but do not block the development gate.

`release` evaluates an isolated candidate tree and strictly forbids generated Python metadata anywhere in that tree. Release CI must create the candidate from a clean source export, such as `git archive HEAD`, rather than inspect the checkout after editable installation.

A report must preserve its `hygiene_scope`. A development PASS is not valid release evidence.
