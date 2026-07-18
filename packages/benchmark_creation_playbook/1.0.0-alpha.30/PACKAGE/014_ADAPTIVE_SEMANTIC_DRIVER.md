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
