# BL-BENCH-055

# BL-BENCH-055 — Current-State-Only Evidence Transfer Archive Generation

Status: **DONE**

## Objective

Add a governed playbook route that produces a compact, current-state-only evidence snapshot for transfer. The route retains only authoritative accepted/current artifacts and excludes development history without changing immutable raw evidence or weakening current bounded claims.

## Implemented decision path

1. Select snapshot policy and bind source evidence catalog.
2. Inventory logical artifact families and all candidates.
3. Resolve the authoritative current artifact using manifests, acceptance/approval records, release bindings and semantic versions—not filesystem time alone.
4. Bind each retained accepted run to its exact package, Driver, evaluator, scorecard, methodology and terminal state.
5. Detect run-bound exceptions when the accepted run used a package older than the latest available package.
6. Calculate historical exclusions and bounded-claim exceptions.
7. Choose archive-retention pattern A, B or C for each source package and document any intentional duplication.
8. Build an isolated staging tree without mutating immutable raw evidence.
9. Generate the manifest, selection, exclusion and language-audit reports.
10. Generate checksums last, freeze staging, seal ZIP and revalidate it in a clean workspace.
11. Release only through the current-state snapshot hard gate.

## Fail-closed conditions

The route blocks when current authority is ambiguous, provenance is missing, accepted-run binding is incomplete, a checksum is invalid, exclusion would invalidate a current claim, or the current accepted run set is incomplete.

## Terminal states

- Success: `CURRENT_STATE_ONLY_ARCHIVE_READY / PASS_RELEASE`
- Failure: `NO_CHANGE / CURRENT_STATE_EVIDENCE_SELECTION_BLOCKED`

## Authoritative outputs

- `CURRENT_STATE_ONLY_EVIDENCE_POLICY.json`
- `schemas/current_state_manifest.schema.json`
- `schemas/current_state_selection_report.schema.json`
- `schemas/current_state_exclusion_report.schema.json`
- `templates/CURRENT_STATE_MANIFEST.template.json`
- `tools/build_current_state_evidence_snapshot.py`
- `tools/validate_current_state_evidence_snapshot.py`
- `reports/CURRENT_STATE_ONLY_EVIDENCE_SNAPSHOT_ACCEPTANCE_TESTS.json`
