# Evidence Storage and Git History Policy

## Purpose

This policy controls storage of Ordo empirical evidence and prevents uncontrolled Git-history growth while preserving evidence identity, provenance, and reproducibility.

## Governing Principles

1. Evidence identity is bound to SHA-256 and provenance, not to a Git path or URL.
2. The public repository carries a current-state-only evidence snapshot.
3. Historical, superseded, rejected, dry-run, and duplicate development packages are excluded from ordinary publication archives.
4. Immutable raw evidence must never be edited in place.
5. Missing required evidence must fail closed; validators must not silently downgrade to normalized records.
6. Rewriting existing Git history is a separate, explicitly approved operation and is not part of routine evidence maintenance.

## Storage Classes

### `git_inline`

Use for individual files up to 5 MiB that are required by normal validation, review, or current-state reproduction.

### `review_required`

Use for files greater than 5 MiB and up to 25 MiB. The contributor must justify why the bytes are required in every clone. Prefer GitHub Release Assets when direct repository checkout is unnecessary.

### `external_immutable_asset`

Use by default for files greater than 25 MiB. Store them as GitHub Release Assets or in another approved immutable store. The repository must retain an English manifest with SHA-256, size, media type, storage locator, release binding, provenance, and availability status.

### `prohibited_inline`

Files approaching or exceeding 50 MiB must not be added to the ordinary Git tree without explicit maintainer approval. Files must never approach GitHub's hard per-file limit.

## Current Decision

The current current-state-only evidence snapshot has no individual evidence binary above 5 MiB. Therefore:

- no Git LFS migration is required now;
- no Git-history rewrite is authorized;
- current evidence binaries remain `git_inline`;
- new files are evaluated under the thresholds above;
- current duplicate run packages remain temporarily because both case-local and accepted-run indexes are part of the current evidence contract.

## Duplicate Bytes

Exact duplicate evidence bytes may exist only when required by two authoritative indexes or contracts. Every duplicate group must be declared in the binary inventory. Future schema work should replace duplicate bytes with content-addressed references, but existing evidence must not be deleted until all consumers and validators are migrated.

## Full and Publication Packages

### Publication package

Contains current-state evidence required for ordinary review and sanctioned validation. It excludes history.

### Full evidence package

May additionally contain externally stored immutable artifacts resolved from the storage manifest. A full package must verify every retrieved artifact against SHA-256.

## Availability States

Each externally stored artifact must use one of:

- `local_verified`;
- `remote_verified`;
- `remote_unverified`;
- `unavailable`;
- `not_required_for_current_gate`.

A required artifact in `remote_unverified` or `unavailable` causes a fail-closed result.

## Required Manifest Fields

Every binary evidence artifact record must include:

- artifact path or artifact ID;
- original filename;
- SHA-256;
- size in bytes;
- media type;
- storage class;
- storage locator when external;
- release binding;
- provenance reference;
- availability status;
- sanctioned-gate requirement;
- retention rule.

## Growth Triggers

A storage review becomes mandatory when any condition is met:

- one new evidence file exceeds 5 MiB;
- cumulative evidence binaries exceed 100 MiB;
- the full repository exceeds 250 MiB uncompressed;
- a clone or CI checkout regression is documented;
- an evidence family requires repeated full binary revisions;
- an individual file exceeds 25 MiB.

Git LFS adoption requires a separate approved change with clean-clone, fork, mirror, CI, quota, and disaster-recovery validation.

## Migration Procedure

1. inventory current bytes;
2. freeze original SHA-256 values;
3. classify every artifact;
4. upload unchanged bytes;
5. retrieve and reverify SHA-256;
6. create locator manifests;
7. update validators and CI;
8. test a clean clone and full retrieval;
9. remove inline bytes only after all consumers pass;
10. decide separately whether historical Git objects should be rewritten.

## Rollback

Before migration, preserve a checksum-bound offline evidence package. If retrieval, quota, CI, or availability fails:

1. stop publication;
2. restore the last verified inline or release-bound package;
3. restore previous manifests;
4. rerun clean-room verification;
5. do not reuse a failed locator without revalidation.

## Git History

Routine deletion from the working tree does not remove historical Git objects. History rewriting is prohibited unless explicitly approved, backed up, communicated to all consumers, and followed by fresh-clone verification.

## Language

All policy, manifest, inventory, and normalized evidence records are English. Immutable raw evidence may preserve its source language when modification would alter evidence identity.
