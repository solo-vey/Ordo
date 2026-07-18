# Program-level Contract Schema Convention

Status: `M64.1 accepted-schema-convention`

M64.1 introduces the **program-level contract** as a documented source-level convention for Ordo packages.
It is not a new runtime opcode, not a compiler rewrite, and not a required migration for all existing packages.

The goal is to make the top-level execution contract explicit before a process is interpreted by an AI executor,
validated by CLI/helper tools, or reviewed by a human.

```text
program-level contract
  → identifies the package and compatibility target
  → declares the process control level and execution mode
  → explains who is responsible for decisions
  → declares whether deviation/backtracking are allowed
  → identifies required validation and approval points
```

## Why this layer exists

Node, gate, state, and output definitions describe the internal process graph. They do not always explain how the
whole package must behave as a live AI-guided process. M64.1 fills that gap by defining a top-level contract block.

This layer is especially useful for standard applied modules such as `ordo.applied_project_factory`, where the
process is conversational, iterative, and requires human approval at specific points.

## Canonical source shape

A package may declare the contract at the top level of `source/program.ordo.yaml`:

```yaml
program_contract:
  program_id: applied_project_factory
  module_id: ordo.applied_project_factory
  version: 0.1.0-rc.1
  ordo_version: "0.12"
  lifecycle: release-candidate
  control_level: standard
  execution_mode: full_runtime
  contract_profile: standard_applied_module
  compatibility:
    language_line: M64
    parent_package: Ordo v0.12
    cli_profile: parent-compatible
    schema_profile: program_level_contract_v1
  runtime_profile:
    ai_layer: guided_process_driver
    cli_layer: deterministic_validator
    human_layer: content_decision_owner
  required_review_points:
    - approve_program_contract
    - approve_runtime_profile
    - approve_output_templates
    - approve_final_package
  required_validation_commands:
    - lint
    - compile
    - test
    - validate-state
    - validate-output
    - consistency
    - go-no-go
```

## Attribute semantics

### `program_id`

- Type: `string`
- Required: yes
- Meaning: local package/program identifier.
- Validation behavior: should be stable across releases of the same package.
- Example: `applied_project_factory`

### `module_id`

- Type: `reverse-domain-like string` or namespaced Ordo identifier
- Required: yes for reusable packages and standard applied modules
- Meaning: canonical module identity used in docs, package indexes, manifests, and handoff reports.
- Example: `ordo.applied_project_factory`

### `version`

- Type: `semver-like string`
- Required: recommended
- Meaning: package/module version, not necessarily the language version.
- Example: `0.1.0-rc.1`

### `ordo_version`

- Type: `string`
- Required: recommended
- Meaning: compatible Ordo language line.
- Example: `0.12`

### `lifecycle`

- Type: `enum`
- Required: recommended for packages intended for release
- Allowed values:
  - `draft`: actively changing, not stable for handoff.
  - `alpha`: early working version; behavior may change.
  - `beta`: feature-complete enough for broader review; still not release candidate.
  - `release-candidate`: intended release candidate; known limitations must be visible.
  - `stable`: accepted stable release.
  - `deprecated`: no longer recommended for new use.
- Validation behavior: unknown values should produce a lint warning unless documented as package-local.

### `control_level`

- Type: `enum`
- Required: recommended
- Allowed values:
  - `light`: minimal structure; good for exploratory or small processes.
  - `standard`: normal controlled process with explicit state, gates, and review points.
  - `strict`: high-control process where missing gates, validation commands, or review points become blockers.
- Validation behavior: `strict` profiles may convert missing required sections from warnings to errors.

### `execution_mode`

- Type: `enum`
- Required: recommended
- Allowed values:
  - `full_runtime`: process is intended to run as a guided runtime package.
  - `chat_internal`: process may run in chat with internal state discipline but without full runtime packaging.
  - `freeform_only`: process is documentation/freeform only; deterministic runtime guarantees are not claimed.
  - `dry_run`: process is intended for non-mutating validation or rehearsal.
  - `test`: process is intended for fixtures/test execution.
- Validation behavior: `full_runtime` should require stronger validation and startup/handoff docs.

### `contract_profile`

- Type: `enum or convention string`
- Required: optional
- Known values:
  - `basic_process`: small Ordo process with minimal package contract.
  - `standard_applied_module`: reusable applied module included in a language package.
  - `runtime_package`: packaged runtime artifact intended for execution/handoff.
  - `companion_utility_workflow`: utility-driven workflow documentation or artifact generation route.
- Validation behavior: unknown values are allowed only when documented by the package.

### `compatibility`

- Type: `map`
- Required: recommended
- Meaning: declares expected language line, parent package, CLI profile, and schema profile.
- Useful fields:
  - `language_line`: example `M64`.
  - `parent_package`: example `Ordo v0.12`.
  - `cli_profile`: example `parent-compatible`.
  - `schema_profile`: example `program_level_contract_v1`.

### `runtime_profile`

- Type: `map`
- Required: recommended for `full_runtime`
- Meaning: declares the responsibility split between AI, CLI/helper tools, and human reviewer.
- Useful fields:
  - `ai_layer`: usually `guided_process_driver`.
  - `cli_layer`: usually `deterministic_validator`.
  - `human_layer`: usually `content_decision_owner` or `approval_owner`.
- Validation behavior: should be internally consistent with `execution_mode` and `control_level`.

### `required_review_points`

- Type: `list[string]`
- Required: recommended for `standard` and `strict`
- Meaning: named points where human approval or review is expected.
- Convention values:
  - `approve_program_contract`
  - `approve_runtime_profile`
  - `approve_branch_contract`
  - `approve_output_templates`
  - `approve_final_package`
- Validation behavior: values are convention strings until M64.3 lint/profile design formalizes a stricter list.

### `required_validation_commands`

- Type: `list[string]`
- Required: recommended for release-candidate/stable packages
- Meaning: validation commands that must be represented in package reports or equivalent evidence.
- Common values:
  - `lint`
  - `compile`
  - `test`
  - `coverage`
  - `validate-state`
  - `next-step`
  - `validate-output`
  - `validate-artifacts`
  - `consistency`
  - `go-no-go`
- Validation behavior: M64.1 documents the convention only. M64.3 may define lint/profile behavior.

## Relationship to opcodes and IR

M64.1 does **not** introduce these as opcodes:

```text
PROGRAM.DEF
INTERACTION.MODEL
PROCESS_RAIL.DEF
CONVERSATION.SEMANTICS
HYBRID_EXECUTION.MODEL
```

They remain source/schema conventions and documentation contracts until enough packages prove that compiler/IR promotion is necessary.

## Promotion ladder

```text
documented package need
→ schema convention
→ used by several packages
→ lint/profile candidate
→ compiler/IR candidate
→ runtime opcode only if necessary
```

## Non-goals

M64.1 does not:

- change runtime core behavior;
- change Semantic JSON IR execution behavior;
- add new opcodes;
- implement `FLOW.JOIN` or `SHARED.TAIL.REFERENCE`;
- create a deterministic natural-language classifier;
- make this contract mandatory for every legacy package.
