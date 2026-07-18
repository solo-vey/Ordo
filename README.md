# Ordo Complete CI Correction Bundle

Apply the seven project files in this bundle to the repository root while preserving their paths.

## Replacements

- `CONSOLIDATED_BACKLOG.md`
- `tools/build_release_archive.py`

## Canonical RC10 restorations

- `empirical_evidence/manifests/EMPIRICAL_EVIDENCE_INDEX.json`
- `empirical_evidence/manifests/SCHEMA_REGISTRY.json`
- `empirical_evidence/schemas/external_adoption_case.schema.json`
- `empirical_evidence/schemas/external_developer_submission.schema.json`
- `empirical_evidence/tools/validate_external_independence.py`

The five empirical-evidence files were copied byte-for-byte from the verified canonical RC10 archive.
The source archive passed ZIP integrity and all 4,698 entries in its root `SHA256SUMS.txt`.

After applying the files, commit to `main` and allow a new `Ordo full delivery gate` run.
Do not re-run an older run tied to an earlier commit.

Suggested commit message:

`Restore canonical evidence and fix delivery gate blockers`
