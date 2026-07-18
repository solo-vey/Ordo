# M63.2 — APF RC Validation Profile / Known Limitations Report

Status: `passed-validation-profile-documentation`  
Generated: `2026-07-08T18:15:31.239861+00:00`

## Summary

M63.2 formalizes the APF rc.1 validation profile and known limitations after M63.1 package import and license patch.

The key result is that APF `v0.1.0-rc.1` stays `release-candidate / go`, with `validate-factory-output` explicitly classified as APF-local / optional and `consistency: passed_with_warnings` retained as visible, non-blocking evidence.

## Inputs

- Base workspace: `ordo_github_workspace_v0_12_m63_1_apf_rc_package_import_with_license_files.zip`
- APF rc.1 dev package: `ordo_applied_project_factory_v0_1_0_rc_1_dev.zip`
- Current APF module id: `ordo.applied_project_factory`
- Current APF version: `0.1.0-rc.1`

## Validation profile decision

Required parent-compatible commands:

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

Optional / APF-local:

```text
validate-factory-output
```

## Observed validation evidence

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

## Scoped packaging fix

During M63.2, the clean-source APF package was checked for the parent runtime-start-file lint standard. The clean-source package needed `reports/CLI_VALIDATION_SUMMARY.md`. This was added as a documentation/packaging artifact only.

This does not change APF runtime logic, source YAML, IR, opcodes, PathWalk, Visual Graph, scoring, calibration, or benchmark behavior.

## Known limitations retained

- `FLOW.JOIN` remains a future IR candidate.
- `SHARED.TAIL.REFERENCE` remains a future IR candidate.
- `validate-factory-output` remains APF-local / optional.
- `consistency: passed_with_warnings` remains non-blocking but visible.

## Decision

APF `v0.1.0-rc.1` is still accepted as a release-candidate standard applied module for the current Ordo language package line.
