# State Lineage Contract

`state_lineage` makes state ownership explicit before compilation. In strict
mode, every `state.schema` path must have exactly one declared owner and a
matching runtime producer unless `allow_multiple_producers: true` is explicit.

```yaml
state:
  schema:
    customer_name: ""

state_lineage:
  version: "1.0"
  mode: strict
  fields:
    - path: customer_name
      shape: string
      owner: N_COLLECT_CUSTOMER_NAME
      collection_mode: analyst_answer
      consumers: [N_REVIEW_CUSTOMER, G_CUSTOMER_READY]
      registries: [CUSTOMER_FIELD_REGISTRY]
      bindings: [CUSTOMER_SUMMARY]
  registries:
    - id: CUSTOMER_FIELD_REGISTRY
      fields: [customer_name]
  template_bindings:
    - id: CUSTOMER_SUMMARY
      fields: [customer_name]
```

The validator compares this declaration against actual `update_state` and
`writes` producers, node/gate `reads`, `inputs`, `required_fields`,
`node_context.required_state`, gate `state.*` conditions, registered fields,
and template bindings. It fails closed for missing or incompatible paths,
unowned schema fields, missing owners, duplicate producers, shape mismatches,
and unconsumed collected values.

Run it independently with:

```text
ordo validate-state-lineage PACKAGE_PATH
```
