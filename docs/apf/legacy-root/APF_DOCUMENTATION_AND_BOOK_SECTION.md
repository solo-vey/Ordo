# M62.2 — APF Documentation and Book Section

Status: `passed-docs-consolidation`
Date: 2026-07-08

M62.2 documents `ordo.applied_project_factory` as a standard applied module in the current Ordo language package and connects it with the existing companion utility workflow.

## Scope

Allowed:

```text
add APF usage guide
add APF + companion utility workflow
update standard applied module index
update package README / developer bundle README / changelog / backlog
add book source chapter
run documentation-aligned smoke checks
```

Not allowed:

```text
rewrite APF source/program.ordo.yaml branch logic
apply branch 1 / branch 2 corrections
implement terminal output binding patch
add new IR/opcodes
run generated testcase execution/scoring/calibration
open watchdog/process-boundary hardening
```

## Stable APF placement

```text
packages/ordo_applied_project_factory/
```

APF is a standard applied module, not a companion utility.

## Documentation entry points

```text
APF_STANDARD_MODULE_GUIDE.md
APF_COMPANION_WORKFLOW.md
STANDARD_APPLIED_MODULES.md
packages/ordo_applied_project_factory/docs/APF_STANDARD_MODULE_GUIDE.md
packages/ordo_applied_project_factory/docs/APF_COMPANION_WORKFLOW.md
```

## Status after M62.2

```text
APF imported: yes, from M62.1
APF docs consolidated: yes
APF branch logic rewritten: no
APF language candidates formalized: no
Runtime execution/scoring opened: no
```

## Next recommended step

`M62.3 — APF Language Pattern Extraction Plan`: classify APF improvement candidates before any formal language/IR additions or APF branch rewrite.
