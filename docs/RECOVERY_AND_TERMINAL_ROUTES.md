# Recovery Routes and Terminal States

Correctable input, validation, and materialization failures must not silently
end an Ordo workflow. Author explicit `failure_routes` on a node or executable
gate so graph validation and the runtime share the same route.

```yaml
failure_routes:
  - kind: input
    classification: recoverable
    next: N_INPUT_RECOVERY
```

A `recoverable` route must target a non-terminal in-graph vertex. A `terminal`
route must target a declared `terminal: true` vertex or an explicitly declared
external terminal target.

For unmatched input, guided intake follows the `kind: input` route after the
configured attempts are exhausted. If no route is declared, it records a
blocked checkpoint at the current node rather than silently terminating the
workflow. The analyst can retry from that node later.

Vertices whose IDs start with `STOP` are reserved for explicit terminal stops.
They must declare `terminal: true`, have an incoming route unless they are the
entry vertex, and be reachable from the entry. Graph validation reports a
dedicated error when route edits leave a STOP node unconnected or unreachable.
