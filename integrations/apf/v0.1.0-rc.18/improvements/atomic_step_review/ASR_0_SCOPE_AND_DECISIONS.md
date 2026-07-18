# ASR-0 — Atomic Step Review scope and decisions

## Purpose

Add an APF authoring-time review layer that detects non-atomic steps in generated playbooks and provides structured recommendations before package validation.

## Core principle

One step should have one primary responsibility, one observable result, and one explicit validation or confirmation boundary.

## Scope

ASR reviews generated-playbook process design. It does not enable new Ordo core syntax and does not change APF runtime behavior.

## Review outcomes

- `passed` — no atomicity issue detected.
- `recommendation` — decomposition would improve clarity or maintainability but is not required for correctness.
- `blocking_issue` — the step hides independent outcomes, confirmation, reconstruction, state transition, or validation in a way that can produce incorrect execution.
- `needs_human_decision` — safe decomposition depends on business intent.

## Initially blocking conditions

1. Generation and approval occur in the same step.
2. Reconstruction is used as confirmed evidence without explicit validation/confirmation.
3. Partial success can trigger transition to the next state.
4. A confirmed-state transition is a side effect of generation or validation.
5. Several independently releasable artifacts share one indivisible readiness status.
6. Validation checks intent, plan, or schema presence but not the materialized artifact.

## Initially advisory conditions

1. A step has multiple tightly related mechanical actions but one result.
2. A step could be decomposed for readability while remaining safely repeatable.
3. Failure routing is broad but does not risk confirmed data or decisions.

## Human authority

APF may propose decomposition but must not silently rewrite confirmed process semantics. Any split that changes business decisions, approvals, ownership, or state transitions requires human confirmation.

## Non-goals

- No internal APF atomicity enforcement yet.
- No automatic rewriting of confirmed nodes.
- No new Ordo language gates in this step.
- No release assembly in ASR-0.
