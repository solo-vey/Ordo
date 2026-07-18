# Jira-ready issue — BL-BENCH-050

**Summary:** Declared-Contract Archive Pre-Release Self-Application Gate

**Issue type:** Story / Process improvement  
**Priority:** Highest  
**Status:** Open

## Description

During archive preparation, the producer can validate integrity and local structure but fail to execute the very validators, runtime prerequisites, entry-point rules and regressions declared inside the archive for the external consumer. This permits invalid archives to be handed to external models and shifts defect discovery to external testing.

Implement a fail-closed pre-release gate that derives every declared verification criterion from the sealed candidate archive and applies that same contract to the exact ZIP in a clean consumer workspace before release.

The complete normative description and acceptance criteria are in `050_DECLARED_CONTRACT_ARCHIVE_PRE_RELEASE_SELF_APPLICATION_GATE.md`.

## Acceptance criteria

- Declared validators and exact paths exist and are invocable.
- Actual runtime entry matches the declared required entry.
- All declared regressions execute on the sealed ZIP.
- No undeclared substitute satisfies a missing check.
- Every criterion has bound evidence; skipped checks are zero.
- Failure returns `NO_CHANGE / PRE_RELEASE_DECLARED_CONTRACT_MISMATCH`.
- External testing bundle generation is blocked without `PASS_RELEASE`.
- Up to five scoped correction passes are supported and preserved.
