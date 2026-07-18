# M63.0 — APF RC Integration Planning / Delta Review

**Date:** 2026-07-08  
**Base language package:** Ordo v0.12 / M62 line closure  
**Target APF:** `ordo.applied_project_factory` `v0.1.0-rc.1`  
**Milestone status:** planning / delta-review gate  
**Implementation scope:** docs-only; no APF source rewrite; no runtime-core changes

## 1. Purpose

M63 starts the release-candidate integration line for APF `v0.1.0-rc.1` after M62 line closure.

The goal of M63.0 is not to import code yet. It records:

1. the current M62 APF import state;
2. the target rc.1 release-candidate state supplied by the maintainer;
3. which adaptation notes must update the parent language package;
4. what is allowed to enter language core, standard applied module docs, companion utilities, future backlog, or remain APF-local.

## 2. Current M62 baseline

M62 line closure contains APF as a standard applied module at the historical import point:

```text
packages/ordo_applied_project_factory/
module_id: ordo.applied_project_factory
imported_version: v0.1.0-alpha.14
role: standard applied module
status: historical M62 import point
```

M62 also established the architectural split:

```text
Ordo language core
  -> runtime / CLI / IR / validation semantics

Companion utilities
  -> PathWalk
  -> Visual Graph Generator

Standard applied modules
  -> ordo_applied_project_factory
```

## 3. Target rc.1 state declared for M63

The target state is:

```text
APF module: ordo.applied_project_factory
APF version: v0.1.0-rc.1
Source base: alpha.21
Target line: M63 / post-M62 APF RC integration
Lifecycle: release-candidate
Go/no-go: go
```

Declared validation evidence from the maintainer:

```text
lint: passed
compile: passed
test: passed
coverage: passed
validate-state: passed
next-step: ready_for_ai_next_move
validate-output: passed
validate-artifacts: passed
consistency: passed_with_warnings
go/no-go: go
repo-check clean source: passed
```

## 4. Local archive availability check

M63.0 checked `/mnt/data` for an explicit APF rc.1 / alpha.21 package archive.

```text
rc_archive_present_in_sandbox: False
matched_candidates: none
```

This means M63.0 can complete the planning gate, but M63.1 package import must not claim file-level replacement of alpha.14 unless the actual APF rc.1 archive is present.

## 5. M63.0 decision

```text
Decision: proceed_to_M63_1_when_rc_archive_available
Planning readiness: passed_with_input_gate
Blocking issue for M63.0: none
Blocking issue for M63.1 import: APF rc.1 archive must be available as an input artifact
```

## 6. Explicit non-goals

M63 must not quietly turn into a broad redesign. The following are out of scope for M63.0:

```text
- APF branch 1 / branch 2 process rewrite
- implementation of FLOW.JOIN in IR
- implementation of SHARED.TAIL.REFERENCE in IR
- promotion of validate-factory-output into parent CLI
- runtime execution of generated testcases
- scoring / calibration
- watchdog / process-boundary hardening
```

## 7. Next milestones

```text
M63.1 — APF rc.1 Package Import / Metadata Sync
M63.2 — APF RC Validation Profile / Known Limitations
M63.3 — APF RC Language Pattern Classification Update
M63 Line Closure — APF rc.1 acceptance decision
```
