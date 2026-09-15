# Graph Contract and Dynamic Routing

Ordo accepts the following equivalent static transition forms:

- node `on_answer` mappings with `next` or `to`;
- node or gate list-based `transitions` containing `next` or `to`;
- node/gate `navigation_contract.allowed_to`;
- gate `on_pass` / `on_fail` and `pass_to` / `fail_to`.

The older node `transition: {next: TARGET}` form remains a supported
compatibility input, but new playbooks should use one of the canonical forms
above.

For an explicit bidirectional graph, every active non-entry vertex declares
`allowed_from`. The declaration may be placed directly on the vertex or in
`navigation_contract.allowed_from`. Static and dynamic outgoing declarations
must be mirrored by the target's incoming declaration.

## Bounded dynamic routes

Use `graph_contract.dynamic_routes` for a recovery, correction, or retry path
that is chosen from runtime state rather than an authored static edge.

```yaml
graph_contract:
  dynamic_routes:
    - id: ROUTE_RETURN_TO_VALIDATED_REVIEW
      kind: recovery
      from: N_RECOVERY_DECISION
      route_key: validated_return_target
      allowed_targets: [N_REVIEW, N_CORRECTION]
      on_invalid_route: block_and_keep_current_node
      max_hops: 1
```

The compiler emits `GRAPH.ROUTE.DEF`. The runtime must call
`validate_dynamic_route` before applying a selected target; unknown route keys,
targets outside the allowlist, missing targets, invalid entry provenance, and
bound overruns block the route. `deleted_ids` reserves historical vertex IDs so
they cannot silently be reused.
