# M82.1 — Hardened Isolated Child Runner and Watchdog

## Status

`implemented / validated-for-M82.1`

Backlog item: `BL-ORDO-003`

## Implemented

- immutable plan fingerprint;
- approved roots for source, testcase and execution paths;
- traversal and symlink rejection before child spawn;
- one job per short-lived child process group;
- closed stdin and allowlisted environment;
- private HOME and TMPDIR inside the sandbox;
- bounded stdout/stderr collectors with truncation flags;
- wall-clock watchdog with process-group termination on POSIX;
- capability reporting for process groups and resource limits;
- atomic result writes using temporary file plus rename;
- refusal to overwrite an existing result artifact;
- explicit cleanup policies: retain all, retain failures, cleanup all;
- default policy retains failures and removes successful sandboxes;
- compatibility with the existing M76.2 commands and tests.

## Validation

Passed:

- 9 dedicated M82.1 hardening tests;
- 4 existing M76.2 compatibility tests;
- aggregate, dry-run, calibration, CSG, harness, matrix-smoke, maze-generation and model-benchmark pilot test groups executed separately.

The monolithic PathWalk test command did not complete within the environment timeout. The relevant test files were therefore executed in smaller groups. One unrelated model-driver retry test group exceeded the execution window and is not claimed as validated by M82.1.

## Scope boundary

M82.1 does not close BL-ORDO-003. The following remain for later milestones:

- M82.2 versioned evidence schema and complete failure taxonomy;
- M82.3 generated testcase integration through the hardened boundary;
- M82.4 complete failure/regression matrix and closure.

## Change impact

`L3 — shared/runtime utility layer`.

No Ordo language semantics were changed.
