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
