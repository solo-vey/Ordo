# alpha.20.0.91-dev — verification JSON export

UI-only extension of the descriptor-driven verification framework.

- Adds `Export results JSON` next to `Run all verifications`.
- Enabled after verification results exist, including failed suites.
- Exports a complete verification snapshot: package metadata, run id, summary, statuses, durations, exit codes and captured output for every registered check.
- Future registry checks are included automatically because export serializes the runtime check list rather than a hard-coded catalog.

No playbook/runtime execution semantics changed.
