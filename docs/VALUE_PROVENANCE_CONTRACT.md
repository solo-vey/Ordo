# Value Provenance Contract

`value_provenance_contract` prevents examples, templates, and model proposals
from silently becoming accepted state. Each state-changing answer must carry a
source label. A value becomes confirmed only when the analyst supplies it and
sets `analyst_confirmed: true`.

```yaml
value_provenance_contract:
  version: "1.0"
  mode: strict
  fields:
    - state_path: risk_name
      allowed_provenance: [analyst, model_derived, automatic, default, reference]
      reference_policy: draft_only
      default_policy: explicit_only
      confirmation_node: N_RISK_NAME_CONFIRM
```

Submit a state-changing value with an explicit envelope:

```yaml
value: Counterparty concentration
provenance: analyst
analyst_confirmed: true
```

`reference`, `default`, `automatic`, and `model_derived` values are preserved
only as visible drafts and route to the declared confirmation node. They never
mutate accepted business state by themselves.

Validate the declaration with:

```bash
ordo validate-value-provenance PACKAGE
```
