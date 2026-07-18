# Playbook Version Rollback Checkpoint Governance

Every playbook version change MUST create and verify an immutable checkpoint of the previous playbook release before mutation. The checkpoint contains the previous package tree, previous `playbook_release.json`, optional runtime state, a manifest, and SHA-256 checksums. A new playbook release is blocked until a disposable restore round-trip succeeds. Rollback records must identify the checkpoint, archive SHA-256, previous version, state compatibility, and verification status. Automatic runtime mutation remains prohibited.

Required lifecycle:

1. Freeze and hash the current playbook package.
2. Capture current runtime state when a run is active.
3. Build an immutable checkpoint archive.
4. Verify ZIP integrity and every checksum after extraction.
5. Restore into a disposable directory and validate release identity.
6. Only then mutate the playbook and bump its version.
7. Record the verified checkpoint in the new `playbook_release.json`.
