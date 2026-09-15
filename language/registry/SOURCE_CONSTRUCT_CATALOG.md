# Ordo Source Construct Catalog

Canonical top-level Ordo Source constructs. The machine-readable source is `source_construct_catalog.yaml`.

| Construct | Status |
|---|---|
| `ordo` | supported |
| `module` | supported |
| `includes` | supported |
| `interaction_model` | supported |
| `process_rail` | supported |
| `conversation_semantics` | supported |
| `conversation_scope_guard` | supported |
| `hybrid_execution` | supported |
| `intent` | supported |
| `contract` | supported |
| `contracts` | supported |
| `state` | supported |
| `state_lineage` | supported — canonical state ownership, shape, consumer, registry and template-binding contract |
| `execution_trace` | supported |
| `graph_contract` | supported — canonical graph, cycle, dynamic-route and deleted-ID contract |
| `nodes` | supported |
| `gates` | supported |
| `assertions` | supported |
| `artifacts` | supported |
| `artifact_requirements` | supported |
| `coverage_rules` | supported |
| `rendered_artifact_assertions` | supported |
| `go_no_go` | supported |
| `outputs` | supported |
| `freeform` | supported |
| `prompt_registry` | supported |
| `startup_package_profile` | supported |

| `flow_reuse` | supported |
| `runtime_capabilities` | supported |

## `graph_contract` forms

`graph_contract` is the canonical source contract for the executable graph.
It supports `entry_node`, declared external terminals, explicit incoming-edge
policy, declared cycle regions, `deleted_ids`, and bounded `dynamic_routes`.

A dynamic route has an `id`, `from`, runtime `route_key`, non-empty
`allowed_targets`, an explicit `on_invalid_route` fail-closed behavior, and a
positive bounded `max_hops`. Its targets are validation-visible graph edges;
authors do not need to add artificial static transitions for recovery,
correction, or retry returns.
