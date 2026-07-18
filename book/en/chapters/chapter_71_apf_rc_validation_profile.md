# Chapter 71. APF rc.1 Validation Profile

At this step, APF `v0.1.0-rc.1` remains a standard applied module in the Ordo language package.

The main decision is that APF does not fail because `validate-factory-output` is absent from the parent CLI. This check is currently APF-local / optional until it is formally promoted to the parent CLI.

The mandatory rc.1 profile is:

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

`consistency: passed_with_warnings` is not hidden and does not become a blocker when `go/no-go = go`. The warnings concern contract/default-value coverage and must remain visible in release notes and validation reports.

This step does not change APF logic, add new IR/opcodes, or move APF-local patterns into core runtime.
