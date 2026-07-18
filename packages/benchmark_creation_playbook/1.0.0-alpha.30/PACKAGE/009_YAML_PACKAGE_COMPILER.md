# 009. YAML Package Compiler Contract

**Backlog:** BL-BENCH-009  
**Output variant:** `PV-YAML`

## Input

- approved test-case source package;
- active Ordo language and ARF baseline;
- canonical RUN registry;
- approved document templates and evaluation contracts when available;
- versioned compiler configuration.

## Required compilation phases

1. **Preflight:** verify hashes, schema versions and source completeness.
2. **Focused scope:** declare exact graph/process layer being generated or patched.
3. **Model binding:** bind test-case entities, RUN contracts, package outputs, states and terminals.
4. **Graph materialization:** create stable node IDs, node profiles, transitions, state updates, gates and terminal nodes.
5. **Reference binding:** bind prompts, templates, contracts and schemas by explicit identifiers.
6. **Static validation:** YAML parse, schema checks, unique IDs, reachable terminals, transition integrity and required-node coverage.
7. **Semantic validation:** verify RUN semantics, correction/invalidation behavior, output allowlists and hidden-data isolation.
8. **Package assembly:** source YAML, dependency manifest, validation report, version metadata and SHA-256.

## Stability rules

- Stable node IDs are part of the public compiler contract.
- Reordering or reformatting must not alter node semantics.
- Existing released nodes must be preserved unless an approved migration or scoped patch changes them.
- The compiler must not rewrite the whole graph to implement a local change.
- `BL-BENCH-041` will add enforceable affected-node allowlists and semantic/structural diff verification; until then this remains a declared constraint, not a completed gate.

## Required outputs

- `source/program.ordo.yaml` or declared equivalent;
- compiler manifest;
- source/dependency registry;
- validation report;
- checksum manifest;
- optional human-readable compiled instructions stored outside the canonical YAML package.

## Failure conditions

Compilation fails when:

- source version is unknown;
- node IDs collide;
- a terminal is unreachable or ambiguous;
- RUN semantics drift;
- hidden/evaluator-only information enters executor-visible nodes;
- unsupported assumptions are invented;
- local patch scope cannot be proven;
- required validation evidence is missing.

## Current implementation status

The contract and authoring rail are defined. A standalone executable compiler is not yet implemented; no claim of runtime compiler readiness is made.
