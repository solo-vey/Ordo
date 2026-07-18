# Clean-Gate Evidence and Release Provenance Linkage

Status: `M69.3 implemented`

M69.3 makes the release provenance file cryptographically identify the exact `repo_clean_check.json` produced by the release clean gate.

## Source of truth

`reports/release/repo_clean_check.json` remains the source-of-truth hygiene result. The provenance wrapper does not recalculate its status.

## Linkage fields

`release_clean_gate_provenance.json` uses schema `ordo.release_clean_gate.provenance.v2` and records:

- report path;
- report schema version, status, exit code and effective profile;
- SHA-256 of the exact report bytes;
- report size in bytes;
- linkage status: `linked` or `report_missing`.

This allows release evidence consumers to verify that provenance and clean-gate result belong to the same workflow run and exact report payload.

## Failure behavior

The provenance step runs with `if: always()`. If the CLI report is absent, provenance is still emitted with `linkage.status: report_missing`; artifact upload remains strict with `if-no-files-found: error`. The workflow never converts a failed clean gate into success.

## Boundary

No package mutation, IR compilation, release archive creation, or duplicate hygiene evaluation is introduced.
