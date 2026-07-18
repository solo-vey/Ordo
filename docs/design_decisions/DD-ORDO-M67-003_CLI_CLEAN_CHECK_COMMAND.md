# DD-ORDO-M67-003 — CLI Clean Check Command Contract

Status: `accepted-design`
Date: 2026-07-09
Milestone: M67.2

## Context

M67.0 introduced package consistency conventions for derived artifact sync, delta backlog, and prompt registry packaging checks. The next step is to define how those conventions should be surfaced by the Ordo CLI without applying them to a specific package and without mutating package contents.

## Decision

Adopt `ordo clean-check <package>` as the future CLI surface for package cleanliness review.

The command contract includes:

- profiles: `light`, `standard`, `strict`;
- status values: `passed`, `passed_with_warnings`, `blocked`, `not_applicable`;
- JSON output mode;
- warning-to-failure option through `--fail-on-warning`;
- deterministic file, YAML, reference, and checksum checks;
- no mutation of package source or derived artifacts.

## Rationale

A dedicated clean-check command gives maintainers and applied-package models a clear go/no-go interface without overloading compile, lint, package, or runtime-status commands.

This keeps package consistency review separate from runtime execution and from package-local authoring.

## Scope

In scope for this decision:

- CLI command contract;
- expected output shape;
- check group definitions;
- profile and status semantics;
- boundaries for future implementation.

Out of scope:

- actual CLI implementation;
- package-local source YAML edits;
- runtime/core/compiler changes;
- opcode promotion;
- lockfile or runtime artifact regeneration;
- deterministic natural-language safety classification.

## Consequences

A later implementation milestone can add `cli/ordo/clean_check.py`, update `cli/ordo/cli.py`, and add tests while conforming to this design.

Applied-package migrations remain delegated to the applied-package model.
