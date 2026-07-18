# APF A5 — Validation Profile and Release Hygiene Policy

## Purpose

This policy aligns the APF working baseline with the Ordo v0.12 validation and clean-package conventions without turning APF-local checks into parent CLI semantics.

## Validation layers

APF validation has three distinct layers:

1. **Parent-compatible CLI validation** — existing Ordo CLI commands and policy-gated repository hygiene checks.
2. **APF-local required validation** — deterministic or reviewable checks owned by the APF package.
3. **Evidence-only or deferred capability checks** — capabilities that must not be claimed before the A6 audit.

Passing one layer does not silently substitute for another.

## Required parent-compatible chain

```text
lint → compile → test → coverage → validate-state → next-step
→ validate-output → validate-artifacts → consistency → go-no-go
→ clean-check → repo-check → repo-check --clean (when policy applies)
```

`clean-check` and `repo-check --clean` evaluate cleanliness. They do not regenerate stale artifacts.

## APF-local blockers

A release is blocked if any of the following fail:

- program-contract alignment;
- interaction/process-rail alignment;
- Prompt Registry integrity and prompt-file checksums;
- runtime-contract consistency;
- APF scope preservation;
- deferred backlog remains unstarted unless separately approved.

These are APF requirements, not claims that Ordo exposes matching generic commands.

## Package classes

APF distinguishes:

```text
clean source package ≠ runtime/development package ≠ evidence pack
```

A clean source package must not carry stale compiled IR, runtime state, generated outputs, caches, local logs or unreferenced evidence. Runtime artifacts may exist in a runtime/development package. Validation outputs and confirmation records belong in an evidence pack or an explicitly approved self-contained transfer/release package.

## Freshness and derived-artifact sync

Every declared derived artifact must identify its source, derivation method, freshness policy and stale action. Silent regeneration is prohibited. A stale artifact either blocks release, is explicitly regenerated, is marked historical, is removed from the clean source package, or is represented by an explicit nonblocking delta-backlog entry.

## Current adaptation boundary

During A5:

- the working copy is not declared a new confirmed release;
- transfer-package checksum manifests are not regenerated yet;
- final archive assembly and whole-package checksums remain deferred to A7;
- replay, snapshot, diff and restore evidence remain deferred to A6;
- no APF authoring-flow semantics are changed.
