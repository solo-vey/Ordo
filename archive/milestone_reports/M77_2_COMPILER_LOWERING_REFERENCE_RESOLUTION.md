# M77.2 — Compiler Lowering and Reference Resolution

## Status

Implemented.

## Compiler behavior

Authored optional flow-reuse constructs are lowered deterministically into graph IR:

- `FLOW.JOIN` becomes a synthetic non-user-visible join node;
- every incoming branch becomes an explicit `FLOW.EDGE` to the synthetic node;
- one explicit outgoing edge connects the join to the resolved target;
- `SHARED.TAIL.REFERENCE` resolves to a qualified tail ID, entry node, and node list;
- source declarations and namespace mappings are preserved in provenance.

The compiler does not discover or rewrite duplicated tails automatically.

## Fail-closed validation

Compilation fails for:

- duplicate flow-reuse IDs;
- join declarations with fewer than two inputs;
- duplicate incoming aliases;
- missing shared tails;
- reference entry mismatch;
- incomplete or many-to-one namespace maps;
- cross-namespace `inherit`;
- non-bijective state rename maps;
- direct or indirect recursive shared-tail dependencies.

## Compatibility

Programs that do not author `flow_reuse` compile exactly as before. Explicit duplicated branches remain valid.
