# ordo-2026.07.14-rc.1 — Formal Versioning Baseline

- Established Ordo Language `0.13.0-rc.1` and Ordo ARF/IRF `0.1.0-rc.1` as independent SemVer lines.
- Added release ledger, upgrade-impact catalog and playbook impact resolver.
- Backfilled closed backlog work into the initial formal release baseline.
- Made backlog-to-release linkage mandatory through `target_release`, `affects` and `completed_in`.
- Added package compatibility ranges and prohibited automatic playbook rewrites during upgrades.

## M88.0 — Stable first-class flow reuse

- Promoted FLOW.JOIN and SHARED.TAIL.REFERENCE to stable_optional after two-package equivalence evidence.
- Added deterministic return_to and bounded max_call_depth runtime contract.
- Added recursive-entry and depth-overflow fail-closed guards.
- Added real adoption in ordo_hybrid_executor.

# M72.1 — EXECUTION_TRACE Core Language Contract

- Added `EXECUTION_TRACE` as a first-class core runtime artifact.
- Added canonical source key `execution_trace` and IR identity `EXECUTION_TRACE.DEF`.
- Added complete schema, closed event catalog, capture levels, replay modes, integrity and privacy invariants.
- Preserved the older `trace:` structure as a legacy compatibility view.
- Added normative specification, registry and source example.

## M67.4 — Clean Package Gate Model

- Added `clean_package_gate` docs/schema aligned to the implemented CLI command.
- Added `derived_artifact_sync_validation_profile` docs/schema.
- Added clean package gate example and Spec 25.
- No runtime/core/compiler/opcode or package-local changes.

## M67.2 — CLI Clean-Check Support Design

- Added Spec 24 — Clean Package CLI Model.
- Added CLI clean-check command design document.
- Added design decision DD-ORDO-M67-003.
- Design only; no CLI implementation or package-local source changes.

## M66.0 — Package Startup Standard / Startup Package Profile

- Added `PACKAGE_STARTUP_STANDARD.md` and `STARTUP_PACKAGE_PROFILE.md`.
- Added startup package profile schema, example, registry values, and Spec 21.
- Documentation/schema convention only; no runtime promotion.

# M65.0 — Prompt Registry Standard

- Added `prompt_registry` as a package-level source/schema convention.
- Added `prompt_refs` convention for nodes and other package elements.
- Added prompt type/audience/lifecycle/visibility/state-change/validation policy registries.
- Added prompt registry and prompt ref schema conventions.
- Added `spec/19_PROMPT_REGISTRY_MODEL.md` and source example.
- Clarified that helper prompts are supportive guidance only and cannot override gates, transitions, state, validation, program contracts, or human approval.
- No runtime core, compiler behavior, CLI command, or opcode change.

# M64 First-Wave Closure

- Closed the first M64 language improvement wave: `M64.0 → M64.1 → M64.2 → M64.3`.
- Confirmed the accepted language/package convention stack: `program_contract`, `interaction_model`, `process_rail`, `conversation_semantics`, and `program_level_approval_gate/profile`.
- Kept all M64 first-wave additions as docs/schema/lint-profile design only.
- No runtime core, compiler, CLI command, Semantic JSON IR execution behavior, or opcode change.

# M64.3 — Program-level approval gate lint/profile design

- Added `PROGRAM_LEVEL_APPROVAL_GATE.md`.
- Added `PROGRAM_LEVEL_APPROVAL_PROFILE.md`.
- Added `registry/PROGRAM_LEVEL_APPROVAL_GATE_VALUES.md`.
- Added `schemas/program_level_approval_gate_schema.yaml`.
- Added `examples/source/program_level_approval_gate_example.ordo.yaml`.
- Added `spec/18_PROGRAM_LEVEL_APPROVAL_GATE_MODEL.md`.
- Defined light/standard/strict approval profile behavior.
- Defined error/warning/info finding severity.
- Kept M64.3 design-only: no runtime, compiler, CLI command, or opcode change.

# M60 — Multi-target Runtime Compilation Layer

# M60.4.2 — Stabilization / Full Regression Pass

