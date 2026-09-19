# Node Responsibility and Process Decomposition

Do not mechanically split a node by copying its question and transitions. A
split must preserve graph connectivity, state ownership, gate bindings, and
any declared cycle region.

## Responsibility check

Add an optional source policy:

```yaml
node_responsibility_policy:
  mode: strict
```

Then run:

```bash
ordo validate-node-responsibilities path/to/package
```

The validator classifies declared or observable responsibilities as
`collection`, `analysis`, `drafting`, `confirmation`, `routing`, or
`technical`. In `strict` mode a node with more than one classification is a
blocking authoring defect. In the default `advisory` mode it is reported as a
warning for incremental adoption.

For unambiguous authoring, set `responsibility_kinds` explicitly on the node
instead of relying on structural classification.

## Plan the split without mutation

```bash
ordo inspect-node-split path/to/package \
  --node N_COMPOUND \
  --replacement N_COLLECT \
  --replacement N_ANALYSE
```

The command writes `reports/node_split_impact_report.json` and never changes
the source. Its preservation surface lists incoming and outgoing edges, touched
gates, containing cycles, direct state reads/writes, and state-lineage owners
and consumers. Rewire and validate the source explicitly after reviewing that
report; no automatic split can safely choose ownership or route order for the
author.
