# Chapter 77. Optional Flow Reuse

M77 adds a mechanism for reusing flow fragments in Ordo. The important boundary is that this is a **recommended mechanism**, not a rule forcing every playbook to split its process into reusable flows.

Reuse is appropriate when the same logic genuinely repeats and has a stable contract.

```text
duplicate stable logic
→ reuse candidate
→ namespace/state contract
→ reference resolution
→ runtime provenance
```

## Namespace and state merge

A reusable flow has its own namespace. Its state must not silently overwrite parent-process state.

Merge rules explicitly define:

```text
input mapping
local state
exported state
conflict policy
```

A conflict without a defined rule is a blocking validation error.

## Compiler lowering

The compiler resolves flow references and creates a runtime representation without introducing a second source of truth. Reuse syntax belongs to the authoring layer; compiled IR receives unambiguous resolved references and provenance.

An unresolved reference, namespace collision, or incompatible contract blocks compile or validation.

## Runtime semantics

When runtime enters a reusable flow, it preserves:

```text
caller
callee
entry transition
state mapping
return transition
provenance
```

The trace must show that logic was executed through a reused flow rather than looking like an unexplained jump between nodes.

## Advisory reuse detection

The CLI may detect similar flow fragments and recommend reuse. The recommendation is not an automatic rewrite.

```text
reuse candidate detected → advisory
```

The author decides whether the logic is semantically shared.

The main M77 principle is:

```text
reuse is optional;
conflicts are explicit;
compiler resolves;
runtime preserves provenance.
```
