# 000. Benchmark Creation Playbook Contract

## 1. Identity

```yaml
playbook_id: ordo.benchmark_creation_playbook
version: 1.0.0-alpha.30
domain: ai_instruction_benchmark_engineering
canonical_contract: 000_PLAYBOOK_CONTRACT.md
source_language_baseline: Ordo 0.13.0-rc.1
framework_baseline: ARF 0.1.0-rc.1
package_lifecycle: validated_alpha_release
authoritative_package_identity: ordo.benchmark_creation_playbook@1.0.0-alpha.30
```

## 2. Vision

Create a deterministic and evidence-driven process for designing, running, evaluating and improving benchmarks that compare alternative representations of the same analytical process.

## 3. Mission

The playbook must prevent ad-hoc benchmark work in which:

- test-case rules are reconstructed from conversation memory;
- different package variants receive different hidden assumptions;
- the evaluator forgets artifact-specific rules;
- prior scores are silently reused after criteria change;
- run identity, package version or evaluation protocol is unclear;
- process correctness is used to excuse weak documents;
- self-evaluation is treated as independent evidence.

## 4. Users and roles

| Role | Responsibility |
|---|---|
| Benchmark Owner | approves scope, task classes, scenarios, package variants and evaluation contracts |
| Playbook Author | materializes and versions the Ordo benchmark playbook |
| Scenario Author | creates hidden facts, branches, corrections and terminal expectations |
| Package Compiler | produces comparable package variants from approved sources |
| Blind Executor | executes one package/run without access to expected scores or prior outputs |
| Process Evaluator | checks route, state transitions, correction handling and terminal result |
| Document Evaluator | applies artifact-specific quality rules to final rendered documents |
| Diagnostic Reviewer | traces defects to node, prompt, template, Driver, validator or source evidence |
| Improvement Owner | applies scoped patches and selects regression runs |

One model may perform several roles only when the run explicitly records that independence is not claimed.

## 5. Scope

### 5.1 In scope

The completed playbook will govern:

1. benchmark-suite creation;
2. task-class and test-case definition;
3. RUN scenario creation and versioning;
4. package-variant registry and generation;
5. step-bound and semantic-adaptive blind execution;
6. preflight integrity and isolation;
7. process evaluation;
8. artifact-specific document evaluation;
9. failure caps and blocking findings;
10. score aggregation and comparative tables;
11. causal diagnosis;
12. improvement patches and regression runs;
13. evidence packaging and handoff.

### 5.2 Out of scope for the playbook

- judging general-purpose model intelligence outside the approved test contract;
- changing model weights or provider infrastructure;
- treating execution logs as a scored model capability unless explicitly added by benchmark design;
- comparing packages that do not implement the same canonical analytical intent;
- inventing missing domain facts during execution or evaluation;
- silently changing historic scores when evaluation criteria are revised.

### 5.3 Historical scope note for version 0.3.0

- executable Drivers;
- full suite-level intake decision tree beyond the completed test-case intake;
- templates for RUN scenarios, package variants, execution results and evaluations beyond the completed test-case source templates;
- scoring engine;
- result registry implementation;
- runtime/evidence package builds;
- complete compiled IR.

This subsection is retained as historical context only. The current implementation status is governed by BACKLOG.md, SUMMARY.json, release notes, and materialized validation evidence.

## 6. Canonical authority hierarchy

When rules conflict, apply:

1. explicit current Benchmark Owner decision;
2. current playbook contract and accepted design decisions;
3. current test-case contract;
4. current RUN scenario contract;
5. artifact-specific evaluation contract;
6. package-variant contract;
7. prompts/templates/validators;
8. previous outputs or examples.

Examples never override current rules.

## 7. Core invariants

### INV-01. Same semantic target
All compared package variants must represent the same approved analytical intent and scenario facts.

### INV-02. Isolation
Blind Executor must not receive expected scores, reference outputs, prior run outputs or hidden evaluator findings.

### INV-03. Separate process and document quality
Process execution and document quality are evaluated independently before aggregation.

### INV-04. Artifact-specific evaluation
Each output document is checked only against its active artifact contract. Criteria from another artifact must not be imported implicitly.

### INV-05. Focused review
Evaluation starts by identifying the exact RUN, package version, artifact and active criteria subset.

### INV-06. No score without evidence
Every score must link to inspected files, criterion findings and applied caps.

### INV-07. Criteria versioning
A score is meaningful only together with evaluation-contract version and audit date.

### INV-08. No silent overwrite
A later audit supersedes an earlier score explicitly; historical values remain traceable.

### INV-09. Honest terminal routes
Blocked or exhausted scenarios may be high-quality outcomes when they match the scenario contract and avoid fabricated documents.

### INV-10. Scoped evolution
A discovered defect produces a classified root cause and scoped patch, not an uncontrolled redesign.

## 8. Functional requirements

