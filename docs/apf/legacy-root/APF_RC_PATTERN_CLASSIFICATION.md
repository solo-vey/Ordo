# APF RC Language Pattern Classification — M63.3

Status: design/classification-only. This document updates the M62.3/M63.1 classification for APF `v0.1.0-rc.1` and does not introduce new IR objects, opcodes, CLI commands, or source YAML migrations.

## Decision rule

APF rc.1 remains a standard applied module. APF patterns are promoted only through a separate evidence-based language design milestone. M63.3 only classifies their current release-candidate status.

| Pattern | Classification | RC status | M63.3 decision |
|---|---|---|---|
| `INPUT.POLICY` | schema_pattern_or_subflow | usable in APF rc.1; candidate for future generic schema support | keep APF-local / schema convention; no core opcode |
| `OUTPUT.CANDIDATE.CATALOG` | documentation/schema pattern | APF-local now; candidate for standard module pattern | document; no runtime promotion |
| `TERMINAL.OUTPUT.BIND` | APF subflow / possible future IR concept | keep APF-local for rc.1 | future review only |
| `TREE.AUTHOR.PROGRESSIVE` | APF workflow pattern | reusable applied-module authoring pattern | document; not core opcode |
| `NODE.REVIEW` | applied-module review pattern | document and test in APF; future generic review layer candidate | document; no IR promotion |
| `BRANCH.REVIEW` | applied-module review pattern | document and test in APF; future generic review layer candidate | document; no IR promotion |
| `SUBTREE.REVIEW` | applied-module review pattern | document and test in APF; future generic review layer candidate | document; no IR promotion |
| `TREE.NORMALIZE` | adapter pattern | APF-local; useful for future import utilities | APF-local; future utility candidate |
| `DIALOGUE.EXTRACT` | AI-assisted extraction pattern | APF-local; not deterministic enough for opcode | APF-local; do not make deterministic opcode |
| `TEMPLATE.RECIPE` | template authoring pattern | strong candidate for standard template-layer docs | standard docs candidate |
| `TEMPLATE.MOCK_RENDER` | validation/review pattern | strong candidate for CLI/template tooling later | future tooling candidate |
| `VALIDATION.HANDOFF.TAIL` | reusable applied-module tail | document as standard pattern; do not hardcode into core | standard applied-module pattern |
| `FLOW.JOIN` | future IR candidate | backlog; current YAML can express joins but not canonically | future IR backlog only |
| `SHARED.TAIL.REFERENCE` | future IR candidate | backlog; reusable subflow references need stable semantics | future IR backlog only |

## Promotion boundary

- Documentation/schema patterns may be reused by other applied modules without changing runtime semantics.
- APF subflows remain module-local until at least one other package needs the same semantics.
- `FLOW.JOIN` and `SHARED.TAIL.REFERENCE` are the only strong future IR candidates in this set.
- `validate-factory-output` remains optional/APF-local and is not part of this pattern promotion decision.

## Non-goals

- no APF branch rewrite;
- no core IR/opcode addition;
- no parent CLI command promotion;
- no breaking source YAML migration;
- no runtime execution/scoring/calibration work.
