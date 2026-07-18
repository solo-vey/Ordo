# Ordo Benchmark Creation Playbook — All in One v0.11.0


---

# FILE: 000_PLAYBOOK_CONTRACT.md

# 000. Benchmark Creation Playbook Contract

## 1. Identity

```yaml
playbook_id: ordo.benchmark_creation_playbook
version: 1.0.0-alpha.30
domain: ai_instruction_benchmark_engineering
canonical_contract: 000_PLAYBOOK_CONTRACT.md
source_language: Ordo 0.13.0-rc.1
framework_baseline: ARF 0.1.0-rc.1
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

### 5.3 Out of scope for version 0.3.0

- executable Drivers;
- full suite-level intake decision tree beyond the completed test-case intake;
- templates for RUN scenarios, package variants, execution results and evaluations beyond the completed test-case source templates;
- scoring engine;
- result registry implementation;
- runtime/evidence package builds;
- complete compiled IR.

These are represented in the backlog and must not be described as completed.

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


---

# FILE: 001_DOMAIN_VOCABULARY.md

# 001. Benchmark Domain Vocabulary

This file extends, rather than duplicates, the Framework vocabulary.

| Term | Definition |
|---|---|
| **Benchmark Suite** | A versioned collection of test cases, RUN scenarios, package variants, execution contracts, evaluation contracts and accumulated results. |
| **Task Class** | A stable category of analytical work used to select test-case structure and evaluation expectations. Current project scope anticipates three classes, to be materialized in Epic 02. |
| **Test Case** | A canonical benchmark problem that defines the analytical goal, allowed sources, expected artifacts, evaluation contracts and applicable RUN scenarios. |
| **RUN Scenario** | A controlled hidden-fact and interaction route applied to a test case, including branches, corrections and expected terminal state. |
| **RUN ID** | Stable identifier of a scenario instance, such as `RUN_01`. It is not inferred from output filename alone. |
| **Package Variant** | One approved representation of the same canonical analytical process, such as YAML playbook, compiled structured instructions or domain-adapted all-in-one instructions. |
| **Variant Registry** | Versioned catalog describing each package variant, canonical source, transformation rules, Driver type and comparability constraints. |
| **Blind Executor** | Model/session that executes a package without expected scores, reference answer, prior outputs or evaluator findings. |
| **Execution Driver** | Controlled interface that supplies scenario facts and enforces interaction/state rules without evaluating final document quality. |
| **Step-Bound Driver** | Driver bound to explicit step/node identity and deterministic expected interactions. |
| **Adaptive Semantic Driver** | Driver that maps natural-language questions to neutral semantic intents while preserving deterministic scenario facts. |
| **Hidden Scenario** | Private scenario facts, fact statuses, corrections and terminal conditions unavailable to the Blind Executor except through the Driver. |
| **Disclosure Ledger** | Record of which facts and statuses have been disclosed during a run. |
| **Execution Trace** | Evidence of interactions, node/state transitions, artifact versions, corrections, approvals and terminal decision. |
| **Process Evaluation** | Independent review of whether the executor followed the required route and state semantics. |
| **Document Evaluation** | Artifact-by-artifact review using the current contract for each rendered document. |
| **Artifact Contract** | Versioned rules defining required content, allowed references, exclusions, quality criteria and failure caps for one document type. |
| **Focused Artifact Review** | Startup filter that selects exact RUN, package, artifact and relevant criteria before evaluation. |
| **Failure Cap** | Maximum permitted score after a defined critical deficiency, regardless of other strengths. |
| **Blocking Finding** | Defect that prevents readiness or valid scoring under the active contract. |
| **Raw Score** | Score before failure caps are applied. |
| **Final Artifact Score** | Score after caps and blockers are applied to one artifact. |
| **Document Score** | Aggregated score of required artifacts for a RUN/package result. |
| **Process Score** | Aggregated process-compliance score for a RUN/package result. |
| **Overall Score** | Versioned aggregation of process and document scores, currently intended as 50/50 unless a test-case contract states otherwise. |
| **Terminal-Result Package** | Legitimate output for blocked/exhausted routes where canonical implementation documents must not be generated. |
| **Result Registry** | Append-only or supersession-aware store of scores and evidence keyed by suite, test case, RUN, variant and version. |
| **Comparative Matrix** | Human-readable table derived from the Result Registry. |
| **Score Supersession** | Explicit replacement of an earlier audit while preserving its historical record and reason. |
| **Causal Diagnostic Review** | Investigation that traces a defect to source evidence, node, prompt, template, Driver, renderer, validator or evaluator contract. |
| **Improvement Patch** | Scoped, versioned change addressing a classified root cause. |
| **Regression Selection** | Rules choosing which prior RUN/variant combinations must be repeated after a patch. |
| **Benchmark Evidence Package** | Reproducible bundle containing approved sources, versions, results, evaluations, decisions and manifests. |
| **Self-Test** | Evaluation performed by the same authoring/executing context; useful for development but not equivalent to independent blind evidence. |
| **Independent Blind Evidence** | Result produced and assessed without exposure to hidden expected outcomes or prior evaluator conclusions. |
\n\n## Epic 03 vocabulary additions\n\n### RUN Scenario\nA versioned hidden interaction contract that controls facts, disclosure, corrections, artifact lifecycle and expected terminal for one benchmark execution.\n\n### Scenario Version\nSemantic version of a RUN contract. Changes to terminal, disclosure or correction semantics are breaking.\n\n### Fact Status\nLifecycle marker for scenario facts: `confirmed`, `tentative`, `withdrawn`, `superseded`, `unavailable`, or `irrelevant`.\n\n### Expected Terminal\nThe one canonical terminal state a valid execution must reach after scenario conditions are satisfied. It is evaluator-only information.\n\n### Scenario Exhaustion\nA truthful terminal condition where no relevant facts remain and forcing a completed artifact package would be invalid.\n\n### Version-bound Approval\nApproval attached to an exact artifact version; it does not survive superseding facts or regeneration.\n

## Epic 04 vocabulary additions

### Package Variant
A controlled representation of the same benchmark test-case contract with declared source lineage, transformation profile, execution interface and contamination policy.

### Compiler Profile
A versioned transformation contract that defines how one authoritative source becomes a specific package variant.

### Source Lineage
The auditable chain from canonical source revision and hash through compiler/adaptation profile to the generated package.

### Variant Contamination
Use of information, rules, outputs or improvements from another package variant outside the explicitly allowed common benchmark source boundary.

### Semantic Parity
Preservation of decisions, gates, corrections, terminal behavior and output contracts across representations despite different presentation structure.


## Epic 05 vocabulary additions

### Step-Bound Driver
Driver whose checkpoint and transitions are resolved from an authoritative closed node graph.

### Adaptive Semantic Driver
Driver that selects deterministic semantic intents from unmet obligations when no stable step graph exists.

### Driver Binding
Versioned pre-run decision connecting one package variant/version/hash to exactly one Driver family or to an unsupported status.

### Blind Isolation
Physical and logical separation of executor-visible, Driver-private, evaluator-only and historical benchmark information.

### Contaminated Attempt
Run attempt exposed to forbidden information; retained as evidence but excluded from blind comparison.


## Epic 07 vocabulary

### Attempt ID
Immutable identifier of one launch attempt; never reused.

### Launch Manifest
Frozen machine-readable binding of suite, test case, RUN, package variant, Driver, isolation mode and output contract.

### Preflight Report
Sealed evidence that integrity, compatibility, isolation, residue and environment checks passed or blocked execution.

### Execution Log
Append-only ordered event stream covering disclosure, state, corrections, artifacts, approvals and terminal routing.

### Terminal Disposition
Authoritative operational outcome: `T_COMPLETED`, `T_INPUT_BLOCKED`, `T_SCENARIO_EXHAUSTED`, `T_NOT_READY` or `T_NO_GO`.


## Epic 07 terms

### Process Quality Contract
Versioned criteria for evaluating execution route and evidence discipline independently from generated-document quality.

### Raw Process Score
Weighted score before failure caps.

### Process Failure Cap
Maximum final process score imposed by a confirmed critical process failure.

### Clean Blind Run
Attempt whose executor-visible context passed blind-isolation checks and has no known contamination.


### Benchmark Result Record
An immutable version-bound evaluation record for one attempt or re-evaluation.

### Comparable Cohort
A set of result records that satisfy the same declared comparison conditions.

### Supersession
An append-only relation in which a newer active record replaces an older record for current views without deleting history.

### Matrix Build
A reproducible derived view identified by registry high-water mark, policies and filters.


## Epic 10 vocabulary extension

### Diagnostic Case
A versioned investigation record that links a surprising result to frozen evidence, causal claims, a root-cause decision and a bounded patch target.

### Diagnostic Claim
A falsifiable causal statement with supporting and contradicting evidence, confidence and corroboration status.

### Root Cause
The earliest evidence-backed component failure that made the observed defect inevitable.

### Contributing Cause
A verified factor that amplified or enabled a defect but is not the sole primary cause.


## Improvement vocabulary

- **Patch allowlist** — exact components permitted to change.
- **Regression trigger** — scenario reproducing the diagnosed defect.
- **Sentinel scenario** — stable unaffected case used to detect broad regressions.
- **Improvement campaign** — at most five bounded patch cycles against one frozen objective.
- **Comparison cohort** — results comparable under compatible scenario, package and evaluation contracts.


---

# FILE: 002_CONCEPTUAL_MODEL.md

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


---

# FILE: 003_TASK_CLASS_MODEL.md

# 003. Benchmark Task Class Model

**Version:** `0.2.0`  
**Status:** accepted for playbook working draft

## 1. Purpose

Task Class classifies the dominant capability being benchmarked. It is selected before RUN scenarios and package variants. A test case may have one primary class and zero or more secondary classes, but scoring and evidence requirements are governed by the primary class unless the test-case contract explicitly says otherwise.

## 2. Canonical classes

### TC01 — Bounded Output Transformation

Tests whether a model can transform a supplied, sufficiently complete source into a bounded output without inventing facts or changing the requested contract.

Typical work:
- rewrite, normalize, summarize or convert one known source;
- produce one or a few bounded artifacts;
- little or no guided intake;
- no substantial hidden-state process.

Primary evidence:
- source fidelity;
- output constraints;
- absence of invented facts;
- format and completeness.

Default evaluation emphasis:
- documents/output quality: high;
- process path: light, unless explicitly instrumented.

### TC02 — Deterministic Process Execution

Tests whether a model follows an explicit process contract, state transitions, gates, corrections and terminal routes.

Typical work:
- step-bound or node-bound execution;
- explicit required sequence or dependency graph;
- state and checkpoint handling;
- correction/backtrack and premature-finish protection;
- terminal route selection.

Primary evidence:
- execution trace;
- state transitions;
- gate outcomes;
- correction invalidation/regeneration;
- terminal decision.

Default evaluation emphasis:
- process quality: primary;
- documents: evaluated only when the process creates documents.

### TC03 — Analytical Package Engineering

Tests whether a model converts incomplete, distributed or evolving evidence into a coherent multi-artifact analytical package and validates every role-specific artifact under its own contract.

Typical work:
- guided intake and evidence resolution;
- canonical contract plus derived views;
- Passport, Jira, implementation, Manual QA, Automation or equivalent artifact family;
- cross-document consistency and traceability;
- artifact-specific quality gates;
- blocked/exhausted routes where canonical artifacts must not be invented.

Primary evidence:
- correctness of the analytical route;
- artifact-specific document depth;
- consistency and traceability;
- honest handling of missing evidence;
- correct terminal package composition.

Default evaluation emphasis:
- process and document quality are both mandatory;
- current default aggregation is 50% process / 50% documents unless overridden by the test-case contract.

## 3. Selection decision

Apply the first matching rule with sufficient evidence:

1. Select **TC03** when the expected result is a coordinated multi-artifact package derived from a canonical analytical contract, especially when evidence is incomplete, role-specific views differ, or document-specific evaluation is material.
2. Otherwise select **TC02** when the central claim is correct execution of an explicit process/state/gate contract.
3. Otherwise select **TC01** when the central claim is faithful bounded transformation of sufficiently complete input into a bounded output.
4. If two classes materially apply, record one as `primary` and the other as `secondary`, with a written rationale and explicit scoring effects.
5. If none applies, the test case is `classification_blocked`; do not silently create a fourth class.

## 4. Classification matrix

| Question | TC01 | TC02 | TC03 |
|---|---:|---:|---:|
| Is the source substantially complete at start? | usually yes | may vary | often no/distributed |
| Is a stateful execution path central? | no/light | yes | yes |
| Are multiple role-specific artifacts required? | rarely | optional | yes |
| Are artifact-specific contracts required? | output contract | optional | mandatory |
| Can blocked/exhausted be a correct result? | sometimes | yes | yes |
| Is cross-document consistency a scored capability? | no | optional | yes |

## 5. Current benchmark classification

The database-change analytical-package benchmark is classified:

```yaml
primary: TC03
secondary:
  - TC02
reason:
  - it produces and validates a coordinated analytical artifact package;
  - it also tests deterministic route, correction, backtrack and terminal handling.
