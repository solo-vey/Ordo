# DD-ORDO-M28-001 — Hybrid Execution Model

Status: accepted
Milestone: M28
Date: 2026-07-06

## Decision

Ordo execution is AI-led and Process Rail guided. A compiled Semantic JSON IR is not executed as a fully deterministic chat wizard. It is interpreted by an AI Ordo Executor, while deterministic CLI/helper tools validate the state, gates, next-step candidates and output readiness.

## Reason

The goal of Ordo is to combine flexible AI reasoning with deterministic process stability. A fully hardcoded runtime loses the ability to handle clarification, corrections, context shifts and human-level explanation. A free AI chat loses repeatability and may skip required process checks. Hybrid execution keeps both: the AI leads the conversation, and the Process Rail plus helper tools keep the process aligned.

## Consequences

- AI Ordo Executor is a first-class role.
- Semantic JSON IR is the machine-readable Process Rail, not a replacement for AI reasoning.
- CLI remains a deterministic helper layer, not the primary conversational runtime.
- Raw helper output is not shown directly to the human by default.
- Execution documentation must describe correction, deviation handling, backtracking and rail resume.
