# DD-ORDO-M30-001 — Book and Specification Alignment for Process Rail

## Status

Accepted

## Milestone

M30 — Book/spec alignment with the Process Rail model

## Context

After M26–M29, the Process Rail, Project Builder, Hybrid Execution, and CLI
helper commands were described in separate conceptual and language documents.
However, the book, entry-point specifications, and compiled book artifacts
could still appear to follow the earlier CLI/runtime-first model.

## Decision

M30 establishes the Process Rail as a cross-cutting model in the book and
specification:

- the book must contain the Process Rail in its manifest and compiled all-in-one;
- the introduction and basic explanatory sections must describe Ordo as an
  AI-first, Process-Rail-centred language;
- the language overview, Semantic JSON IR, and execution model must explicitly
  show AI-led authoring/execution;
- the CLI is described as a deterministic helper layer, not the main
  conversational runtime.

## Consequences

After M30, future GitHub cleanup must use the new model as the canonical
direction. Earlier CLI-first wording must be treated as legacy wording and
corrected during cleanup.
