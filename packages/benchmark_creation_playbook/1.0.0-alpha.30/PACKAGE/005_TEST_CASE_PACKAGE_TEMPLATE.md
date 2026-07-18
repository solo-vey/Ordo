# 005. Test Case Source Package Contract

**Version:** `0.2.0`  
**Status:** accepted proposed-template set

## 1. Purpose

A Test Case Source Package is the authoritative, non-execution bundle from which RUN scenarios and comparable package variants may later be produced. It must separate public executor inputs, hidden scenario data and evaluator-only contracts.

## 2. Required structure

```text
<TEST_CASE_ID>_SOURCE_V<VERSION>/
├── README.md
├── TEST_CASE_CONTRACT.yaml
├── SOURCE_REGISTRY.yaml
├── OPEN_QUESTIONS.yaml
├── APPROVAL_RECORD.yaml
├── PUBLIC_INPUTS/
│   └── README.md
├── HIDDEN_SCENARIO_INPUTS/
│   └── README.md
├── ARTIFACT_CONTRACTS/
│   └── README.md
├── EVALUATION/
│   ├── PROCESS_EVALUATION_BINDING.yaml
│   └── DOCUMENT_EVALUATION_BINDINGS.yaml
├── TEMPLATES/
│   └── expected_output_registry.yaml
├── MANIFESTS/
│   └── SHA256SUMS.txt
└── CHANGELOG.md
```

RUN-specific files are not required until Epic 03. Compiled package variants are not part of this source package.

## 3. File contracts

### `README.md`
Human navigation, identity, classification, canonical target, source authority, current readiness and reading order.

### `TEST_CASE_CONTRACT.yaml`
Canonical machine-readable test-case definition. Must include identity, classes, semantic target, boundaries, source authority, artifacts, process claims, scenario dimensions, variants, evaluation and approvals.

### `SOURCE_REGISTRY.yaml`
Every input with ID, path, version/hash, authority class, visibility and allowed consumer roles.

### `OPEN_QUESTIONS.yaml`
Structured unresolved items, affected downstream units, severity and blocking status. Empty list is valid; missing file is not.

### `APPROVAL_RECORD.yaml`
Owner review state, reviewed version/hash, decision, reviewer and timestamp/reference.

### `PUBLIC_INPUTS/`
Inputs that may be delivered to the Blind Executor or package compiler according to variant rules.

### `HIDDEN_SCENARIO_INPUTS/`
Private facts and scenario material. Must never be copied into a blind execution package except through the Driver contract.

### `ARTIFACT_CONTRACTS/`
Versioned document-quality contracts by output type. References are allowed when hashes/versions are fixed.

### `EVALUATION/`
Bindings to active process/document contracts and scoring formula; no actual run scores.

### `MANIFESTS/SHA256SUMS.txt`
Integrity manifest over all package files except the manifest itself, using stable relative paths.

## 4. Visibility classes

```text
public_executor
compiler_only
scenario_author_only
evaluator_only
owner_only
```

A source entry must declare exactly one visibility class and allowed roles.

## 5. Package gates

Pass only when:
- the canonical contract validates structurally;
- the primary class exists and matches expected artifacts;
- every referenced source exists and has a fixed version/hash;
- public and hidden inputs are physically separated;
- no expected score or reference answer appears in public executor inputs;
- artifact contract bindings are explicit;
- approval is tied to the exact test-case version/hash;
- manifest verification passes;
- no compiled RUN or result output is mixed into the source package.

## 6. Templates supplied by this release

- `templates/TEST_CASE_INTAKE.template.yaml`
- `templates/TEST_CASE_CONTRACT.template.yaml`
- `templates/SOURCE_REGISTRY.template.yaml`
- `schemas/test_case_contract.schema.json`

Owner review status: `proposed-template / usable for Epic 02 authoring; production acceptance pending first complete test-case materialization`.