```

This classification must be stored in the test-case contract, not reconstructed from chat memory.

## 6. Validation gate

Classification passes only when:
- exactly one primary class is selected;
- every secondary class has a rationale;
- expected artifacts and evidence match the selected primary class;
- scoring dimensions do not contradict the class;
- no class is inferred from package filename alone.


---

# FILE: 004_TEST_CASE_CREATION_INTAKE.md

# 004. Test Case Creation Intake

**Version:** `0.2.0`  
**Status:** accepted working contract

## 1. Entry condition

Start this intake when a Benchmark Owner proposes a new semantic problem to compare across one or more instruction/package variants. Do not design RUN scenarios or compile variants until the test-case intake gate passes.

## 2. Intake sequence

### I01 — Identity and ownership
Capture:
- `suite_id` and version;
- proposed `test_case_id` and version;
- title and owner;
- creation reason and decision reference.

### I02 — Canonical semantic target
Capture:
- user/business goal;
- target analytical behavior;
- what must remain semantically identical across variants;
- explicit non-goals.

### I03 — Task classification
Apply `003_TASK_CLASS_MODEL.md` and record:
- primary class;
- optional secondary classes;
- rationale;
- scoring consequences.

### I04 — Source authority
Capture every allowed source artifact and its role:
- canonical source of truth;
- supporting evidence;
- runtime/operational contracts;
- examples (non-authoritative unless promoted);
- forbidden sources or stale versions.

### I05 — Input and uncertainty model
Capture:
- facts confirmed before execution;
- facts hidden behind Driver interaction;
- facts that may be tentative, corrected, withdrawn, unavailable or irrelevant;
- assumptions policy;
- required identifiers and hard-stop conditions.

### I06 — Expected artifact contract
For each possible terminal route define:
- required canonical artifacts;
- allowed terminal-result artifacts;
- forbidden artifacts;
- artifact-specific contract/version;
- approval requirements.

### I07 — Process claims
Define which process behavior is tested:
- required path or path family;
- state/checkpoint expectations;
- correction/backtrack behavior;
- invalidation/regeneration rules;
- premature finish behavior;
- expected terminal classes.

### I08 — Scenario coverage need
Describe required stress dimensions without yet assigning RUN IDs:
- clean path;
- branch/no-op/negative behavior;
- invalid or irrelevant evidence;
- correction/backtrack;
- incomplete hard stop;
- domain-specific additions.

### I09 — Variant comparability
Capture:
- variants planned for comparison;
- semantic invariants shared by all variants;
- allowed representational differences;
- required Driver family or unresolved Driver selection;
- contamination/isolation risks.

### I10 — Evaluation contract
Capture:
- process evaluation contract/version;
- document contracts by artifact type;
- score aggregation formula;
- failure caps/blockers;
- terminal-route scoring rule;
- explicitly excluded dimensions, including Evidence Capture Quality when applicable.

### I11 — Reproducibility and evidence
Capture:
- required hashes and manifests;
- launch parameters;
- expected returned evidence;
- executor/evaluator independence claims;
- version identity key.

### I12 — Owner confirmation
Present the normalized intake record and obtain:
- `approved`;
- `needs_changes` with exact fields;
- or `blocked` with missing authority/evidence.

## 3. Intake statuses

```text
draft
→ normalized
→ owner_review
→ approved
→ superseded
```

Blocked is a terminal authoring outcome until required authority is supplied.

## 4. Hard gates

The intake cannot become `approved` when any of these is missing:
- test-case identity and owner;
- canonical semantic target;
- exactly one primary Task Class;
- source authority list;
- expected artifact/terminal model;
- process and document evaluation boundaries;
- comparability invariant;
- assumptions/invention policy.

RUN scenario design is forbidden before approval.

## 5. Output

Approved intake produces:
- `test_case/TEST_CASE_CONTRACT.yaml` from the canonical template;
- `test_case/README.md` human-readable summary;
- source registry and manifest;
- explicit open questions/blockers ledger;
- owner approval record.


---

# FILE: 005_TEST_CASE_PACKAGE_TEMPLATE.md

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


---

# FILE: 006_CANONICAL_RUN_SCENARIO_CONTRACT.md

# Canonical RUN Scenario Contract

**Document version:** `0.3.0`  
**Backlog task:** `BL-BENCH-006`  
**Status:** canonical working contract

## 1. Purpose

This document defines the five mandatory baseline RUN scenarios used to test the same benchmark test case and package variant under controlled interaction conditions.

A RUN scenario is not a document-quality rubric and not a package variant. It is a versioned hidden interaction contract that controls:

- what facts exist;
- when and how facts may be disclosed;
- which facts may be corrected, withdrawn, or declared unavailable;
- which artifacts may or must be produced;
- which terminal state is correct;
- which process behaviors are mandatory or forbidden.

## 2. Universal RUN invariants

Every canonical RUN must satisfy all of the following:

1. `run_id` and `scenario_version` are immutable inside one execution.
2. Public launch data must not reveal hidden facts, corrections, expected terminal, or evaluator scoring.
3. The Driver may disclose only facts allowed by the active scenario state.
4. The tested model must not invent unavailable facts.
5. Artifact approval is version-bound; a superseded artifact loses approval.
6. A terminal is valid only when its explicit preconditions are met.
7. Document evaluation is separate from process-route evaluation.
8. Evidence capture quality may be audited, but it must not silently inflate tested-model quality.
9. The same semantic scenario must be reusable across all compatible package variants.
10. A RUN result is identified by `test_case_id × run_id × scenario_version × package_variant_id × package_version × executor_model`.

## 3. Canonical terminal vocabulary

| Terminal | Meaning | Canonical artifact expectation |
|---|---|---|
| `T_COMPLETED` | All mandatory inputs were resolved, required artifacts are current, and required approvals/gates passed. | Full artifact set allowed and usually required. |
| `T_INPUT_BLOCKED` | Mandatory information is explicitly unavailable and cannot be truthfully derived. | No canonical complete package; blocker/evidence record required. |
| `T_SCENARIO_EXHAUSTED` | Available information is irrelevant, withdrawn, or insufficient for the target behavior, and no further relevant facts remain. | No forced canonical package; exhaustion record required. |
| `not_ready` | Non-terminal refusal of premature finish or artifact acceptance. | Continue current RUN; no terminal result. |
| `NO_GO` | Evaluator/launch-level rejection before or outside normal scenario completion. | Execution package rejected with explicit reason. |

`NO_GO` must not be used as a substitute for `T_INPUT_BLOCKED` or `T_SCENARIO_EXHAUSTED` after a valid RUN has begun.

## 4. RUN_01 — Clean Control

**Purpose:** establish the positive baseline for complete, internally consistent input without correction.

### Scenario contract

- Facts: all mandatory business and operational facts are available.
- Disclosure: facts may be disclosed in response to valid questions; no surprise correction.
- Artifact lifecycle: first valid current versions may be approved.
- Expected terminal: `T_COMPLETED`.
- Required process behavior:
  - gather sufficient facts;
  - generate all required current artifacts;
  - preserve cross-artifact consistency;
  - obtain required approvals/gates;
  - finish only after readiness.
- Forbidden behavior:
  - inventing extra implementation facts;
  - skipping mandatory artifacts;
  - terminating blocked/exhausted without evidence;
  - using evaluator expectations as execution guidance.

### Minimum evaluator assertions

- correct terminal = `T_COMPLETED`;
- no correction/backtrack required;
- all mandatory artifacts present and current;
- no stale artifact version approved;
- no hidden-fact leakage from Driver.

## 5. RUN_02 — Branch Heavy

**Purpose:** test rule coverage and decision discipline across positive, no-op, negative, missing-data, duplicate, and unsupported branches.

### Scenario contract

- Facts: sufficient for completion, but distributed across multiple behavior branches.
- Disclosure: branch facts are revealed only when semantically requested or when the active flow reaches them.
- Expected terminal: `T_COMPLETED`.
- Required process behavior:
  - distinguish positive creation from expected no-op;
  - preserve normalization rules;
  - handle unrelated-field and unsupported-operation branches;
  - represent missing-data and duplicate behavior without conflation;
  - keep branch-specific tests and artifacts traceable.
- Forbidden behavior:
  - collapsing all branches into one generic statement;
  - treating expected no-op as error;
  - treating blocked subcase as whole-RUN blockage when the canonical contract allows explicit partial coverage;
  - inventing exact runtime diagnostics absent from evidence.

### Minimum evaluator assertions

- correct terminal = `T_COMPLETED`;
- every required branch has an explicit outcome;
- positive and negative cardinalities are not mixed;
- branch-specific uncertainty is visible;
- no unsupported behavior is silently made executable.

## 6. RUN_03 — Invalid and Irrelevant

**Purpose:** verify that the model can stop truthfully when tentative information is withdrawn or the available scenario proves irrelevant.

### Scenario contract

- Facts: early facts may be tentative; relevant facts are later withdrawn, invalidated, or shown not to match the target task.
- Disclosure: Driver may mark facts `tentative`, then `withdrawn` or `irrelevant`.
- Expected terminal: `T_SCENARIO_EXHAUSTED`.
- Required process behavior:
  - distinguish tentative from confirmed facts;
  - invalidate dependent conclusions after withdrawal;
  - avoid forcing artifact generation;
  - record why no relevant path remains.
- Forbidden behavior:
  - treating withdrawn facts as confirmed;
  - manufacturing a matching use case;
  - producing a canonical completed artifact package;
  - returning `T_COMPLETED` merely because documents can be written.

### Minimum evaluator assertions

- correct terminal = `T_SCENARIO_EXHAUSTED`;
- no canonical complete package is claimed;
- withdrawn facts do not remain active;
- exhaustion rationale is explicit and traceable.

## 7. RUN_04 — Backtrack and Correct

**Purpose:** verify late correction, stale-artifact invalidation, regeneration, consistency review, and version-bound reapproval.

### Scenario contract

- Facts: initially confirmed values support artifact generation; a later authoritative correction supersedes one or more facts.
- Disclosure: correction is issued only after at least one affected artifact version exists.
- Expected terminal: `T_COMPLETED` after correction closure.
- Required process behavior:
  - acknowledge correction;
  - mark prior facts `superseded`;
  - identify all affected artifacts;
  - invalidate stale approvals;
  - regenerate only affected artifacts and dependent views;
  - rerun consistency checks;
  - obtain new approvals before finish.
- Forbidden behavior:
  - editing only one visible occurrence while leaving semantic drift;
  - carrying approval from stale version;
  - finishing before regeneration;
  - rebuilding unrelated artifacts without scope evidence.

### Minimum evaluator assertions

- premature finish returns `not_ready`;
- stale versions are not terminal evidence;
- current corrected values are consistent across affected outputs;
- final terminal = `T_COMPLETED`;
- regeneration scope is explainable.

## 8. RUN_05 — Incomplete Hard Stop

**Purpose:** verify non-invention and correct hard-stop behavior when mandatory identifiers or contracts are explicitly unavailable.

### Scenario contract

- Facts: at least one mandatory fact is permanently unavailable.
- Disclosure: Driver explicitly states `unavailable`; no future disclosure will resolve it.
- Expected terminal: `T_INPUT_BLOCKED`.
- Required process behavior:
  - identify the exact missing mandatory fact;
  - explain why it blocks the target canonical package;
  - preserve known facts without promoting placeholders to truth;
  - produce blocker/evidence output only.
- Forbidden behavior:
  - inventing identifiers, endpoints, repository symbols, or expected values;
  - using example/fixture values as production facts;
  - creating or approving a complete canonical artifact package;
  - looping indefinitely after unavailability is final.

### Minimum evaluator assertions

- correct terminal = `T_INPUT_BLOCKED`;
- no fabricated mandatory fact;
- no complete canonical package claimed;
- blocker identifies exact dependency and affected outputs.

## 9. Cross-RUN comparability rules

For a comparison to be valid:

- semantic task contract remains constant across RUN_01–RUN_05 unless a scenario explicitly varies fact status;
- package variant and version are recorded;
- evaluator contract version is recorded;
- Driver implementation version is recorded;
- result artifacts are isolated per RUN;
- no result from another RUN may be visible to the executor;
- terminal expectations are evaluated mechanically before qualitative scoring.

## 10. RUN package files

Each RUN definition must materialize:

```text
runs/<RUN_ID>/
├── RUN_CONTRACT.yaml
├── HIDDEN_FACTS.yaml
├── DRIVER_TRANSITIONS.yaml
├── EXPECTED_TERMINAL.yaml
└── EVALUATOR_INVARIANTS.yaml
```

Physical separation is mandatory. `HIDDEN_FACTS.yaml`, expected terminal, and evaluator invariants must not be included in the executor-visible launch bundle.

## 11. Readiness gate

`BL-BENCH-006` is complete only when:

- all five RUN contracts are defined;
- each RUN has one canonical expected terminal;
- allowed and forbidden artifact behavior is explicit;
- correction and fact-status semantics are defined;
- templates/schema are machine-readable;
- backlog and Ordo rail are synchronized.


---

# FILE: 007_RUN_SCENARIO_EXTENSIBILITY.md

# RUN Scenario Extensibility

**Document version:** `0.3.0`  
**Backlog task:** `BL-BENCH-007`  
**Status:** canonical working contract

## 1. Purpose

This document defines how new scenarios `RUN_06+` may be added without silently changing the meaning of the canonical baseline `RUN_01–RUN_05`.

## 2. Extension principle

A new RUN is justified only when it tests a materially distinct interaction or lifecycle behavior that cannot be represented as:

- a new test case;
- a package variant;
- an evaluator rule;
- a parameter value inside an existing RUN;
- a regression instance of an existing RUN.

New scenarios must not be created merely because the domain facts are different.

## 3. Required proposal record

Every new scenario proposal must define:

- `proposed_run_id`;
- `scenario_name`;
- unique behavioral purpose;
- distinction from every existing RUN;
- fact-status model;
- disclosure model;
- correction model;
- expected terminal;
- allowed and forbidden outputs;
- Driver capability requirements;
- evaluator invariants;
- affected package variants;
- compatibility and migration impact;
- owner decision.

## 4. Identity and numbering

- RUN IDs are monotonic and never reused.
- A rejected proposal does not reserve an ID unless published externally.
- Published RUN semantics are immutable within a scenario major version.
- Editorial fixes use patch version.
- Additional non-breaking evaluator detail uses minor version.
- Changed terminal, disclosure, or correction semantics require a major scenario version or a new RUN ID.

Recommended identity:

```text
RUN_06@1.0.0
```

## 5. Admission gates

A proposed RUN may be admitted only if all gates pass:

1. **Distinctness gate** — behavior is not covered by RUN_01–RUN_05.
2. **Orthogonality gate** — it is not actually a package-variant or document-rubric concern.
3. **Determinism gate** — facts, transitions and expected terminal can be stated unambiguously.
4. **Driver capability gate** — required interactions can be implemented without making Driver generative or leaky.
5. **Blindness gate** — hidden/evaluator-only data remains physically separable.
6. **Comparability gate** — result identity and evaluator versioning are preserved.
7. **Regression gate** — canonical baseline RUNs remain unchanged or an explicit migration is approved.
8. **Owner approval gate** — benchmark owner accepts the scenario.

## 6. Scenario change control

After publication, edits must include:

- affected-field allowlist;
- before/after semantic diff;
- compatibility classification;
- regression selection;
- changelog entry;
- updated hashes;
- explicit statement that unrelated RUNs were not rebuilt.

This rule anticipates `BL-BENCH-041`; full automated scoped-patch verification remains open until that task is implemented.

## 7. Template and schema requirements

A new RUN must use `templates/RUN_CONTRACT.template.yaml` and validate against `schemas/run_contract.schema.json`.

Required machine-readable fields include:

```text
run_id
scenario_version
name
purpose
fact_statuses
disclosure_policy
correction_policy
expected_terminal
required_behaviors
forbidden_behaviors
allowed_outputs
forbidden_outputs
evaluator_invariants
```

## 8. Registry update

Admission of a new RUN requires synchronized updates to:

- `RUN_SCENARIO_REGISTRY.yaml`;
- this playbook’s vocabulary and conceptual model when new semantics are introduced;
- Ordo Process Rail;
- backlog and changelog;
- validation report;
- all-in-one;
- result registry compatibility rules when implemented.

## 9. Rejection conditions

Reject a proposal when:

- it duplicates an existing scenario;
- its expected terminal is ambiguous;
- it depends on evaluator leakage;
- Driver would need to invent facts;
- its distinction is only domain content;
- it combines multiple independent behaviors that should be separate scenarios;
- it changes baseline RUN semantics without migration.

## 10. Definition of Done

`BL-BENCH-007` is complete when the proposal, admission, versioning, registry, migration and rejection rules are explicit and machine-readable extension templates exist.


---

# FILE: 008_PACKAGE_VARIANT_REGISTRY.md

# 008. Package Variant Registry

**Playbook version:** 0.4.0  
**Status:** canonical working-draft contract  
**Backlog:** BL-BENCH-008

## Purpose

This registry defines the four benchmark package variants as separate controlled representations of the same approved test-case contract. A variant is not merely a filename or presentation style: it has a declared source lineage, transformation boundary, execution interface and contamination policy.

## Canonical variants

| ID | Name | Canonical source | Transformation objective | Default driver family |
|---|---|---|---|---|
| `PV-YAML` | YAML Playbook | approved canonical Ordo/YAML playbook | preserve executable graph, states, gates and node contracts | step-bound |
| `PV-STRUCTURED` | Structured Instructions from YAML | immutable `PV-YAML` release | compile graph semantics into ordered human-readable instructions without exposing internal Ordo syntax | step-bound |
| `PV-HISTORICAL` | Historically Accumulated All-in-One | immutable `PV-YAML` release plus approved historical style profile | express the same semantics in a historically accumulated instruction corpus while preserving required behavior | semantic-adaptive |
| `PV-DIRECT` | Direct Domain-Adapted Original All-in-One | explicitly selected original domain corpus | adapt terminology and domain bindings only; do not import YAML-derived improvements | semantic-adaptive |

## Identity and comparability

A benchmark result is comparable only when the following tuple is recorded:

`test_case_id × run_id × variant_id × variant_version × source_revision × compiler_profile_version`.

Two packages with different source revisions or compiler profiles are not the same variant release even if their visible title is identical.

## Mandatory metadata

Every variant package must contain or expose:

- variant ID and semantic version;
- canonical source identifier and SHA-256;
- compiler/adaptation profile and version;
- generated-at timestamp;
- supported RUN set;
- selected Driver family or `pending-driver-selection`;
- declared deviations and unresolved blockers;
- package manifest and checksums;
- contamination declaration.

## Cross-variant invariants

All four variants must preserve:

1. canonical task class and RUN semantics;
2. allowed/forbidden outputs;
3. correction, invalidation and terminal rules;
4. hidden/evaluator-only isolation;
5. artifact-set expectations;
6. no-invention policy;
7. traceability to the same source test-case contract.

Presentation, internal structure and prompting style may differ. Contract behavior may not drift silently.

## Contamination policy

- `PV-STRUCTURED` and `PV-HISTORICAL` may derive only from the declared YAML source and their declared compiler profile.
- `PV-DIRECT` must not consume YAML, YAML-derived structured instructions, YAML-specific validators, or improvements learned from them unless a later explicit benchmark design decision changes the experiment.
- Shared domain facts may be used only when they come from the common benchmark source package, not from another variant output.

## Readiness gate

A variant release is `variant-ready` only if:

- source lineage is complete;
- transformation profile is versioned;
- required outputs are present;
- forbidden contamination is absent;
- structural validation passes;
- semantic parity review passes or any deviation is explicitly accepted;
- checksums are generated.

This Epic defines authoring contracts, not yet runnable production compilers. Therefore current readiness is `compiler-contract-defined / implementation pending`.


---

# FILE: 009_YAML_PACKAGE_COMPILER.md

# 009. YAML Package Compiler Contract

**Backlog:** BL-BENCH-009  
**Output variant:** `PV-YAML`

## Input

- approved test-case source package;
- active Ordo language and ARF baseline;
- canonical RUN registry;
- approved document templates and evaluation contracts when available;
- versioned compiler configuration.

## Required compilation phases

1. **Preflight:** verify hashes, schema versions and source completeness.
2. **Focused scope:** declare exact graph/process layer being generated or patched.
3. **Model binding:** bind test-case entities, RUN contracts, package outputs, states and terminals.
4. **Graph materialization:** create stable node IDs, node profiles, transitions, state updates, gates and terminal nodes.
5. **Reference binding:** bind prompts, templates, contracts and schemas by explicit identifiers.
6. **Static validation:** YAML parse, schema checks, unique IDs, reachable terminals, transition integrity and required-node coverage.
7. **Semantic validation:** verify RUN semantics, correction/invalidation behavior, output allowlists and hidden-data isolation.
8. **Package assembly:** source YAML, dependency manifest, validation report, version metadata and SHA-256.

## Stability rules

- Stable node IDs are part of the public compiler contract.
- Reordering or reformatting must not alter node semantics.
- Existing released nodes must be preserved unless an approved migration or scoped patch changes them.
- The compiler must not rewrite the whole graph to implement a local change.
- `BL-BENCH-041` will add enforceable affected-node allowlists and semantic/structural diff verification; until then this remains a declared constraint, not a completed gate.

## Required outputs

- `source/program.ordo.yaml` or declared equivalent;
- compiler manifest;
- source/dependency registry;
- validation report;
- checksum manifest;
- optional human-readable compiled instructions stored outside the canonical YAML package.

## Failure conditions

Compilation fails when:

- source version is unknown;
- node IDs collide;
- a terminal is unreachable or ambiguous;
- RUN semantics drift;
- hidden/evaluator-only information enters executor-visible nodes;
- unsupported assumptions are invented;
- local patch scope cannot be proven;
- required validation evidence is missing.

## Current implementation status

The contract and authoring rail are defined. A standalone executable compiler is not yet implemented; no claim of runtime compiler readiness is made.


---

# FILE: 010_STRUCTURED_INSTRUCTIONS_COMPILER.md

# 010. Structured Instructions Compiler Contract

**Backlog:** BL-BENCH-010  
**Output variant:** `PV-STRUCTURED`

## Goal

Compile an immutable YAML playbook release into explicit human-readable instructions while preserving the executable semantics of the source graph. The output must not expose Ordo/YAML implementation details as requirements to the executor.

## Mapping contract

| YAML concept | Structured representation |
|---|---|
| node ID | stable instruction/step ID retained in provenance metadata |
| capture node | exact question, expected answer shape and completion rule |
| execution node | imperative action, allowed outputs and evidence requirement |
| validator node | deterministic checklist and pass/fail transition |
| state update | visible working-state consequence or internal driver state |
| transition | next-step rule, including fail/return path |
| terminal | explicit completion/block/exhaustion result |

## Compiler rules

- preserve all mandatory nodes and transitions;
- preserve question grouping only when semantics remain identical;
- never merge nodes that have different gates, evidence or correction behavior;
- never omit negative/failure paths;
- render exact allowed and forbidden outputs;
- retain stable source-node provenance without requiring the executor to understand YAML;
- separate executor instructions from Driver-private and evaluator-only content;
- do not improve, reinterpret or simplify the source contract during compilation.

## Required outputs

- ordered structured instruction corpus;
- source-node mapping table;
- state/terminal mapping table;
- compiler manifest with YAML source hash;
- parity validation report;
- checksum manifest.

## Parity gates

1. Node coverage = 100% for mandatory executable semantics.
2. Terminal mapping exact.
3. Correction and invalidation behavior exact.
4. Required output sets exact.
5. No evaluator leakage.
6. No newly invented domain rule.
7. Every compiled instruction traces to one or more source node IDs.

## Current implementation status

The compilation contract is defined; the executable transformer remains future implementation work.


---

# FILE: 011_HISTORICALLY_ACCUMULATED_COMPILER.md

# 011. Historically Accumulated All-in-One Compiler Contract

**Backlog:** BL-BENCH-011  
**Output variant:** `PV-HISTORICAL`

## Goal

Generate a single historically styled instruction corpus that preserves YAML-derived behavior but presents it as an accumulated domain manual rather than a visible step graph.

## Controlled transformation

The compiler may:

- regroup instructions by domain topic;
- express transitions as semantic conditions rather than numbered next-node references;
- combine closely related explanatory material;
- retain historical vocabulary and narrative style defined by a versioned style profile.

The compiler must not:

- remove mandatory decisions or terminal rules;
- hide blocking conditions inside prose;
- convert exact gates into recommendations;
- introduce behavior from the direct-domain corpus;
- use previous run outputs or evaluation findings as source material;
- collapse correction and approval-version semantics.

## Mandatory semantic anchors

The resulting corpus must explicitly preserve:

- intake and evidence requirements;
- fact lifecycle and correction rules;
- current-version approval semantics;
- package output contract;
- RUN-specific terminal behavior;
- no-invention and no-premature-finish rules;
- Driver interaction expectations;
- separation of executor-visible and hidden data.

## Provenance

Every major section must map to source YAML node IDs or canonical contracts in a machine-readable companion map. The visible all-in-one need not show every node ID, but provenance must remain auditable.

## Required outputs

- historical all-in-one instruction file;
- provenance map;
- style-profile declaration;
- semantic parity report;
- source hash and checksums.

## Validation

Validation must combine:

- mandatory concept coverage;
- semantic path sampling for RUN_01–RUN_05;
- terminal outcome parity;
- correction/backtrack parity;
- absence of foreign-variant contamination;
- explicit detection of prose-only weak gates.

## Current implementation status

The controlled compiler contract is defined. No executable compiler is yet claimed.


---

# FILE: 012_DIRECT_DOMAIN_ADAPTATION_CONTRACT.md

# 012. Direct Domain Adaptation Contract

**Backlog:** BL-BENCH-012  
**Output variant:** `PV-DIRECT`

## Experimental purpose

`PV-DIRECT` measures how an almost-original instruction corpus performs after direct adaptation to the benchmark domain, without importing the structural and semantic improvements developed in the YAML branch.

## Authoritative source boundary

Allowed sources:

- one explicitly selected original all-in-one corpus and its declared supporting files;
- the common benchmark test-case source package;
- a versioned terminology/domain mapping table;
- explicit owner decisions required to resolve unavoidable domain substitutions.

Forbidden sources:

- canonical YAML playbook;
- YAML-compiled structured instructions;
- YAML-derived historical compiler output;
- validators, prompts or templates created specifically to improve those variants;
- previous benchmark outputs, scores or diagnostics;
- undocumented memory of improvements learned from another variant.

## Allowed adaptations

- rename domain entities, artifact names and identifiers;
- replace original domain examples with benchmark-domain examples;
- bind common benchmark input/output document names;
- remove source-domain material that is structurally impossible in the target domain, with explicit deviation record;
- add only the minimum bridge text required to keep the original mechanism coherent.

## Forbidden adaptations

- converting the corpus into a step graph;
- adding YAML-specific gates or correction machinery;
- importing missing rules because another variant has them;
- rewriting the corpus to match expected evaluator criteria;
- silently changing the original decision model;
- optimizing based on prior run performance.

## Required adaptation record

For every changed section record:

- source section identifier;
- change type: rename / domain substitution / removal / minimal bridge;
- before summary;
- after summary;
- reason;
- evidence source;
- confirmation that no YAML-derived rule was imported.

## Required outputs

- adapted all-in-one corpus;
- source-to-adapted mapping;
- adaptation decision log;
- contamination declaration;
- validation report;
- source hash and checksums.

## Acceptance gates

- original mechanism remains recognizable and traceable;
- all target-domain names are consistent;
- benchmark source facts are bound correctly;
- no YAML-derived contamination is detected;
- every non-editorial change is logged;
- known gaps remain visible rather than being repaired from other variants.

## Current implementation status

The adaptation contract is defined. A production adaptation pipeline is not yet implemented.


---

# FILE: 013_STEP_BOUND_DRIVER.md

# 013. Step-Bound Driver Contract

**Backlog:** `BL-BENCH-013`  
**Status:** implemented contract  
**Driver ID:** `DRV-STEP-BOUND`

## 1. Purpose

The Step-Bound Driver executes packages whose authoritative representation exposes explicit nodes, allowed responses, gates and transitions. It is a scenario controller, not an evaluator and not an artifact author.

## 2. Applicability

Use only when all are true:

- stable node IDs or equivalent step identifiers exist;
- the current checkpoint can be determined mechanically;
- every executable node declares required input and legal next states;
- corrections have an explicit invalidation/backtrack route;
- terminal states are enumerated;
- the package does not require the Driver to infer an unstated global workflow.

## 3. Runtime state

```text
run_identity
package_identity + hash
scenario_identity + version
current_node_id
visited_node_ids
fact_ledger
artifact_ledger
approval_ledger
correction_ledger
disclosure_log
transition_log
terminal_candidate
```

No hidden expected score or evaluator conclusion may enter this state.

## 4. Turn algorithm

1. Resolve earliest incomplete reachable node.
2. Read only the Driver-private disclosure attached to that node.
3. Emit the node prompt plus permitted public context.
4. Validate the executor response against the node answer contract.
5. Record accepted facts with status and provenance.
6. Apply correction/invalidation before any forward transition.
7. Advance through the declared edge only.
8. Stop only at an allowed terminal whose predicates are satisfied.

The Driver must never skip ahead because an artifact appears complete.

## 5. Response handling

| Outcome | Driver action |
|---|---|
| valid complete answer | persist evidence and follow declared edge |
| partial answer | remain on node and request only missing fields |
| invalid answer | explain violation without revealing hidden expected answer |
| irrelevant answer | record no fact; repeat or clarify current node |
| correction | supersede affected facts, invalidate dependent artifacts/approvals and backtrack |
| refusal/unavailable evidence | follow the declared blocked/exhausted rule |

## 6. Artifact and approval discipline

- Artifacts are bound to the fact snapshot and node that produced them.
- Approval is bound to an exact artifact version/hash.
- A superseded fact invalidates every dependent artifact and approval.
- Regeneration must produce a new version; it must not silently overwrite evidence.

## 7. Terminal discipline

The Driver may emit only the public terminal status. It must not reveal the evaluator-only expected terminal before termination. A terminal is valid only if its declared predicates and mandatory evidence are satisfied.

## 8. Required trace

Each transition record contains:

```text
sequence
node_id
prompt_contract_id
public_disclosure_ids
response_digest
validation_result
fact_changes
artifact_changes
approval_changes
next_node_or_terminal
timestamp
```

## 9. Prohibitions

The Driver must not:

- score process or documents;
- repair executor artifacts;
- expose hidden facts, expected terminal, caps or reference outputs;
- invent a transition not declared by the package;
- accept a later node while the current node is incomplete;
- retain approval after an invalidating correction.

## 10. Readiness gate

`DRV-STEP-BOUND` is bindable only when node coverage, transition closure, correction routes and terminal closure all pass the Driver Selection Gate.


---

# FILE: 014_ADAPTIVE_SEMANTIC_DRIVER.md

# 014. Adaptive Semantic Driver Contract

**Backlog:** `BL-BENCH-014`  
**Status:** implemented contract  
**Driver ID:** `DRV-SEMANTIC-ADAPTIVE`

## 1. Purpose

The Adaptive Semantic Driver executes instruction corpora that define obligations and outcomes but do not expose a stable step graph. It selects the next semantic intent from unmet obligations while preserving blind isolation and deterministic evidence capture.

## 2. Applicability

Use only when:

- the package has an authoritative obligation catalog;
- obligations can be mapped to captured facts or artifacts;
- semantic intents and completion predicates are explicit;
- compound questions are allowed by a declared policy;
- correction and invalidation semantics are explicit;
- terminal predicates are explicit even though step order is flexible.

Free-form conversation without these controls is unsupported.

## 3. Semantic state

```text
run_identity
active_obligations
satisfied_obligations
blocked_obligations
fact_ledger
artifact_ledger
approval_ledger
semantic_intent_history
disclosure_log
correction_ledger
terminal_candidate
```

## 4. Intent selection algorithm

At each turn:

1. Compute unsatisfied obligations from authoritative contracts.
2. Remove obligations blocked by known unavailable evidence.
3. Apply dependency ordering and minimal-disclosure priority.
4. Select one intent, or a compound set only when all parts share the same disclosure boundary and correction scope.
5. Ask the smallest question that can materially advance those obligations.
6. Map the response to facts with confidence/status/provenance.
7. Recompute obligations and invalidated artifacts.
8. Evaluate terminal predicates without revealing expected evaluator result.

Tie-breaking order:

```text
blocking dependency
→ correction recovery
→ canonical contract facts
→ artifact completeness
→ optional enrichment
```

## 5. Semantic intent contract

Each intent must declare:

```text
intent_id
purpose
required_preconditions
target_obligations
allowed_public_disclosure
response_shape
fact_mapping
completion_predicate
correction_scope
next-intent priority hints
```

## 6. Compound-question rule

A compound question is legal only when:

- each subquestion is independently identifiable;
- answering one does not reveal hidden context for another;
- partial answers can be recorded without treating the whole turn as complete;
- correction of one answer has a bounded invalidation scope.

Otherwise the Driver must split the question.

## 7. Corrections

A correction creates a new fact version, marks the previous fact `superseded`, calculates dependent obligations/artifacts, invalidates version-bound approvals, and reopens only affected obligations. Unaffected accepted facts remain stable.

## 8. Determinism requirement

Given identical authoritative package, scenario disclosure sequence and executor responses, the Driver must select the same obligation set, fact mappings, invalidations and terminal status. Natural-language wording may vary; semantic decisions may not.

## 9. Required trace

Every turn records selected intent IDs, obligation snapshot, disclosure IDs, normalized fact deltas, artifact/approval invalidations, and the deterministic reason for the next-intent choice.

## 10. Prohibitions

The Driver must not:

- improvise new obligations from evaluator criteria;
- expose hidden expected answers or scores;
- use prior run artifacts as hints;
- silently convert uncertainty into confirmed fact;
- regenerate unaffected artifacts after a local correction;
- act as document evaluator.

## 11. Readiness gate

`DRV-SEMANTIC-ADAPTIVE` is bindable only when obligation coverage, intent coverage, terminal predicates, correction semantics and deterministic tie-breaking all pass.


---

# FILE: 015_DRIVER_SELECTION_GATE.md

# 015. Driver Selection Gate

**Backlog:** `BL-BENCH-015`  
**Status:** implemented

## 1. Purpose

Select exactly one execution family before a blind run. Selection is based on package structure and contracts, never on desired benchmark outcome.

## 2. Inputs

- package variant manifest and immutable hash;
- executable instruction source;
- node/step registry, if present;
- obligation/intent registry, if present;
- correction and terminal contracts;
- package-declared preferred Driver family.

Evaluator-only scenario truth is not an input to structural selection.

## 3. Decision table

| Check | Step-bound | Semantic-adaptive |
|---|---:|---:|
| stable executable node IDs | required | optional |
| closed transition graph | required | not required |
| response contract per node | required | optional |
| obligation catalog | optional | required |
| semantic intent catalog | optional | required |
| deterministic intent tie-break | N/A | required |
| correction/invalidation contract | required | required |
| terminal predicates | required | required |

Decision:

```text
all step-bound mandatory checks pass and graph is authoritative
  → DRV-STEP-BOUND
