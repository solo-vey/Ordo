# 002. Benchmark Conceptual Model

## 1. Central model

```text
Benchmark Owner Decision
        ↓
Benchmark Suite
        ├── Task Classes
        ├── Test Cases
        │     ├── RUN Scenarios
        │     ├── Artifact Contracts
        │     └── Expected Terminal Routes
        ├── Package Variants
        │     └── Driver Contract
        └── Evaluation Protocol
              ↓
Blind Execution
        ↓
Generated Result + Execution Trace
        ↓
Process Evaluation + Document Evaluation
        ↓
Result Registry → Comparative Matrix
        ↓
Causal Diagnosis → Improvement Patch → Regression Run
```

## 2. Entity catalog

### 2.1 Benchmark Suite

Aggregate root for one benchmark program. Owns identity, versions, approved task classes, test cases, variants, evaluation contracts and result registry.

### 2.2 Task Class

Classification layer that defines broad problem structure. It does not itself contain hidden RUN facts.

### 2.3 Test Case

Canonical semantic problem. It fixes what is being tested and which artifacts must or must not be produced.

### 2.4 RUN Scenario

Behavioral stress path layered over a Test Case. It controls facts, branches, correction timing and terminal route.

### 2.5 Package Variant

Instruction representation under comparison. A variant may change structure and interaction style, but not canonical target behavior.

### 2.6 Execution Driver

Scenario interface. It reveals only relevant facts, records disclosure/state and enforces route semantics. It must not become a document-quality evaluator.

### 2.7 Generated Result

Returned artifact set plus declared status. Filename is not authoritative for RUN identity; internal evidence and scenario facts are.

### 2.8 Evaluation Contract

Versioned criteria. Split into Process Contract and per-artifact Document Contracts.

### 2.9 Evaluation Record

Immutable audit record containing evidence, findings, raw scores, caps, final scores and evaluator metadata.

### 2.10 Result Registry

Supersession-aware history of Evaluation Records.

### 2.11 Diagnostic Case

Root-cause investigation connected to one or more findings and evidence items.

### 2.12 Improvement Patch

Versioned change with affected components and required regression set.

## 3. Key relationships

| Source | Relationship | Target | Constraint |
|---|---|---|---|
| Benchmark Suite | contains | Test Case | Test-case IDs unique within suite version |
| Test Case | supports | RUN Scenario | RUN semantics compatible with test class |
| Test Case | requires | Artifact Contract | Terminal route may mark artifact N/A |
| Package Variant | executes through | Driver Contract | Driver type explicitly declared |
| Blind Execution | uses | Test Case + RUN + Variant | exact versions fixed before start |
| Blind Execution | produces | Generated Result | no evaluation embedded as authoritative score |
| Evaluation Record | evaluates | Generated Result | active contract versions recorded |
| Result Registry | derives | Comparative Matrix | matrix never becomes source of truth |
| Finding | may create | Diagnostic Case | only when cause is not already proven |
| Diagnostic Case | may create | Improvement Patch | patch is scoped to established root cause |
| Improvement Patch | requires | Regression Selection | affected scenarios rerun |

## 4. Identity model

Canonical result key:

```text
suite_id
+ suite_version
+ test_case_id
+ test_case_version
+ run_id
+ run_version
+ variant_id
+ variant_version
+ executor_model/session identity
+ attempt_id
```

Evaluation key additionally includes:

```text
evaluation_protocol_version
+ evaluator identity
+ audit_timestamp
```

## 5. State model

### Authoring state

```text
planned
→ in_progress
→ draft_complete
→ validated
→ accepted
→ superseded
```

### Run state

```text
not_started
→ preflight
→ executing
→ awaiting_required_input | correction_pending | artifact_pending
→ terminal_completed | terminal_blocked | terminal_exhausted | no_go
```

### Evaluation state

```text
not_evaluated
→ focused_scope_selected
→ evidence_loaded
→ artifact_reviews_complete
→ process_review_complete
→ score_calculated
→ published
→ superseded
```

