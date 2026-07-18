# 34. Optional Flow Reuse Model

## Status

`FLOW.JOIN` and `SHARED.TAIL.REFERENCE` are **stable optional first-class constructs**. They remain optional authoring optimizations. They are not mandatory normalization rules.

A program remains valid when equivalent branch tails are written explicitly. The compiler and linter MUST NOT rewrite duplicated branches automatically and MUST NOT fail compilation solely because reusable tails were not extracted.

## `FLOW.JOIN`

`FLOW.JOIN` declares a named convergence point for two or more explicitly listed incoming branches.

Required source fields:

- `id` — package-unique join identifier;
- `incoming` — at least two source node IDs;
- `target` — the first node of the shared continuation;
- `state_contract` — fields whose values must be compatible at convergence;
- `conflict_policy` — `reject`, `require_equal`, or `explicit_resolver`.

A join does not erase branch history. Runtime trace MUST retain the actual incoming branch and the join ID.

## `SHARED.TAIL.REFERENCE`

`SHARED.TAIL.REFERENCE` points to a separately declared reusable tail.

Required source fields:

- `id` — reference identifier;
- `tail_id` — target shared-tail identifier;
- `entry` — entry node inside the shared tail;
- `namespace_policy` — `inherit`, `qualified`, or `explicit_map`.

A reference is compile-time reuse syntax. The compiled IR MUST preserve source provenance and MUST expose the resolved target.

## Namespace model

Every join, shared tail, and reference belongs to an explicit package-local namespace. Unqualified identifiers resolve only inside the declaration namespace. Cross-namespace reuse MUST use either a qualified target or an explicit namespace map.

Namespace policies:

- `inherit` — the referenced tail executes in the caller namespace; valid only when the tail declares no private namespace-bound identifiers;
- `qualified` — all tail-local identifiers remain qualified by the tail namespace;
- `explicit_map` — the author provides a complete source-to-target namespace map.

Unresolved, partial, ambiguous, or many-to-one namespace mappings are hard failures. Namespaces MUST NOT be guessed from node names.

## State merge model

A join merges only fields listed by its `state_contract`. All other branch-local fields remain in branch provenance and are not injected into the shared continuation.

Field groups:

- `required_fields` — must exist on every incoming branch;
- `protected_fields` — must be byte-for-byte equal across all incoming branches and can never be resolved by precedence;
- `optional_fields` — may be absent and use an explicit merge rule;
- `branch_local_fields` — are never merged into the shared state.

The default merge rule is fail-closed. Supported field rules are `require_equal`, `prefer_non_null`, `prefer_left`, `prefer_right`, `explicit_resolver`, and `discard`. `prefer_left` and `prefer_right` are valid only when incoming aliases establish a deterministic ordering.

A shared-tail reference uses explicit `import_state` and `export_state` allow-lists. State not listed in these contracts remains private to its original namespace. Rename maps MUST be one-to-one.

## Conflict rules

A conflict exists when required fields are missing, protected fields differ, a field has multiple unequal values without a permitted merge rule, a resolver is missing, or a namespace/state map is ambiguous.

Conflict handling is fail-closed:

1. `reject` blocks compilation or runtime entry into the authored reuse construct.
2. `explicit_resolver` requires a declared deterministic resolver reference.
3. Protected-field conflicts always reject and cannot be overridden by a resolver.
4. No implicit last-write-wins, branch-order preference, coercion, or model-selected resolution is allowed.

A failure in an optional reuse construct does not invalidate equivalent explicitly duplicated authoring; the author may remove the construct and retain the duplicated branches.

## Advisory behavior

The linter MAY emit `FLOW_REUSE_CANDIDATE` when materially identical branch tails are detected. This is informational unless a project profile explicitly upgrades it to a warning. It can never be a compile error by default.

Automatic extraction, replacement, or mutation of authored branches is forbidden without an explicit authoring command.

## Hard failures

The compiler MUST fail only when an authored reuse construct is invalid, including:

- duplicate join/reference IDs;
- fewer than two join inputs;
- missing join target or shared tail;
- recursive shared-tail references;
- incompatible state contracts without an allowed resolver;
- unresolved namespace mappings;
- a join/reference that introduces a forbidden graph cycle.

## Promotion rule

These constructs are `stable_optional` after semantic-equivalence validation in both `ordo_applied_project_factory` and `ordo_hybrid_executor`. New references MUST declare deterministic `return_to`, enforce `max_call_depth`, preserve provenance, and fail closed on recursive entry.


## Stable runtime call contract

A shared-tail reference MUST declare `return_to` and MAY declare `max_call_depth` from 1 to 128 (default 16). Runtime appends the resolved tail ID to path history, rejects recursive entry, rejects depth overflow before state mutation, imports only allow-listed state, and returns only allow-listed exports to the declared continuation.
