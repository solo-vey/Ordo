# CSG Integration Line

## Maturity note introduced by M74.0

The CSG line distinguishes specification consistency from toolchain, runtime, model-benchmark, and production readiness.

Current maturity:

```yaml
specification: language_integrated
schema_support: integrated
toolchain_support: integrated
runtime_enforcement: integrated_helper_runner
model_benchmark: passed_cross_model_repeated_runs
production_recommendation: ready
```

## CSG-0 — Scope and Language Dependency

Status: completed — specification PASS

## CSG-1 — Deviation Classification Contract

Status: completed — specification PASS

## CSG-2 — Strictness and Escalation Policy

Status: completed — specification PASS

## CSG-3 — Response and State-Protection Rules

Status: completed — specification PASS

## CSG-4 — Authoring-Flow and Package Integration

Status: completed — specification PASS

## CSG-5 — Validation, Regression, and Specification Release

Status: completed — specification consistency PASS

Validated evidence:

```text
contract and schema consistency
taxonomy and policy consistency
state-protection invariant consistency
package-binding consistency
manifest integrity
fixture coverage as declarative examples
```

Validated after M75 closure:

```text
real-model classification accuracy across three model/version targets
repeated blind-run stability
helper-runner runtime enforcement
protected/control-state separation
production thresholds, fallback and rollback readiness
```

Closure lines:

```text
M74.1 — registry and minimal CSG lint/compiler support — completed
M74.3 — empirical benchmark infrastructure and first real-model evidence — completed
M75.1 — runtime enforcement — completed
M75.2 — multi-step integration — completed
M75.3.1 — corrected cross-model repeated-run benchmark — completed
M75.4 — production thresholds, fail-closed fallback and rollback — completed
```
