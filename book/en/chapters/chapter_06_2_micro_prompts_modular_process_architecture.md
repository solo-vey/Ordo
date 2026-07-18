# Chapter 6.2. Micro-Prompts as Modular Process Architecture

A micro-prompt is often understood as a shorter version of a large prompt. In this book, it is treated differently: as a **local unit of behavior** that can be evolved, tested, versioned, replaced, and rolled back independently without rebuilding the entire process.

The core idea is simple:

> A process should evolve as a composition of independent behavioral modules, not as one large instruction.

This is not a normative language requirement and not a mandatory syntactic element. It is a practical architectural recommendation for processes in which a language model performs many different actions.

## 1. From a Large Instruction to a Composition of Behavior

### Monolithic Approach

In a monolithic approach, the entire process is described by one large text:

    One large instruction
    ↓
    Any local change
    ↓
    Almost the entire process must be reread and retested
    ↓
    The risk of accidentally changing other behavior increases

Such text may contain rules for fact collection, reconstruction, generation, validation, confirmation, failure routes, and final response formatting. Even when only one rule changes, it remains inside a shared context with every other rule.

A language model does not execute the text as an isolated set of functions. It interprets the text as one context. Because of this, a local edit may:

- change the priority of neighboring instructions;
- weaken a constraint in another step;
- add a new assumption where none existed;
- change the style or completeness of outputs from other nodes;
- create a contradiction between the beginning and end of the prompt;
- increase the risk that some rules disappear inside a long context.

### Modular Approach

In a modular approach, the process tree remains a separate structure and every node references its own behavioral instruction:

    Decision Tree
          │
          ├── Step A → Prompt A
          ├── Step B → Prompt B
          ├── Step C → Prompt C
          └── Step D → Prompt D

If Step C behavior must be improved, Prompt C changes. Prompt A, Prompt B, and Prompt D are not rewritten without a separate reason.

This does not mean other parts of the process are automatically guaranteed to remain unchanged. But the area of potential impact becomes smaller, more visible, and easier to validate.

## 2. What a Micro-Prompt Is in Process Architecture

A micro-prompt is not merely a short text. It is a local behavioral module that:

- serves one defined responsibility;
- accepts concrete inputs;
- creates a concrete output;
- operates within the node contract;
- has its own quality criteria;
- may have its own tests;
- may have an independent version;
- leaves an observable execution trace.

It is useful to separate the node itself from the micro-prompt that implements its behavior:

    Node
       │
       ├── Contract
       ├── Prompt
       ├── Tests
       ├── Trace
       └── Versions

The node defines **what must be done**. The micro-prompt describes **how the model should perform that local behavior** within the allowed contract.

Therefore, changing micro-prompt text must not silently change:

- the purpose of the node;
- its input type;
- its output form;
- completion criteria;
- allowed transitions;
- confirmed state;
- failure route.

If at least one of these changes, the work is no longer only a local micro-prompt refactor. It is a contract or process-architecture change.

## 3. Analogy with Software Engineering

Micro-prompts are closer to modules in a software system than to separate paragraphs of documentation.

### Function

A function has parameters, performs one operation, and returns a result. A micro-prompt should likewise receive a defined context and create one expected result.

### Module or Library

A module hides internal implementation behind a stable interface. In the same way, micro-prompt text may change while the node contract remains stable.

### Class

A class combines behavior around a defined responsibility. A micro-prompt should also be attached to a concrete role rather than trying to govern the whole process at once.

### Dependency Injection

A process may reference a concrete version of a prompt module instead of embedding the text directly. This makes it possible to substitute another implementation without changing the process tree.

### Interface and ABI/API Contract

The most important analogy is a stable interface. Safe local evolution is possible only when a new micro-prompt version does not break the interaction contract with neighboring nodes.

For example:

    node_contract:
      id: reconstruction_step
      input:
        confirmed_facts: list
        open_gaps: list
      output:
        proposed_values: list
        unresolved_gaps: list
        evidence_links: list
      completion_criteria:
        - every proposal has evidence
        - every gap is resolved or explicitly open

The prompt implementation may change. But if a new version stops returning `evidence_links`, that is an interface violation.

### Local Refactoring

Refactoring improves internal implementation without changing external behavior. Similarly, you may:

- make an instruction more precise;
- remove ambiguity;
- add a better analysis order;
- clarify the local response format;
- add protection against a common error;

while preserving the node contract unless a separate decision changes it.

## 4. Main Advantages

### 4.1. Locality of Changes

Improving one step happens in one place. The author does not need to find every mention of the behavior inside a large prompt.

Locality criterion:

> Changing the behavior of one node does not require editing the texts of other nodes if their contracts have not changed.

