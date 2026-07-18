# M63.0 — APF Release Candidate Adaptation Report

**Date:** 2026-07-08T16:06:45.636775+00:00  
**Status:** `release-candidate-ready`  
**APF version:** `0.1.0-rc.1`  
**Source APF version:** `0.1.0-alpha.21`  
**Parent language package:** `Ordo 0.12.0-preview-rc1` / M62 line closure

## What changed in the language package

The supplied M62 language package already incorporated our APF work at the language-package level as classification and standard-module infrastructure:

```text
- APF is now a Standard Applied Module under packages/ordo_applied_project_factory/
- APF pattern candidates are classified in APF_PATTERN_CLASSIFICATION_MATRIX.*
- output/template, progressive authoring, node/branch review, scoped patches, minimal/full validation split are documented as APF patterns or schema conventions
- FLOW.JOIN and SHARED.TAIL.REFERENCE remain future IR candidates, not runtime-core changes
```

## Adaptation decision

APF alpha.21 can be adapted to the M62 language package without changing language runtime core.

Required adaptation was package-level only:

```text
- replace imported APF alpha.14 module content with APF rc.1 content based on alpha.21
- preserve M62 standard-applied-module documentation
- update module metadata from alpha to release-candidate
- align validation profile with commands exposed by the M62 parent CLI
- keep future IR candidates as documented candidates
```

## Compatibility result

```text
runtime-core changes: none
IR/opcode changes: none
APF process logic changes after alpha.21: none
module packaging/docs changes: yes
validation profile adaptation: yes
release candidate status: ready
```

## Notes

The M62 parent CLI does not promote APF-specific `validate-factory-output` as a parent runtime-core command. RC validation therefore uses the current parent CLI command set plus APF fixture reports. This is compatible with the M62 decision that APF patterns are standard-module/subflow conventions before any future IR promotion.


## Validation result

```text
lint: passed
compile: passed
test: passed
coverage: passed
validate-state: passed
next-step: generated
validate-output: passed
validate-artifacts: passed
consistency: passed_with_warnings
go/no-go: go
repo-check clean source: passed
```

Decision: `APF is ready as v0.1.0-rc.1 on M62 line closure.`