## 6. Separation of concerns

- Scenario facts belong to RUN Scenario, not package instructions.
- Interaction control belongs to Driver, not evaluator.
- Document shape belongs to artifact templates/contracts, not Driver.
- Process score does not repair document deficiencies.
- Document score does not repair a wrong terminal route.
- Comparative tables are derived outputs, not canonical evidence.

## 7. Current known package variants

The initial registry will contain four variants:

1. YAML playbook;
2. structured instructions compiled from YAML;
3. historically accumulated all-in-one aligned to the YAML domain model;
4. near-original domain-adapted all-in-one.

They are recorded here as known domain entities; their binding rules remain Epic 04 work.

## 8. Current known RUN family

The initial scenario family is expected to include:

- clean control;
- branch heavy;
- invalid/irrelevant;
- correction/backtrack;
- incomplete hard stop.

Their authoritative contracts remain Epic 03 work.

## 9. Improvement loop

```text
Finding
→ confirm active criteria
→ classify defect
→ collect generation/execution evidence
→ establish root cause
→ choose affected component
→ make scoped patch
→ validate package integrity
→ select regression set
→ rerun blindly
→ append new evaluation
→ supersede comparison table entry explicitly
```

## 10. Model boundaries

The playbook is itself an Ordo/ARF authoring product. The benchmark artifacts it later creates are separate domain products with independent versions. Updating this playbook must not silently mutate existing benchmark result records.
\n\n## Epic 03 model extension\n\n```text\nTest Case\n  └── RUN Scenario Registry\n        ├── RUN_01 Clean Control\n        ├── RUN_02 Branch Heavy\n        ├── RUN_03 Invalid and Irrelevant\n        ├── RUN_04 Backtrack and Correct\n        └── RUN_05 Incomplete Hard Stop\n\nRUN Scenario\n  ├── Public launch contract\n  ├── Driver-private facts and transitions\n  ├── Evaluator-only expected terminal and invariants\n  └── Result identity bound to package variant/version and executor\n```\n\nA RUN varies interaction conditions, not package representation. A Package Variant varies instructions, not hidden scenario truth. An Evaluator Contract judges the result, but must not guide execution.\n

## Epic 05 model extension

```text
Package Variant + Manifest
  → Driver Selection Gate
      ├── DRV-STEP-BOUND
      ├── DRV-SEMANTIC-ADAPTIVE
      └── UNSUPPORTED_OR_HYBRID
  → Blind Isolation Precondition
  → Execution (Epic 07)
```

The Driver owns disclosure and route control. The executor owns answers and artifacts. The evaluator owns post-terminal scoring. No role may silently take another role's authority.


## Epic 07 execution relationship

```text
Launch Manifest
  → Preflight Integrity Gate
  → Driver-mediated Attempt
  → Append-only Execution Log
  → Terminal Gate
  → Terminal Disposition + Sealed Return Package
```

The executor can claim completion but cannot select the authoritative terminal or evaluate its own output.


## Epic 07 process evaluation model

```text
Execution evidence → dimension criteria → raw process score → confirmed failures → lowest cap → final process score
```

Process evaluation and document evaluation are sibling views and must never be merged before comparative aggregation.


## Epic 09 result layer

```text
Execution evidence → Result record → Comparability gate → Active registry view → Comparative matrix → Cross-variant findings
```

Registry events are sources of truth; matrices are rebuildable derived artifacts.


## Epic 10 diagnostic model

```text
Benchmark Result / Finding
        ↓ freeze evidence
Diagnostic Request
        ↓ executor explanation (hypothesis)
Evidence Triangulation
        ↓ claim assessment + counterfactual
Root Cause Decision
        ↓ bounded patch target + regression implications
```

Original execution evidence remains immutable throughout diagnosis.


## Improvement and regression layer

A diagnostic case may produce a scoped patch proposal. The proposal binds a frozen baseline, change allowlist and regression set. Accepted changes create a new package version and explicit compatibility disposition; historical evidence is never overwritten.
