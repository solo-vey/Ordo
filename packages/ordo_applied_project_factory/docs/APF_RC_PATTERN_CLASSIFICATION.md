# APF RC Pattern Classification — M63.1

This table updates APF language-pattern candidate classification for rc.1. It is not an IR/opcode implementation.

| Pattern | Classification | Status | M63.1 decision |
|---|---|---|---|
| `INPUT.POLICY` | schema_pattern_or_subflow | usable in APF; candidate for future generic schema support | no core promotion in rc.1 |
| `OUTPUT.CANDIDATE.CATALOG` | documentation/schema pattern | APF-local now; candidate for standard module pattern | document |
| `TERMINAL.OUTPUT.BIND` | APF subflow / possible future IR concept | keep APF-local for rc.1 | future review |
| `TREE.AUTHOR.PROGRESSIVE` | APF workflow pattern | document as reusable applied-module pattern, not core opcode yet | document |
| `NODE.REVIEW` | applied-module review pattern | document and test in APF; future generic review layer candidate | document |
| `BRANCH.REVIEW` | applied-module review pattern | document and test in APF; future generic review layer candidate | document |
| `SUBTREE.REVIEW` | applied-module review pattern | document and test in APF; future generic review layer candidate | document |
| `TREE.NORMALIZE` | adapter pattern | APF-local, useful for future import utilities | APF-local |
| `DIALOGUE.EXTRACT` | AI-assisted extraction pattern | APF-local; do not make deterministic opcode yet | APF-local |
| `TEMPLATE.RECIPE` | template authoring pattern | strong candidate for standard template-layer docs | standard docs candidate |
| `TEMPLATE.MOCK_RENDER` | validation/review pattern | strong candidate for CLI/template tooling later | future tooling |
| `VALIDATION.HANDOFF.TAIL` | reusable applied-module tail | document as standard pattern; do not hardcode into core | document |
| `FLOW.JOIN` | future IR candidate | backlog, because current YAML can express joins but not canonically | future IR backlog |
| `SHARED.TAIL.REFERENCE` | future IR candidate | backlog, because reusable subflow references need stable semantics | future IR backlog |
