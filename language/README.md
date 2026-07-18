## M67.4 — Clean Package Gate Model

M67.4 documents `clean_package_gate` and `derived_artifact_sync_validation_profile` as language-level conventions aligned to the implemented `ordo clean-check` CLI command.

Start here:

- `CLEAN_PACKAGE_GATE.md`
- `DERIVED_ARTIFACT_SYNC_VALIDATION_PROFILE.md`
- `schemas/clean_package_gate_schema.yaml`
- `schemas/derived_artifact_sync_validation_profile_schema.yaml`
- `examples/source/clean_package_gate_example.ordo.yaml`
- `spec/25_CLEAN_PACKAGE_GATE_MODEL.md`

## M67.2 — Clean Package CLI Model

M67.2 documents the CLI-facing model for a future `ordo clean-check <package>` command.

Start here:

- `spec/24_CLEAN_PACKAGE_CLI_MODEL.md`
- `../cli/docs/CLEAN_CHECK_COMMAND.md`
- `../docs/design_decisions/DD-ORDO-M67-003_CLI_CLEAN_CHECK_COMMAND.md`

This is design only: no CLI implementation, runtime, compiler, opcode, or package-local change.

## M66.0 — Package Startup Standard

M66.0 documents `startup_package_profile` as a package-level startup convention for declaring startup modes, entry files, default start path, readiness gates, and startup authority boundaries.

Start here:

- `PACKAGE_STARTUP_STANDARD.md`
- `STARTUP_PACKAGE_PROFILE.md`
- `registry/STARTUP_PACKAGE_PROFILE_VALUES.md`
- `schemas/startup_package_profile_schema.yaml`
- `examples/source/startup_package_profile_example.ordo.yaml`
- `spec/21_PACKAGE_STARTUP_MODEL.md`

This is docs/schema convention only: no runtime core, compiler, CLI command, or opcode change.

## M65.0 — Prompt Registry Standard

M65.0 documents `prompt_registry` and `prompt_refs` as package-level source/schema conventions for small helper prompts.

Start here:

- `PROMPT_REGISTRY.md`
- `registry/PROMPT_REGISTRY_VALUES.md`
- `schemas/prompt_registry_schema.yaml`
- `schemas/prompt_ref_schema.yaml`
- `examples/source/prompt_registry_example.ordo.yaml`
- `spec/19_PROMPT_REGISTRY_MODEL.md`

This is docs/schema/lint-profile design only: helper prompts support package execution but do not override nodes, gates, transitions, state, validation evidence, or human approval.

## M64 First-Wave Closure

M64.0–M64.3 are closed as the first program-level language-improvement wave.

Accepted language/package conventions:

- `program_contract`
- `interaction_model`
- `process_rail`
- `conversation_semantics`
- `program_level_approval_gate`
- approval profiles: `light`, `standard`, `strict`

See root-level `M64_FIRST_WAVE_CLOSURE_REPORT.md` for closure status and backlog boundaries.

## M64.3 — Program-level approval gate lint/profile design

M64.3 documents the program-level approval gate as a lint/profile design layer for reviewing `program_contract`, `interaction_model`, `process_rail`, and `conversation_semantics`.

Start here:

- `PROGRAM_LEVEL_APPROVAL_GATE.md`
- `PROGRAM_LEVEL_APPROVAL_PROFILE.md`
- `registry/PROGRAM_LEVEL_APPROVAL_GATE_VALUES.md`
- `schemas/program_level_approval_gate_schema.yaml`
- `examples/source/program_level_approval_gate_example.ordo.yaml`
- `spec/18_PROGRAM_LEVEL_APPROVAL_GATE_MODEL.md`

This is docs/schema/lint-profile design only: no runtime core, compiler, CLI command, or opcode change.

## M64.2 — Interaction / Process Rail / Conversation Semantics

M64.2 documents three source-level conventions:

- `interaction_model`
- `process_rail`
- `conversation_semantics`

They are package authoring contracts and future lint/profile candidates. They are not opcodes and not deterministic natural-language classifiers.

Start here:

- `INTERACTION_MODEL.md`
- `PROCESS_RAIL_SCHEMA_CONVENTION.md`
- `CONVERSATION_SEMANTICS.md`
- `HYBRID_EXECUTION_POLICY_CONVENTION.md`
- `registry/INTERACTION_PROCESS_RAIL_CONVERSATION_VALUES.md`
- `spec/17_INTERACTION_PROCESS_RAIL_CONVERSATION_MODEL.md`


# Ordo Language Specification v0.12

