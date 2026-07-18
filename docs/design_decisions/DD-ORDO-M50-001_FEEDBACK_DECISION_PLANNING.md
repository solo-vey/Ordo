# DD-ORDO-M50-001 — Feedback Decision / Post-Review Change Planning

## Status

Accepted.

## Context

M49 introduced feedback intake materials. Before applying external feedback, Ordo needs a small decision layer so review findings are classified and prioritized consistently.

## Decision

Add an M50 post-review decision route that converts feedback items into accepted, deferred, rejected, or owner-decision-required tasks. This route does not change language semantics, CLI runtime behavior, or package business logic.

## Consequences

- External feedback can be processed without destabilizing the frozen release candidate.
- Future implementation milestones can be scoped from concrete accepted feedback items.
- Release-blocking feedback can be separated from backlog or documentation improvements.