### 4.2. Smaller Regression Scope

A monolithic instruction creates a broad regression scope: even a small edit may affect the entire context.

    Monolith
    ↓
    one local change
    ↓
    almost complete process retesting

Micro-prompts make it possible to narrow the validation area:

    Micro-prompt of node C
    ↓
    local change
    ↓
    node C tests
    ↓
    contract tests for C → downstream nodes
    ↓
    limited end-to-end regression

A numeric percentage is not universal. The principle matters: the more stable the contracts between nodes, the smaller the part of the process that must be retested after a local change.

### 4.3. Independent Versioning

Every micro-prompt may have its own history:

    node:
      id: document_review
      contract_version: 1.0.0
      prompt:
        id: review_prompt
        version: 1.4.2
      approved_regression_suite: review-suite-7
      rollback_version: 1.4.1

It is important to distinguish:

1. the node contract version;
2. the prompt text version;
3. the test version;
4. the version of the process using the prompt.

A prompt change does not always require a contract change. A contract change always requires broader dependency validation.

### 4.4. Targeted Experiments

A new version can be tested on one node only:

- A/B comparison of two versions;
- replay of the same input;
- output comparison;
- evaluation of one concrete metric;
- validation on a local edge-case set.

### 4.5. Simpler Review

A reviewer can see:

- which node changed;
- why it changed;
- which contract was preserved;
- which tests were added;
- which regression scope was checked.

This is much more reliable than reviewing a diff in a large instruction where a local change disappears among dozens of other rules.

### 4.6. Simple Rollback

If a new version makes the result worse, the previous version of one prompt module can be restored without rolling back the entire process.

Rollback is safe only when the previous version remains compatible with the current node contract.

### 4.7. Better Execution Trace

Trace should record not only the node name but the actual behavior version:

    trace_event:
      node_id: reconstruction_step
      contract_version: 1.0.0
      prompt_id: reconstruction_prompt
      prompt_version: 1.4.2
      input_artifact: evidence-104
      output_artifact: proposal-105
      validation_status: passed

This makes it possible to:

- repeat a run with the same version;
- compare results from different versions;
- localize a regression;
- determine which behavioral implementation affected the result;
- reproduce a historical decision.

### 4.8. Local Knowledge Capture

In a monolith, new knowledge is often added to the general text. Over time, it becomes difficult to understand which step a particular rule belongs to.

In a modular architecture, experience is stored next to the node:

    Node C
    ├── prompt.md
    ├── contract.yaml
    ├── examples/
    ├── tests/
    ├── regressions/
    ├── known_failures.md
    └── changelog.md

An error in a concrete node produces:

- a local prompt change;
- a local regression test;
- a local note about the known problem;
- a local explanation of the decision.

Knowledge does not spread across one huge document.

## 5. Abstract Example: Reconstruction as a Local Module

Imagine a four-step process:

    Fact collection
    → Reconstruction
    → Document generation
    → Review

### Variant 1. Monolithic Instruction

All behavior is described in one prompt. Practical use reveals that reconstruction rules too easily treat a plausible value as a confirmed fact.

To fix the problem, the author edits the large text. Afterward, the author must check:

- whether fact collection changed;
- whether reconstruction output format changed;
- whether document generation began to skip open gaps;
- whether review logic changed;
- whether transition order remained intact.

A local problem created an almost complete regression scope.

### Variant 2. Separate Reconstruction Micro-Prompt

The process keeps a stable structure:

    FACT_COLLECTION → RECONSTRUCTION → DOCUMENT_GENERATION → REVIEW

The `RECONSTRUCTION` node has a separate prompt. Only these rules change:

- every proposed value must reference evidence;
- plausibility does not equal confirmed;
- an uncertain value remains an open gap;
- confirmed facts must not be changed;
- output preserves provenance for every reconstruction.

After the change, run:

1. unit-like tests for the reconstruction micro-prompt;
2. a contract test of its output;
3. validation of the `RECONSTRUCTION → DOCUMENT_GENERATION` transition;
4. a short end-to-end regression for the whole process.

Other prompt modules are not rewritten.

Success criterion:

> The new version reduces reconstruction errors, preserves the node contract, and does not change neighboring-node behavior outside the defined regression scope.

## 6. Prompt Dependency Graph

Separate prompts do not exist in a vacuum. They form a dependency graph.

    Process Graph
          │
          ├── Node A ──uses── Prompt A v1.2
          ├── Node B ──uses── Prompt B v2.0
          ├── Node C ──uses── Prompt C v1.4
          └── Node D ──uses── Prompt D v3.1

But `node → prompt` links are not the only important relationships. Contract dependencies must also be visible:

    Prompt A output contract
            ↓
    Prompt B input contract
            ↓
    Prompt C precondition