**Статус:** canonical draft для Ordo v0.12.  
**Назва версії:** Reliability, Trust Semantics & Execution Modes.  
**Мета:** вирівняти мову, IR, compiler/linter rules і приклади так, щоб книга «Ordo для чайників» описувала вже формалізовану специфікацію, а не лише концепцію.


## M26 — Process Rail Reframing

M26 додає концептуальне уточнення: Ordo не є CLI-first runtime або повністю детермінованим wizard. Ordo є AI-guided process language, де **Process Rail** стабілізує роботу ШІ.

Ключові наслідки:

1. ШІ залишається активним cognitive executor.
2. CLI є deterministic helper layer.
3. Semantic JSON IR є машинозчитуваною формою Process Rail.
4. Backtracking, deviation handling і human explanation policy стають first-class concerns.

Див. `spec/11_PROCESS_RAIL_MODEL.md`.


## M29 — CLI Helper Commands Model

M29 вирівнює CLI як deterministic helper layer для AI-guided authoring/execution. CLI helper commands (`validate-state`, `check-gate`, `next-step`, `diff-state`, `explain-validation`) дають машинозчитуваний feedback для AI, але не замінюють AI Ordo Developer / AI Ordo Executor.

Документ специфікації: `spec/14_CLI_HELPER_COMMANDS_MODEL.md`.

## M30 — Book / Spec Alignment

M30 синхронізує основні entry points специфікації та книги під Process Rail модель. Після цього `00_ORDO_OVERVIEW.md`, `03_SEMANTIC_JSON_IR.md`, `04_EXECUTION_MODEL.md`, book manifest і compiled book all-in-one узгоджено з AI-first / Process-Rail-centered напрямом.

## M64.1 — Program-level Contract Schema Convention

M64.1 introduces `program_contract` as a top-level source/schema convention for package identity, lifecycle, control level, execution mode, compatibility, runtime profile, review points, and validation expectations.

See:

- `PROGRAM_LEVEL_CONTRACT.md`
- `spec/16_PROGRAM_LEVEL_CONTRACT_MODEL.md`
- `schemas/program_level_contract_schema.yaml`
- `registry/PROGRAM_LEVEL_CONTRACT_VALUES.md`

No new opcodes or runtime-core changes are introduced by M64.1.

## Що додає v0.12

1. Обовʼязкове `gate.method` і `trust_class`.
2. Явне `trace_source` для debug/execution trace.
3. Формальні `execution_mode`: `full_runtime`, `chat_internal`, `freeform_only`.
4. Канонічний примітив `ASSERTION`, з якого компілятор розгортає runtime/test/debug представлення.
5. `on_unmatched_input` і `CLARIFY.REQUEST` для контрольованого виходу за межі `allowed_answers`.
6. `control_level`: `light`, `standard`, `strict`.
7. Namespaced IDs і versioning для Core/Profile/Domain Pack/Library.
8. Layer priority і явний override.
9. FREEFORM maturity lifecycle.
10. Compiler/linter rules, які роблять reliability-вимоги перевірними.

## Що навмисно НЕ входить у v0.12

У цей пакет не включено платформні API-нотатки або інтеграційні механізми конкретних екосистем. v0.12 описує внутрішню еволюцію мови Ordo.

## Структура пакета

```text
spec/          canonical language chapters
registry/      довідники значень, op-кодів і пріоритетів
schemas/       YAML-схеми основних обʼєктів IR
examples/      Source, compiled IR і test-case приклади
lint_rules/    правила компілятора/лінтера
design_notes/  стислий design note v0.12
```

## Статус реалізації

Це **специфікаційне оновлення мови**, а не готовий програмний компілятор. Реальний компілятор/лінтер має реалізувати правила з `spec/10_COMPILER_RULES.md` і `lint_rules/LINT_RULES.md`.

## M27 — Project Builder Model

M27 додає authoring-сценарій: PM описує новий Ordo-проєкт природною мовою, а AI Ordo Developer перетворює цей опис у Ordo YAML, запускає helper checks і компілює Semantic JSON IR. Reference package: `packages/ordo_project_builder/`.

Документ специфікації: `spec/12_PROJECT_BUILDER_MODEL.md`.

## M28 — Hybrid Execution Model

M28 додає execution-сценарій: AI Ordo Executor виконує готовий Semantic JSON IR як Process Rail, використовує CLI/helper tools для детермінованих перевірок і пояснює результат людині без raw tool dump. Reference package: `packages/ordo_hybrid_executor/`.

Документ специфікації: `spec/13_HYBRID_EXECUTION_MODEL.md`.

## M46.1 — Contract / Artifact Coverage IR Model

