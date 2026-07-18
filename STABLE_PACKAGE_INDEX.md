## M67.4 — Clean Package Gate Docs/Schema Alignment

Status: `accepted-docs-schema-alignment / passed-validation`

Primary files:

- `language/CLEAN_PACKAGE_GATE.md`
- `language/DERIVED_ARTIFACT_SYNC_VALIDATION_PROFILE.md`
- `language/spec/25_CLEAN_PACKAGE_GATE_MODEL.md`
- `M67_4_CLEAN_PACKAGE_GATE_DOCS_SCHEMA_ALIGNMENT_REPORT.md`

- M67.3: CLI clean-check minimal implementation patch (`ordo clean-check`) — implemented-minimal / passed-cli-validation.
## M67.2 CLI Clean-Check Support Design

Status: `accepted design / no implementation patch`.

M67.2 defines the future `ordo clean-check <package>` CLI contract for package cleanliness review. It does not implement the command and does not touch applied packages.

## M66.0 Package Startup Standard

Status: `accepted docs/schema convention / no runtime promotion`.

M66.0 adds `startup_package_profile` for package startup modes, entry files, readiness gates, and authority boundaries. It builds on M64 program-level contracts and M65 prompt registry conventions.

Runtime/core/CLI/opcode behavior remains unchanged.

## M65.1 APF / History Event Factory Prompt Registry Adoption Plan

Status: `accepted adoption plan / no source rewrite`.

M65.1 defines how `packages/history_event_guided_intake/` should adopt M65.0 Prompt Registry: quick-start prompt, selected node helpers, artifact helpers, repair helpers, manifest coverage, validation profile, and smoke test plan.

It does not create final prompt files or change APF source YAML/runtime behavior. The next implementation patch may be M65.2.

## M65.0 Prompt Registry Standard

Status: `accepted docs/schema convention / no runtime promotion`.

M65.0 adds `prompt_registry` and `prompt_refs` as package-level conventions for helper prompts. It does not change current stable runtime/package behavior. APF rc.1 remains the current standard applied module; concrete APF prompt files are future package adoption work.

## M64 First-Wave Closure

Status: `closed-first-wave / passed`.

M64.0–M64.3 form the current program-level package contract baseline for Ordo v0.12 preview work:

```text
program_contract → interaction_model → process_rail → conversation_semantics → program_level_approval_gate/profile
```

This baseline is documentation/schema/lint-profile design only and remains compatible with M63.3/APF rc.1 runtime/package behavior.

## M64.3 Program-level approval gate lint/profile design

Status: `docs/schema/lint-profile design / no runtime promotion`. M64.3 adds the program-level approval gate model, severity levels, approval decisions, and light/standard/strict profile behavior. Runtime/package behavior remains compatible with M64.2 and M63.3/APF rc.1.

## M64.2 Interaction/process/conversation schema conventions

Status: `docs/schema convention / no runtime promotion`. M64.2 adds `interaction_model`, `process_rail`, and `conversation_semantics` documentation and schemas. Runtime/package behavior remains compatible with M64.1 and M63.3/APF rc.1.



## M64.1 Program-level contract schema convention

Status: `schema convention / docs only`. Current runtime/package behavior remains M63.3/APF rc.1. M64.1 adds `program_contract` documentation and schema convention without runtime/opcode promotion.

# Stable Package Index — M63.1

Current line: Ordo v0.12 / post-M62 APF rc integration.

## Current standard applied module

- `packages/ordo_applied_project_factory/` — `ordo.applied_project_factory` `0.1.0-rc.1`, lifecycle `release-candidate`, standard applied module `true`.

## Historical note

- APF `0.1.0-alpha.14` was the M62 historical import point. It is obsolete for current use.

## Companion utilities

- `ordo_pathwalk/`
- `utilities/ordo_visual_graph_generator/`


### M63.2 APF rc.1 validation profile

APF `ordo.applied_project_factory` remains the current `0.1.0-rc.1` standard applied module. Validation profile is formalized in `M63_2_APF_RC_VALIDATION_PROFILE.md`; known limitations are listed in `M63_2_APF_RC_KNOWN_LIMITATIONS.md`.


## M63.3 APF RC language-pattern classification update

- APF `v0.1.0-rc.1` pattern candidates reclassified for RC integration.
- `FLOW.JOIN` and `SHARED.TAIL.REFERENCE` remain future IR candidates.
- No runtime-core, IR/opcode, parent CLI, or APF source YAML changes.

## M64.0 Language Improvement Intake

Status: `planning/intake only`

Current stable runtime/package behavior remains M63.3/APF rc.1. M64.0 adds no runtime or opcode changes. It only preserves and classifies the M64 prep improvement pack and sets the M64.1–M64.3 planning path.

## M65.2 History Event Factory Prompt Registry Skeleton

Status: `implemented-skeleton / package-local`.

M65.2 implements prompt files, `prompt_registry`, selected `prompt_refs`, and `PROMPT_MANIFEST.json` for `packages/history_event_guided_intake/`. Runtime/core/CLI/opcode behavior remains unchanged.

## M65.3 stable additions

