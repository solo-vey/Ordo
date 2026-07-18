# Artifact Helper — QA Package generation

Use this helper when generating or reviewing `05_QA_PACKAGE_<ALIAS>.md`.

## Goal

Keep QA executable and aligned with confirmed test strategy.

## Include

- positive trigger scenarios;
- negative/no-op scenarios;
- empty/null/missing transitions;
- normalization cases;
- functional and unit coverage if selected;
- pass/fail criteria;
- observability or evidence expectations when known.

## Do not

- Do not create parallel test IDs if canonical IDs already exist.
- Do not make QA reconstruct inputs from unrelated documents when concrete inputs are available.
- Do not claim manual or automated tests were executed unless evidence exists.

## Authority boundary

This helper supports QA artifact generation only. It cannot replace real QA execution or validation reports.
