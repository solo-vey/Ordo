# 10. Compiler and Linter Rules

## Compilation errors

The compiler MUST fail when:

1. A `gate` has no `method`.
2. A `gate` has no `trust_class`.
3. `method` and `trust_class` are incompatible.
4. `execution_mode` is missing.
5. `control_level` is missing.
6. A `strict` program has no tests for mandatory gates/assertions.
7. A compiled IR object still uses unresolved local IDs where namespaced IDs are required.
8. An `include` has no `version`.
9. A layer conflict exists without explicit override.
10. A `NODE.DEF` with constrained `allowed_answers` has no `on_unmatched_input`, unless it explicitly sets `unmatched_policy: impossible_by_source` with justification.

## Warnings

The linter SHOULD warn when:

1. FREEFORM incident threshold is exceeded.
2. A `self_verification` gate has no evidence protocol.
3. A `self_consistency` gate has `runs < 3`.
4. `chat_internal` uses critical hard gates without end-of-run audit.
5. `light` control level contains many mandatory gates and may actually be `standard`.
6. `strict` control level uses too much FREEFORM without coverage.

## Projection rules

Compiler MUST project `ASSERTION.DEF` into:

```text
runtime checks
test expectations
debug violation classification
coverage targets
```

The projection MUST preserve source traceability.


## EXECUTION_TRACE compilation rules (M72.2)

The source-level `execution_trace:` block compiles to exactly one `EXECUTION_TRACE.DEF` operation. The compiler MUST normalize omitted values to `enabled: true`, `capture_level: standard`, JSON append-only storage at `runtime/execution_trace.json`, and deterministic replay. Unknown capture or replay modes are compile errors. The compiled operation is configuration for one trace per runtime `RUN`; runtime event objects are never embedded into compiled IR.

## Optional flow reuse rules (BL-ORDO-007)

`FLOW.JOIN` and `SHARED.TAIL.REFERENCE` are optional authoring constructs. Explicitly duplicated tails remain valid. The compiler MUST NOT fail solely because reusable flow was not extracted, and MUST NOT perform automatic extraction.

When either construct is authored, invalid IDs, unresolved targets, recursive references, incompatible state contracts, unresolved namespace mappings, or newly introduced forbidden cycles are compilation errors. Duplicate-tail detection may emit `FLOW_REUSE_CANDIDATE` as advisory output only.
