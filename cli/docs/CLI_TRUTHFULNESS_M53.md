# CLI Truthfulness

Use `ordo validate-cli-status <report>` to check whether a handoff or validation report truthfully declares CLI execution status.

Allowed status values:

```text
executed_cli_passed
executed_cli_failed
logical_self_check_only
not_run_cli_unavailable
not_run_user_skipped
```

A report claiming `executed_cli_passed` must include `executed_commands` or `cli_evidence`.
