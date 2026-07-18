# M69.4 — CI/release fixture and smoke-test matrix

Status: `implemented-validation-matrix / passed`.

## Scope

Added a cross-gate fixture/smoke matrix covering PR, main, and release behavior. No clean-check, repo-check, runtime, compiler, opcode, or applied-package implementation changed.

## Coverage

- clean required root passes every gate class;
- warnings pass PR but block main/release;
- blocked required root blocks every gate class;
- missing repo policy remains delegated/not-applicable and non-blocking;
- JSON stdout equals the `--out` report after parsing;
- release provenance SHA-256 and byte-size link exact report bytes.

## Validation

See `M69_4_VALIDATION_REPORT.json`.