- `language/PROMPT_REGISTRY_VALIDATION_PROFILE.md`
- `language/schemas/prompt_registry_validation_profile_schema.yaml`
- `language/examples/source/prompt_registry_validation_profile_example.ordo.yaml`
- `language/spec/20_PROMPT_REGISTRY_VALIDATION_MODEL.md`
- `language/improvement_intake/m65_3/M65_3_PROMPT_REGISTRY_VALIDATION_LINT_PROFILE_REPORT.md`
## M65 first-wave closure

- `M65_FIRST_WAVE_CLOSURE_REPORT.md`
- `M65_0_PROMPT_REGISTRY_STANDARD_REPORT.md`
- `M65_1_APF_HISTORY_EVENT_FACTORY_PROMPT_ADOPTION_PLAN_REPORT.md`
- `M65_2_HISTORY_EVENT_FACTORY_PROMPT_REGISTRY_IMPLEMENTATION_PATCH_REPORT.md`
- `language/improvement_intake/m65_3/M65_3_PROMPT_REGISTRY_VALIDATION_LINT_PROFILE_REPORT.md`

## M66.1 package startup profile application

Latest package-local startup-profile patch: `packages/history_event_guided_intake/source/program.ordo.yaml` declares `startup_package_profile`; default mode is `analyst_quick_start`.

## M66.2 startup validation artifacts

- `language/STARTUP_PROFILE_VALIDATION_PROFILE.md`
- `language/schemas/startup_profile_validation_profile_schema.yaml`
- `language/examples/source/startup_profile_validation_profile_example.ordo.yaml`
- `language/spec/22_STARTUP_PROFILE_VALIDATION_MODEL.md`

## M66 first-wave closure

Stable package-startup line closed: `M66.0 → M66.1 → M66.2`.

Stable artifacts include `startup_package_profile`, package startup model docs, History Event Factory startup profile application, and startup readiness validation profile.

## M67.0 package-consistency additions

- Derived artifact sync standard.
- Delta backlog standard.
- Prompt registry packaging checks.


## M67 first-wave closure

Closed: M67.0, M67.2, M67.3, M67.4. Excluded: M67.1 package-local patch.

## M68.0 — CLI Clean-Check Hardening Plan

Status: `accepted-plan / passed-scope-validation`

Artifacts:

- `cli/docs/CLEAN_CHECK_HARDENING_PLAN.md`
- `cli/docs/CLEAN_CHECK_FIXTURE_MATRIX.md`
- `cli/docs/REPO_LEVEL_PACKAGE_HYGIENE_PLAN.md`
- `language/spec/26_CLI_CLEAN_CHECK_HARDENING_FIXTURE_MODEL.md`
- M68.1 clean-check fixture test suite: implemented.


## M68.2

- `ordo clean-check` output and exit-code hardening accepted.
- Scope remains CLI utility hardening; applied packages are unchanged.

## M68.3 — Repo-level package hygiene design

Status: `accepted-design / implementation deferred`.

Artifacts:

- `cli/docs/REPO_LEVEL_PACKAGE_HYGIENE_DESIGN.md`
- `cli/docs/REPO_LEVEL_PACKAGE_HYGIENE_PLAN.md`
- `language/spec/27_REPO_LEVEL_PACKAGE_HYGIENE_MODEL.md`
- `docs/design_decisions/DD-ORDO-M68-002_REPO_LEVEL_PACKAGE_HYGIENE_DESIGN.md`

Preferred future command shape: `ordo repo-check <repo> --clean`.

## M68.4

- `repo-check --clean` optional integration is implemented for repo-level package hygiene aggregation.

## M68 first-wave closure

Closed line: `M68.0 → M68.1 → M68.2 → M68.3 → M68.4`. Status: `closed-first-wave / passed`. Scope: CLI clean-check hardening, real fixtures, output/exit-code hardening, repo-level hygiene design, and optional `repo-check --clean` integration. Applied packages remain delegated.

- M69.0: CI / release clean gate design and policy matrix — accepted design.

- **M69.1 CI workflow implementation** — `implemented-ci-workflow / passed-validation`.

- `M69.2`: release clean gate integration — implemented and validated.

- M69.3: clean-gate evidence / release provenance linkage.

## M69.4
- Added CI/release fixture and smoke-test matrix; 34 targeted tests passed.

- M70.0: production repo hygiene policy design and root classification — accepted design.

- M70.1: production `repo_hygiene.yml` safe initial policy adoption.

- M70.4 — production CI/release validation (`passed-validation`).

- M70 first-wave closure — production repo hygiene enforcement and CI/release validation closed.

## M71.0 review artifact
- `M71_0_PROMPT_REGISTRY_STABLE_IDS_DELTA_REVIEW_REPORT.md`

- M71.1 — stable prompt identity and versioning convention (accepted).

- M71.2 schema/profile update recorded; package prompt migration remains pending within M71.

- `M71.3` — History Event Factory stable prompt ID migration — implemented, validation passed.

### M71.4

Runtime prompt application-order and trace-evidence contract validated for History Event Factory. Core session-trace writer remains unchanged pending any separately authorized implementation work.

- `M71 first-wave closure` — stable semantic Prompt Registry migration and trace-evidence contract.
