# Input and Clarification Contract

`input_contract` is an opt-in, fail-closed source contract for analyst data.
It prevents missing or ambiguous answers from being silently mapped to an
unrelated state field.

```yaml
state:
  schema:
    customer_name: ""

input_contract:
  version: "1.0"
  mode: strict
  inputs:
    - id: CUSTOMER_NAME
      state_path: customer_name
      shape: string
      required: true
      responsible_node: N_COLLECT_NAME
      missing_route: N_COLLECT_NAME
      ambiguity:
        policy: clarify
        clarification_node: N_CLARIFY_NAME

nodes:
  - id: N_COLLECT_NAME
    input_contract:
      state_writes:
        customer_name: CUSTOMER_NAME
```

In `strict` mode every authored node state update must have an explicit
`state_writes` binding. The binding must point to the input whose `state_path`
it writes, and the input must name the node responsible for collection.

At runtime an optional answer envelope can explicitly identify its concept:

```yaml
value: Acme Ltd
concept: CUSTOMER_NAME
ambiguous: false
```

An absent required value is blocked and returns `missing_route`. An envelope
marked `ambiguous: true` returns `clarification_node` without mutating state.
A mismatching `concept` is rejected without mutation.

Run an independent machine-readable check with:

```text
ordo validate-input-contract PACKAGE_PATH
```
