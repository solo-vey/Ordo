# APF Atomic Step Decomposition Proposal Policy

A decomposition proposal is a review artifact, not an automatic rewrite.

APF creates one when a step combines responsibilities, outputs, validation, approval, reconstruction, or transitions that can succeed or fail independently.

## Minimal safe split

The proposal must:

- preserve confirmed business intent and evidence;
- split only the responsibilities required to remove the detected risk;
- give each new step one observable result and completion criterion;
- define explicit transitions and local failure routes;
- keep generation, validation, approval, and confirmed-state transition separate where required;
- flag any semantic, ownership, or approval-boundary change for human decision.

## Human boundary

APF may diagnose and propose. It must not silently apply a split that changes business meaning, authority, ownership, approval boundaries, or confirmed state behavior.

After an approved split, Atomic Step Review must be rerun for every replacement step before downstream authoring continues.
