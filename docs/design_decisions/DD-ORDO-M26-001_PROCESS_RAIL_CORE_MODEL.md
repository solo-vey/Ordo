# DD-ORDO-M26-001 — Process Rail as Ordo's Core Model

**Status:** accepted
**Milestone:** M26 — Process Rail Reframing
**Date:** 2026-07-06

## Decision

Ordo is treated as an **AI-guided process language**, not as a CLI-first
runtime or a fully deterministic wizard.

Ordo's core model is the **Process Rail**: a formalised supporting process
structure that helps AI conduct a live conversation with a person without
losing route, state, gates, backtracking, checks, or output-generation rules.

## Rationale

Ordo's main goal is to combine AI flexibility with deterministic parts of a
process.

AI must remain an active reasoning executor: it analyses, asks questions,
advises, interprets answers, and explains decisions. The Process Rail does
not replace this reasoning; it stabilises it.

## Consequences

- The CLI is a deterministic helper layer, not the main conversational runtime.
- Semantic JSON IR is the machine-readable form of the Process Rail.
- Ordo has two key modes: AI-guided authoring and hybrid execution.
- Raw tool output is not human-facing output by default; AI must interpret it
  in plain language.
- Backtracking, correction handling, and deviation/resume semantics are
  first-class language concerns.
