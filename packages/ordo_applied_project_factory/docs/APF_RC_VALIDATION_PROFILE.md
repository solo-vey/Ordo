# APF RC Validation Profile — M63.2

Status: `release-candidate / go`  
Module id: `ordo.applied_project_factory`  
Version: `0.1.0-rc.1`  
Parent language line: `Ordo v0.12 / M62 line closure`  
Generated: `2026-07-08T18:15:31.239861+00:00`

## Purpose

This document fixes the validation contract for APF `v0.1.0-rc.1` inside the current Ordo language package line.

It separates parent-compatible validation commands from APF-local validation helpers so that rc.1 is not failed for a command that has not been promoted to the parent CLI.

## Required parent-compatible validation profile

| Check | Required for rc.1 | Status |
|---|---:|---|
| lint | yes | passed |
| compile | yes | passed |
| test | yes | passed |
| coverage | yes | passed |
| validate-state | yes | passed |
| next-step | yes | ready_for_ai_next_move |
| validate-output | yes | passed |
| validate-artifacts | yes | passed |
| consistency | yes | passed_with_warnings |
| go/no-go | yes | go |
| repo-check clean source | yes | passed |

## Optional / APF-local validation

| Check | Classification | Policy |
|---|---|---|
| validate-factory-output | APF-local / optional | Not a parent CLI blocker until promoted. Equivalent APF-local runtime/dev-package evidence may satisfy this check for rc.1. |

## Clean-source vs dev/runtime package split

The language workspace keeps APF as a clean-source standard module. Generated validation artifacts, runtime outputs, compiled outputs and release reports belong in APF dev/runtime packages and evidence packs.

The clean-source APF package may include `reports/CLI_VALIDATION_SUMMARY.md` as a required human-readable validation summary because parent lint requires the runtime start-file standard.

## Decision

APF `v0.1.0-rc.1` remains accepted as a release-candidate standard applied module for the current Ordo language package line.
