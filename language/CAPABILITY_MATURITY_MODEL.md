# Ordo Capability Maturity Model

**Status:** normative language-governance convention  
**Introduced by:** M74.0  
**Purpose:** prevent specification consistency, toolchain support, runtime enforcement, model behavior, and production readiness from being reported as one undifferentiated `validated` status.

## 1. Principle

A language capability can be internally coherent without being executable, empirically verified, or production-ready. Ordo therefore records capability maturity as independent dimensions rather than a single optimistic status.

## 2. Canonical dimensions

```text
specification
schema_support
toolchain_support
runtime_enforcement
model_benchmark
production_recommendation
```

### specification

Whether the normative contract, taxonomy, invariants, examples, fixtures, and cross-artifact references are internally consistent.

Canonical values:

```text
not_started
draft
language_integrated
superseded
```

### schema_support

Whether declared Source constructs and package bindings have machine-readable schemas with deterministic validation.

Canonical values:

```text
not_started
partial
integrated
```

### toolchain_support

Whether linter/compiler/CLI mappings recognize the capability, reject invalid values, and emit canonical diagnostics or IR.

Canonical values:

```text
not_started
design_only
partial
integrated
```

### runtime_enforcement

Whether a helper runner or native runtime technically enforces the capability rather than relying only on model instruction-following.

Canonical values:

```text
not_started
simulated
partial
enforced
```

### model_benchmark

Whether real model executions have been run against representative examples and measured against declared expectations.

Canonical values:

```text
not_run
planned
running
passed_with_limits
failed
```

### production_recommendation

Whether the capability is recommended for production use at its declared trust boundary.

Canonical values:

```text
not_ready
experimental
conditional
recommended
```

## 3. Required evidence

A maturity claim MUST name its evidence.

```yaml
maturity:
  specification:
    status: language_integrated
    evidence:
      - reports/CSG_FULL_REGRESSION_REPORT.json
  model_benchmark:
    status: not_run
    evidence: []
```

A document-only consistency suite MUST NOT be presented as a model benchmark. A model self-report MUST NOT be presented as deterministic runtime enforcement.

## 4. Canonical readiness gates

Capabilities that include model-semantic behavior SHOULD use separate gates:

```text
G_<CAPABILITY>_SPEC_RELEASE_READY
G_<CAPABILITY>_TOOLCHAIN_READY
G_<CAPABILITY>_MODEL_BENCHMARK_READY
G_<CAPABILITY>_PRODUCTION_READY
```

`G_<CAPABILITY>_PRODUCTION_READY` MUST depend on the trust boundary declared by the capability. For model-semantic classification capabilities, it MUST NOT pass before a model benchmark has been executed and its acceptance criteria are satisfied.

## 5. Legacy status compatibility

The legacy phrase:

```text
integrated optional language capability
```

means only:

```text
specification.status == language_integrated
```

unless toolchain, runtime, benchmark, and production statuses are explicitly reported.

## 6. Conversation Scope Guard baseline

Historical M74.0 maturity is preserved in `reports/M74_0_CSG_MATURITY_REASSESSMENT.json`.
The current canonical maturity after M75.4 is:

```yaml
specification: language_integrated
schema_support: integrated
toolchain_support: integrated
runtime_enforcement: integrated_helper_runner
model_benchmark: passed_cross_model_repeated_runs
production_recommendation: ready
```

Current evidence is registered in `manifests/CURRENT_MATURITY_STATE.json`. Historical reports remain valid for the milestone at which they were produced but must not be used as current status.
