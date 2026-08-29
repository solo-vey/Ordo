# 08. Library Model

Ordo Library — reusable пакет Ordo-конструкцій, який явно підключається до поточної програми.

## Include example

```yaml
include:
  - library: ordo.validation.contract_first
    version: "^0.2.0"
    as: contract_first
```

## Rules

1. No implicit imports.
2. Every include MUST specify version.
3. Every imported object MUST be resolved into a namespace.
4. Overrides MUST be explicit and human-approved when they affect Core-level behavior.

## Namespaced IDs

```text
library.contract_first.G_NO_FINAL_OUTPUT
profile.documentation.G_RENDER_VALIDATED
domain_pack.history_event.G_CONTRACT_CONFIRMED
```

## Layer priority

```text
Core
> active Profile
> active Domain Pack
> explicitly included Libraries
> controlled FREEFORM
```

## Conflict gate

Ordo v0.12 defines system gate:

```yaml
gate:
  id: G_NO_UNRESOLVED_LAYER_CONFLICT
  method: mechanical
  trust_class: deterministic
  assert: NO_UNRESOLVED_LAYER_CONFLICT
```

If a lower layer conflicts with a higher layer and no explicit override exists, execution MUST be blocked.