- Added validation report for the M60.4.1 baseline after PathWalk M60-native adaptation.
- Recorded class-split core CLI regression as the reliable acceptance gate for this environment: 82/82 passed across 21 unittest classes.
- Recorded PathWalk pytest result: 17/17 passed.
- Re-verified embedded runtime smoke for `runtime-status`, `verify-targets`, `next-step --format auto`, `intake --submit`, `restore-session`, `verify-session`, and embedded authoring-command blocking.
- No runtime feature changes were introduced.


- Added explicit horizontal targets: `json-ir`, `ordo-code-view`, and `session-trace`.
- Added `compiled/targets.manifest.json` to bind target hashes and `canonical_ir_hash`.
- Added CLI-rendered AI-facing Ordo-code view through `render-runtime-view` and `next-step --format ordo-code|auto`.
- Added `runtime/session.ordo.trace` as a CLI-written proof program for accepted runtime transitions.
- Added runtime packaging modes: `--runtime-view json`, `--runtime-view ordo-code`, and `--runtime-view json,ordo-code`.
- Extended verification so `verify-targets` and `verify-session` check target-set, session-chain, session-trace, and canary state.

# M30 — Book / Spec Alignment

- Оновлено language overview, Semantic JSON IR і execution model під Process Rail модель.
- Зафіксовано, що Semantic JSON IR є машинозчитуваною Process Rail для AI, а не повною заміною AI reasoning.
- Синхронізовано книгу, glossary і compiled all-in-one з language/spec напрямом M26–M29.

# M29 — CLI Helper Commands Model

- Додано `spec/14_CLI_HELPER_COMMANDS_MODEL.md`.
- Зафіксовано CLI як deterministic helper layer для AI-led authoring/execution.
- Додано helper command classes: `validate-state`, `check-gate`, `next-step`, `diff-state`, `explain-validation`.

# M28 — Hybrid Execution Model

- Додано `spec/13_HYBRID_EXECUTION_MODEL.md`.
- Зафіксовано AI Ordo Executor як головного виконавця готового Semantic JSON IR.
- Визначено execution loop: human input → AI interpretation → rail mapping → helper validation → AI explanation → next move.

# M27 — Project Builder Model

- Додано `spec/12_PROJECT_BUILDER_MODEL.md`.
- Зафіксовано AI-guided authoring як first-class сценарій Ordo.
- PM не пише YAML напряму; AI Ordo Developer створює Ordo project і компілює Semantic JSON IR через helper tools.

# Ordo Changelog

## v0.12.0-draft — Reliability, Trust Semantics & Execution Modes

### Added

- `gate.method`: `mechanical`, `self_verification`, `self_consistency`, `human`.
- `trust_class`: `deterministic`, `model_judgment`, `repeated_model_judgment`, `human_decision`.
- `trace_source`: `model_self_report`, `runtime_enforced`, `hybrid`.
- `execution_mode`: `full_runtime`, `chat_internal`, `freeform_only`.
- Canonical `ASSERTION` primitive.
- `on_unmatched_input` for `NODE.DEF`.
- `CLARIFY.REQUEST` op-code.
- `control_level`: `light`, `standard`, `strict`.
- Namespaced IDs in compiled IR.
- Version requirements for Profiles, Domain Packs and Libraries.
- Layer priority and explicit override model.
- `FREEFORM.maturity`, `incident_count`, `incident_threshold`.
- Compiler/linter rules for reliability checks.

### Changed

- `ASSERT.NOT` is now treated as a shortcut/projection of `ASSERTION` with `polarity: not`.
- `EXPECT.NOT` is now treated as a test projection of `ASSERTION`.
- Gate reports must show `method`, `trust_class`, and evidence requirements.
- Debug traces must show `trace_source`.

### Not included

- No platform-specific API implementation notes.
- No external platform integration notes.

## M46.1 — Contract / Artifact Coverage IR Model

- Added first-class language primitives for contracts, artifact requirements, coverage rules, rendered artifact assertions, and go/no-go decisions.
- Added Semantic JSON IR schema fields for contract-to-artifact coverage.
- Added schemas for `Contract`, `Artifact`, `ArtifactRequirement`, `CoverageRule`, `RenderedArtifactAssertion`, and `GoNoGo`.
- Added specification docs for contract propagation and rendered artifact validation.
- Updated opcode catalog with coverage-related constructs.