| ID | Requirement |
|---|---|
| FR-01 | Maintain a versioned benchmark charter and domain vocabulary. |
| FR-02 | Support approved task classes and test-case templates. |
| FR-03 | Support multiple RUN scenarios with explicit expected terminal routes. |
| FR-04 | Support multiple comparable package representations. |
| FR-05 | Select an appropriate Driver contract for each package representation. |
| FR-06 | Enforce blind-execution isolation. |
| FR-07 | Validate process and documents separately. |
| FR-08 | Apply current artifact-specific rules on every new result. |
| FR-09 | Maintain a versioned result registry and comparison matrix. |
| FR-10 | Diagnose weak results causally using execution and generation evidence. |
| FR-11 | Apply scoped improvements and run selected regressions. |
| FR-12 | Produce reproducible evidence and handoff packages. |

## 9. Non-functional requirements

- **Determinism:** same approved input and versioned rules should produce structurally equivalent execution decisions.
- **Reproducibility:** every result identifies package, scenario, Driver and evaluation versions.
- **Auditability:** findings are traceable to inspected evidence.
- **Comparability:** variants differ by representation, not hidden facts or evaluator treatment.
- **Extensibility:** new task classes, RUNs and variants can be added without rewriting existing records.
- **Human readability:** reports expose key decisions and blockers clearly.
- **Fail-fast honesty:** missing mandatory evidence blocks readiness rather than being filled by assumption.

## 10. Lifecycle

```text
Planned
→ Foundation Defined
→ Test Model Defined
→ Execution Architecture Defined
→ Evaluation Contracts Defined
→ Pilot Ready
→ Blind Validated
→ Near Production
→ Production Ready
→ Deprecated
```

Current state: `Near Production`.

## 11. Terminal statuses of the authoring playbook

| Status | Meaning |
|---|---|
| `T_EPIC_COMPLETED` | selected epic DoD and validation gates passed |
| `T_BLOCKED_DECISION` | owner decision is mandatory and absent |
| `T_BLOCKED_EVIDENCE` | required source/language/package evidence is absent |
| `T_DRAFT_SAVED` | partial non-blocking work stored honestly |
| `T_PLAYBOOK_RELEASED` | complete release gates passed |

Current terminal result: `T_PLAYBOOK_RELEASED` for validated alpha release `1.0.0-alpha.30`.

## 12. Definition of Done — Epic 01

Epic 01 is complete when:

- charter, purpose, users and boundaries are explicit;
- domain vocabulary is defined;
- conceptual entities and relationships are defined;
- authority hierarchy and invariants are recorded;
- complete backlog exists with statuses;
- Ordo source skeleton records the authoring rail;
- validation confirms internal consistency;
- package does not claim full execution readiness.

All conditions are met in version `0.1.0`.

## 13. Full-playbook readiness criteria

The full playbook cannot become execution-ready until:

- intake decision tree and terminal paths exist;
- every generated artifact has an accepted template;
- Driver selection and isolation are implemented;
- process and document evaluation contracts are machine-checkable where feasible;
- result registry and score supersession are implemented;
- pilot runs prove replayability and correct failure handling;
- dev, runtime and evidence package profiles pass self-validation.


## Epic 03 extension

The playbook now defines versioned canonical RUN scenarios and extension admission rules. Expected terminals and evaluator invariants are evaluator-only and must remain physically separated from executor-visible input.


## Epic 05 contract extension — Blind execution architecture

The playbook supports exactly two initial Driver families: `DRV-STEP-BOUND` and `DRV-SEMANTIC-ADAPTIVE`. Every package must pass a deterministic Driver binding gate before launch. Unsupported or ambiguous hybrid packages are blocked, not guessed. Executor-visible, Driver-private, evaluator-only and historical information must be physically/logically isolated. Drivers control disclosure, corrections and terminal predicates but may not score or repair artifacts.


## Epic 07 extension — Benchmark execution contract

Every benchmark attempt must use an immutable launch identity, pass integrity/isolation preflight before first executor interaction, produce append-only ordered evidence, and end with exactly one authoritative terminal disposition. Executor self-scoring is forbidden. Production launcher/runtime implementation is not claimed by v0.8.0.


## Epic 07 extension — Process validation

The playbook defines an independent process score, eight weighted dimensions, immutable evidence requirements and a lowest-applicable-cap rule. Document quality is evaluated only by Epic 08 contracts.


## Epic 09 extension — Results as immutable evidence

Benchmark outcomes are append-only versioned observations. Registry identity, supersession, comparability and derived matrices are governed by `028`–`031`; no score may be silently overwritten.


## Epic 10 contract extension — diagnostics

The playbook shall diagnose weak or surprising results through frozen evidence, structured executor questioning, corroborated claims and a versioned root-cause taxonomy. Executor self-report shall never be sufficient by itself to confirm causality.


## Epic 11 extension

The playbook now defines bounded improvement patches, deterministic regression selection, a hard five-cycle campaign mode and stable benchmark evolution. Production patch execution and regression tooling are not claimed.
