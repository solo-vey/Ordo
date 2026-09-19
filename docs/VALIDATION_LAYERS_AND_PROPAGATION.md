# Validation Layers and Validator Propagation

`ordo lint` is the aggregate authoring gate. Use the separate layer report
when a finding must be assigned to an owning concern rather than treated as a
generic lint error:

```bash
ordo validate-layers path/to/package
```

The resulting `reports/validation_layers_report.json` has five independent
layers, in a stable order:

1. `schema` — parsed source shape and graph-element identifiers.
2. `graph` — reachability, transitions, terminal paths, and cycle contracts.
3. `lineage` — state producer/consumer ownership and bindings.
4. `artifact` — confirmed-contract-to-artifact mapping completeness.
5. `semantic` — input, provenance, analyst interaction, correction/replay,
   and reusable-flow contracts.

Each layer carries its own status and issues. A failed layer fails the command,
while an intentionally unused optional contract is reported as `not_enabled`.

## Shipping validator changes

A package that embeds copies of canonical validators must include a root
`validator_propagation_contract.json`:

```json
{
  "schema_version": "1.0",
  "mappings": [
    {
      "canonical": "cli/ordo/graph_validation.py",
      "packaged": "cli_embedded/ordo_pkg/ordo/graph_validation.py"
    }
  ]
}
```

Validate a package against its checked-out canonical source before releasing:

```bash
ordo validate-validator-propagation path/to/package --repo-root .
```

The command compares SHA-256 bytes for every declared mapping. A missing or
drifted packaged copy is blocking, so a local validator fix cannot be claimed
as part of a release until the package carries the same implementation.
