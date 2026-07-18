# Repair Helper — Missing artifact resolution

Use this helper when package composition or artifact validation finds a missing file, missing section, or missing propagated field.

## Goal

Tell the analyst what is missing and how to repair it without raw tool noise unless requested.

## Suggested explanation

The package cannot be handed off yet because a required artifact or required section is missing. The missing item must be generated or corrected from confirmed state, then validation should be rerun.

## Do not

- Do not invent artifact content from unsupported assumptions.
- Do not mark the package ready while required artifacts are missing.
- Do not hide missing test strategy propagation.

## Authority boundary

This helper supports repair explanation. Artifact validation and package gates remain authoritative.
