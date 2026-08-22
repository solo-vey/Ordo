# EXECUTION_DEBUG_EVIDENCE_EXPORT v1.0

Reusable optional pattern for producing a bounded debug-evidence package for an execution run.

The pattern activates only when debug export is required by runtime/host policy. In normal mode it performs no package materialization and simply finalizes the optional branch. In debug mode it collects only declared execution evidence, builds an explicit include/exclude manifest, applies a mandatory redaction boundary before packaging, materializes and validates the bundle, registers it, and presents it only after validation PASS.

The generic core owns evidence classes, packaging safety, redaction ordering, validation and delivery semantics. Domain-specific attachments and domain evidence sources are extensions and are never implicitly included.

## v1.1 compiler-hardening note

This revision preserves the prior process semantics and adds a mandatory compiler-valid lowering/preflight contract. See `COMPILATION_CONTRACT.md`.
