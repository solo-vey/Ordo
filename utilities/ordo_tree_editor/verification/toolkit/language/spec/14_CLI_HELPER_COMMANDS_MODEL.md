# 14. CLI Helper Commands Model

## Status

Milestone: M29  
Scope: Process Rail deterministic helper alignment

## Core rule

CLI commands are deterministic helpers for AI-guided work. They validate, compile, compare and suggest, but they do not become the main conversational executor.

```text
AI leads the human interaction.
CLI stabilizes deterministic parts.
AI interprets CLI output before user-facing response.
```

## Helper command classes

| Command class | Purpose |
|---|---|
| `validate-state` | Check current state against required fields, gates, assertions and output allowance. |
| `check-gate` | Evaluate one gate from the current/proposed state. |
| `next-step` | Suggest a Process Rail next action from missing fields and blocked gates. |
| `diff-state` | Compare two state snapshots after correction/backtracking. |
| `explain-validation` | Produce AI-facing validation summary that must be rewritten for humans. |

## Non-goals

- Do not implement a fully deterministic dialogue wizard.
- Do not bypass AI judgment for open semantic questions.
- Do not expose raw technical dumps to PM/user unless explicitly requested.

## Semantic IR relationship

Semantic JSON IR may contain `tool_hooks` that reference these helper classes. The helper output is evidence for AI reasoning, not a replacement for AI reasoning.
