# alpha.20.0.8 — Recovery Loop Hardening

- Routed `GateFailure` is now first-class revisit evidence for the exact recovery target.
- A revisit reached from a failed gate is `needs_extension` even when canonical state dependencies are unchanged.
- `missing_information`, `missing_coverage`, and failed checks are exposed as `revisit_context.required_extension`.
- Automatic live execution halts on a repeated identical gate-failure fingerprint when runtime state is unchanged.
- The no-progress breaker is fail-safe: a changed runtime state permits another recovery attempt.
