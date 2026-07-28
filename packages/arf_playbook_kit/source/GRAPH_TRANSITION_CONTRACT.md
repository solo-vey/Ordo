# Graph transition contract

The playbook source must declare both directions of every active internal
transition. If a node `A` declares `next: B`, the target node `B` must list
`A` in `allowed_from`.

The compiler gate rejects:

- unknown source or target IDs;
- asymmetric `next` / `allowed_from` declarations;
- duplicate incoming sources or same-scope transition declarations;
- outgoing transitions from terminal nodes;
- active non-entry nodes without an incoming edge;
- unreachable active nodes and active dead ends.

Converging branches are valid when each branch declares the same target in its
own answer scope. `allowed_from` is explicit source contract data; it is not
inferred or repaired during compilation. This validation protects package
authors from shipping a graph whose visible route differs from its declared
entry contract.
