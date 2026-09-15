# Cross-Artifact Contract

`cross_artifact_contract` makes the authoring and delivery surfaces of a
document mutually auditable before a package is accepted. It is opt-in; when
enabled in `strict` mode, failures block lint and compilation without changing
business state or rendered files.

```yaml
cross_artifact_contract:
  version: "1.0"
  mode: strict
  documents:
    - id: SUMMARY
      template: templates/summary.md
      bindings:
        customer_name: state.customer_name
      validator:
        expected_headings: [Customer Details]
      finalization:
        node: N_FINALIZE
        writes: [state.final_status, state.metadata_version]
        rendered_artifact: rendered/summary.md
        rendered_fields: [customer_name, final_status, metadata_version]
```

The validator checks these pairs:

- template headings ↔ validator expectations, in both directions;
- template placeholders ↔ explicit bindings ↔ declared state paths;
- finalization contract ↔ actual writes of the named node;
- finalization state values ↔ rendered output when a runtime state file is
  supplied or available.

Heading comparisons normalize case, punctuation and whitespace. Optional
`semantic_aliases` can declare accepted equivalent headings; validation does
not rely on brittle literal-only matching.

Every issue records `owner_layer`, `mismatch_class`, `source artifact`, and a
`remediation_target`. Missing runtime values are warnings marked as a
business-data condition; malformed contract surfaces are blocking contract or
validator defects.

Run it independently with:

```text
ordo validate-cross-artifact-contract PACKAGE_PATH --state STATE.yaml
```
