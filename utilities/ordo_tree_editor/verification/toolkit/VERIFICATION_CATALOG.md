# Ordo playbook & graph verification catalog

Source: the Ordo 0.4.10 language/tooling embedded in Vibe ARF alpha.9 after the documented compatibility alignments in `COMPATIBILITY_KNOWLEDGE_ORDO_0.4.10_ALPHA9.md`.

This package contains the verification mechanisms currently available to us for an Ordo playbook, its graph, generated artifacts, and release/package integrity. It does **not** invent new checks.

## 1. Core source / language checks

### `lint`
**Command:** `python -m ordo.cli lint <package>`

Checks the playbook source against the Ordo language model. This is the primary static language validation contour. It checks recognized constructs/fields, schema-level correctness, graph/source constraints exposed through the linter, strict-control requirements, and other source-level rules.

Expected successful result: exit code 0 and no lint errors. Warnings may still be reported depending on the source.

### `compile`
**Command:** `python -m ordo.cli compile <package>`

Compiles Ordo Source to Semantic JSON IR. Compilation is also a structural compatibility test: source that cannot be represented by the current compiler/IR contract fails here.

Use after lint. `--force` exists, but should be used only for diagnosis because it permits compilation attempts after lint failure.

### Registry/schema checks used by lint/compiler
The executable package includes:
- `language/schemas/*`
- `language/registry/*`
- `language/registries/*`
- `ordo_pkg/ordo/registry_checks.py`
- `ordo_pkg/ordo/schemas/source_schema.yaml`
- `ordo_pkg/ordo/schemas/ir_schema.yaml`

These are not normally invoked as separate user commands; they are part of the language validation implementation.

## 2. Graph checks

### Graph validation
Implemented by:
- `ordo_pkg/ordo/graph_validation.py`
- `ordo_pkg/ordo/graph_topology.py`

Used by the language/tooling validation pipeline to verify graph topology and transition targets. It covers graph structure such as known targets and external terminal targets according to the graph contract.

### `verify-targets`
**Command:** `python -m ordo.cli verify-targets <package>`

Verifies the compiled target manifest and AI-facing target hashes. Useful after compile to detect stale or mismatched compiled targets.

### Visual graph generator validation
Location:
`utilities/ordo_visual_graph_generator/`

The generator parses the Ordo graph and can render SVG/DOT/Mermaid outputs. In alpha.9 it is aligned with canonical `graph_contract.external_terminal_targets`.

A successful graph render is an additional practical graph-consumability check: the graph can be interpreted by the visual tooling without unknown-target failures.

### Tree Editor validation
Location:
`utilities/ordo_tree_editor/`

The editor service validates source before loading/editing. In alpha.9 it was repaired to use the package's real `tests/test_cases.yaml` for strict playbooks rather than an empty test set.

A successful editor validation is useful as an integration check because it exercises the language tooling through the editor's own consumption path.

## 3. Static tests and coverage

### `test`
**Command:** `python -m ordo.cli test <package>`

Runs the package's static Ordo test cases from its test definitions. This validates expected static behavior/contracts encoded in the playbook's own test suite.

### `coverage`
**Command:** `python -m ordo.cli coverage <package>`

Generates coverage information for the playbook/test relation. Use together with `test`; a passing test suite can still have insufficient declared coverage.

## 4. State, gate and journey checks

### `validate-state`
**Command:** `python -m ordo.cli validate-state <package> [--state ...] [--answers ...]`

Deterministically validates Ordo state. Useful when playbook correctness depends on state fields and confirmed answers.

### `check-gate`
**Command:** `python -m ordo.cli check-gate <package> <gate_id> [--state ...] [--answers ...]`

Evaluates one gate deterministically using the current state/answers.

### `validate-journey`
**Command:** `python -m ordo.cli validate-journey <package> [--journey ...]`

Validates the contractual manual-run journey ledger.

These checks are runtime-contract checks rather than pure graph syntax checks, but they are important for verifying that the compiled playbook can enforce its control model.

## 5. Generated artifact / document consistency checks

### `validate-artifacts`
**Command:** `python -m ordo.cli validate-artifacts <package>`

