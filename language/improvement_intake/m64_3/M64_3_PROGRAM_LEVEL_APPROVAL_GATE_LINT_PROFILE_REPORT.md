# M64.3 Program-level Approval Gate / Lint Profile Report

Status: `passed-docs-lint-profile-design`

## Scope

M64.3 defines a documentation and lint/profile design layer for evaluating top-level M64 program contracts.

It covers:

- `program_level_approval_gate` model;
- severity levels: `error`, `warning`, `info`;
- approval decisions: `approved`, `approved_with_warnings`, `blocked`, `not_applicable`;
- approval profiles: `light`, `standard`, `strict`;
- conventional lint/check IDs;
- schema convention and example source fragment;
- documentation links and backlog update.

## Created / updated documents

Created:

- `language/PROGRAM_LEVEL_APPROVAL_GATE.md`
- `language/PROGRAM_LEVEL_APPROVAL_PROFILE.md`
- `language/registry/PROGRAM_LEVEL_APPROVAL_GATE_VALUES.md`
- `language/schemas/program_level_approval_gate_schema.yaml`
- `language/examples/source/program_level_approval_gate_example.ordo.yaml`
- `language/spec/18_PROGRAM_LEVEL_APPROVAL_GATE_MODEL.md`
- `M64_3_PROGRAM_LEVEL_APPROVAL_GATE_LINT_PROFILE_REPORT.md`
- `M64_3_PROGRAM_LEVEL_APPROVAL_GATE_LINT_PROFILE_REPORT.json`
- `M64_3_VALIDATION_REPORT.json`

Updated:

- `README.md`
- `CHANGELOG.md`
- `FUTURE_BACKLOG.md`
- `STABLE_PACKAGE_INDEX.md`
- `language/README.md`
- `language/CHANGELOG.md`

## Design decision

The approval gate is a reviewer/linter contract, not a runtime primitive.

It may classify top-level contract readiness, but it must not override:

- node/gate semantics;
- human approval ownership;
- runtime evidence;
- generated artifact validation;
- final go/no-go.

## Profile behavior summary

| Profile | Intended use | Blocking behavior |
|---|---|---|
| `light` | drafts/examples | mostly warnings |
| `standard` | standard applied modules/reusable packages | missing identity/runtime authority can block |
| `strict` | release-candidate/stable/high-control packages | missing routing/resume/authority policies block |

## Non-changes

M64.3 intentionally does not introduce:

- runtime-core changes;
- compiler behavior changes;
- CLI command changes;
- new opcodes;
- deterministic natural-language classifier;
- `FLOW.JOIN` implementation;
- `SHARED.TAIL.REFERENCE` implementation.

## Validation result

Result: `passed-docs-lint-profile-design`

The new model remains inside the M64 documentation/schema convention line and is ready for discussion or first-wave closure.
