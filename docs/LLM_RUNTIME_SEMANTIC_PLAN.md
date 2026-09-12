# Compiled LLM Runtime Semantic Plan

`compiled/llm_execution_plan.json` is a deterministic, derived projection of
canonical `source/program.ordo.yaml`. It is not a second authoring format and
must never replace YAML as the semantic source of truth.

## What the plan contains

- compact LLM phases: only the question, answer contract, clarification policy,
  projected state fields, projected resource references and permitted runtime
  routes;
- runtime-only elements: gates, operations, document generation and terminals;
- recursive resource dependency closure and declared includes;
- canonical YAML SHA-256 and semantic IR SHA-256 bindings.

Default-satisfiable immutable state fields are provided by runtime and are not
presented as LLM dependencies. Raw YAML DSL, gate conditions and runtime
operations are intentionally not rendered into LLM instructions.

## Lifecycle

Run `ordo compile PACKAGE`. It writes the IR and semantic plan together. Verify
an existing plan explicitly with:

```bash
ordo validate-llm-plan compiled/llm_execution_plan.json \
  --source source/program.ordo.yaml \
  --ir compiled/program.ir.json
```

Runtime helpers validate the plan when it exists. Missing, stale, malformed or
unresolved plans are fail-closed; a helper must not silently fall back to raw
YAML or an earlier plan.

The IR semantic hash excludes the intentional anti-leak canary value and
compile timestamp. This keeps the plan reproducible while still detecting a
meaningful IR change.