## M60.3.2 — Runtime CLI Safety Patch

- Added fail-fast behavior for bare `intake <package>` in non-TTY automation when no `--submit`, `--answers`, or `--non-interactive` mode is provided.
- Added regression coverage for subprocess `stdin=DEVNULL` so intake cannot hang a scenario-testing worker.
- Confirmed `next-step` keeps checkpoint details in report files rather than stdout.
- Updated scenario-testing documentation and book source guidance for PathWalk-style utilities.

## M60.4 — Native Restore Session / Append-only Rollback

- Added `ordo restore-session <package> --to-seq <N>` as a runtime command for correction/backtrack flows.
- Restore is append-only: it does not delete prior snapshots, evidence reports, or trace steps.
- Restore writes `reports/restore_session_report.json`, restore evidence, a restore state snapshot, a `session.ordo.trace` step with `action: restore_session`, and updates `runtime/live_session_state.json`.
- Embedded runtime CLI allowlist now includes `restore-session`.
- `verify-session` validates restore through the existing target-set, session-chain, session-trace, evidence, snapshot, and canary checks.

## M60.5 — PathWalk Benchmark Readiness

- Added benchmark-readiness documentation for scenario-testing utilities.
- Added PathWalk matrix-smoke as a compatibility gate outside runtime core.
- Runtime semantics unchanged.


## M65.1 — APF / History Event Factory Prompt Registry Adoption Plan

- Added package-level adoption plan for applying the Prompt Registry standard to History Event Guided Intake.
- Added current-node mapping, target structure, validation profile, and smoke test plan.
- No source YAML rewrite, prompt file implementation, runtime-core change, CLI change, or opcode promotion.

## M65.2 — History Event Factory Prompt Registry Skeleton

- Created concrete prompt files and prompt registry skeleton for History Event Guided Intake.
- Added prompt refs to selected nodes/artifacts/gates/output validation in package source YAML.
- Added package-local prompt manifest checksums.
- Kept runtime/core/CLI/opcode behavior unchanged.

## M65.3

- Added prompt registry validation/lint profile convention.
- Added prompt registry validation schema and example.
- Added spec chapter 20.
- No runtime/core/CLI/opcode changes.

## M66.2

Added startup profile validation/lint profile docs, schema, example, and spec chapter.

## M67.0

Added derived artifact sync, delta backlog, and prompt registry packaging check conventions.

## M68.0 — CLI clean-check hardening plan + fixture matrix

- Added planning docs for `ordo clean-check` hardening.
- Added synthetic fixture matrix for M68.1 tests.
- Added repo-level package hygiene planning notes.
- No CLI implementation, tests, packages, runtime, compiler, opcodes, lockfiles, or embedded CLI bundles changed.
- M68.1: clean-check fixture test suite evidence added.


## M68.2

- Recorded clean-check output / exit-code hardening as CLI-backed clean gate evidence refinement.

## M68.3

- Added repo-level package hygiene model as spec chapter 27.
- Defined policy-first aggregation over package-level clean-check results.
- Confirmed applied packages are delegated by default.
- No runtime, compiler, opcode, applied-package, or CLI implementation changes.

## M68.4

- Recorded optional `repo-check --clean` integration for repo-level package hygiene aggregation.

## M69.0

Added CI/release clean gate policy convention, schema, example, and spec chapter 28.

## M69.1

CI consumption of the repo-level clean gate is now implemented without changing language/runtime semantics.

## M69.2

- Integrated the accepted release clean-gate policy with repository workflow evidence.

## M69.3
- Added release clean-gate provenance linkage schema and model.

## M69.4
- Added CI/release fixture and smoke-test matrix; 34 targeted tests passed.

## M70.0

Added production repository root classification model; no language runtime semantics changed.

## M70.1

Production repository hygiene policy adopted without synthetic package enforcement for language or CLI roots.

## M70.2
- Added repository root contract model for release-critical language and CLI roots.

## M71.0
- Accepted delta review for stable semantic Prompt Registry IDs.
- M71.1: stable semantic prompt identity/versioning convention accepted.
