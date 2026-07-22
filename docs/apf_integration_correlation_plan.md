# M62.0 — APF Integration Correlation Plan

Status: `passed-design-docs-only`

This document is the first controlled integration step for `ordo.applied_project_factory` (APF) into the current Ordo language package line after M61 Companion Utilities Line Closure.

M62.0 does **not** import APF code into the current workspace. It establishes the correlation, package layer, risks, and next-step plan.

## Inputs analyzed

| Input | Role |
|---|---|
| `ORDO_LANGUAGE_MODEL_IMPROVEMENTS_PACKAGE.md` | Language/process-model improvement handoff. |
| `ordo_applied_project_factory_v0_1_0_alpha_14_dev.zip` | Current standalone APF module package. |
| `ordo_github_workspace_v0_12_apf_v0_1_0_alpha_14_existing_process_improvement_branch.zip` | Older full language workspace that already carried APF as a package. |
| M61 Line Closure workspace | Current stable language package and companion utility boundary. |

## APF snapshot

| Field | Value |
|---|---|
| module id | `ordo.applied_project_factory` |
| module version | `0.1.0-alpha.14` |
| language compatibility declared by APF | `ordo >= 0.12.0-preview-rc1` |
| source YAML SHA-256 | `dbeb51f58b19a1048146f9714a523213b0b61c99cbbc1ba1aed75c85b366e14a` |
| nodes | `54` |
| gates | `38` |
| assertions | `28` |
| outputs | `1` |
| alpha.14 minimal validation | `passed_minimal_validation` |
| APF package present in older workspace branch | `True` |

## Correlation with current M61 line

M61 closed the companion utility layer:

```text
Visual Graph Generator = read-only visualization utility
PathWalk = real-module graph/testcase/review artifact utility
```

APF should not be treated as another companion utility. It is a higher-level standard applied module whose purpose is to author new Ordo playbooks/process packages.

Recommended package taxonomy after M62:

```text
Ordo language core
  → runtime semantics, CLI, IR, validation rules

Companion utilities
  → utilities/ordo_visual_graph_generator/
  → utilities/ordo_pathwalk/

Standard applied modules
  → packages/ordo_applied_project_factory/   # planned M62.1 import
```

## What is already compatible

- APF is already packaged as an Ordo module with `source/program.ordo.yaml`, output templates, reports, tests, runtime traces, and docs.
- APF alpha.14 already uses scoped patch discipline and minimal validation rather than forcing full validation after every change.
- The existing-process improvement branch is already implemented as a reusable pattern: baseline load, improvement mode selection, before/after review, confirmed change set, scoped YAML patch, minimal validation, and shared-tail handoff join.
- M61 utilities can support APF review without being merged into APF:
  - Visual Graph Generator can render APF source graph views.
  - PathWalk can produce terminal paths, clean/noise cases, and review cards for APF once imported.

## What is not yet compatible / not yet integrated

- APF is not yet present in the current M61 workspace.
- The current APF source still needs adaptation to the latest stable package layout and docs conventions from M61.
- Branch 1 and Branch 2 reviews are not closed; their progressive tree authoring and terminal output binding corrections should not be silently marked as complete.
- Language-level constructs from the improvement package remain candidate patterns, not formal IR/opcode contracts.
- Full validation remains deferred by APF design and should not be claimed until a terminal/pre-handoff gate runs it.

## Integration boundary for M62.1

M62.1 should import APF as a standard applied module, not as a utility and not into runtime core:

```text
packages/ordo_applied_project_factory/
  source/program.ordo.yaml
  output_templates/
  docs/
  tests/
  reports/
  run_inputs/
  runtime/
  visuals/
```

M62.1 should preserve the standalone APF package contents and add current-package integration notes. It should not rewrite APF branch logic yet.

## Language pattern extraction boundary

The improvement document contains strong candidates for future language/process-model patterns. In M62.0 they are classified, not implemented.

| Pattern group | Candidate examples | M62.0 classification |
|---|---|---|
| Input/output readiness | `INPUT.POLICY`, `OUTPUT.CANDIDATE.CATALOG` | language design pattern / APF schema convention |
| Terminal outputs | `TERMINAL.OUTPUT.BIND`, `TERMINAL.READY.CHECK` | high-priority APF reusable subflow; future language construct candidate |
| Template review | `OUTPUT.TEMPLATE.CHECK`, `OUTPUT.MOCK.EXAMPLE`, `OUTPUT.TEMPLATE.REVIEW` | APF-level flow first; future lint/schema candidate |
| Progressive authoring | `TREE.VISION.CAPTURE`, `SUBTREE.DRAFT`, `NODE.REVIEW`, `BRANCH.REVIEW` | APF authoring runtime pattern |
| Flow reuse | `FLOW.JOIN`, `SHARED.TAIL.REFERENCE` | general Ordo language pattern candidate |
| Patch discipline | `YAML.PATCH.SCOPED`, `VALIDATION.MINIMAL`, `VALIDATION.FULL.DEFERRED` | package authoring standard and validation policy |
| Review rendering | `CURRENT.NODE.DISPLAY.BLOCK`, `CONTROL.ACTION.BOOKKEEPING` | user-facing runtime/review rendering standard |

## Recommended next milestones

### M62.1 — APF Package Import into Current Language Package

Import the APF package under `packages/ordo_applied_project_factory/`, preserve its current alpha.14 structure, add integration notes, and run structural smoke checks.

Non-goals:

- no APF branch rewrite;
- no runtime-core changes;
- no formal IR opcode additions;
- no full validation claim.

### M62.2 — APF Documentation and Book Section

Document APF as a standard applied module and explain how it relates to companion utilities.

### M62.3 — APF Language Pattern Extraction Plan

Promote only the most stable APF concepts into language-pattern documentation, grouped by level: APF subflow, schema convention, lint candidate, IR candidate.

### M62 Line Closure

Close the APF import/correlation line after APF is present, documented, and its language-pattern extraction backlog is explicit.

## Explicit non-goals for M62.0

- No APF code import.
- No rewrite of `source/program.ordo.yaml`.
- No runtime execution of generated testcases.
- No scoring/calibration/model benchmark.
- No watchdog/process-boundary hardening.
- No merge of APF with PathWalk or Visual Graph Generator.
- No claim that Branch 1 / Branch 2 APF review is closed.

## Decision

Proceed to M62.1 only as a controlled package import.

Stable base for M62.1: `M61 Line Closure`.

APF candidate source: `ordo_applied_project_factory_v0_1_0_alpha_14_dev.zip`.
