# CLI Validation Summary — ordo.applied_project_factory v0.1.0-rc.1

Status: release-candidate / go.  
CLI status: parent-compatible rc.1 validation profile executed; warnings visible and non-blocking.  
Parent language line: Ordo v0.12 / M62 line closure.  
M63.2: validation profile and known limitations formalized.

## Required parent-compatible validation profile

```text
lint: passed
compile: passed
test: passed
coverage: passed
validate-state: passed
next-step: ready_for_ai_next_move
validate-output: passed
validate-artifacts: passed
consistency: passed_with_warnings
go/no-go: go
repo-check clean source: passed
```

## Optional / APF-local validation

```text
validate-factory-output: APF-local / optional
```

Absence of `validate-factory-output` in the parent CLI is not a release-candidate blocker when equivalent APF-local reports or runtime package validation cover factory output readiness.

## Non-blocking warnings policy

`consistency: passed_with_warnings` remains visible and non-blocking. The current warning class is contract/default-value coverage; it does not block deterministic execution path readiness for rc.1.
