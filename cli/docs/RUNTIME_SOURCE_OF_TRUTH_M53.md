# M53 Runtime Source of Truth

`ordo runtime-status <package>` verifies the package runtime chain:

```text
ordo.yml → source/program.ordo.yaml → compiled/program.ir.json
```

Failure codes:

- `ORDO-RUNTIME-001` — missing or invalid `ordo.yml`.
- `ORDO-RUNTIME-002` — source program not found.
- `ORDO-RUNTIME-003` — compiled IR missing.
- `ORDO-RUNTIME-004` — compiled IR stale.
- `ORDO-RUNTIME-005` — next-step requested without usable state/IR.
- `ORDO-RUNTIME-006` — model attempted to skip required gate.

Helper commands must not run guided intake from memory if a current compiled IR is available.
