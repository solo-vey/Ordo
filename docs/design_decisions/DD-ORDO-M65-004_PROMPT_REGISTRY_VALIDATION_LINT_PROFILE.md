# DD-ORDO-M65-004 — Prompt Registry Validation / Lint Profile Design

Status: `accepted-design`

## Decision

Adopt a prompt registry validation/lint profile convention with `light`, `standard`, and `strict` profiles, plus `error`, `warning`, and `info` severities.

## Rationale

M65.0 made prompts first-class package elements. M65.2 added a concrete skeleton to the History Event Factory package. A validation profile is needed so packages can detect missing prompt files, stale refs, unsafe authority claims, manifest gaps, and discoverability failures before release.

## Boundaries

This decision does not add runtime behavior, compiler behavior, CLI commands, opcodes, deterministic natural-language classification, or compiled IR regeneration.

## Consequence

Future package releases may use `PROMPT_REGISTRY_VALIDATION_GATE` as a package-level release gate or manual review checklist.
