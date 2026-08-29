# alpha.20.0.89-dev — descriptor-driven Verify Playbook page

Adds an extensible playbook verification framework backed by the current Ordo 0.4.10 / alpha.9 verification toolkit snapshot.

## UI
- New top-level `Verify Playbook` page.
- One `Run all verifications` action.
- Sequential execution with progress bar.
- Per-check live status: PENDING, RUNNING, PASS, FAIL, ERROR, SKIPPED.
- Command output is expandable per check.
- Verification runs against an isolated temporary copy of the loaded package.

## Extension model
- Checks are discovered dynamically from `verification/checks/*.json`.
- The UI has no hard-coded verification names.
- Current registry contains 31 user-visible verification capabilities derived from `VERIFICATION_CATALOG.md`.
- Checks requiring gate IDs, bindings, template instances, release context, etc. remain visible and are SKIPPED when context is unavailable.

## Language/tooling integration
See:
- `verification/LANGUAGE_PACKAGE_INTEGRATION_CONTRACT.md`
- `verification/check_descriptor.schema.json`
- `verification/VERIFICATION_SOURCE.json`

A future Editor build can replace the toolkit snapshot and reconcile descriptor files without changing verification-page UI code.
