# Evidence Base Catalog Governance

Version: 1.0.0-alpha.24

This document is the normative human-readable companion to `EVIDENCE_CATALOG_CONTRACT.json`.

## Core rules

1. Internal self-validation, internal dry evaluation, and external blind evidence are separate evidence classes and directories.
2. Original external RUN archives are immutable and append-only. Corrections create a new RUN or implementation version.
3. Every catalog object has a stable ID, lifecycle state, SHA-256, provenance, and version bindings.
4. Canonical scores may reference only `CONFIRMED` external blind RUN evidence with complete package, prompt, methodology, case-profile, audit, acceptance, and evidence bindings.
5. Rejected, invalidated, quarantined, deprecated, or superseded evidence remains historically visible but cannot enter the confirmed score ledger.
6. Filesystem, object manifests, score ledgers, lifecycle ledgers, and transfer manifests must agree exactly.
7. Transfer packages must be checksum-bound and restorable without relying on undocumented local files.

## Fail-closed outcome

Any missing object, broken binding, class contamination, mutable-history rewrite, ineligible score, or non-restorable transfer routes to `NO_CHANGE / EVIDENCE_BASE_CATALOG_GOVERNANCE_FAILURE`.
