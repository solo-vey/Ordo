# Checkpoint Lifecycle Audit

Status: `open — audit complete; disposition deferred`

This audit covers the four pre-RC6 rollback archives under `checkpoints/playbooks/`.
They are historical recovery artifacts, not current runtime inputs.

| Checkpoint ID | Archive | Size | Verification | Direct active references |
| --- | --- | ---: | --- | ---: |
| `history_event.guided_intake@0.1.2` | `history_event_guided_intake_pre_rc6.rollback.zip` | 189 KB | checksum, ZIP integrity, identity, and restore round-trip passed | 0 |
| `ordo.applied_project_factory@0.1.1-rc.2` | `ordo_applied_project_factory_pre_rc6.rollback.zip` | 909 KB | checksum, ZIP integrity, identity, and restore round-trip passed | 0 |
| `ordo.hybrid_executor@0.1.1` | `ordo_hybrid_executor_pre_rc6.rollback.zip` | 14 KB | checksum, ZIP integrity, identity, and restore round-trip passed | 0 |
| `ordo.project_builder@0.1.1` | `ordo_project_builder_pre_rc6.rollback.zip` | 16 KB | checksum, ZIP integrity, identity, and restore round-trip passed | 0 |

The archives remain checksum-bound through `SHA256SUMS.txt` and each paired
verification record. Their total current payload is approximately 1.1 MB.

## Required disposition work

Do not delete or rewrite these archives in place. First decide whether each
checkpoint must remain in every clone, move to an approved external immutable
store, or be retained as a local historical archive. Any move requires a
checksum-bound locator manifest, clean retrieval and restore verification,
consumer/reference updates, and only then removal of inline bytes.

This is a lifecycle and storage decision, not a runtime or language-semantics
change.