Validates rendered Markdown/JSON/YAML artifacts against confirmed contract fields.

### `validate-document-fields`
**Command:** `python -m ordo.cli validate-document-fields <package> --bindings <bindings-file>`

Validates document-field producers and path bindings.

### `consistency`
**Command:** `python -m ordo.cli consistency <package>`

Creates cross-artifact consistency evidence (`CONSISTENCY_CHECK_REPORT.json` by default).

### `validate-output`
**Command:** `python -m ordo.cli validate-output <package>`

Validates generated output artifacts.

## 6. Package/runtime/release integrity checks

### `runtime-status`
**Command:** `python -m ordo.cli runtime-status <package>`

Checks source-of-truth runtime readiness and stale compiled IR.

### `repo-check`
**Command:** `python -m ordo.cli repo-check <repo>`

Validates repository-level references and generated metadata. With `--clean`, it also aggregates package hygiene.

### `clean-check`
**Command:** `python -m ordo.cli clean-check <package> [--profile light|standard|strict]`

Checks whether a package is clean enough for handoff/release review. The strict profile is the strongest normal release-oriented profile.

### `validate-lock`
**Command:** `python -m ordo.cli validate-lock <package>`

Validates `ordo.lock.json` against currently resolved dependencies.

### `check-conflicts`
**Command:** `python -m ordo.cli check-conflicts <package>`

Detects unresolved dependency/layer conflicts.

### `validate-provenance`
**Command:** `python -m ordo.cli validate-provenance <package>`

Validates the release provenance manifest.

### `validate-release`
Available in the CLI as the release-validation/archive contour. It is broader than a read-only checker because it can create release artifacts, so it is intentionally not part of the default safe runner in this toolkit.

## 7. Prompt-only, template and reusable-tree checks

### `validate-prompt`
Validates a prompt-only compilation and its source binding.

### `template validate`
Validates one generic template contract.

### `template registry-check`
Validates a Template Registry and all referenced contracts.

### `template review`
Reviews a rendered template artifact and emits structured evidence.

### `template diff`
Compares template contract versions and enforces breaking-change policy.

### `tree-module validate-instance`
Validates a generated reusable tree-module instance.

### `tree-module diff-instance`
Reports divergence between an instance and its source template.

These are relevant when a playbook uses the corresponding language/template features.

## 8. Aggregate checks

### `go-no-go`
**Command:** `python -m ordo.cli go-no-go <package>`

Runs the final deterministic validation pipeline and produces a go/no-go report. Depending on options it can include intake, generation, state validation and artifact validation.

### `tools/quick_authoring_preflight.py`
The fast alpha.9 authoring preflight. It was added to make the most important compatibility checks repeatable instead of manually rediscovering integration failures. In the alpha.9 self-contained package it covers portable integrity/language/tooling plus lint, compile, tests, coverage, clean/editor/graph-related verification.

### `tools/verify_portable_authoring_bundle.py`
Checks the self-contained authoring bundle itself: support/provenance hashes, embedded-language alignment, runtime availability and isolated authoring smoke behavior.

This second tool is mainly for the Vibe self-contained bundle rather than an arbitrary third-party playbook.

## Recommended verification levels

### FAST source change
1. `lint`
2. `compile`
3. impacted static tests

### Playbook verification
1. `lint`
2. `compile`
3. `test`
4. `coverage`
5. `runtime-status`
6. `verify-targets`
7. `clean-check --profile strict`
8. editor validation
9. visual graph render/validation
10. any applicable state/gate/artifact checks

### Milestone / release
Everything above plus applicable:
- `validate-journey`
- `validate-artifacts`
- `validate-document-fields`
- `consistency`
- `validate-output`
- dependency lock/conflict checks
- provenance/release checks
- `go-no-go`

## Important compatibility note

Do not treat the checks as independent of language/tooling version. During the alpha.9 integration we found drift between different copies/consumers of Ordo 0.4.10 language metadata and utilities. Read `COMPATIBILITY_KNOWLEDGE_ORDO_0.4.10_ALPHA9.md` before replacing any component with a newer version.
