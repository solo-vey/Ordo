# M80.1 — Package fingerprinting, cache persistence and atomic operations

Status: PASS

Implemented:

- deterministic package fingerprinting for files and directories;
- canonical atomic JSON persistence for session cache state;
- staged package load followed by atomic active-cache replacement;
- automatic rollback to the previous valid cache when replacement or state commit fails;
- atomic cache invalidation with optional payload removal;
- path-escape, missing-file, symlink and fingerprint mismatch protection;
- process state remains outside cache mutation operations and is never advanced by load/invalidate.

Validation:

- M80.0 + M80.1 target tests: 16/16 PASS.
- Failed replacement preserves previous cache payload and state file unchanged.