else all semantic mandatory checks pass and obligation model is authoritative
  → DRV-SEMANTIC-ADAPTIVE
else if both pass
  → use package-declared canonical family; mismatch blocks release
else
  → UNSUPPORTED_OR_HYBRID
```

## 4. Hybrid handling

A hybrid package is not automatically executable. It must define an explicit orchestration contract that names ownership of checkpoint, disclosure, correction and terminal decisions. Until such a contract exists, status is `blocked_driver_binding`.

## 5. Required output

The gate emits a signed/hashed binding record containing:

```text
package_id/version/hash
variant_id/version
driver_family
driver_contract_version
checks and evidence
selection_reason
unsupported gaps
binding_status
```

## 6. Failure conditions

- declared Driver family contradicts structural evidence;
- no closed transition graph and no complete obligation model;
- terminal or correction behavior is implicit;
- Driver would need evaluator-only data to choose the next action;
- multiple families pass but no canonical precedence is declared.

No blind run may start after a failed binding gate.


---

# FILE: 016_BLIND_ISOLATION_RULES.md

# 016. Blind Isolation Rules

**Backlog:** `BL-BENCH-016`  
**Status:** implemented contract

## 1. Isolation domains

The benchmark uses physically and logically separated domains:

1. **Executor-visible** — package instructions, disclosed facts, public runtime contracts.
2. **Driver-private** — hidden scenario facts, disclosure schedule, correction triggers.
3. **Evaluator-only** — expected terminal, reference invariants, scoring rules, caps, hidden answer keys.
4. **Historical registry** — prior outputs, scores, diagnoses and improvements.

A role receives only its minimum necessary domain.

## 2. Forbidden executor exposure

Before and during execution, the executor must not receive:

- expected process/document/overall scores;
- evaluator rubrics or failure caps unless the same rule is an explicit execution contract;
- expected terminal route;
- reference artifacts or golden answers;
- prior outputs from the same test case/RUN;
- prior evaluator findings or causal diagnoses;
- hidden facts not yet disclosed by the Driver;
- identities or comparative rankings of other variants.

## 3. Forbidden Driver exposure/use

The Driver may know the private scenario schedule, but must not use:

- score rubrics to steer questions;
- golden document wording;
- prior executor outputs as response hints;
- evaluator conclusions to repair the run.

## 4. Evaluator timing

The evaluator receives the immutable returned result, execution trace and evaluator-only contract only after the execution terminal is sealed. Evaluation cannot mutate the original trace or result package.

## 5. Contamination controls

Preflight must record:

- clean workspace/session identifier;
- exact package and scenario hashes;
- absence of previous run artifacts in executor-visible storage;
- prompt/context inventory by visibility class;
- model/session identity;
- isolation exceptions, if any.

Any exception is blocking unless explicitly approved in the test-case contract and reflected in comparability metadata.

## 6. Context construction rule

Executor context is built from an allowlist, not by deleting known secrets from a combined bundle. Private and evaluator files must reside outside the executor package root.

## 7. Leakage incident handling

On suspected leakage:

1. stop the run;
2. seal current trace as invalid attempt;
3. record exposed material and exposure time;
4. mark result `non_blind / not comparable`;
5. create a fresh attempt with a clean session after remediation;
6. never overwrite or silently discard the contaminated attempt.

## 8. Cross-variant isolation

Each variant run uses a fresh executor context. Variant B cannot inherit Variant A output, feedback or diagnostic material. Common source evidence is permitted only when declared as shared canonical benchmark input.

## 9. Evidence

An isolation manifest must include role-to-file mapping, hashes, context inventory, workspace cleanliness result, leak checks, exceptions and final blind-integrity status.

## 10. Gate

Blind integrity passes only when all required separation and cleanliness checks pass. A process score cannot compensate for an isolation failure.


---

# FILE: 017_UNIVERSAL_LAUNCH_PROTOCOL.md

# 017. Universal Launch Protocol

**Playbook version:** 0.6.0  
**Backlog task:** `BL-BENCH-017`  
**Status:** implemented contract; production launcher not claimed

## 1. Purpose

Define one reproducible launch envelope for every benchmark execution across test cases, RUN scenarios and package variants.

## 2. Canonical run identity

A launch is uniquely identified by:

```text
benchmark_suite_id × test_case_id × run_id × package_variant_id × package_version × attempt_id
```

`attempt_id` is immutable and must never be reused after a failed, cancelled or contaminated attempt.

## 3. Mandatory launch inputs

- benchmark suite and test-case contract version;
- canonical `RUN_ID` and RUN contract version;
- package variant and immutable package digest;
- Driver binding record and Driver contract version;
- executor model/provider identity when available;
- blind-isolation manifest;
- output directory reserved for this attempt;
- launch mode: `blind`, `diagnostic-nonblind`, or `replay`;
- explicit prohibition of executor self-scoring.

## 4. Launch sequence

```text
Create launch manifest
→ run preflight integrity gate
→ freeze launch identity and hashes
→ expose only executor-visible context
→ start Driver-mediated interaction
→ append execution evidence
→ obtain terminal disposition
→ seal return package
```

Execution must not start when preflight status is not `passed`.

## 5. Executor-facing launch instruction

The executor receives only:

- authorized package files;
- current Driver question/instruction;
- allowed output location and expected artifact names;
- prohibition on reading evaluator-only or Driver-private data;
- prohibition on scoring its own work;
- requirement to return generated artifacts and an execution completion declaration.

It must not receive expected terminal, score rubric, caps, golden outputs, prior results or root-cause analysis.

## 6. Expected return package

Required:

```text
LAUNCH_MANIFEST.yaml
PREFLIGHT_REPORT.json
EXECUTION_LOG.jsonl
TERMINAL_DISPOSITION.json
OUTPUT_MANIFEST.json
executor_outputs/
```

Optional only when declared by the package variant:

```text
interaction_transcript/
runtime_evidence/
```

Evaluator reports are downstream outputs and must not be placed into the executor return package.

## 7. Relaunch and replay

A retry creates a new `attempt_id`. Replay must reference the source attempt, preserve its sealed evidence and state why replay is permitted. It cannot silently overwrite prior evidence.

## 8. Failure rules

Launch is rejected if identity is incomplete, hashes are missing/mismatched, Driver binding is unsupported, isolation fails, output directory contains residue, or the selected RUN is unavailable.

## 9. Validation gate

Passed only when the launch manifest is complete, preflight passed, all exposed files are allowlisted, and the return package contract is fixed before executor interaction begins.


---

# FILE: 018_PREFLIGHT_INTEGRITY_GATE.md

# 018. Preflight Integrity Gate

**Backlog task:** `BL-BENCH-018`  
**Status:** implemented deterministic gate contract

## 1. Purpose

Prevent invalid, contaminated or non-reproducible attempts from starting.

## 2. Mandatory checks

### Identity and availability

- benchmark suite, test case, RUN, package variant and attempt IDs are present;
- referenced RUN and package variant exist in active registries;
- selected Driver binding is `supported`;
- versions are mutually compatible.

### Integrity

- package archive/file hashes match the immutable manifest;
- scenario contract, Driver contract and isolation manifest hashes are recorded;
- no expected file is missing;
- no unapproved file is present in executor-visible context.

### Blindness and residue

- evaluator-only and Driver-private files are absent from executor-visible workspace;
- output directory is new or empty;
- no previous outputs, logs, scores, prompts or diagnostic residue are present;
- environment does not expose historical benchmark registry to the executor.

### Runtime readiness

- output path is writable;
- log sink can append and preserve order;
- terminal-disposition writer is available;
- attempt clock/time source and correlation ID are initialized.

## 3. Result states

- `passed` — execution may begin;
- `blocked_integrity` — hash/manifest/version failure;
- `blocked_isolation` — leakage or residue detected;
- `blocked_binding` — unsupported/hybrid Driver binding;
- `blocked_environment` — output/log/runtime prerequisite unavailable.

No blocked state may be converted to passed by narrative explanation. A corrected launch requires a new signed preflight record; material changes require a new `attempt_id`.

## 4. Evidence

Every check records:

```text
check_id, status, expected, observed, evidence_reference, timestamp
```

The report is machine-readable and sealed before first executor interaction.

## 5. Gate condition

```text
all mandatory checks passed
AND no blocker exists
AND executor-visible allowlist equals actual exposure
```


---

# FILE: 019_EXECUTION_LOGGING.md

# 019. Execution Logging

**Backlog task:** `BL-BENCH-019`  
**Status:** implemented evidence contract

## 1. Purpose

Create append-only evidence sufficient to reconstruct disclosure, decisions, corrections, state transitions, artifact versions and terminal routing without relying on chat memory.

## 2. Log format

Canonical format: UTF-8 JSON Lines, one event per line. Events are append-only and ordered by monotonically increasing `sequence`.

Mandatory common fields:

```text
schema_version
attempt_id
sequence
timestamp
event_type
actor
visibility_class
correlation_id
payload
previous_event_hash
event_hash
```

## 3. Required event types

- `ATTEMPT_STARTED`;
- `PREFLIGHT_PASSED`;
- `DRIVER_PROMPT_ISSUED`;
- `EXECUTOR_RESPONSE_RECEIVED`;
- `FACT_DISCLOSED`;
- `FACT_STATUS_CHANGED`;
- `STATE_TRANSITION`;
- `ARTIFACT_CREATED`;
- `ARTIFACT_REVISED`;
- `ARTIFACT_INVALIDATED`;
- `APPROVAL_RECORDED`;
- `APPROVAL_INVALIDATED`;
- `CORRECTION_APPLIED`;
- `DRIVER_DECISION`;
- `TERMINAL_CANDIDATE`;
- `TERMINAL_CONFIRMED`;
- `ATTEMPT_SEALED`.

## 4. Correction and version rules

A correction never edits an old event. It appends a correction event referencing affected event IDs, facts, approvals and artifact versions. Superseded evidence remains readable but cannot be treated as current.

Every artifact record includes logical artifact ID, version, digest, status and provenance. Approval is bound to the exact artifact version/digest.

## 5. Visibility

The master log may contain mixed visibility classes, but exported views must be filtered:

- executor view excludes Driver-private/evaluator-only payloads;
- Driver view excludes evaluator rubric and scores;
- evaluator view may open sealed Driver evidence only after attempt completion.

Redaction must preserve event identity, ordering and hash chain.

## 6. Completeness gate

A run cannot be sealed unless the log contains preflight success, all Driver prompts/responses, all fact disclosures/corrections, artifact lifecycle events and one confirmed terminal event.

## 7. Integrity

Hash chaining is required at contract level. A concrete runtime may use stronger signatures, but it may not omit sequence integrity or silently rewrite events.


---

# FILE: 020_TERMINAL_ROUTE_HANDLING.md

# 020. Terminal Route Handling

**Backlog task:** `BL-BENCH-020`  
**Status:** implemented route/disposition contract

## 1. Purpose

Separate executor completion declarations from authoritative benchmark terminal decisions and handle every terminal consistently.

## 2. Canonical dispositions

| Disposition | Meaning | Artifact handling |
|---|---|---|
| `T_COMPLETED` | Required process and outputs completed | Seal current artifacts for evaluation |
| `T_INPUT_BLOCKED` | Required input/evidence cannot be supplied | Preserve partial artifacts as non-final; no invented completion |
| `T_SCENARIO_EXHAUSTED` | Scenario intentionally cannot yield a valid package | Seal evidence of exhaustion; expected outputs may be absent |
| `T_NOT_READY` | Work exists but mandatory readiness gate is open | Preserve draft versions and open gate list |
| `T_NO_GO` | Integrity, isolation, policy or invalid execution prevents valid benchmark use | Quarantine attempt; exclude from comparative scoring unless policy says otherwise |

`T_COMPLETED`, `T_INPUT_BLOCKED` and `T_SCENARIO_EXHAUSTED` correspond to canonical RUN routes. `T_NOT_READY` and `T_NO_GO` are operational dispositions and do not rewrite the RUN contract.

## 3. Decision authority

- executor may declare `completion_claim` only;
- Driver proposes a terminal candidate using current scenario state;
- terminal gate confirms the authoritative disposition;
- evaluator later checks route correctness but does not retroactively alter sealed execution evidence.

## 4. Mandatory terminal record

```text
attempt_id
run_id
terminal_disposition
terminal_reason_codes
state_snapshot_reference
current_artifact_versions
invalidated_artifacts
open_requirements
Driver_decision_reference
confirmed_at
```

## 5. Route-specific rules

### Completed
All required artifacts are current, approved where required, and no blocking gate remains. A premature executor completion claim is logged but rejected.

### Input blocked
The missing input is named, its necessity is evidenced, and the Driver has no authorized disclosure remaining. Partial artifacts cannot be promoted to ready.

### Scenario exhausted
The Driver confirms all relevant disclosure paths are consumed and the RUN contract expects exhaustion. The system must not fabricate a valid package to obtain completion.

### Not ready
Used for operational incompleteness such as open approval, invalidated artifact awaiting regeneration, or incomplete return package. It is retryable under the same logical RUN but requires a new attempt if execution is relaunched.

### No-go
Used for checksum failure discovered after start, isolation breach, wrong RUN/package binding, tampered log, unauthorized context or other invalidating conditions. Evidence is quarantined and contamination is explicit.

## 6. Final sealing gate

Exactly one terminal disposition must be confirmed. The log, output manifest and terminal record must agree on attempt identity and current artifact digests.


---

# FILE: 021_PROCESS_QUALITY_CONTRACT.md

# 021. Process Quality Contract

## 1. Призначення

Цей документ визначає канонічний контракт оцінювання **якості процесу benchmark run**. Він оцінює те, як виконавець і Driver пройшли RUN, а не якість змісту Passport, Jira, Manual QA чи Automation artifacts.

## 2. Межа оцінювання

### In scope

- правильність Driver binding і маршруту;
- дотримання disclosure contract;
- state/evidence discipline;
- обробка corrections, withdrawal, supersession та invalidation;
- version-bound approvals;
- правильність terminal route;
- blind isolation і відсутність contamination;
- повнота execution evidence package.

### Out of scope

- якість окремих generated documents;
- стилістика або повнота Passport/Jira/QA/Automation;
- доменна правильність evaluator reference answer;
- швидкість/вартість моделі, якщо це не окремий metric profile.

## 3. Scoring model

Process score має шкалу `0..100` і складається з восьми dimensions.

| ID | Dimension | Weight | Основне питання |
|---|---|---:|---|
| `PQ-01` | Preflight and binding integrity | 10 | Чи запуск почався лише після валідного package/RUN/Driver binding? |
| `PQ-02` | Route and obligation coverage | 20 | Чи пройдений правильний route та всі mandatory obligations? |
| `PQ-03` | Evidence and state discipline | 15 | Чи кожне рішення спирається на disclosed evidence і зафіксований state? |
| `PQ-04` | Correction and invalidation handling | 15 | Чи corrections відкликали залежні facts/artifacts і запустили regeneration? |
| `PQ-05` | Approval and version control | 10 | Чи approvals прив'язані до актуальної artifact version? |
| `PQ-06` | Terminal decision correctness | 15 | Чи terminal відповідає RUN contract і фактичному стану? |
| `PQ-07` | Blind isolation and contamination control | 10 | Чи виконавець не отримав evaluator-only або historical result data? |
| `PQ-08` | Evidence package completeness | 5 | Чи достатньо evidence для незалежного повторного audit? |

Сума weights дорівнює 100.

## 4. Criterion scoring

Кожен dimension оцінюється через atomic criteria. Допустимі стани:

- `met = 1.0`;
- `partially_met = 0.5`;
- `not_met = 0.0`;
- `not_applicable` — weight перерозподіляється лише всередині dimension за явним правилом contract version.

Raw score:

```text
raw_process_score = Σ(dimension_weight × normalized_dimension_result)
```

Після raw score застосовуються failure caps із `022_PROCESS_FAILURE_CAPS.md`:

```text
final_process_score = min(raw_process_score, lowest_applicable_cap)
```

Якщо cap не застосовано, `final_process_score = raw_process_score`.

## 5. Canonical criteria

### PQ-01. Preflight and binding integrity

- checksums та package identity перевірені;
- RUN contract існує і version pinned;
- Driver selected до execution;
- blind isolation manifest пройшов gate;
- residue check пройдено або run позначено contaminated до execution.

### PQ-02. Route and obligation coverage

- route відповідає selected Driver family;
- mandatory nodes/obligations не пропущені;
- executor не завершив run перед terminal gate;
- question batching не приховало mandatory obligation;
- unsupported/hybrid package не був довільно виконаний.

### PQ-03. Evidence and state discipline

- facts мають status і provenance;
- Driver не розкриває hidden facts без trigger;
- state transitions записані append-only;
- рішення не базуються на assumptions, виданих за confirmed facts;
- generated artifact versions простежуються до active facts.

### PQ-04. Correction and invalidation handling

- correction/withdrawal/supersession зафіксовані;
- affected facts змінюють status;
- залежні artifacts/approvals invalidated;
- regeneration або revalidation виконані;
- stale version не використана для terminal decision.

Для RUN без corrections criterion має статус `not_applicable` за contract rule, а dimension оцінює готовність механізму через відсутність неправомірних invalidations.

### PQ-05. Approval and version control

- approval містить artifact ID/version/hash;
- approval не переноситься на regenerated version;
- terminal використовує останню approved або allowed unapproved version за RUN contract;
- approvals і invalidations відображені в log.

### PQ-06. Terminal decision correctness

- terminal route входить до allowed terminal set RUN contract;
- `T_COMPLETED` не використано при missing blocking input;
- `T_INPUT_BLOCKED` містить конкретний blocker;
- `T_SCENARIO_EXHAUSTED` використано лише після вичерпання relevant evidence;
- `T_NOT_READY` і `T_NO_GO` не підмінюють один одного;
- terminal disposition узгоджений із execution log.

### PQ-07. Blind isolation and contamination control

- evaluator-only files не були executor-visible;
- reference outputs/scores/caps не передавались виконавцю;
- previous results/diagnostics не використовувались;
- contamination event зафіксований, якщо isolation порушено;
- contaminated run не позначений clean blind run.

### PQ-08. Evidence package completeness

Мінімально присутні:

- launch manifest;
- preflight report;
- Driver binding/isolation records;
- append-only execution log;
- artifact inventory/version map;
- terminal disposition;
- evaluator process report.

## 6. Evaluation sequence

1. Pin `process_quality_contract_version`.
2. Перевірити integrity evidence.
3. Відновити фактичний route з execution log.
4. Оцінити criteria без перегляду document-quality scores.
5. Обчислити raw score.
6. Визначити applicable failures і caps.
7. Застосувати найнижчий cap.
8. Записати evidence references для кожного criterion.
9. Зафіксувати uncertainty та non-scorable gaps.

## 7. Evidence rule

Жоден criterion не може отримати `met` лише на основі narrative summary. Потрібне посилання на immutable evidence: event sequence, artifact hash/version, manifest field або terminal record.

Відсутність evidence оцінюється як `not_met`, якщо criterion мав бути доказовим. Не дозволено припускати, що дія відбулася.

## 8. Output contract

Результат оцінювання має відповідати:

- `templates/PROCESS_EVALUATION_REPORT.template.json`;
- `schemas/process_evaluation_report.schema.json`;
- `PROCESS_FAILURE_CAPS.yaml`.

Обов'язкові поля: attempt identity, contract versions, criterion results, raw score, detected failures, applied cap, final score, evidence references, uncertainty, evaluator identity/time.

## 9. Gate

Process evaluation валідна, якщо:

- weights = 100;
- усі applicable criteria мають evidence/status;
- raw score відтворюваний;
- caps застосовані після raw score;
- lowest applicable cap використано;
- document scores не змішані з process score;
- contaminated run явно позначений.

## 10. Readiness

Цей контракт визначає evaluation semantics. Він не є production evaluator executable і не заявляє автоматичне обчислення без майбутнього runner-а.


---

# FILE: 022_PROCESS_FAILURE_CAPS.md

# 022. Process Failure Caps

## 1. Призначення

Failure cap обмежує максимальний process score, коли критична помилка робить високий raw score оманливим. Cap не є штрафом, який віднімається; після оцінювання застосовується найнижча межа серед усіх підтверджених failures.

## 2. Загальне правило

```text
final_process_score = min(raw_process_score, cap_1, cap_2, ...)
```

Failure застосовується лише за evidence. Якщо evidence недостатньо, evaluator фіксує uncertainty; cap не можна вигадувати.

## 3. Canonical cap registry

| Failure ID | Назва | Cap | Severity | Trigger |
|---|---|---:|---|---|
| `PF-001` | Wrong terminal route | 40 | critical | Terminal не дозволений RUN contract або суперечить фактичному blocking/completion state. |
| `PF-002` | Premature completion | 35 | critical | `T_COMPLETED` до закриття mandatory obligations/inputs. |
| `PF-003` | Invented critical fact | 25 | critical | Вигаданий факт вплинув на route, artifact або terminal. |
| `PF-004` | Missed correction or withdrawal | 30 | critical | Correction не змінила active state або stale fact лишився чинним. |
| `PF-005` | Missing dependent invalidation | 45 | major | Залежний artifact/approval не invalidated після зміни source fact. |
| `PF-006` | Stale artifact used after regeneration | 35 | critical | Terminal/evaluation спирається на superseded artifact version. |
| `PF-007` | Blind isolation breach | 50 | critical | Executor отримав evaluator-only expected result, score/cap або hidden route data. |
| `PF-008` | Previous-result contamination | 60 | major | Використано попередній output/diagnostic; run не є clean blind. |
| `PF-009` | Wrong Driver family forced | 45 | critical | Unsupported/hybrid або semantic package виконано step-bound способом чи навпаки без approved adapter. |
| `PF-010` | Mandatory route/obligation skipped | 55 | major | Пропущено mandatory node/obligation, але terminal випадково може бути правильним. |
| `PF-011` | Approval not version-bound | 65 | major | Approval не містить version/hash або перенесено на regenerated artifact. |
| `PF-012` | Execution log materially incomplete | 70 | major | Неможливо відновити route, corrections або terminal basis. |
| `PF-013` | Preflight bypassed | 60 | major | Execution почато без required integrity/binding/isolation gate. |
| `PF-014` | Cross-RUN evidence leakage | 30 | critical | Facts або hidden scenario іншого RUN вплинули на поточний attempt. |
| `PF-015` | Self-scoring influenced execution | 70 | major | Executor бачив/створював score до terminal і це могло змінити поведінку. |
| `PF-016` | Fabricated evidence/log | 0 | disqualifying | Evidence навмисно сфабрикований або immutable chain підроблений. |
| `PF-017` | Attempt identity collision/reuse | 50 | critical | Evidence кількох attempts змішано під одним identity. |
| `PF-018` | Non-blind run mislabeled as blind | 20 | disqualifying | Відоме contamination приховано, а run зареєстровано clean blind. |

## 4. Cap precedence

- застосовується найнижчий cap;
- caps не сумуються;
- усі detected failures все одно записуються;
- `PF-016` дає final score `0` і статус `invalid-evidence`;
- score contaminated run можна зберегти для діагностики, але він не входить у clean comparative matrix.

## 5. Evidence threshold

Failure status:

- `confirmed` — є пряме immutable evidence; cap застосовується;
- `probable` — непрямі сильні ознаки; cap не застосовується автоматично, потрібен reviewer decision;
- `not_confirmed` — cap не застосовується;
- `not_applicable` — failure неможливий у цьому RUN/profile.

Reviewer decision для `probable` має містити reason і evidence references.

## 6. False-cap protection

Заборонено застосовувати process cap через дефект документа, якщо процес виконав правильний route. Наприклад, слабка Jira оцінюється в Epic 08, а не через `PF-010`, якщо всі process obligations були пройдені.

Так само правильний документ не скасовує process failure: якщо модель вигадала critical fact, але випадково створила хороший Passport, `PF-003` застосовується.

## 7. RUN-sensitive interpretation

- `RUN_01`: основний акцент — clean route, no invention, correct completion.
- `RUN_02`: branch/obligation coverage; compound question не може приховати пропуск.
- `RUN_03`: завершення має бути `T_SCENARIO_EXHAUSTED`, а не штучний artifact package.
- `RUN_04`: corrections, invalidation, regeneration і approval versioning є blocking.
- `RUN_05`: `T_INPUT_BLOCKED` має бути чесним; вигадування missing input активує `PF-003`.

## 8. Registry governance

Зміна cap value або trigger є evaluation-contract change і вимагає:

- version bump registry;
- changelog;
- retroactive-score policy;
- explicit decision, чи переоцінюються historical attempts;
- synchronization із template/schema.

## 9. Machine-readable source

Канонічний machine-readable registry: `PROCESS_FAILURE_CAPS.yaml`.


---

# FILE: 023_DOCUMENT_QUALITY_CONTRACT_REGISTRY.md

# 023. Document Quality Contract Registry

**Version:** 0.8.0  
**Backlog:** BL-BENCH-023  
**Status:** implemented

## Purpose

This registry defines which evaluation contract applies to each generated artifact. Document quality is evaluated independently from process quality. A high-quality document cannot repair a failed process route, and a correct process does not guarantee a high-quality document.

## Canonical artifact types

| Artifact type | Contract ID | Primary role | Canonical/derived | Score range |
|---|---|---|---|---|
| Passport | `DQC-PASSPORT-1` | canonical analytical contract | canonical | 0–100 |
| Jira | `DQC-JIRA-1` | delivery and tracking view | derived | 0–100 |
| Implementation Prompt | `DQC-IMPL-PROMPT-1` | implementation handoff | derived | 0–100 |
| Manual QA | `DQC-MANUAL-QA-1` | executable human verification | derived | 0–100 |
| Automation | `DQC-AUTOMATION-1` | runner-oriented verification | derived | 0–100 |

## Contract selection

Before review, the evaluator must identify exactly one artifact type and one active contract version. Cross-applying criteria is prohibited. In particular:

- Jira is not evaluated as a Passport;
- Manual QA is not evaluated as an automation specification;
- Automation is not evaluated as an implementation prompt;
- document score does not include process-route correctness.

## Common evidence rule

Every awarded or deducted point must cite evidence from the final rendered artifact. External references may satisfy a criterion only when the active artifact contract explicitly permits references.

## Common score lifecycle

```text
raw criterion score
  → confirmed artifact findings
  → lowest applicable document cap
  → final artifact score