M46.1 adds the language-level model for checking whether confirmed contracts are propagated into generated artifacts. It introduces first-class IR objects for `contract`, `artifact`, `artifact_requirement`, `coverage_rule`, `rendered_artifact_assertion`, and `go_no_go`.

Key documents:

- `spec/15_CONTRACT_ARTIFACT_COVERAGE_MODEL.md`
- `CONTRACTS.md`
- `ARTIFACT_COVERAGE.md`
- `GENERATED_ARTIFACT_VALIDATION.md`
- `GO_NO_GO.md`

This step is intentionally specification-first. Later M46 slices implement CLI behavior for `validate-artifacts`, `consistency`, and `go-no-go`.
- `CONSISTENCY_CHECK_REPORT.md` — machine-readable cross-artifact consistency report model.

- `RUNTIME_GUIDED_INTAKE_PROTOCOL.md` — runtime entry and guided-intake start rules.

## M57 Runtime Checkpoint Discipline

Runtime Mode now enforces a checkpoint layer: one node, one contract, and one decision at a time. Helper reports expose `checkpoint_table`, `earliest_incomplete_node`, `open_required_fields`, and `forward_allowed`. `next-step` prioritizes the earliest incomplete node, and `generate-output` is blocked while checkpoint gaps remain. Detailed rules live in `language/RUNTIME_CHECKPOINTS.md` and package `START_HERE_RUNTIME_MODE.md`; minimal runtime prompts stay minimal.


- `MULTI_TARGET_RUNTIME_COMPILATION.md` — M60.3 horizontal runtime targets: json-ir, ordo-code-view, session-trace, runtime view modes, target verification.

- `SCENARIO_TESTING_COMPATIBILITY.md` — M60.3.1 compatibility contract for external scenario-testing utilities such as PathWalk.

## M65.3 Prompt Registry Validation

Prompt registry validation is documented in `PROMPT_REGISTRY_VALIDATION_PROFILE.md` and `spec/20_PROMPT_REGISTRY_VALIDATION_MODEL.md`. It defines `light`, `standard`, and `strict` lint profiles for prompt refs, prompt manifests, discoverability, and authority-safe text review.

## M66.2 startup validation

Startup profile validation is documented in `STARTUP_PROFILE_VALIDATION_PROFILE.md` and spec chapter 22.

## M67.0 package consistency layer

M67.0 adds source/derived artifact sync conventions, delta backlog conventions, and prompt/startup packaging checks.

## M68.0 — CLI clean-check hardening plan + fixture matrix

M68.0 adds the planning layer for hardening `ordo clean-check`: fixture matrix, exit-code policy, JSON-output stability expectations, and repo-level hygiene planning. This milestone is planning-only and does not change CLI implementation or applied packages.
- M68.1 documents fixture-backed validation for CLI clean-check.


## M68.2

M68.2 keeps the M67 clean package gate contract aligned with a hardened CLI report shape for `ordo clean-check`.

## M68.3 — Repo-level package hygiene model

M68.3 adds spec chapter 27 for repo-level package hygiene. It defines repository clean aggregation as a policy layer above package-level `ordo clean-check`. The preferred future CLI integration is `ordo repo-check <repo> --clean`. This is not runtime or compiler semantics.

### M68.4

M68.4 implements optional repo-level hygiene aggregation through `repo-check --clean`, aligned with the M68.3 design.

- `spec/28_CI_RELEASE_CLEAN_GATE_MODEL.md` — CI/release orchestration contract above repo hygiene.

- M69.1 CI workflow implementation: `../cli/docs/CI_WORKFLOW_IMPLEMENTATION.md`.

- M69.2 implements the release automation consumer of the CI/release clean-gate contract.

- `spec/29_CLEAN_GATE_EVIDENCE_PROVENANCE_LINKAGE_MODEL.md`

## M69.4
- Added CI/release fixture and smoke-test matrix; 34 targeted tests passed.

- M70.0 adds the production repository root classification model in `spec/30_PRODUCTION_REPO_HYGIENE_POLICY_MODEL.md`.

- M70.1 adopts the repository hygiene Phase A policy; dedicated language-root enforcement remains a later contract.

### M71.0
Stable semantic prompt IDs are an accepted migration target; M65 registry infrastructure remains the base.

M71.1 adds the stable semantic prompt identity and versioning convention.


## New core artifact: EXECUTION_TRACE

Ordo defines `EXECUTION_TRACE` as the canonical append-only history of a process run. Normative references: `spec/33_EXECUTION_TRACE_MODEL.md`, `schemas/execution_trace_schema.yaml`, `registry/EXECUTION_TRACE_VALUES.md`.
