# M88.0 — Anti-pattern Layer scope and existing-language capability audit

Status: **completed**

## Backlog split

- BL-ORDO-020 is now the active Anti-pattern Layer.
- BL-ORDO-024 was created for Process Pattern Engineering.

## Existing reusable capabilities

- `GATE.REPORT`
- `PATH.EXPLAIN`
- `STATE.SNAPSHOT`
- `STATE.DIFF`
- `DECISION.LOG`
- generic gate, recovery, severity, advisory and blocking concepts

## Missing canonical primitives

- `ANTIPATTERN.DEF`
- `DETECT.RULE`
- `ANTIPATTERN.FINDING`

`REMEDIATION.ACTION`, `RECOVERY.ROUTE` and `EVIDENCE.REQUIREMENT` should not be separate opcodes yet. Their first version should be represented as structured fields inside `ANTIPATTERN.DEF`.

## Architecture decision

- Language: declarations and schemas.
- Runtime: detection, matching, severity, enforcement and findings.
- APF: domain registry and activation profile.

## Next milestone

M88.1 — canonical `ANTIPATTERN.DEF` schema and initial registry.
