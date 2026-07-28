# APF bidirectional graph transition contract

The APF source tree is authoritative for both sides of every active graph
edge. A node's `on_answer` transition declares where execution may go; the
target node's `allowed_from` list declares which nodes may enter it.

For every internal edge, the compiler gate requires:

```text
A.on_answer[...].next == B
B.allowed_from contains A
```

The gate fails closed on unknown targets or incoming sources, asymmetric edge
declarations, duplicate incoming sources, duplicate transitions in one
transition-list scope, terminal nodes with outgoing edges, and active
non-entry nodes without an incoming edge. Existing reachability, dead-end,
terminal-path, and cycle-policy checks remain in force.

`allowed_from` is a source contract, not an inferred convenience field. The
validator does not repair or infer missing declarations. Converging branches
that reach the same target remain valid when they are declared in separate
answer scopes.

This contract is enforced by `cli/ordo/graph_validation.py`, consumed by the
CLI linter/compiler, and therefore blocks package compilation and release
builds when the source graph is inconsistent. It changes authoring validation,
not runtime transition semantics.
