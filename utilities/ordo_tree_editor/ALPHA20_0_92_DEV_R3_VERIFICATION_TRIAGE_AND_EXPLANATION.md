# alpha.20.0.92-dev — Verification triage and model explanations

- Finished verification runs are displayed FAIL/ERROR first, then SKIPPED, then PASS.
- Running suites remain in execution order.
- FAIL/ERROR checks can be explained on demand by the configured model.
- Explanation is read-only and receives only verification metadata/output plus playbook language settings.
- Model must classify likely source and propose diagnostics without overriding the verification result.
