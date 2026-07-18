# APF RC Known Limitations — M63.2

Status: `non-blocking / visible`  
Module id: `ordo.applied_project_factory`  
Version: `0.1.0-rc.1`

## Non-blocking warnings policy

APF rc.1 has:

```text
consistency: passed_with_warnings
go/no-go: go
```

Warnings are not blockers, but they must remain visible in reports and release notes.

## Current warning class

The current known warning class is contract/default-value coverage. It does not invalidate deterministic execution path readiness for rc.1.

## Known limitations

| Limitation | Status | Release impact |
|---|---|---|
| `FLOW.JOIN` | future IR candidate | non-blocking |
| `SHARED.TAIL.REFERENCE` | future IR candidate | non-blocking |
| `validate-factory-output` | APF-local / optional | non-blocking until promoted to parent CLI |
| contract/default-value coverage warnings | visible warnings | non-blocking |

## Boundary

M63.2 does not redesign APF process logic, promote new IR/opcodes, or change parent CLI semantics. It documents the rc.1 validation boundary.
