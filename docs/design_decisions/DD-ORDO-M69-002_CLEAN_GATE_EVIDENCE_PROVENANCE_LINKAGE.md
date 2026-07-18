# DD-ORDO-M69-002 — Clean-Gate Evidence / Provenance Linkage

Decision: release provenance must cryptographically bind to the exact clean-gate report with SHA-256 and byte size while preserving the CLI report as source of truth.

Rejected: copying the full report into provenance, recomputing gate status in workflow code, or linking only by filename.

Reason: filename-only linkage is ambiguous; duplicated status logic risks divergence from CLI semantics.
