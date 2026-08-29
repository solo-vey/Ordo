# Capability Maturity Registry Values

Canonical dimensions and values for `capability_maturity`.

```yaml
specification:
  - not_started
  - draft
  - language_integrated
  - superseded

schema_support:
  - not_started
  - partial
  - integrated

toolchain_support:
  - not_started
  - design_only
  - partial
  - integrated

runtime_enforcement:
  - not_started
  - simulated
  - partial
  - enforced

model_benchmark:
  - not_run
  - planned
  - running
  - passed_with_limits
  - failed

production_recommendation:
  - not_ready
  - experimental
  - conditional
  - recommended
```

Each dimension MUST contain `status` and MAY contain `evidence`, `limitations`, and `acceptance_gate`.
