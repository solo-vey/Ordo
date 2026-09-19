# Checkpoint Lifecycle Audit

Status: `closed — external archive verified`

This audit covers the four pre-RC6 rollback archives formerly stored under `checkpoints/playbooks/`.
They are historical recovery artifacts, not current runtime inputs, and are retained in the checksum-bound external provenance archive.

| Checkpoint ID | Archive | Size | Verification | Direct active references |
| --- | --- | ---: | --- | ---: |
| `history_event.guided_intake@0.1.2` | `history_event_guided_intake_pre_rc6.rollback.zip` | 189 KB | checksum, ZIP integrity, identity, and restore round-trip passed | 0 |
| `ordo.applied_project_factory@0.1.1-rc.2` | `ordo_applied_project_factory_pre_rc6.rollback.zip` | 909 KB | checksum, ZIP integrity, identity, and restore round-trip passed | 0 |
| `ordo.hybrid_executor@0.1.1` | `ordo_hybrid_executor_pre_rc6.rollback.zip` | 14 KB | checksum, ZIP integrity, identity, and restore round-trip passed | 0 |
| `ordo.project_builder@0.1.1` | `ordo_project_builder_pre_rc6.rollback.zip` | 16 KB | checksum, ZIP integrity, identity, and restore round-trip passed | 0 |

The archives remain checksum-bound through the external archive manifest and its
attached checksums. Their total payload is approximately 1.1 MB.

## Required disposition work

The approved disposition is external archival. The GitHub Release asset,
checksum-bound locator, clean retrieval check, and restore evidence are listed
in [`../docs/EXTERNAL_ARCHIVES.md`](../docs/EXTERNAL_ARCHIVES.md). The inline
bytes may be removed only with the same change that updates active references
and repository checksums.

This is a lifecycle and storage decision, not a runtime or language-semantics
change.
