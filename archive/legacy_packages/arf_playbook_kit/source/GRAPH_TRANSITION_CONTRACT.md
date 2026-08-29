# Graph transition contract

The playbook source may use `nodes[]` and executable top-level `gates[]` as
vertices of one process graph. A node route uses `next`; a routing gate uses
`on_pass` and/or `on_fail`. When the explicit incoming-edge policy is enabled,
both directions of every active internal transition must be declared. For
example, if node `A` declares `next: G_READY`, gate `G_READY` must list `A` in
`allowed_from`; the same rule applies from a gate to a node or another gate.

Catalogue gates that only describe a control outcome such as `on_fail: block`
are not graph vertices unless a route reaches them. They remain valid gate
definitions and do not create synthetic dead ends.

The compiler gate rejects:

- unknown node, gate, or terminal target IDs;
- asymmetric `next`, `on_pass`, `on_fail`, and `allowed_from` declarations;
- duplicate incoming sources or same-scope transition declarations;
- outgoing transitions from terminal vertices;
- active non-entry nodes or gates without an incoming edge;
- unreachable active nodes or gates and active dead ends.

Converging branches are valid when each branch declares the same target in its
own answer scope. `allowed_from` is explicit source contract data; it is not
inferred or repaired during compilation. This validation protects package
authors from shipping a graph whose visible route differs from its declared
entry contract.
