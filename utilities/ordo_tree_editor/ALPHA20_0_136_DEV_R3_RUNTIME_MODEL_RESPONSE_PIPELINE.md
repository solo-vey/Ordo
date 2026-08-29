# alpha.20.0.136-dev

Introduces a generic runtime model-response pipeline:

`PARSE -> NORMALIZE -> VALIDATE -> DRY COMMIT -> REPAIR RETRY -> COMMIT`

## Covered paths
- normal/compiled LLM execution;
- recovery conversation;
- semantic-plan execution keeps its existing stricter 3-attempt validator;
- semantic recovery keeps its bounded schema-repair validator.

## Generic guard
The guard:
- requires a JSON object;
- normalizes legacy `state_updates` to StatePatch;
- runtime-owns `base_revision`;
- applies safe metadata normalization;
- validates StatePatch against exact allowed write paths;
- validates route_key against the route allowlist;
- dry-runs the exact atomic commit before execution continues;
- retries the model up to 3 times with exact runtime validation errors.

If the contract remains unsatisfied, execution halts with
`contract_unsatisfiable_by_model`; invalid model data is never committed.

No playbook/domain source was changed.
