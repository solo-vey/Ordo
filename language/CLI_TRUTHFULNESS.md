# CLI truthfulness

A report may claim deterministic validation only when CLI commands actually ran.

Allowed statuses:

```text
executed_cli_passed
executed_cli_failed
logical_self_check_only
not_run_cli_unavailable
not_run_user_skipped
```

`executed_cli_passed` requires command evidence. Missing CLI status is invalid for release/runtime handoff reports.

Use `ordo validate-cli-status <report.json>` for machine validation of CLI truthfulness reports.


## M59.1 clarification

`not_run_cli_unavailable` is no longer a soft permission to keep working as if Runtime Mode were enforced. It means the session is blocked unless the user explicitly approves nondeterministic fallback, and generated artifacts must be marked `DETERMINISM_NOT_ENFORCED`.
