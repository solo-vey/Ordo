# M60.3.2 Runtime CLI Safety Report

This patch adds fail-fast behavior for bare `intake <package>` in non-TTY automation and documents the safe CLI usage expected from scenario-testing utilities.

## Accepted behavior

```text
no --submit
no --answers
no --non-interactive
stdin is not a TTY
→ failed reason=no_answers_and_not_interactive_and_no_tty
```

`next-step` stdout remains compact; full checkpoint details stay in `reports/next_step_report.json`.

## Scope exclusions

`restore-session`, PathWalk code changes, and score calibration are intentionally deferred.