A micro-prompt registry should therefore answer at least:

- which node uses the prompt;
- which version is active;
- which contract it implements;
- which nodes depend on its output;
- which tests protect a change;
- which version is allowed for rollback;
- in which processes it is reused.

An abstract registry:

    prompt_registry:
      - prompt_id: reconstruction_prompt
        version: 1.4.2
        implements_contract: reconstruction_contract@1.0.0
        used_by:
          - process_a.reconstruction
          - process_b.missing_data_resolution
        tests:
          - reconstruction_unit_suite
          - reconstruction_contract_suite
        rollback_to: 1.4.1

## 7. Contract Compatibility and the Boundary of a Local Change

Micro-prompts reduce risk but do not remove it.

A local update is sufficient if:

- the node purpose does not change;
- input schema does not change;
- output schema does not change;
- status semantics do not change;
- completion criteria do not change;
- failure route does not change;
- the prompt receives no new right to change confirmed state.

A local update is not sufficient if:

- the node begins making a new business decision;
- the output type changes;
- the meaning of a status changes;
- a new mandatory dependency appears;
- the prompt begins doing the work of a neighboring node;
- process order changes;
- the contract between nodes changes.

In that case, the work requires:

- a new contract version;
- Prompt Dependency Graph analysis;
- broader regression scope;
- updated trace semantics;
- possible migration of processes using the old contract.

## 8. Micro-Prompt Architecture Patterns

### Pattern: One Node — One Behavioral Module

**When to use:** when a node has one clear responsibility.

**Structure:**

    Node contract
    → one micro-prompt
    → one observable output
    → local validation

**Advantage:** behavior changes are easy to localize.

**Risk:** the prompt may silently grow and begin performing several tasks.

**Control:** review it together with step-atomicity criteria.

### Pattern: Prompt Behind a Stable Contract

**When to use:** when behavior improves frequently but the interface must remain stable.

    Stable node contract
            │
            ├── Prompt v1.2
            ├── Prompt v1.3
            └── Prompt v1.4

**Criterion:** every version passes the same contract suite.

### Pattern: Prompt Registry

**When to use:** when prompts are reused or have several versions.

The registry separates a behavior reference from process text. The process specifies `prompt_id` and version policy, while the prompt itself is stored separately.

### Pattern: Contract Test Before End-to-End Test

Validate local contract compliance first and the entire process afterward.

    prompt test
    → output schema test
    → semantic contract test
    → neighboring-node integration
    → selected end-to-end regression

### Pattern: Traceable Prompt Resolution

Before execution, the runtime or model must record which prompt version was actually selected.

This protects against a process referencing `latest` when the historical run cannot later be reproduced.

### Pattern: Local Failure Knowledge

Every discovered error is linked to a concrete prompt module, test, and fix version.

    issue:
      id: ISSUE-17
      affected_prompt: reconstruction_prompt@1.4.1
      failure_class: unsupported_inference
      regression_test: REC-CASE-09
      fixed_in: 1.4.2

### Pattern: Approved Promotion

A new version does not become active immediately after editing.

    draft
    → local tests passed
    → contract tests passed
    → regression passed
    → review approved
    → promoted

## 9. Risks and Antipatterns

### Antipattern: Micro-Prompt in Name Only

The prompt is called a micro-prompt but contains data collection, decision-making, generation, review, and a state transition.

**Sign:** changing one part requires retesting everything inside the prompt.

**Fix:** first separate responsibilities at the process level.

### Antipattern: Hidden Contract in Prompt Text

The contract exists only as several sentences inside prompt text.

**Risk:** a new version accidentally changes output or statuses.

**Fix:** move the contract into an explicit structure and test it separately.

### Antipattern: Floating Latest

The process references the “latest” version without recording actual resolution.

**Risk:** two identical runs use different behavior and replay becomes unreliable.

**Fix:** record the resolved version in the execution trace.

### Antipattern: Shared Prompt with Divergent Responsibilities

One prompt is reused by nodes with similar names but different contracts.

**Risk:** an improvement for one process makes another worse.

**Fix:** use a shared core with separate adapters or separate prompts.

### Antipattern: Prompt Change Without Regression Artifact

The text changes, but there is no example, test, or trace showing which problem was fixed.

**Fix:** every meaningful improvement should add or update a local regression case.

### Antipattern: Prompt Owns the State Transition

The micro-prompt not only creates output but also decides that the process is now confirmed.

**Risk:** local behavior gains the right to change global state.

**Fix:** keep state transition as a separate operation with preconditions.

### Antipattern: Over-Fragmentation

