# DD-ORDO-M29-001 — CLI helper commands alignment

Status: accepted  
Milestone: M29

## Decision

Ordo CLI is aligned as a deterministic helper layer for Process Rail workflows.

The CLI may validate state, evaluate gates, suggest next steps, compare state snapshots and summarize validation evidence. It must not be positioned as the main conversational runtime.

## Reason

The core Ordo model is AI-first: AI Ordo Developer and AI Ordo Executor remain active cognitive actors. Deterministic tools are needed to stabilize syntax, gates, state and reproducibility, but direct tool output is not the human interaction layer.

## Impact

M29 adds or documents helper commands:

```text
validate-state
check-gate
next-step
diff-state
explain-validation
```

README, CLI docs, language spec and validation reports must describe these as AI-facing helper commands.

## Non-goal

M29 does not create a full deterministic wizard runtime.
