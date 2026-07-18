# M63.1 — APF rc.1 Package Import / Metadata Sync

Status: `passed-package-import`  
Generated: `2026-07-08T17:14:37.838821+00:00`

## Imported module

```yaml
packages/ordo_applied_project_factory:
  is_standard_applied_module: true
  module_id: ordo.applied_project_factory
  version: 0.1.0-rc.1
  lifecycle: release-candidate
  parent_language_line: M62 line closure
```

## Import decision

The previously imported APF `0.1.0-alpha.14` is now historical. The current standard applied module import is APF `0.1.0-rc.1`, based on alpha.21 and adapted to the M62 parent language package.

## Scope

Included:

- replace `packages/ordo_applied_project_factory/` with rc.1 dev package contents;
- synchronize root and package-level documentation;
- keep APF as a standard applied module, not a companion utility;
- preserve APF process logic;
- preserve APF-local validation/reporting artifacts.

Not included:

- APF branch rewrite;
- new IR/opcodes;
- core runtime changes;
- promotion of `validate-factory-output` to parent CLI;
- implementation of `FLOW.JOIN` / `SHARED.TAIL.REFERENCE`;
- runtime execution of generated testcases;
- scoring/calibration/watchdog work.

## Validation summary

Imported RC validation report declares:

```json
{
  "lint": "passed",
  "compile": "passed",
  "test": "passed",
  "coverage": "passed",
  "validate_state": "passed",
  "next_step": "generated",
  "validate_output": "passed",
  "validate_artifacts": "passed",
  "consistency": "passed_with_warnings",
  "go_no_go": "go",
  "repo_check_clean_source": "passed"
}
```

Warnings remain non-blocking and visible.


## Decision

APF v0.1.0-rc.1 is imported as a release-candidate standard applied module.


## Final M63.1 validation

| Check | Status |
|---|---|
| lint | passed |
| compile | passed |
| test | passed |
| coverage | passed |
| validate-state | passed |
| next-step | ready_for_ai_next_move |
| validate-output | passed |
| validate-artifacts | passed |
| consistency | passed_with_warnings |
| go/no-go | go |
| repo-check clean source | passed |

## Clean source / package split

The language workspace keeps `packages/ordo_applied_project_factory/` as a clean source package. APF dev/runtime packages and validation artifacts are emitted separately as release outputs/evidence.

## M63.1 readiness

Decision: `go`. APF `v0.1.0-rc.1` is accepted for release-candidate standard-module import.