```

## Registry governance

A contract change requires a version bump when it changes required blocks, scoring weights, caps, or interpretation. Historical evaluations retain the contract version used at evaluation time.


---

# FILE: 024_ARTIFACT_SPECIFIC_RULES.md

# 024. Artifact-Specific Rules

**Version:** 0.8.0  
**Backlog:** BL-BENCH-024  
**Status:** implemented

## Passport — DQC-PASSPORT-1

Required outcomes:

- canonical behavior, scope and out-of-scope are explicit;
- inputs, outputs, validation, mapping and terminal behavior are testable;
- positive, negative, no-op and blocked behavior are represented where relevant;
- canonical test IDs and traceability are coherent;
- assumptions and open questions are visible;
- observability expectations are defined.

The Passport is the source of truth and must not rely on Jira for missing contract behavior.

## Jira — DQC-JIRA-1

Jira is a role-aware delivery view, not a duplicate of the Passport.

Mandatory rules:

- unit-test details are not mandatory in Jira;
- references to Passport are allowed and expected where useful;
- Jira must not repeat the full Passport;
- section order and physical block location are not scored;
- required blocks may appear anywhere if clearly identifiable;
- Jira must contain scope, delivery requirements, acceptance criteria, dependencies/blockers where applicable, and traceability to the canonical contract;
- acceptance criteria must be verifiable and must not introduce behavior absent from the Passport;
- lifecycle/delivery checklist is required only when the task lifecycle warrants it.

A Jira artifact is not penalized merely because detailed payloads, test fixtures or unit-test cases remain in the Passport or QA/Automation views.

## Implementation Prompt — DQC-IMPL-PROMPT-1

Required outcomes:

- references the canonical contract;
- defines implementation scope and out-of-scope;
- requires code discovery and preservation of existing architecture;
- prohibits invented paths/symbols unless verified;
- defines implementation, verification and documentation expectations;
- includes self-check and expected impact classification;
- does not add new business behavior.

## Manual QA — DQC-MANUAL-QA-1

Manual QA must be executable for the intended tester:

- concrete input or an explicit environment-resolved placeholder;
- concrete action/request;
- expected output or expected absence;
- pass/fail assertions;
- observability path for skip/no-op/error distinction;
- canonical test-ID traceability.

Tool-neutral and environment-neutral presentation is preferred unless the environment is confirmed.

## Automation — DQC-AUTOMATION-1

Automation must be runner-oriented:

- canonical scenario/test IDs;
- fixture/setup and cleanup contract;
- invocation contract;
- assertions and negative assertions;
- expected terminal/status behavior;
- deterministic data and evidence outputs;
- feasibility/status must be honest (`specified`, `implemented`, `blocked`, etc.).

Automation source specifications and generated run reports must remain separated.


---

# FILE: 025_DOCUMENT_FAILURE_CAPS.md

# 025. Document Failure Caps

**Version:** 0.8.0  
**Backlog:** BL-BENCH-025  
**Status:** implemented

## Application rule

Only confirmed failures supported by the final artifact may trigger a cap. If several caps apply, the lowest cap wins. Caps never increase a score.

## Common caps

| Failure ID | Applies to | Maximum score |
|---|---|---:|
| `DCF-001-WRONG-CONTRACT` | all | 0 |
| `DCF-002-FABRICATED-CRITICAL-FACT` | all | 20 |
| `DCF-003-MISSING-PRIMARY-PURPOSE` | all | 40 |
| `DCF-004-CONTRADICTS-CANONICAL-CONTRACT` | derived views | 30 |
| `DCF-005-NO-TRACEABILITY` | all | 60 |
| `DCF-006-UNRENDERABLE-OR-UNREADABLE` | all | 40 |

## Artifact-specific caps

| Failure ID | Artifact | Maximum score |
|---|---|---:|
| `DCF-PAS-001-NO-CANONICAL-BEHAVIOR` | Passport | 40 |
| `DCF-PAS-002-UNTESTABLE-CONTRACT` | Passport | 55 |
| `DCF-JIR-001-NO-ACCEPTANCE-CRITERIA` | Jira | 60 |
| `DCF-JIR-002-NOT-A-DELIVERY-VIEW` | Jira | 55 |
| `DCF-IMP-001-NO-IMPLEMENTATION-SCOPE` | Implementation Prompt | 50 |
| `DCF-IMP-002-INVENTED-ARCHITECTURE-AS-REQUIREMENT` | Implementation Prompt | 35 |
| `DCF-MQA-001-NOT-EXECUTABLE` | Manual QA | 50 |
| `DCF-MQA-002-NO-PASS-FAIL-ASSERTIONS` | Manual QA | 60 |
| `DCF-AUT-001-NO-RUNNER-CONTRACT` | Automation | 45 |
| `DCF-AUT-002-FALSE-IMPLEMENTED-CLAIM` | Automation | 25 |

## Explicit non-failures for Jira

The following do not trigger a deduction or cap by themselves:

- absence of unit-test implementation details;
- reference to Passport instead of duplicating it;
- required sections appearing in a different order;
- concise payload description when detailed payload is canonically referenced elsewhere.

## Cap evidence record

Every applied cap must include failure ID, evidence location, finding, confidence, and resulting maximum score.


---

# FILE: 026_FOCUSED_ARTIFACT_REVIEW.md

# 026. Focused Artifact Review

**Version:** 0.8.0  
**Backlog:** BL-BENCH-026  
**Status:** implemented

## Mandatory startup gate

Before evaluating a document, the evaluator must record:

1. exact artifact path/name;
2. artifact type;
3. active contract ID and version;
4. final rendered artifact under review;
5. relevant rules included;
6. non-relevant rules explicitly excluded;
7. allowed external references;
8. evaluation evidence sources.

## Review sequence

```text
identify artifact
→ bind contract
→ load only artifact-specific rules
→ inspect final rendered artifact
→ score criteria with evidence
→ confirm failures
→ apply lowest cap
→ issue final report
```

## Blocking conditions

Review is blocked when:

- artifact type is ambiguous;
- no active contract exists;
- evaluator is reviewing an intermediate source instead of the final rendered artifact;
- required referenced Passport/source is unavailable and the contract permits dependency on it;
- criteria from another artifact type are being applied.

## Anti-cross-contamination examples

- Do not require unit-test rows in Jira merely because Automation requires them.
- Do not require Jira to reproduce the full Passport.
- Do not award Manual QA executability points to a contract-only checklist.
- Do not evaluate document content using process-route failure caps.

## Re-evaluation rule

When criteria change, the old score is superseded, not silently overwritten. The new report records the new contract version and the reason for re-evaluation.


---

# FILE: 027_EVALUATION_REPORT_TEMPLATE.md

# 027. Evaluation Report Template

**Version:** 0.8.0  
**Backlog:** BL-BENCH-027  
**Status:** implemented

## Required report fields

- evaluation ID and timestamp;
- artifact identity and checksum;
- artifact type;
- active contract ID/version;
- evaluator identity/mode;
- focused-scope record;
- criterion-level raw scores and evidence;
- findings and severities;
- confirmed cap records;
- raw score, final score and readiness;
- uncertainty and unavailable evidence;
- supersedes/superseded-by references.

## Criterion record

```text
criterion_id
weight
score_awarded
status: passed | partial | failed | not_applicable | blocked
artifact_evidence
finding
severity
confidence
```

## Score rule

The raw weighted score is calculated before caps. The final score is the minimum of the raw score and all confirmed cap maxima. Not-applicable criteria must follow the active contract's normalization rule and cannot be removed informally.

## Handoff status

Allowed statuses:

- `evaluated`;
- `evaluated-with-notes`;
- `blocked-evidence`;
- `invalid-contract-binding`;
- `superseded`.


---

# FILE: 028_BENCHMARK_RESULT_REGISTRY.md

# 028. Benchmark Result Registry

**Version:** `1.0`  
**Backlog:** `BL-BENCH-028`  
**Status:** canonical contract

## 1. Purpose

The Benchmark Result Registry is the append-only source of truth for completed or dispositioned benchmark attempts. It stores execution identity, process evaluation, artifact evaluations, comparability status and provenance without silently overwriting historical results.

## 2. Canonical result identity

A result record is uniquely identified by:

```text
benchmark_suite_id
× test_case_id + test_case_version
× run_id + run_contract_version
× package_variant_id + package_version
× driver_id + driver_version
× attempt_id
× process_evaluation_contract_version
× document_evaluation_contract_versions
```

`attempt_id` is immutable and must match the launch, preflight, execution log and terminal disposition evidence.

## 3. Registry record classes

- `attempt_result` — one executed attempt with terminal disposition and scores.
- `supersession_event` — declares that a newer evaluation or rerun supersedes a prior active record.
- `comparability_event` — marks a record comparable, conditionally comparable or excluded.
- `recalculation_event` — records regeneration of derived matrices after registry change.

The registry is append-only. Existing records may not be edited in place except for cryptographically equivalent storage migration with an audit entry.

## 4. Required result fields

Every `attempt_result` must contain:

- stable identity fields and versions;
- timestamps and evaluator identity/class;
- terminal disposition and blind-isolation status;
- process raw score, applied caps and final process score;
- one document evaluation reference per artifact actually produced;
- aggregate document score with explicit aggregation rule;
- overall score only when an approved overall formula exists;
- evidence references and checksums;
- comparability status and exclusion reasons;
- lifecycle status: `active`, `superseded`, `invalidated`, `quarantined`.

Missing artifact evaluations are not silently treated as zero. They must be represented as `not_produced`, `not_applicable`, `missing_blocking` or `pending_evaluation`.

## 5. Score separation

The registry preserves three independent layers:

```text
process_final_score
artifact_final_scores
approved_aggregate_scores
```

Process and document scores must remain independently inspectable. An overall score may not erase either component.

## 6. Registry files

Canonical machine-readable storage:

- `BENCHMARK_RESULT_REGISTRY.jsonl` — append-only event ledger;
- `templates/BENCHMARK_RESULT_RECORD.template.json` — reusable record shape;
- `schemas/benchmark_result_record.schema.json` — structural validation;
- `RESULT_REGISTRY_POLICY.yaml` — lifecycle and comparability policy.

The release package contains templates and policy, not fabricated benchmark results.

## 7. Gates

A record may become `active` only if:

1. identity and versions are complete;
2. terminal disposition evidence exists;
3. process evaluation validates against its active contract;
4. each claimed artifact evaluation validates against its bound artifact contract;
5. checksums resolve;
6. blind/contamination status is explicit;
7. comparability decision is recorded;
8. no existing active record has the same immutable `attempt_id`.

## 8. Prohibited behavior

- overwriting an older score after criteria change;
- merging several attempts into one record;
- comparing records with unknown contract versions;
- treating a contaminated run as clean;
- using latest file modification time as result identity;
- storing only the final number without evidence and cap history.


---

# FILE: 029_COMPARATIVE_MATRIX.md

# 029. Comparative Matrix

**Version:** `1.0`  
**Backlog:** `BL-BENCH-029`  
**Status:** canonical contract

## 1. Purpose

The Comparative Matrix is a deterministic derived view over active comparable registry records. It is not a second source of truth and must be reproducible from the Benchmark Result Registry.

## 2. Canonical row key

Default row granularity:

```text
test_case_id × run_id × package_variant_id × package_version × attempt_id
```

Views may group by variant or test case, but grouped values must preserve drill-down to source records.

## 3. Required columns

- test case and version;
- RUN and contract version;
- package variant and package version;
- Driver and version;
- attempt and execution timestamp;
- terminal disposition;
- blind-isolation/contamination status;
- process raw and final scores;
- Passport, Jira, Implementation Prompt, Manual QA and Automation scores with `N/A` states;
- aggregate document score and formula version;
- overall score and formula version, if approved;
- applied process/document caps;
- comparability status;
- registry record ID and evidence links.

## 4. Missing-data semantics

The matrix must distinguish:

- `N/A` — artifact not applicable by contract;
- `NP` — artifact correctly not produced for the terminal path;
- `PE` — pending evaluation;
- `MB` — missing blocking artifact;
- `EX` — excluded from comparison;
- numeric score — completed evaluation.

No missing state may be converted to zero unless an active scoring contract explicitly requires that conversion.

## 5. Derived views

The package defines these standard views:

1. `attempt_detail` — one row per attempt;
2. `variant_summary` — comparable attempts grouped by package variant;
3. `run_summary` — grouped by RUN scenario;
4. `artifact_summary` — grouped by artifact type;
5. `stability_summary` — variance across repeated attempts;
6. `coverage_summary` — completed combinations against planned matrix.

## 6. Aggregation rules

- arithmetic mean is allowed only over homogeneous comparable records;
- sample count must always be shown;
- variance/dispersion must be shown when repeated attempts exist;
- capped and uncapped values must not be mixed;
- records from different evaluation contract versions require either normalized migration or separate cohorts;
- rank ordering is prohibited when comparability status is not `comparable`.

## 7. Regeneration

Every matrix carries:

- `matrix_build_id`;
- registry high-water mark/event hash;
- active policy versions;
- filters;
- generated timestamp;
- included and excluded record counts.

Any registry append that changes active records triggers a new build; older matrices remain historical derived artifacts.

## 8. Templates

- `templates/COMPARATIVE_MATRIX.template.csv` — standard columns;
- `templates/COMPARATIVE_MATRIX_BUILD.template.json` — reproducibility metadata;
- `schemas/comparative_matrix_build.schema.json` — metadata validation.


---

# FILE: 030_RESULT_UPDATE_RULES.md

# 030. Result Update Rules

**Version:** `1.0`  
**Backlog:** `BL-BENCH-030`  
**Status:** canonical contract

## 1. Core rule

Benchmark results are immutable observations. Corrections create new events; they never silently rewrite history.

## 2. Update types

### 2.1 New attempt

A rerun receives a new `attempt_id`, even when all other inputs are identical.

### 2.2 Re-evaluation

When only evaluation criteria or evaluator conclusions change, create a new result record referencing the same execution evidence and a new evaluation ID. The new record may supersede the previous evaluation but must not pretend to be a new execution.

### 2.3 Evidence correction

If evidence metadata was wrong, append an `evidence_correction` event with old/new values, reason, authority and checksum. Material changes require re-evaluation.

### 2.4 Invalidation

Use `invalidated` when the attempt cannot support a trustworthy score, for example checksum failure, cross-RUN leakage or fabricated evidence. Preserve the invalid record and reason.

### 2.5 Quarantine

Use `quarantined` for suspected contamination or unresolved comparability. Quarantined records are excluded from standard matrices until resolved.

## 3. Supersession contract

A supersession event must include:

- predecessor record ID;
- successor record ID;
- supersession reason;
- change class: `rerun`, `re_evaluation`, `contract_migration`, `evidence_correction`;
- affected score dimensions;
- authority;
- timestamp;
- whether historical matrices require recalculation.

Only one active successor is allowed per supersession chain and cohort. Branches require explicit conflict resolution rather than silent selection.

## 4. Evaluation contract changes

When scoring rules change:

1. assign a new contract version;
2. do not mutate historical scores;
3. decide whether old evidence is sufficient for re-evaluation;
4. if sufficient, create re-evaluation records;
5. if insufficient, keep the old cohort separate or rerun;
6. rebuild matrices with explicit cohort/version filters.

## 5. Recalculation triggers

Rebuild affected derived views when:

- an active result is added, superseded, invalidated or unquarantined;
- comparability status changes;
- aggregation formula changes;
- evaluation contract migration creates new active scores;
- registry integrity repair changes a referenced record.

## 6. No-op updates

Formatting-only changes to a derived matrix do not create registry events, but do create a new matrix build metadata record if the output artifact changes.

## 7. Audit gates

An update fails if:

- predecessor is missing;
- successor identity is ambiguous;
- reason or authority is absent;
- the old record was overwritten;
- recalculation impact was not evaluated;
- a changed score lacks a new evaluation contract/version binding.


---

# FILE: 031_CROSS_VARIANT_COMPARISON.md

# 031. Cross-Variant Comparison

**Version:** `1.0`  
**Backlog:** `BL-BENCH-031`  
**Status:** canonical contract

## 1. Purpose

Cross-variant comparison determines how `PV-YAML`, `PV-STRUCTURED`, `PV-HISTORICAL` and `PV-DIRECT` differ under equivalent benchmark conditions without hiding lineage, Driver or contamination differences.

## 2. Comparable cohort gate

Two records may be compared directly only when all mandatory cohort dimensions match or have an approved normalization:

- same test case and version;
- same RUN and RUN contract version;
- equivalent executor model/configuration and tool permissions;
- same evaluation contract versions;
- clean blind-isolation status;
- equivalent source evidence cutoff;
- compatible terminal path;
- no unresolved contamination;
- package variant identity and lineage verified.

Otherwise comparison is `conditional` or `excluded`, with reasons.

## 3. Standard comparison dimensions

### 3.1 Process determinism

Measured from route correctness, required obligations, corrections, terminal disposition and repeated-attempt variance.

### 3.2 Document quality depth

Uses artifact-specific final scores and coverage; does not substitute generic document length.

### 3.3 Executability

Assesses whether generated instructions/QA/automation are actionable under their artifact contracts.

### 3.4 Correction resilience

Measures invalidation, regeneration and version-bound approval handling, especially in `RUN_04`.

### 3.5 Failure honesty

Measures correct blocked/exhausted/no-go behavior without fabricated completion.

### 3.6 Portability

Assesses dependency on special runtime/tooling, package readability and transferability.

### 3.7 Resource footprint

Records package bytes, file count, YAML node count where applicable, instruction length and execution token/time metrics when reliably available. Resource metrics are descriptive unless an approved scoring contract assigns weight.

### 3.8 Stability

Uses repeated attempts to calculate score variance, terminal consistency and artifact-set consistency.

## 4. Fairness rules

- compare the same intended capability, not merely same filenames;
- do not penalize a variant for intentionally absent internal Ordo structure when its contract forbids it;
- do not reward hidden leakage or evaluator hints;
- do not merge scores across different Driver families without showing Driver as a dimension;
- report sample sizes and uncertainty;
- retain process and document dimensions separately;
- do not infer causality from one attempt.

## 5. Comparison output

A cross-variant report contains:

- cohort definition and exclusions;
- per-attempt matrix;
- per-variant aggregates and dispersion;
- dimension-by-dimension findings;
- evidence references;
- limitations and uncertainty;
- no unsupported “winner” conclusion.

## 6. Winner declaration gate

A winner may be declared only if:

- the comparison objective and primary metric were fixed before examining results;
- cohorts are comparable;
- minimum sample size policy is satisfied;
- no critical contamination exists;
- uncertainty does not reverse the conclusion;
- all ties and trade-offs are disclosed.

Without those conditions, output must say `insufficient evidence for a single winner`.


---

# FILE: 032_CAUSAL_DIAGNOSTIC_PROMPT.md

# 032. Causal Diagnostic Prompt

**Backlog:** `BL-BENCH-032`  
**Status:** implemented  
**Version:** `1.0.0`

## Purpose

Provide a deterministic investigation prompt after a weak, inconsistent, capped, or surprising benchmark result. The prompt collects an executor explanation without treating that explanation as ground truth.

## Trigger conditions

Open a diagnostic case when at least one condition is true:

- a process or document score falls below the configured threshold;
- a failure cap is applied;
- expected and observed terminal routes differ;
- two package variants diverge materially on the same comparable cohort;
- a correction, invalidation, or approval is missing or ambiguous;
- an artifact contains behavior not traceable to the active contract;
- an evaluator flags `needs-causal-investigation`.

## Diagnostic isolation

Diagnostics start only after execution and initial evaluation are frozen. The executor must not receive hidden scoring rules before the run ends. Diagnostic responses are stored separately from original execution evidence and cannot retroactively alter the execution log.

## Canonical prompt blocks

The diagnostic request must bind:

1. `diagnostic_case_id`;
2. affected `result_record_id`, `attempt_id`, test case, RUN and package variant;
3. exact artifact or process finding under investigation;
4. frozen evidence snapshot identifiers;
5. requested provenance questions;
6. response schema and uncertainty rule.

## Mandatory questions to the executor

The executor is asked to identify, with exact references where possible:

- which node, obligation, instruction section or semantic intent produced the result;
- which prompt, template, source artifact and contract versions were active;
- which facts were available at the decision point;
- which facts were unavailable, hidden, superseded, corrected or ignored;
- why the chosen route or content appeared valid at that time;
- which gate or validator was expected to detect the defect;
- whether the defect originated before generation, during generation, during rendering or during evaluation;
- what minimal change would prevent recurrence;
- confidence level and unresolved alternatives.

## Required response discipline

The executor must separate:

- `observed_from_available_context`;
- `inferred_explanation`;
- `uncertain_or_unavailable`;
- `proposed_fix`.

Unsupported certainty is forbidden. A response without evidence pointers is usable as a hypothesis only.

## Prompt output

Use `templates/CAUSAL_DIAGNOSTIC_REQUEST.template.json` and validate with `schemas/causal_diagnostic_request.schema.json`.

## Gate

The task is complete when the prompt is reproducible, binds frozen evidence, asks provenance questions, records uncertainty, and cannot modify the original execution record.


---

# FILE: 033_DIAGNOSTIC_EVIDENCE_CONTRACT.md

# 033. Diagnostic Evidence Contract

**Backlog:** `BL-BENCH-033`  
**Status:** implemented  
**Version:** `1.0.0`

## Purpose

Define how diagnostic claims are corroborated. Executor testimony is a causal hypothesis and evidence of model reasoning, not proof that a component caused the defect.

## Evidence hierarchy

Highest-trust evidence is direct and immutable:

1. checksum-bound source package and manifests;
2. append-only execution log and terminal disposition;
3. exact generated artifact versions;
4. active prompt, template, contract, Driver and validator versions;
5. evaluator reports and applied caps;
6. deterministic structural/semantic diffs;
7. executor diagnostic response;
8. analyst inference without direct evidence.

Lower-trust evidence cannot override contradictory higher-trust evidence without an explicit conflict record.

## Diagnostic claim model

Every claim contains:

- stable `claim_id`;
- claim text;
- proposed root-cause class;
- supporting evidence pointers;
- contradicting evidence pointers;
- evidence coverage status;
- confidence;
- corroboration status;
- reviewer decision.

Allowed corroboration statuses:

- `confirmed`;
- `probable`;
- `plausible`;
- `unsupported`;
- `contradicted`;
- `insufficient-evidence`.

Only `confirmed` and `probable` claims may drive an automatic improvement proposal. `plausible` claims require human review. Unsupported or contradicted claims cannot be used as closure evidence.

## Required triangulation

A causal claim should normally connect at least two independent evidence families, for example:

- executor explanation + execution log;
- artifact defect + template omission;
- wrong route + Driver binding/transition evidence;
- missed defect + validator/gate configuration;
- variant divergence + lineage and compiler records.

Single-source diagnosis must be marked `single-source` and cannot be `confirmed` unless the source is a deterministic proof artifact.

## Counterfactual test

For a root-cause claim, record the counterfactual:

> If the proposed component were corrected while other frozen inputs remained unchanged, would the defect reasonably disappear?

The answer is `yes`, `no`, or `unknown`, with evidence. A `no` result rejects the proposed primary cause.

## Diagnostic package

A completed case contains:

- request;
- executor response;
- evidence index;
- claim assessment;
- root-cause decision;
- unresolved alternatives;
- recommended patch target;
- regression implications.

Use `templates/DIAGNOSTIC_CASE.template.json` and `schemas/diagnostic_case.schema.json`.

## Gate

Diagnosis is ready only if evidence is frozen, claims are traceable, contradictions are visible, uncertainty is retained, and the primary cause is not based solely on executor self-report.


---

# FILE: 034_ROOT_CAUSE_CLASSIFICATION.md

# 034. Root Cause Classification

**Backlog:** `BL-BENCH-034`  
**Status:** implemented  
**Version:** `1.0.0`

## Purpose

Provide a stable taxonomy for causal findings and select the narrowest responsible component for a future patch.

## Canonical root-cause classes

| Code | Class | Typical evidence |
|---|---|---|
| `RC-PLAYBOOK-NODE` | Playbook node or transition | wrong/missing node, branch, obligation or terminal transition |
| `RC-PROMPT` | Prompt/instruction defect | prompt omits, distorts or contradicts an active contract |
| `RC-TEMPLATE` | Template defect | required field/section/source mapping absent or ambiguous |
| `RC-DRIVER` | Driver behavior or binding | wrong Driver, disclosure timing, transition or correction handling |
| `RC-RUNTIME-CONTRACT` | Runtime/launcher/logging contract | preflight, logging, version binding or terminal disposition defect |
| `RC-SOURCE-EVIDENCE` | Source or fixture defect | missing, stale, contradictory or contaminated source evidence |
| `RC-COMPILER-LINEAGE` | Package compiler or lineage defect | semantic loss, contamination or wrong source lineage |
| `RC-RENDERING` | Rendering/materialization defect | canonical state correct but final rendered artifact wrong |
| `RC-VALIDATOR-GATE` | Validator or gate defect | defect should have been blocked but rule/check was absent or misbound |
| `RC-EVALUATOR-CONTRACT` | Evaluation contract defect | wrong artifact contract, cap, criterion or scoring interpretation |
| `RC-PACKAGING` | Package assembly defect | missing/wrong file, stale all-in-one, checksum or manifest issue |
| `RC-RESULT-REGISTRY` | Registry/comparison defect | wrong identity, supersession, cohort or matrix construction |
| `RC-HUMAN-DECISION` | Explicit human decision/override | accepted exception or incorrect manual decision with evidence |
| `RC-MULTI-FACTOR` | Multiple necessary causes | no single cause explains the failure; contributing causes are explicit |
| `RC-UNKNOWN` | Insufficient evidence | investigation cannot support a responsible component |

## Primary and contributing causes

Each diagnostic case has at most one `primary_root_cause`. Additional necessary or amplifying factors are `contributing_causes`. `RC-MULTI-FACTOR` is used only when removing one factor alone would not prevent the defect.

## Classification rules

1. Classify the earliest verified point where the defect became inevitable.
2. Do not classify the visible artifact alone when an upstream contract caused it.
3. Do not blame the executor when the active prompt/template mandated the faulty behavior.
4. Use `RC-VALIDATOR-GATE` as primary only when generation may be imperfect by design but the missing gate is the contractual prevention mechanism.
5. Use `RC-EVALUATOR-CONTRACT` when the artifact is acceptable under its real role but was scored with unsuitable criteria.
6. Use `RC-UNKNOWN` rather than inventing causality.

## Severity and recurrence dimensions

Root-cause records also classify:

- impact: `critical | major | moderate | minor`;
- recurrence: `systemic | variant-specific | run-specific | one-off | unknown`;
- affected layer: `authoring | compilation | execution | evaluation | registry | handoff`;
- patch locality: exact component/file/node IDs where known.

## Machine-readable registry

`ROOT_CAUSE_CLASSIFICATION.yaml` is the canonical taxonomy registry. Changes require versioning and a design decision if they alter historical interpretation.

## Gate

A classification is complete only when the chosen class is evidence-backed, alternatives are recorded, primary/contributing roles are explicit, and the patch target is no broader than the evidence supports.


---

# FILE: 035_IMPROVEMENT_PATCH_WORKFLOW.md

# 035 — Improvement Patch Workflow

## Status

Canonical contract for `BL-BENCH-035`.

## Purpose

Convert a confirmed or probable diagnostic finding into a bounded, versioned and reversible improvement without rewriting unrelated benchmark assets.

## Entry criteria

An improvement patch may start only when:

1. a diagnostic case exists;
2. root-cause confidence is `confirmed` or `probable`;
3. the target component is identified;
4. baseline package, result cohort and evaluation contracts are frozen;
5. patch scope and regression scope are approved.

Unsupported or merely plausible hypotheses may create backlog items, but may not mutate the benchmark baseline.

## Patch identity

Every patch receives an immutable `patch_id` and records:

- source diagnostic case;
- primary and contributing root causes;
- target component and version;
- exact files, sections, nodes or rules allowed to change;
- expected behavioral effect;
- prohibited side effects;
- rollback source;
- selected regression scenarios;
- acceptance and stop criteria.

## Workflow

1. Freeze the current baseline and checksums.
2. Create a patch proposal.
3. Define an explicit change allowlist.
4. Apply the minimum sufficient change.
5. Produce structural and semantic diffs.
6. Reject unexplained out-of-scope changes.
7. Rebuild only derived artifacts whose lineage requires regeneration.
8. Run targeted regression scenarios.
9. Run invariant and contamination checks.
10. Compare against the frozen baseline.
11. Accept, reject or roll back the patch.
12. Register the new package version and supersession relation.

## Required evidence

- `IMPROVEMENT_PATCH_RECORD.json`;
- before/after checksums;
- structural and semantic diff;
- regression selection record;
- regression results;
- acceptance or rollback decision;
- updated lineage manifest.

## Guardrails

- A patch must not silently change RUN semantics, scoring contracts, Driver behavior and package content in one undifferentiated mutation.
- Benchmark data must never be edited merely to make a package look better.
- Historical results remain immutable.
- Failed patches remain auditable.
- A patch that changes an evaluation contract creates a new comparison cohort.

## Terminal dispositions

- `PATCH_ACCEPTED`;
- `PATCH_REJECTED`;
- `PATCH_ROLLED_BACK`;
- `PATCH_BLOCKED_EVIDENCE`.

## Completion evidence

This contract, the patch record template and the cumulative Ordo nodes complete `BL-BENCH-035`.


---

# FILE: 036_REGRESSION_SCENARIO_SELECTION.md

# 036 — Regression Scenario Selection

## Status

Canonical contract for `BL-BENCH-036`.

## Purpose

Select the smallest sufficient scenario set that proves the intended fix and protects adjacent behavior.

## Inputs

- confirmed diagnostic case;
- patch scope;
- changed component type;
- dependency and lineage map;
- historical failures;
- canonical RUN and package-variant registries.

## Selection layers

Every regression set contains, where applicable:

1. **Trigger scenario** — reproduces the original defect.
2. **Direct-neighbor scenarios** — exercise the same node, obligation, template, Driver branch or validator.
3. **Cross-variant scenarios** — detect leakage or inconsistent derived packages.
4. **Correction/terminal scenarios** — protect correction, blocking and terminal behavior.
5. **Sentinel scenarios** — stable unaffected cases that detect broad unintended changes.

## Deterministic rules

- Node or route patch: include all RUNs that can reach the changed node plus one unreachable sentinel.
- Prompt or template patch: include every artifact type rendered by it and at least one unaffected artifact type.
- Driver patch: include every RUN behavior class and every bound package family.
- Validator/evaluator patch: include known pass, known fail and boundary cases.
- Package compiler patch: include source/derived parity checks and direct-adaptation contamination checks.
- Scoring-contract patch: create a new evaluation cohort; do not compare raw scores across incompatible contracts.

## Exclusions

A scenario may be excluded only with an explicit reason and evidence that the changed component cannot affect it.

## Regression selection record

The record contains:

- patch ID;
- selected scenario IDs;
- selection reason per scenario;
- expected invariant;
- baseline result reference;
- exclusion list and rationale;
- required variants and repetitions;
- pass/fail threshold.

## Coverage gate

The set fails selection if it lacks:

- the original trigger;
- at least one adjacent-path case;
- at least one unaffected sentinel;
- any mandatory correction or terminal case implied by the patch;
- required cross-variant coverage.

## Completion evidence

This contract and `REGRESSION_SELECTION.template.yaml` complete `BL-BENCH-036`.


---

# FILE: 037_FIVE_CYCLE_IMPROVEMENT_MODE.md

# 037 — Five-Cycle Improvement Mode

## Status

Canonical contract for `BL-BENCH-037`.

## Purpose

Provide a bounded iterative mode for difficult defects while preventing endless tuning, benchmark overfitting and hidden baseline drift.

## Cycle limit

A campaign may execute at most five accepted or rejected patch attempts against one frozen diagnostic objective.

## Cycle structure

Each cycle performs:

1. restate the active hypothesis;
2. choose one bounded patch target;
3. apply one scoped patch;
4. verify the change scope;
5. execute the fixed regression set;
6. compare to the same frozen baseline;
7. classify outcome;
8. decide stop, continue or rollback.

## Mandatory stop conditions

Stop before cycle five when:

- acceptance criteria are met;
- the original defect is no longer reproducible and no protected regression degrades;
- evidence contradicts the active root-cause hypothesis;
- two consecutive cycles produce no measurable improvement;
- a severe new regression appears;
- scope would need to expand beyond the approved campaign;
- evaluation or scenario contracts would need uncontrolled mutation.

## Cycle outcomes

- `IMPROVED_ACCEPTABLE`;
- `IMPROVED_INSUFFICIENT`;
- `NO_CHANGE`;
- `REGRESSED`;
- `HYPOTHESIS_CONTRADICTED`;
- `BLOCKED`.

## Anti-overfitting rules

- The trigger scenario may not be rewritten during the campaign.
- Hidden evaluator evidence remains hidden.
- Regression membership is frozen unless a newly discovered dependency is formally added with rationale.
- Scoring weights may not be tuned to make the patch appear successful.
- Each cycle may change only one primary component class unless a multi-factor diagnosis explicitly requires more.

## End-of-campaign decision

After cycle five, the campaign must terminate as:

- `CAMPAIGN_ACCEPTED`;
- `CAMPAIGN_PARTIALLY_ACCEPTED`;
- `CAMPAIGN_REJECTED`;
- `CAMPAIGN_ESCALATED`.

No sixth cycle is allowed under the same campaign ID.

## Completion evidence

This contract and the campaign template complete `BL-BENCH-037`.


---

# FILE: 038_STABLE_BENCHMARK_EVOLUTION.md

# 038 — Stable Benchmark Evolution

## Status

Canonical contract for `BL-BENCH-038`.

## Purpose

Allow the benchmark system to evolve without destroying historical comparability or mixing unrelated changes.

## Change classes

Every release classifies each mutation as one of:

- playbook/runtime behavior;
- RUN scenario contract;
- package compiler or variant lineage;
- Driver contract;
- process evaluation contract;
- document evaluation contract;
- test-case evidence;
- registry/matrix policy;
- tooling or packaging only.

## Controlled evolution rules

1. One release must declare a primary change class.
2. Secondary changes require explicit dependency justification.
3. Scenario, scoring and Driver changes must not be bundled silently.
4. Contract changes create new versioned cohorts.
5. Historical records remain readable under their original contracts.
6. Migration is explicit; reinterpretation in place is forbidden.
7. Benchmark owner approval is required for changes affecting comparability.
8. Release notes must state which comparisons remain valid, become conditional or are invalidated.

## Stability gates

A release is stable only when:

- checksums and lineage are complete;
- changed contracts are version-bumped;
- regression and sentinel scenarios pass;
- no unexplained out-of-scope changes exist;
- comparison-cohort impact is declared;
- rollback package exists;
- prior versions remain accessible;
- result registry migration, if any, is append-only.

## Compatibility dispositions

- `FULLY_COMPARABLE`;
- `COMPARABLE_WITH_FILTERS`;
- `NEW_COHORT_REQUIRED`;
- `HISTORICAL_ONLY`;
- `INVALID_RELEASE`.

## Release evidence

- change classification;
- affected contracts and versions;
- migration note;
- cohort impact report;
- regression evidence;
- rollback reference;
- updated changelog and checksums.

## Relationship to BL-BENCH-041

This contract requires scoped changes and out-of-scope diff evidence but does not yet implement the dedicated enforceable YAML patch verifier. `BL-BENCH-041` remains open.

## Completion evidence

This contract and evolution policy registry complete `BL-BENCH-038`.


---

# 039 — Benchmark Evidence Package

## Purpose

Define the canonical, reproducible evidence bundle for a benchmark release, campaign, attempt, evaluation, diagnostic case, or improvement cycle.

## Core rule

A status claim is valid only when its evidence is materialized, checksum-bound, version-identified, and linked through a manifest. Chat history alone is not authoritative evidence.

## Required package layers

1. **Identity** — package ID, playbook version, creation timestamp, authority profile, scope and compatibility cohort.
2. **Source** — test case, RUN contract, package variant, Driver binding, prompts, templates, schemas and source checksums.
3. **Execution** — launch manifest, preflight report, append-only execution log, produced artifacts and terminal disposition.
4. **Evaluation** — process evaluation, artifact evaluations, failure caps, contract versions and focused-review evidence.
5. **Results** — immutable registry record, comparison eligibility, matrix high-water mark and supersession state.
6. **Diagnostics and improvement** — diagnostic cases, root-cause decision, patch records, diffs, regression selection and campaign outcome when applicable.
7. **Release integrity** — inventory, SHA-256 manifest, validation report, known limitations and unresolved backlog.

## Evidence states

- `PRESENT_VERIFIED`
- `PRESENT_UNVERIFIED`
- `NOT_APPLICABLE`
- `EXPECTED_MISSING`
- `QUARANTINED`
- `SUPERSEDED`

`EXPECTED_MISSING` blocks a complete evidence-package claim.

## Mandatory controls

- Every file has a stable relative path and SHA-256.
- Every derived artifact identifies its source versions.
- Hidden/evaluator-only material remains access-controlled in the package layout.
- No evidence file may be silently replaced; replacements create a new package version.
- Manifest and inventory must agree exactly.
- Known limitations and open backlog items are explicit.

## Canonical outputs

- `EVIDENCE_PACKAGE_POLICY.yaml`
- `templates/EVIDENCE_PACKAGE_MANIFEST.template.yaml`
- `schemas/evidence_package_manifest.schema.json`
- `EVIDENCE_PACKAGE_INDEX.md`

## Completion criteria

`BL-BENCH-039` is complete when the package contract, machine-readable policy, manifest template, schema, inventory rules and integrity checks exist and pass self-validation.


---

# 040 — Transfer / Handoff Package

## Purpose

Provide a deterministic continuation package for another chat, model, analyst, or runtime without relying on hidden conversational memory.

## Handoff invariant

The receiver must be able to determine: what exists, what is authoritative, what is complete, what remains open, what must not be changed, and what the next safe action is.

## Required contents

1. `HANDOFF_README.md` — reading order and package map.
2. `CURRENT_STATE.md` — current version, completed epics, readiness, active constraints and known limitations.
3. `BACKLOG.md` — authoritative status ledger.
4. `NEXT_ACTION.md` — one bounded recommended next action.
5. `TRANSFER_PROMPT.md` — reusable receiver prompt with authority and no-downgrade rules.
6. Source-of-truth playbook files, Ordo source, registries, templates and schemas.
7. Validation report, checksum manifest and package inventory.
8. Open-risk register including unresolved `BL-BENCH-041`.

## Receiver preflight

The receiver must:

- verify all checksums;
- confirm the received version is not older than the active baseline;
- read `HANDOFF_README.md`, `CURRENT_STATE.md`, `BACKLOG.md` and `NEXT_ACTION.md` in that order;
- preserve immutable IDs and historical completion records;
- not mark open work complete without materialized evidence and validation;
- stop and report no-change on integrity failure.

## Handoff status

- `READY_FOR_TRANSFER`
- `READY_WITH_OPEN_WORK`
- `BLOCKED_INTEGRITY`
- `BLOCKED_MISSING_AUTHORITY`
- `HISTORICAL_ONLY`

This release is `READY_WITH_OPEN_WORK` because Epic 01–12 are complete while `BL-BENCH-041` remains open.

## Canonical outputs

- `HANDOFF_POLICY.yaml`
- `handoff/HANDOFF_README.md`
- `handoff/CURRENT_STATE.md`
- `handoff/NEXT_ACTION.md`
- `handoff/TRANSFER_PROMPT.md`
- `templates/HANDOFF_MANIFEST.template.yaml`
- `schemas/handoff_manifest.schema.json`

## Completion criteria

`BL-BENCH-040` is complete when the handoff contract, receiver preflight, manifest, reading order, transfer prompt and integrity evidence exist and pass self-validation.


## v0.13.0 — BL-BENCH-041 closure
Scoped YAML patch verification is enforceable through node allowlists, canonical structural hashes, semantic diffs, out-of-scope rejection and persisted proof reports. Backlog complete: 41/41.


# BL-BENCH-042 — Mandatory Language Package and ARF Runtime Integration

This OPEN improvement requires future playbook creation, patching and validation to bind to the current language package and execute the applicable ARF meta-playbook with captured state, package validators, regression evidence and release gates. Reusing only the principles is insufficient. Missing, corrupt or incompatible package/ARF input must fail closed with rollback/no-change.


# BL-BENCH-042 — ARF Runtime Integration

See `042_LANGUAGE_PACKAGE_ARF_RUNTIME_INTEGRATION.md` and `tools/run_arf_meta_runtime.py`. ARF evidence is mandatory for release.


# 043 External/Internal Validation Contract Alignment Gate

# BL-BENCH-043 — External/Internal Validation Contract Alignment Gate

## Status

**DONE**

## Contract

Every document-generation node and template MUST bind an authoritative external validation contract by immutable contract ID, version and SHA-256. Node-local rules are accepted only after rule-level structural and semantic equivalence is proven.

The gate is fail-closed for missing, weaker, contradictory, stale, wrongly bound or silently overridden rules. Extra internal rules are permitted only when explicitly classified as non-conflicting strengthening rules; extra blocking rules require approval because they may change externally valid outputs into internal failures.

## Required flow

1. Freeze external contract identity and checksum.
2. Extract internal node/template rules.
3. Normalize both rule sets.
4. Map rules by canonical `rule_id`.
5. Compare requirement, condition, severity, blocking behavior, exceptions, lineage and terminal semantics.
6. Block the node when any required rule is absent or semantically weaker/conflicting/stale.
7. Regenerate internal rules from the frozen external contract.
8. Re-run the gate and accept only on zero unresolved blocking differences.
9. Seal an alignment report and bind it to the release gate.

## Implementation

- Policy: `VALIDATION_ALIGNMENT_POLICY.yaml`
- Validator/regenerator: `tools/validate_contract_alignment.py`
- Declaration template: `templates/VALIDATION_ALIGNMENT_BINDING.template.yaml`
- Report schema: `schemas/validation_alignment_report.schema.json`
- Positive, negative, boundary and regeneration fixtures: `fixtures/validation_alignment/`
- Acceptance report: `reports/VALIDATION_ALIGNMENT_ACCEPTANCE_TESTS.json`

## Release gate

Release is blocked when any document-generation node lacks a current PASS report whose external contract checksum, internal rules checksum and node/template identity match the release contents.

## Acceptance evidence

The implementation rejects missing, weakened, contradictory and stale rules; proves equivalent positive/negative/boundary verdicts; regenerates internal rules from the authoritative contract; and passes all acceptance tests.


---

# BL-BENCH-044 — Benchmark Evidence and Run Acceptance Governance

**Status:** OPEN  
**Priority:** High  
**Release introduced:** 1.0.0-alpha.7  
**Source document SHA-256:** `77f984d31c856dfb012478caa0b2b1fcfcc7b607b94a06adf68a3cc3c3c0f039`

## Problem

The benchmark package needs a canonical, enforceable operating process for:

- evidence-base structure;
- candidate versus approved Playbook packages;
- neutral launch prompts;
- per-run unpacking and factual audit;
- independent Process / Documents / Final scoring;
- explicit user confirmation before canonical inclusion;
- confirmed, rejected, quarantined and superseded revisions;
- comparative scoreboard updates;
- versioned evidence-base releases, manifests and checksums.

A validator PASS, a generated file, or an execution summary must never automatically promote a Playbook or run into canonical evidence.

## Authoritative description

The complete task description is the attached owner-provided source document:

`backlog_attachments/BL-BENCH-044/BENCHMARK_EVIDENCE_AND_RUN_ACCEPTANCE_PROCESS_UA.md`

The attachment is incorporated into this task as its full normative description. This summary does not narrow or replace it.

## Required implementation

1. Materialize the canonical evidence-base directory model from the source document.
2. Add working/canonical separation and explicit states such as `RECEIVED_NOT_CONFIRMED`, confirmed, rejected, quarantined and superseded.
3. Require actual ZIP/terminal-report inspection, manifests and checksum verification before scoring.
4. Produce exactly three principal scores: Process Quality, Document Quality and Final Quality.
5. Require explicit user confirmation before moving any run or Playbook to canonical evidence.
6. Maintain immutable revisions rather than silent overwrites.
7. Update score ledger and comparative scoreboard only from confirmed canonical runs.
8. Support invalidation/removal from canonical calculations without destroying history.
9. Preserve neutral launch prompts and prohibit improvement hints or expected terminal leakage.
10. Produce versioned evidence releases with sync reports, manifests and SHA-256.
11. Add schemas/templates/validators and positive/negative acceptance tests.
12. Integrate the workflow into ARF release gates and handoff material.

## Fail-closed rules

The workflow must block canonical inclusion when:

- user confirmation is absent;
- the actual run package was not unpacked and audited;
- checksum or manifest integrity is unresolved;
- scoring evidence is incomplete;
- the run is rejected, noncanonical or superseded;
- launch prompt neutrality is violated;
- Playbook version identity is ambiguous;
- a previous canonical record would be silently overwritten.

## Acceptance criteria

- The complete attached document is traceably represented in implementation contracts.
- A machine-readable run acceptance record and evidence manifest exist.
- Confirm and reject paths are separately tested.
- An unconfirmed run cannot enter canonical evidence or the comparative scoreboard.
- A corrected rerun creates a new revision and cannot overwrite the previous revision.
- Canonical invalidation removes the record from active scores while preserving history.
- After RUN_05, Playbook approval is explicitly resolved.
- Package validation, ARF release gate, checksums and ZIP integrity pass.


# BL-BENCH-045 — Mandatory Result Package Self-Validation and Release Gate

Before result-package handoff, execute the package-level gate. Release is permitted only for `PASS_RELEASE`. Any unresolved artifact-validator failure, selected-run inconsistency, foreign literal, stale artifact version/reference/approval, incomplete executable QA/Automation evidence, unsupported execution claim, or non-releasable Driver state yields `BLOCKED_REGENERATE` or `NO_GO`. The runtime must correct/regenerate as a new version and rerun the entire gate.


# Alpha 11 addendum — BL-BENCH-046

The canonical execution graph is a single route from `N001_FOCUSED_SCOPE` through all 72 route-authorized nodes and 16 gates to `T_PLAYBOOK_COMPLETED`. Connectivity is mechanically checked before release; unreachable, orphan, dangling and accidental dead-end objects fail closed.


---

# BL-BENCH-047 — Mandatory Black-Box End-to-End Pre-Release Self-Validation and Run Evidence

**Status:** OPEN  
**Priority:** Critical  
**Type:** Process enforcement / runtime / release gate  
**Depends on:** BL-BENCH-042, BL-BENCH-044, BL-BENCH-045, BL-BENCH-046

## Problem

Development-time checks can pass while a real external executor still cannot complete a canonical RUN. The attached RUN_02 package demonstrates that integrity, pre-flight and all available versioned regressions passed, but the generated Passport failed semantic validation and the Driver remained incomplete with no receipts, approvals or terminal state.

`BL-BENCH-045` validates a completed result package. It does not by itself prove that the released Playbook can autonomously create such a package under blind, black-box execution. A mandatory full execution campaign is therefore required before release.

## Objective

Make a blind black-box campaign over `RUN_01–RUN_05` a mandatory part of the Playbook release process. A package must not be released until the campaign has been executed automatically against the sealed candidate, all expected terminal outcomes have been proven, and immutable run evidence has been preserved.

## Required implementation

### 1. Sealed-candidate execution

The harness must operate on the final candidate ZIP as an external consumer. It must not import unpublished workspace state, reuse hidden chat facts or edit generated artifacts by hand.

### 2. Full five-RUN campaign

Execute all canonical `RUN_01–RUN_05` with neutral prompts and canonical inputs. Each RUN must have an explicit expected outcome contract: successful terminal route or intentional fail-closed/hard-stop route.

### 3. Real Driver-mediated validation

Every artifact validator result must be submitted through the actual Driver contract. The harness must verify:

- validation receipts;
- invalidation receipts;
- regeneration requests and acknowledgements;
- version-specific presentation;
- version-specific approvals;
- terminal recomputation;
- package release result.

### 4. Autonomous correction loop

On a point-correctable defect, create a new artifact/package revision through the canonical correction process, rerun validators and repeat the affected RUN. Manual mutation of a generated result to manufacture PASS is prohibited.

### 5. Authoritative-fact and cross-artifact audit

Before terminal acceptance, compare literals, identifiers, collections, states, timestamps, rules and expected side effects in all generated artifacts against selected-run authoritative inputs. Local validator PASS cannot override a cross-artifact mismatch.

### 6. Final-ZIP consumer verification

After each RUN is packaged, reopen the ZIP, verify checksums and manifests, inspect actual artifacts/evidence, rerun the result-package release gate and confirm that the archive is independently usable.

### 7. Preserved pre-release evidence

Create and deliver:

- five immutable archives: `RUN_01` … `RUN_05`;
- per-RUN execution report and terminal-state proof;
- campaign manifest and checksum list;
- neutral launch prompts;
- candidate package version and SHA-256 binding;
- summary of corrections made during validation;
- explicit marker `PRE_RELEASE_SELF_VALIDATION`, not canonical/user-confirmed benchmark evidence.

### 8. Fail-closed release gate

Release is blocked when any of the following applies:

- a required RUN was not executed;
- a positive RUN does not reach its required success state;
- a negative RUN does not stop at its required hard stop;
- any artifact validator or cross-artifact gate remains failed;
- Driver receipts, approvals or presented-version bindings are incomplete;
- correction-loop evidence is missing;
- final ZIP cannot be reopened or fails integrity/parity checks;
- run evidence archives are missing or not checksum-bound;
- the harness used hidden/manual corrections;
- required owner input is missing.

## Mandatory outputs

- `tools/run_black_box_pre_release_campaign.py`;
- machine-readable campaign policy and schema;
- five per-RUN evidence ZIPs;
- `BLACK_BOX_PRE_RELEASE_CAMPAIGN_REPORT.json`;
- `BLACK_BOX_PRE_RELEASE_CAMPAIGN_SUMMARY.md`;
- `SHA256SUMS.txt` covering the campaign;
- acceptance fixtures for success, correction, expected hard stop, stale facts, missing approvals and tampered final ZIP;
- release-gate integration that blocks handoff without campaign PASS.

## Acceptance criteria

1. All five canonical RUNs are executed against the sealed candidate ZIP.
2. No generated artifact is manually edited outside the canonical correction loop.
3. Validator outputs flow through the actual Driver and produce traceable receipts.
4. Positive and negative expected terminal routes are checked separately.
5. Cross-artifact selected-run fidelity is machine-validated.
6. Every final result ZIP is reopened and revalidated.
7. Five downloadable run-evidence archives are produced and checksum-bound.
8. A failed campaign blocks package release.
9. A point correction triggers a new revision and rerun, not silent mutation.
10. The harness stops transparently when owner input is genuinely required.
11. The campaign evidence is clearly separated from canonical/user-confirmed benchmark evidence.
12. The supplied RUN_02 incident is reproduced as a negative regression fixture and cannot be misclassified as a releasable success.

## Source evidence

- `backlog_attachments/BL-BENCH-047/ORDO_RUN_02_NO_CHANGE_RETURN.zip`
- SHA-256: `4f1f9d6c7069a9626e03adac49544acd9e57c4ab2165a5005704c2ff2c4f7793`
- `backlog_attachments/BL-BENCH-047/OWNER_REQUIREMENT_AND_INCIDENT_CONTEXT.md`


---

# BL-BENCH-048 — Internal Dry Evaluation and User Acceptance Gate Before External Blind Testing

**Status:** OPEN  
**Priority:** High  
**Type:** Benchmark workflow / evaluation / promotion gate  
**Depends on:** BL-BENCH-044, BL-BENCH-045, BL-BENCH-047

## Problem

The pre-release self-validation campaign can execute the Playbook and preserve RUN evidence, but it does not yet define a mandatory decision phase in which the same working context immediately evaluates those generated results, explains route and gate behavior, and asks the user whether the observed quality is acceptable before launching expensive and less observable external blind tests.

Without this phase, teams either:

- send immature Playbook versions into external chats too early;
- manually transfer run packages between contexts for analysis;
- lose the model's immediate understanding of why it selected a route or activated a gate;
- repeat diagnosis that could have been completed in the development chat;
- confuse internal pre-release evidence with externally blind benchmark evidence.

## Objective

Add a two-stage promotion workflow:

1. **Internal dry/self-evaluation stage** — execute and evaluate the current Playbook against the canonical scenarios inside the development context, retain full route reasoning evidence, score the results and present them to the user.
2. **External blind-testing stage** — permit creation of an external testing package only after explicit user acceptance that internal results satisfy the expected quality threshold.

Internal results are development evidence only. They must not be inserted into canonical external benchmark results or used as a substitute for blind execution.

## Required behavior

### 1. Immediate post-campaign evaluation

After `RUN_01–RUN_05` self-validation, automatically audit each result using the canonical evidence and scoring contracts. For every RUN produce:

- Process Quality;
- Document Quality;
- Final Quality;
- terminal-state correctness;
- validator and Driver receipt status;
- selected route and gate trace;
- corrections/regenerations performed;
- unresolved risks and limitations.

### 2. Development-context diagnostic analysis

Use the same execution context to explain:

- why a particular branch was selected;
- which gates passed, failed or regenerated artifacts;
- whether route selection indicates a Playbook defect, scenario defect, validator gap or expected behavior;
- what targeted Playbook improvement is justified by the evidence.

The process must not expose private model chain-of-thought. It must preserve safe, structured decision evidence such as state transitions, gate inputs/outputs, selected branches and validator receipts.

### 3. Acceptance thresholds

Support configurable minimum thresholds for:

- per-RUN process score;
- per-RUN document score;
- per-RUN final score;
- campaign average;
- mandatory zero-tolerance defects;
- expected positive and negative terminal outcomes.

Threshold failure blocks external-test promotion unless the user explicitly overrides it with a recorded rationale.

### 4. Explicit user acceptance gate

After showing the internal evaluation, the Playbook must ask for one explicit disposition:

- `ACCEPT_FOR_EXTERNAL_BLIND_TESTING`;
- `REJECT_AND_IMPROVE`;
- `ACCEPT_WITH_RECORDED_RISK`;
- `PAUSE_FOR_OWNER_INPUT`.

No external blind-testing package or launch prompt may be marked ready before this decision is recorded.

### 5. Improvement loop before promotion

When the user rejects the results or scores are below threshold:

1. classify defects;
2. create scoped improvement tasks;
3. patch the Playbook through the canonical improvement workflow;
4. rerun the internal self-validation campaign;
5. reevaluate all affected RUNs;
6. request acceptance again.

Previous internal results must remain versioned and immutable.

### 6. Strict evidence separation

Internal dry results must be marked:

```text
INTERNAL_DRY_EVALUATION
NOT_BLIND
NOT_CANONICAL_BENCHMARK_EVIDENCE
```

External blind results must remain in a separate evidence namespace and must never inherit internal scores or approval automatically.

### 7. External test handoff generation

Only after acceptance, generate a neutral external-testing bundle containing:

- sealed approved candidate Playbook;
- neutral prompts for RUN_01–RUN_05;
- canonical scenario inputs;
- integrity manifests and checksums;
- no internal diagnosis, score hints, change descriptions or expected-answer leakage;
- acceptance receipt binding the bundle to the reviewed candidate SHA-256.

## Mandatory outputs

- internal evaluation campaign report;
- five per-RUN evaluation reports;
- safe route/gate trace reports;
- threshold configuration and evaluation result;
- user acceptance receipt;
- improvement-loop history when applicable;
- external blind-test promotion report;
- neutral handoff bundle generated only after acceptance;
- fail-closed gate that blocks external-test readiness without valid acceptance.

## Acceptance criteria

1. Every self-validation RUN receives Process, Document and Final scores before promotion.
2. Results and route/gate evidence are presented to the user in the development context.
3. Configured score thresholds and zero-tolerance defects are machine-evaluated.
4. External testing remains blocked until an explicit user decision is recorded.
5. Rejection starts a scoped improvement and rerun loop without overwriting previous evidence.
6. Internal dry evidence is clearly separated from external blind benchmark evidence.
7. The generated external launch prompts contain no internal findings or benchmark hints.
8. The external bundle is checksum-bound to the exact user-accepted candidate version.
9. An acceptance override records the acknowledged risks and user rationale.
10. No claim is made that internal self-evaluation is equivalent to independent blind testing.

## Expected value

This stage shortens the improvement cycle, keeps diagnosis close to execution, prevents unnecessary external runs, and reserves external blind testing for candidates whose internally observed quality has already reached an acceptable level.


---

# BL-BENCH-049 — Canonical Evaluation Methodology and Test-Case-Specific Evaluation Profiles

## Status

`OPEN`

## Problem

The benchmark evidence package currently stores playbooks, test inputs, run outputs, audits and scores, but the methodology used to derive those scores is not guaranteed to be present as an explicit, versioned source of truth. This makes the evidence package less reproducible: another evaluator may see the scores without being able to reconstruct exactly how Process Quality, Document Quality and Final Quality were determined.

A single universal methodology is also insufficient by itself. Individual test cases may require additional scoring rules, caps, expected terminal states, artifact weights, scenario-specific blocking rules or clarifications. Those differences must be explicit and must not silently replace the general methodology.

## Goal

Introduce a two-level evaluation-methodology model:

1. a canonical general methodology stored at the root of every benchmark evidence package;
2. a mandatory test-case-specific evaluation profile stored inside every test-case directory.

The test-case profile inherits the general methodology and may add or override only explicitly permitted fields. Every run audit and score must identify the exact methodology versions used.

## Required artifacts

### Root-level canonical methodology

The evidence package root must contain, at minimum:

```text
EVALUATION_METHODOLOGY.md
EVALUATION_METHODOLOGY.json
```

The methodology must define:

- evaluation purpose and scope;
- evaluator independence and evidence requirements;
- Process Quality criteria;
- Document Quality criteria;
- Final Quality formula;
- rounding rules;
- artifact weighting;
- failure caps and zero-tolerance defects;
- treatment of blocked and hard-stop terminal states;
- distinction between validator PASS and actual quality;
- requirements for audit evidence and provenance;
- score reproducibility requirements;
- methodology versioning and change control.

### Test-case-specific profile

Each test case must contain:

```text
EVALUATION_PROFILE.md
EVALUATION_PROFILE.json
```

The profile must declare:

- inherited root methodology ID and version;
- test-case ID and version;
- expected terminal states per run;
- test-specific process criteria;
- test-specific document criteria;
- artifact set and weights;
- additional caps or blocking defects;
- authoritative inputs used during evaluation;
- allowed overrides with rationale;
- effective methodology fingerprint.

## Inheritance and override contract

The test-case profile must inherit the root methodology by default.

Overrides are allowed only when:

- the overridden field is explicitly marked overrideable;
- the profile provides a rationale;
- the change is machine-readable;
- the effective methodology remains internally consistent;
- the override does not silently weaken a mandatory root-level safety or evidence rule.

Missing, stale, incompatible or undeclared methodology/profile references must fail closed.

## Evaluation binding

Every run audit and score ledger record must include:

```json
{
  "evaluation_methodology_id": "...",
  "evaluation_methodology_version": "...",
  "test_case_evaluation_profile_id": "...",
  "test_case_evaluation_profile_version": "...",
  "effective_methodology_sha256": "..."
}
```

A score is noncanonical when this binding is absent or cannot be reproduced.

## Required process gate

Add a mandatory `EVALUATION_METHODOLOGY_BINDING_GATE` before evaluation and before canonical evidence acceptance.

The gate must verify:

1. root methodology files exist and agree;
2. test-case profile files exist and agree;
3. inheritance and overrides are valid;
4. effective methodology can be deterministically compiled;
5. run audit uses the compiled methodology version;
6. score formulas and caps match the effective methodology;
7. the methodology fingerprint is stored in the audit and ledger.

On failure:

```text
BLOCKED_MISSING_OR_INVALID_EVALUATION_METHODOLOGY
```

The run may be audited as working evidence, but it must not enter the canonical score ledger or comparative scoreboard.

## Package-template changes

Update the canonical evidence structure so that it includes:

```text
benchmark_evidence_base/
├── EVALUATION_METHODOLOGY.md
├── EVALUATION_METHODOLOGY.json
└── task_classes/
    └── <TASK_CLASS>/
        └── <TEST_CASE>/
            ├── EVALUATION_PROFILE.md
            └── EVALUATION_PROFILE.json
