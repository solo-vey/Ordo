# alpha.20.0.86-dev — model response synthesis + runtime artifact surfacing

Generic R3 runtime/editor hardening.

- Assistant-directed response synthesis nodes are no longer misclassified as analyst input.
- Compiler and runtime share the same narrow synthesis classification.
- Deterministic package-tool outputs are mirrored to their declared run-relative paths.
- Downstream model nodes can read referenced run-local text artifacts as context.
- Referenced generated runtime files are automatically surfaced as transcript artifacts/download cards.
- Source playbooks do not need to copy generated reports back into the package.

No domain-specific Risk Factor or JSON Validation node IDs are recognized by the core.
