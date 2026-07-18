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