Every sentence is moved into a separate prompt even though the actions form one mechanical operation.

**Risk:** too many dependencies, difficult version management, and unnecessary orchestration overhead.

**Fix:** the prompt-module boundary should match a real responsibility boundary, not text length.

## 10. Versioning and Lifecycle

Recommended minimum version record:

    micro_prompt:
      id: document_review_prompt
      version: 2.3.0
      implements_contract: document_review@1.1.0
      status: approved
      created_from: 2.2.1
      change_reason: detect missing concrete examples
      regression_suite: review-regression-12
      rollback_to: 2.2.1

A practical version-change rule:

- **patch** — wording clarification without a contract change;
- **minor** — new compatible behavior or additional local protection;
- **major** — incompatible change requiring a new contract or dependency migration.

This is not a rigid standard but a useful discipline. The important thing is that history can answer:

- what changed;
- why;
- which problem it fixes;
- which tests prove the improvement;
- how to return to the previous version;
- which processes use this version.

## 11. Testing Micro-Prompts

### Local Examples

A set of short inputs that checks the primary behavior of the node.

### Edge Cases

Cases with gaps, contradictions, ambiguity, missing evidence, or an invalid format.

### Contract Tests

They check interface compliance rather than the beauty of the text:

- all mandatory fields are present;
- statuses use allowed values;
- output contains no forbidden state transitions;
- every decision has evidence;
- open gaps are not hidden.

### Metamorphic Tests

They check invariants. For example, changing the order of independent facts should not change the decision.

### Replay Tests

The same input is executed on old and new versions. Results are compared using defined criteria.

### Neighbor Integration Tests

They check whether the next node can correctly consume the new version's output.

### Selected End-to-End Regression

Even with a stable contract, a limited end-to-end test is needed. Language models may create side effects that a formal schema does not detect.

## 12. Relationship to Other Principles in This Book

### Step Atomicity

A micro-prompt makes sense only when the node itself is atomic. If the node mixes several responsibilities, a separate prompt merely hides a monolith under a new name.

### Single Responsibility

One prompt module should own one behavior type and one primary result.

### Explicit Contracts

A contract separates stable external behavior from changing internal implementation.

### Local Failure Routes

An error in a concrete prompt should return to the nearest node capable of fixing it, not restart the whole process.

### Execution Trace

Trace records node, prompt ID, prompt version, contract version, input, output, and validation evidence.

### Independent Validation

A prompt must not declare its own result correct. Validation remains a separate operation or separate node.

### Artifact-Oriented Approach

Micro-prompt input and output are better represented as observable intermediate artifacts. This makes behavior testable and reproducible.

## 13. Practical Checklist

Before extracting a separate micro-prompt, check:

1. Does the node have one responsibility?
2. Is there one primary observable output?
3. Are input and output contracts defined?
4. Can the internal instruction change without changing the process?
5. Does the prompt have its own tests?
6. Is its version recorded in trace?
7. Is there a local rollback?
8. Is the regression scope clear?
9. Does the prompt avoid changing confirmed state by itself?
10. Does it avoid hidden work belonging to a neighboring node?
11. Is one prompt avoided across incompatible contracts?
12. Is the reason for a new prompt stronger than a desire to shorten text?

Before a local update, check:

- the node contract has not changed;
- dependent inputs/outputs remain compatible;
- a regression case was added;
- local tests passed;
- contract tests passed;
- selected end-to-end regression passed;
- the resolved version will be recorded in the execution trace;
- a rollback version is defined.

## 14. Final Table

| Situation | Risk | Correct Action | Validation Scope |
|---|---|---|---|
| Wording of one local rule was clarified | Side effect on node behavior | New micro-prompt patch version | Local and contract tests |
| Compatible edge-case protection was added | Regression on old inputs | New minor version and regression case | Node, neighbor integration, selected end-to-end |
| Output schema changed | Downstream nodes break | New contract version | Dependency graph and broad integration validation |
| One prompt is used by different contracts | Unpredictable side effects | Split implementations or add adapters | All consuming processes |
| A new version worsened the result | Defect propagation | Local rollback | Rollback-version compatibility validation |
| Trace lacks prompt version | Reliable replay is impossible | Record resolved prompt version | Trace validation |
| Prompt began performing several responsibilities | Hidden monolith | Decompose the node | Atomicity review |

## 15. Final Rule

> The smaller and clearer the responsibility scope of a micro-prompt, the easier it is to improve, test, roll back, and reuse.

And one more architectural generalization:

> A stable process should depend on behavioral-module contracts, not on the accidental shape of one large instruction.

Micro-prompts do not eliminate the need for system testing. They make changes more local, dependencies more visible, regression scope smaller, and process evolution governable.
