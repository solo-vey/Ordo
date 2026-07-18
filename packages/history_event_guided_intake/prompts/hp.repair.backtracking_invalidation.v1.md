# Repair Helper — Backtracking invalidation

Use this helper when an earlier answer changes and downstream answers or artifacts may become stale.

## Goal

Explain which later answers, generated text, or validation assumptions need review after backtracking.

## Suggested explanation

When an earlier process answer changes, later answers that depended on it may no longer be safe. The process should review affected nodes and artifacts before continuing.

## Do not

- Do not delete prior evidence silently.
- Do not treat old downstream answers as still confirmed without review.
- Do not hide the impact of the changed answer.

## Authority boundary

This helper explains invalidation. Actual restore/backtrack behavior must follow process rail and CLI/session rules.
