# M62.1 — APF Package Import

Status: `passed-package-import`  
Date: 2026-07-08

M62.1 imports `ordo.applied_project_factory` v0.1.0-alpha.14 into the current Ordo language package as a **standard applied module**.

## Package location

```text
packages/ordo_applied_project_factory/
```

## Category

```text
standard applied module
```

APF is not a companion utility. It is a self-hosted authoring process for creating or improving Ordo playbooks/process packages.

## Import boundary

M62.1 is a controlled package import. It does not rewrite APF branch logic and does not promote APF pattern candidates to formal IR/opcodes.

Allowed:

```text
copy APF alpha.14 package
refresh current CLI lint / compile / static test
add import notes
sync package indexes and docs
```

Not allowed in this milestone:

```text
runtime-core changes
APF branch-logic rewrite
terminal output binding implementation patch
runtime execution of generated testcases
scoring / calibration / model benchmark
watchdog / process-boundary hardening
```

## APF status after import

| Item | Status |
|---|---|
| APF module version | `0.1.0-alpha.14` |
| package location | `packages/ordo_applied_project_factory/` |
| source YAML imported | yes |
| output templates imported | yes |
| docs imported | yes |
| current CLI lint | expected pass |
| current CLI compile | expected pass |
| current CLI static test | expected pass |
| full validation | deferred by design |
| APF human review closure | not claimed |

## Relationship to utilities

APF can be inspected by the existing companion utilities:

```text
APF source/program.ordo.yaml
  → Visual Graph Generator for Mermaid/SVG/PNG structure views
  → PathWalk for source-level graph summary and review artifacts
```

These utilities remain downstream aids; they do not decide APF runtime correctness.

## Next step

M62.2 should document APF as a standard applied module in the book and user-facing package docs, without starting APF branch rewrites.
