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
