# Application implementation module usage

## Role

This tree module operates on the code module that implements a business capability already described by an approved analytical artifact.

Example host flow:

```text
analytical specification approved
→ functional/unit/edge-case knowledge available
→ implementation prompt generated
→ analyst supplies the application code module
→ code inspected and scope assessed
→ model-direct implementation or developer handoff
→ tests and verification
→ result returned to the host playbook
```

## Entry contract

The module should be entered only when:

1. the analytical artifact is approved;
2. the implementation prompt exists;
3. the confirmed requirement fields referenced by the instance are available;
4. the host knows where to continue after success.

## Evidence intake contract

The analyst may provide one of these baseline forms:

- ZIP archive containing the target code module;
- Git repository URL with an explicit branch, tag, or commit;
- supported local or connector-backed code location;
- explicit statement that the baseline cannot be provided, which routes to developer handoff.

The host should preserve provenance for the supplied baseline and record the immutable reference used for verification.

## Outputs

The module returns one of two host-consumable outcomes:

- a verified changed candidate with changed-file and test evidence;
- a developer handoff artifact describing the required change and available evidence.

The module does not publish or deploy the changed application module unless the host playbook explicitly adds those steps.
