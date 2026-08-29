# Node-Local Deterministic Execution and Transition Provenance

## Invariant

A runtime session has exactly one active node. A node action may execute only after the runtime proves the node was entered through an accepted direct predecessor or an explicitly declared entry mode.

## Source contract

```yaml
graph_contract:
  entry_node: N_START
  transition_provenance:
    enabled: true
    mode: strict
    direct_edges_only: true
    invalid_entry_behavior: block_and_recover

nodes:
  - id: N_START
    allowed_from: []
    entry_modes: [root, resume, recovery, migration]
    node_context:
      version: "1.0"
      required_state: [current_node]
      knowledge_refs: []
      allowed_tools: []
      output_contract:
        state_diff: required
        next_node: explicit

  - id: N_NEXT
    allowed_from: [N_START]
```

`allowed_from` contains direct one-hop predecessors only. Transitive reachability never satisfies the provenance gate.

## Bidirectional validation

For every direct outbound edge `A -> B`, `B.allowed_from` must contain `A`. For every inbound declaration `B.allowed_from += A`, node `A` must contain a direct outbound edge to `B`.

Blocking defect classes:

- `GRAPH_OUTBOUND_NOT_ACCEPTED`;
- `GRAPH_INBOUND_WITHOUT_OUTBOUND`;
- `GRAPH_INBOUND_SOURCE_MISSING`;
- `GRAPH_INBOUND_DECLARATION_MISSING`;
- `GRAPH_ROOT_ENTRY_MODE_MISSING`.

## Runtime entry gate

Before a node action runs, runtime validates `previous_node_id` against `allowed_from`. Missing or invalid provenance blocks normal execution and returns transition-provenance recovery diagnostics without mutating state.

Root, resume, retry, recovery and migration entry are valid only when explicitly declared in `entry_modes`.

## Node-local context

`node_context` is the bounded context envelope for a node. Runtime projects only declared state fields, knowledge references and tool permissions into the execution envelope. Nodes are treated as deterministic functions of explicit context and state, producing an explicit state diff and next node.
