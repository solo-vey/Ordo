# Chapter 45. Feedback Decision Planning

After external review, it is important not to rush into rewriting code. For Ordo, something else matters more: every comment must pass through a short decision process.

```text
comment → classification → decision → milestone → acceptance criterion → verification
```

## Why this is a separate layer

Feedback intake collects comments. But the existence of a comment does not mean it must immediately be added to the release candidate.

M50 adds a simple rule: decision first, change second.

## Decision types

```text
accepted_now
accepted_next_milestone
deferred
rejected
needs_reproduction
needs_owner_decision
```

This prevents blockers, useful ideas, documentation clarifications, and strategic owner decisions from being mixed together.

## What a decision must contain

Every decision must contain:

- a short description;
- severity;
- affected layer;
- target milestone;
- rationale;
- acceptance criteria;
- validation commands.

## How this works for Ordo

Ordo does not merely accept feedback. Ordo converts feedback into a controlled change plan. This continues the Process Rail idea: the model may reason flexibly, but the process must not lose its trace.

## Important limitation

M50 does not change the CLI, runtime, or package business logic. It is a decision layer for subsequent changes.
