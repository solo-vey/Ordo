# M74.0 — Language Trust and Capability Maturity Baseline

M74.0 accepts the strategic audit findings and corrects the trust semantics of the language baseline before adding new behavior.

## Decision

Conversation Scope Guard remains an optional, language-integrated specification. Its current regression evidence is reclassified as specification and cross-artifact consistency evidence.

It is not yet represented as:

```text
toolchain-integrated
runtime-enforced
model-benchmarked
production-recommended
```

## CSG maturity at M74.0

```yaml
specification:
  status: language_integrated
schema_support:
  status: partial
toolchain_support:
  status: not_started
runtime_enforcement:
  status: not_started
model_benchmark:
  status: not_run
production_recommendation:
  status: not_ready
```

## Gate correction

The former `G_CSG_RELEASE_READY` is retained as a legacy alias for specification release only. New canonical gates are:

```text
G_CSG_SPEC_RELEASE_READY
G_CSG_TOOLCHAIN_READY
G_CSG_MODEL_BENCHMARK_READY
G_CSG_PRODUCTION_READY
```

Only `G_CSG_SPEC_RELEASE_READY` passes at M74.0.

## Trust rule

A validation report MUST state what was actually executed. Terms such as `regression`, `validated`, and `passed` MUST be qualified by scope when they do not include real runtime or model execution.
