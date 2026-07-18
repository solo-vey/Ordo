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
