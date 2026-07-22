# DD-ORDO-M27-001 — Ordo Project Builder

## Status

Accepted

## Context

After M26, the Process Rail became Ordo's central model. The next practical
step was to describe a mechanism through which a PM or analyst creates new
Ordo projects through a conversation with an AI Ordo Developer rather than by
writing YAML manually.

## Decision

Add `ordo.project_builder` as the first Ordo package for AI-guided authoring.

A PM describes their intent in plain language. The AI Ordo Developer asks
questions, designs the Process Rail, creates or updates YAML files, runs
deterministic helper checks, and compiles Semantic JSON IR. The CLI does not
communicate with the PM directly; AI interprets validation results.

## Consequences

- Authoring becomes a first-class Ordo scenario.
- A PM is not required to write Ordo YAML.
- The AI Ordo Developer becomes a distinct language role.
- The CLI remains a deterministic helper layer.
- Semantic JSON IR is the result of the authoring loop, not only an internal
  build artifact.
