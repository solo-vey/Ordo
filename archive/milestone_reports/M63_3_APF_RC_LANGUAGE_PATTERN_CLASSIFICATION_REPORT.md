# M63.3 APF RC Language Pattern Classification Update Report

Status: `passed-design-classification-only`.

## Scope

M63.3 updates the APF release-candidate language-pattern classification after the APF `v0.1.0-rc.1` package import and validation-profile documentation.

This milestone does not modify APF source YAML, runtime logic, Semantic JSON IR, parent CLI commands, scoring, calibration, or watchdog behavior.

## Decision

APF `v0.1.0-rc.1` remains accepted as a release-candidate standard applied module pattern source. Its observed patterns are classified, not promoted.

## Classification summary

- total candidates: 14
- future IR candidates: 2 (`FLOW.JOIN`, `SHARED.TAIL.REFERENCE`)
- APF-local / applied-module patterns: 8
- template-layer documentation/tooling candidates: 2
- validation / handoff pattern: 1
- adapter / AI-assisted extraction patterns: 2

## Known limitations retained

- `FLOW.JOIN` and `SHARED.TAIL.REFERENCE` remain future IR candidates.
- `validate-factory-output` remains APF-local or optional.
- consistency warnings remain visible and non-blocking.

## Validation stance

M63.3 is a documentation/classification milestone. The validation gate checks package structure, documentation availability, APF rc.1 parent-compatible commands, and archive integrity. Full runtime execution and calibration remain out of scope.
