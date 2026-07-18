# M64.0 Proposed Patch Sequence

Status: `accepted-planning-sequence / no runtime patch`

## First wave

```text
M64.1 — Program-level contract schema convention
M64.2 — Interaction model + process rail + conversation semantics docs
M64.3 — Program-level approval gate lint/profile design
```

## Later M64 candidates

```text
M64.4 — Package profile + startup package standard
M64.5 — Derived artifact sync/hash manifest hardening
M64.6 — Graph artifact/SVG provenance and annotation standard
M64.7 — Real-module testcase generation standard
```

## Design spike / possible M65

```text
FLOW.JOIN
SHARED.TAIL.REFERENCE
```

These are not quick opcodes. They may affect source YAML semantics, semantic JSON IR, compiler projection, path enumeration, graph rendering and validation tooling.

## Runtime boundary

M64.0 intentionally performs only intake and classification. It does not modify compiler behavior, CLI behavior, source schemas, runtime execution, benchmark scoring or calibration.
