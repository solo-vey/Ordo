# Proposed Language Patch Sequence

Status: `proposal`  
Target line: Ordo language package after APF rc.4-post-svg.

## Suggested order

```text
M64.0 — Language backlog intake and classification
M64.1 — Program-level contract schema convention
M64.2 — Interaction model + process rail + conversation semantics docs
M64.3 — Program-level approval gate lint/validation
M64.4 — Package profile + startup package standard
M64.5 — Derived artifact sync/hash manifest hardening
M64.6 — Graph artifact/SVG provenance standard
M64.7 — Real-module testcase generation standard
M64.8 — FLOW.JOIN / SHARED.TAIL.REFERENCE design spike
```

## Why this order

Program-level metadata is the highest-priority missing layer. It affects how every full package starts, resumes, validates, and hands off.

`FLOW.JOIN` / `SHARED.TAIL.REFERENCE` should not be rushed because it may change IR graph semantics.

## Immediate APF-compatible next step

Before changing the language package runtime core, implement APF:

```text
FUTURE-PROGRAM-CONTRACT-01
```

Then use that implementation as evidence for the language package M64.1/M64.2 design.
