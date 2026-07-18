# Jira-ready issue — BL-BENCH-047

## Summary
Mandatory black-box end-to-end pre-release self-validation and five-RUN evidence

## Issue type
Story / Critical release-control improvement

## Description
Implement a mandatory blind external-executor campaign against the sealed Playbook candidate before release. Execute RUN_01–RUN_05, route all validation through Driver, permit canonical correction loops, verify terminal outcomes and final ZIPs, and preserve five immutable pre-release evidence archives.

The attached RUN_02 evidence proves that integrity, pre-flight and regressions may pass while artifact generation still fails and the Driver remains incomplete. Static/package-level checks alone are insufficient.

Full normative description: `047_BLACK_BOX_END_TO_END_PRE_RELEASE_SELF_VALIDATION.md`.

## Acceptance criteria
- Sealed candidate only; no hidden workspace state.
- RUN_01–RUN_05 executed automatically.
- All validator results processed through Driver.
- Correction loops use new versions and reruns.
- Selected-run facts and cross-artifact fidelity validated.
- Positive and expected-negative terminal outcomes verified.
- Every final ZIP reopened and revalidated.
- Five checksum-bound execution-evidence archives produced.
- Release blocked unless the campaign passes.
- Missing authoritative owner input causes explicit stop, not fabrication.

## Attachments
- `ORDO_RUN_02_NO_CHANGE_RETURN.zip` (`4f1f9d6c7069a9626e03adac49544acd9e57c4ab2165a5005704c2ff2c4f7793`)
- `OWNER_REQUIREMENT_AND_INCIDENT_CONTEXT.md`
