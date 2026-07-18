# M63.0 — APF RC Delta Review

**Base:** M62 line closure imported APF `v0.1.0-alpha.14`  
**Target:** APF `v0.1.0-rc.1`, source base `alpha.21`  
**Status:** planning delta; rc.1 archive required for file-level import diff

## 1. Delta summary

| Area | M62 state | M63 target | Action |
|---|---|---|---|
| APF package version | `v0.1.0-alpha.14` historical import | `v0.1.0-rc.1` | replace package in M63.1 after rc archive is available |
| Lifecycle | imported standard module | release-candidate standard module | update metadata/docs |
| Standard module status | documented in M62 | must remain explicit | verify docs in M63.1 |
| Validation profile | M62 import smoke + APF lint/compile/test | full RC profile incl. coverage/state/output/artifacts/consistency/go-no-go | formalize in M63.2 |
| `validate-factory-output` | not parent CLI requirement | APF-local/optional | document non-blocking optional status |
| Warnings | cycle/path notes and classification notes | consistency warnings non-blocking | visible known limitations |
| Language patterns | M62.3 classification | rc.1-specific classification update | M63.3 docs/matrix update |

## 2. Required metadata target

```yaml
packages/ordo_applied_project_factory:
  is_standard_applied_module: true
  module_id: ordo.applied_project_factory
  version: 0.1.0-rc.1
  lifecycle: release-candidate
```

## 3. Historical import handling

M62 imported alpha.14. M63 must not leave alpha.14 documented as the current APF release-candidate.

Required convention:

```text
alpha.14 = historical M62 import point
alpha.21 = source base for rc.1
v0.1.0-rc.1 = current APF release-candidate target
```

## 4. File-level diff limitation

No explicit `v0.1.0-rc.1` APF archive was found in `/mnt/data` during M63.0.

Therefore this delta review does **not** claim:

```text
- exact file-level diff alpha.14 -> rc.1
- exact source/program.ordo.yaml node/edge changes
- exact rc.1 artifact inventory
```

Those belong to M63.1 once the rc.1 archive is available.