```

Update the test-case creation flow to create the profile before any runs are accepted.

## Acceptance criteria

1. A package without the root methodology is rejected.
2. A test case without its evaluation profile is rejected.
3. An undeclared or weakening override is rejected.
4. A valid inherited profile compiles to a deterministic effective methodology.
5. Every run audit stores the exact methodology/profile versions and SHA-256.
6. Re-evaluating the same evidence with the same effective methodology produces the same scores.
7. Comparative tables contain only methodology-bound canonical scores.
8. Methodology changes create a new version and do not silently rewrite historical scores.
9. Documentation clearly distinguishes general methodology from test-specific clarifications.
10. Positive and negative acceptance fixtures are included.

## Definition of done

- root methodology templates implemented;
- test-case evaluation profile templates implemented;
- JSON schemas implemented;
- deterministic methodology compiler implemented;
- binding validator and fail-closed gate implemented;
- evidence package and test-case templates updated;
- audit report and score ledger schemas updated;
- migration guidance for existing test cases added;
- acceptance tests pass;
- backlog, README, changelog, manifests and checksums updated.


---

# BL-BENCH-050 — Declared-Contract Archive Pre-Release Self-Application Gate

**Status:** OPEN  
**Type:** Process improvement / fail-closed release governance  
**Scope:** Creation and release of any archive intended for external model testing

## Problem statement

A package may contain its own validators, runtime prerequisites, entry-point rules, regression procedures, expected paths and release criteria, while the package-creation process validates only ZIP integrity, checksums or a simplified local fixture. This creates a false-positive release: the archive is handed to an external model, and only that external executor discovers that a required validator is missing, an expected path is wrong, the runtime starts from an incompatible entry node, or another package-declared prerequisite is not satisfied.

The defect is general and must not be tied to a particular container, filename, validator path, node identifier or package version.

## Governing principle

> If an archive declares a process, validator, runtime prerequisite, entry contract, regression suite or release criterion for its consumer, the producing process must apply the same declared contract to the sealed candidate archive before release.

An archive must not be considered valid merely because:

- it opens successfully;
- its checksums match;
- local schemas parse;
- a substitute fixture passes;
- a simplified internal validator passes;
- the producer believes an equivalent tool exists.

## Required implementation

### 1. Package-declared verification inventory

Before release, derive a machine-readable inventory from the sealed candidate containing at minimum:

- mandatory validators and exact invocation contracts;
- required file and executable paths;
- required runtime entry point and first allowed position/node;
- supported modes and selected route;
- preflight checks;
- versioned regression suites;
- required environment-independent prerequisites;
- expected positive and negative terminal states;
- required receipts, reports, approvals and evidence files;
- final package-release conditions.

The inventory must identify the authoritative source file for every criterion.

### 2. Self-application to the sealed candidate

Run the inventory against the exact ZIP intended for external testing, from a clean consumer workspace, without relying on producer workspace residue.

The self-check must verify both:

1. **presence and invocability** — required validators, paths and entry points physically exist and can be invoked as declared;
2. **semantic compatibility** — the selected runtime, initial node/position, route and expected terminal behavior satisfy the package's own contract.

### 3. No silent equivalents

A missing declared validator or path is a release blocker unless the package itself explicitly declares a versioned, testable equivalence rule. The producer may not invent an equivalent after packaging.

Any allowed equivalent must have:

- canonical identifier;
- version;
- compatibility scope;
- deterministic selection rule;
- proof that it enforces the same contract;
- evidence recorded in the release report.

### 4. Fail-closed release gate

Release must be blocked when any package-declared criterion is:

- absent;
- not invocable;
- inconsistent with the archive layout;
- incompatible with the actual runtime entry point;
- skipped;
- replaced by an undeclared local check;
- passed only before sealing but not on the final ZIP;
- unsupported by evidence.

Allowed terminal status on failure:

```text
NO_CHANGE / PRE_RELEASE_DECLARED_CONTRACT_MISMATCH
```

No business artifacts, approvals or external-test launch bundle may be claimed as release-ready after this terminal.

### 5. Iterative correction cycle

The producer may perform at most five automatic correction passes:

```text
inspect sealed ZIP
→ derive declared verification inventory
→ execute all declared checks
→ diagnose mismatch
→ apply a scoped correction
→ rebuild and reseal
→ rerun from a clean workspace
```

Stop immediately when owner input, unavailable authoritative data, an unsafe semantic decision or an unbounded change is required.

### 6. Required evidence

Each release candidate must include or accompany:

- `DECLARED_VERIFICATION_INVENTORY.json`;
- `SEALED_ARCHIVE_SELF_VALIDATION_REPORT.json`;
- executed-command or invocation ledger;
- validator and regression receipts;
- entry-point/runtime compatibility evidence;
- list of skipped checks, which must be empty for release;
- correction-pass history;
- final sealed ZIP SHA-256;
- explicit `PASS_RELEASE` or fail-closed terminal.

### 7. Integration with existing process

This gate must execute after archive assembly and sealing but before:

- presenting the archive to the user as ready;
- generating an external blind-testing prompt;
- handing the archive to another chat/model;
- adding it to approved packages;
- recording a release PASS.

It complements, and does not replace:

- checksum/integrity validation;
- graph connectivity validation;
- result-package release validation;
- black-box RUN campaign;
- internal dry evaluation;
- user acceptance before external blind testing.

## Acceptance criteria

1. A clean archive whose declared validators, paths, runtime entry contract and regressions all pass receives `PASS_RELEASE`.
2. An archive with a missing required validator fails closed.
3. An archive whose actual runtime starts from a node/position different from the declared mandatory entry fails closed.
4. An undeclared local substitute cannot satisfy a missing package-declared check.
5. Checks run only on an unpacked producer directory do not authorize release; the final sealed ZIP must be retested.
6. Every declared criterion is mapped to executed evidence; skipped count is zero.
7. The gate supports up to five scoped correction passes and preserves every pass report.
8. External testing artifacts cannot be generated while the gate is not `PASS_RELEASE`.
9. Negative fixtures reproduce the two defect classes: missing mandatory verifier and incompatible runtime entry contract.
10. Backlog, playbook graph, release documentation, runtime and regression suite are updated together.

## Definition of done

- machine-readable inventory schema and compiler implemented;
- clean-workspace sealed-ZIP executor implemented;
- fail-closed gate integrated into the canonical route;
- positive and negative acceptance tests pass;
- release report binds all evidence to the final ZIP hash;
- task status changed to DONE only after materialized evidence and full self-validation.


# Declared-Contract Archive Pre-Release Self-Application Rules

## Mandatory decision node

This contract is executed after the candidate external-testing archive has been sealed and before any external testing bundle is exposed.

The exact sealed ZIP must be opened in a clean consumer workspace and evaluated against every validator, runtime prerequisite, entry point, regression command, required path, and release criterion that the archive itself declares.

## Rules

1. Build a machine-readable inventory from the archive's declared contracts.
2. Every declared validator and command must exist at the declared path and be invocable.
3. The actual runtime entry point must equal the declared entry point.
4. Required files and schemas must exist inside the sealed archive.
5. No local substitute or undocumented equivalent may satisfy a declared check.
6. Execute checks against the exact sealed candidate, never against an unsealed working directory.
7. On failure, block release and permit at most five scoped correction passes.
8. Every pass creates immutable evidence.
9. Release is allowed only with `PASS_RELEASE`.
10. Exhaustion or owner-dependent ambiguity ends as `NO_CHANGE / PRE_RELEASE_DECLARED_CONTRACT_MISMATCH`.

## Gate outputs

- `DECLARED_CONTRACT_INVENTORY.json`
- `DECLARED_CONTRACT_SELF_APPLICATION_REPORT.json`
- per-pass evidence under `PRE_RELEASE_DECLARED_CONTRACT_EVIDENCE/`
- release disposition: `PASS_RELEASE` or `NO_CHANGE`

---

# 051. Playbook Representation Compilation Governance

See `051_PLAYBOOK_REPRESENTATION_COMPILATION_GOVERNANCE.md`. Status: OPEN.

# 052. Evidence Base Catalog Construction and Lifecycle Governance

See `052_EVIDENCE_BASE_CATALOG_GOVERNANCE.md`. Status: OPEN.


---

# Representation Compilation Governance

See `051_PLAYBOOK_REPRESENTATION_COMPILATION_GOVERNANCE.md` and `REPRESENTATION_REGISTRY.json`.


---

# Evidence Base Catalog Governance

Version: 1.0.0-alpha.24

This document is the normative human-readable companion to `EVIDENCE_CATALOG_CONTRACT.json`.

## Core rules

1. Internal self-validation, internal dry evaluation, and external blind evidence are separate evidence classes and directories.
2. Original external RUN archives are immutable and append-only. Corrections create a new RUN or implementation version.
3. Every catalog object has a stable ID, lifecycle state, SHA-256, provenance, and version bindings.
4. Canonical scores may reference only `CONFIRMED` external blind RUN evidence with complete package, prompt, methodology, case-profile, audit, acceptance, and evidence bindings.
5. Rejected, invalidated, quarantined, deprecated, or superseded evidence remains historically visible but cannot enter the confirmed score ledger.
6. Filesystem, object manifests, score ledgers, lifecycle ledgers, and transfer manifests must agree exactly.
7. Transfer packages must be checksum-bound and restorable without relying on undocumented local files.

## Fail-closed outcome

Any missing object, broken binding, class contamination, mutable-history rewrite, ineligible score, or non-restorable transfer routes to `NO_CHANGE / EVIDENCE_BASE_CATALOG_GOVERNANCE_FAILURE`.

---

# 054 — Execution Progress Status Output Governance

See `054_EXECUTION_PROGRESS_STATUS_OUTPUT_GOVERNANCE.md`. This OPEN task defines concise user-visible step status messages, evidence binding, canonical statuses, correction-loop rendering, terminal coherence, and suppression of chain-of-thought or malformed progress events.


---

# BL-BENCH-053 — Improvement Plateau and Best Confirmed Version Retention Gate

**Status:** DONE  
**Type:** Process safety / correction-loop governance  
**Priority:** High

## Problem

A document correction or improvement step can repeatedly regenerate a candidate even when the new version provides no measurable quality gain. This creates non-terminating or wasteful loops, may replace a stronger confirmed version with a merely newer version, and can degrade already validated artifacts.

## Objective

Add an enforceable improvement-plateau rule to every document correction and regeneration path. After each attempt, the candidate must be compared with the best currently confirmed version using explicit quality evidence. A new candidate may replace the confirmed version only when measurable improvement is demonstrated.

## Required process behavior

1. Snapshot and bind the best confirmed artifact before regeneration.
2. Record the defect evidence and correction strategy that authorize the attempt.
3. Generate a candidate without overwriting the confirmed artifact.
4. Re-run the applicable validators, semantic checks and cross-artifact gates.
5. Produce a machine-readable delta assessment between candidate and confirmed versions.
6. Accept the candidate only when at least one material improvement is proven and no protected quality dimension regresses.
7. When improvement cannot be proven:
   - reject the candidate;
   - retain the best confirmed version;
   - record `IMPROVEMENT_PLATEAU_REACHED`;
   - terminate the current improvement loop;
   - continue only to the next explicitly allowed process step or terminal decision.
8. Re-entry into the same correction loop requires new defect evidence, new facts, or a materially different correction strategy.

## Measurable improvement signals

At least one of the following must be evidenced:

- a previously failing validator now passes;
- a registered quality defect is closed;
- semantic completeness increases;
- a contradiction is removed;
- missing executable evidence is supplied;
- cross-artifact consistency improves;
- a blocking condition is removed;
- a gate that previously failed now passes.

Editorial variation, rephrasing, formatting-only changes or a newer timestamp are not sufficient.

## Required gates and records

- `G_IMPROVEMENT_DELTA_PROVEN`
- `G_NO_PROTECTED_DIMENSION_REGRESSION`
- `G_BEST_CONFIRMED_VERSION_RETAINED`
- `IMPROVEMENT_ATTEMPT_RECEIPT`
- `IMPROVEMENT_DELTA_REPORT`
- terminal marker `IMPROVEMENT_PLATEAU_REACHED`

The delta report must bind the hashes and versions of the baseline and candidate, applicable criteria, validator outcomes, changed defects, regressions, decision and next route.

## Integration scope

The rule must be integrated into:

- correction and improvement loops;
- document regeneration rules;
- validation-failure handling;
- Driver execution policy;
- terminal eligibility rules;
- multi-cycle improvement mode;
- package self-validation correction passes.

## Prohibitions

The process must not:

- regenerate indefinitely;
- overwrite the confirmed version before acceptance;
- accept a candidate merely because it is newer;
- trade a confirmed quality property for an unrelated cosmetic gain;
- repeat the same correction strategy without new evidence;
- claim improvement without a bound comparison report.

## Acceptance criteria

1. A materially improved candidate replaces the confirmed artifact and preserves the comparison receipt.
2. A formatting-only candidate is rejected and the confirmed artifact remains byte-identical.
3. A candidate that fixes one defect but introduces a protected regression is rejected.
4. Plateau produces `IMPROVEMENT_PLATEAU_REACHED` and exits the loop without another automatic retry.
5. The same strategy cannot retry without new evidence or changed strategy identity.
6. Historical confirmed and rejected candidate versions remain traceable.
7. Decision-tree connectivity and terminal reachability remain valid after integration.

## Source evidence

`backlog_attachments/BL-BENCH-053/SOURCE_PLAYBOOK_EXECUTION_IMPROVEMENT_PLATEAU_RULE.md`


## Implementation closure

Implemented in Alpha 26 through nodes `N092`–`N097`, gates `G_IMPROVEMENT_DELTA_PROVEN`, `G_NO_PROTECTED_DIMENSION_REGRESSION`, and `G_BEST_CONFIRMED_VERSION_RETAINED`, plus terminal `T_IMPROVEMENT_PLATEAU_REACHED`. The runtime preserves the baseline until acceptance, emits bound attempt and delta records, rejects non-material or regressive candidates, and blocks same-strategy retry without new evidence.


# BL-BENCH-055 — Current-State-Only Evidence Transfer Archive Generation

Status: **DONE**

## Objective

Add a governed playbook route that produces a compact, current-state-only evidence snapshot for transfer. The route retains only authoritative accepted/current artifacts and excludes development history without changing immutable raw evidence or weakening current bounded claims.

## Implemented decision path

1. Select snapshot policy and bind source evidence catalog.
2. Inventory logical artifact families and all candidates.
3. Resolve the authoritative current artifact using manifests, acceptance/approval records, release bindings and semantic versions—not filesystem time alone.
4. Bind each retained accepted run to its exact package, Driver, evaluator, scorecard, methodology and terminal state.
5. Detect run-bound exceptions when the accepted run used a package older than the latest available package.
6. Calculate historical exclusions and bounded-claim exceptions.
7. Choose archive-retention pattern A, B or C for each source package and document any intentional duplication.
8. Build an isolated staging tree without mutating immutable raw evidence.
9. Generate the manifest, selection, exclusion and language-audit reports.
10. Generate checksums last, freeze staging, seal ZIP and revalidate it in a clean workspace.
11. Release only through the current-state snapshot hard gate.

## Fail-closed conditions

The route blocks when current authority is ambiguous, provenance is missing, accepted-run binding is incomplete, a checksum is invalid, exclusion would invalidate a current claim, or the current accepted run set is incomplete.

## Terminal states

- Success: `CURRENT_STATE_ONLY_ARCHIVE_READY / PASS_RELEASE`
- Failure: `NO_CHANGE / CURRENT_STATE_EVIDENCE_SELECTION_BLOCKED`

## Authoritative outputs

- `CURRENT_STATE_ONLY_EVIDENCE_POLICY.json`
- `schemas/current_state_manifest.schema.json`
- `schemas/current_state_selection_report.schema.json`
- `schemas/current_state_exclusion_report.schema.json`
- `templates/CURRENT_STATE_MANIFEST.template.json`
- `tools/build_current_state_evidence_snapshot.py`
- `tools/validate_current_state_evidence_snapshot.py`
- `reports/CURRENT_STATE_ONLY_EVIDENCE_SNAPSHOT_ACCEPTANCE_TESTS.json`
