# M63.0 — APF RC Validation Profile Plan

## Required parent-compatible validation commands

For APF rc.1 on the M62/M63 parent language package line, the required validation profile is:

```text
lint
compile
test
coverage
validate-state
next-step
validate-output
validate-artifacts
consistency
go-no-go
repo-check clean source
```

## Optional / APF-local validation

```text
validate-factory-output
```

This command must not block rc.1 acceptance merely because it is not a parent CLI command, if equivalent APF-local factory-output validation is covered by APF reports or runtime package artifacts.

## Warning policy

```text
consistency: passed_with_warnings
go/no-go: go
```

Warnings are non-blocking when they do not affect deterministic execution, but they must remain visible in RC notes and known limitations.

## M63.2 requirement

M63.2 must convert this plan into an APF-specific validation profile document and updated validation report.
