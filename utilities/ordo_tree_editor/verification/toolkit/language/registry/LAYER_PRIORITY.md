# Layer Priority Registry

Priority from highest to lowest:

```text
Core
> active Profile
> active Domain Pack
> explicitly included Libraries
> controlled FREEFORM
```

## Override rule

Lower layer MUST NOT silently override higher layer.

```yaml
override:
  target: core.G_NO_UNSUPPORTED_FACTS
  reason: "..."
  approved_by: human
```

Core-level overrides require human approval.
