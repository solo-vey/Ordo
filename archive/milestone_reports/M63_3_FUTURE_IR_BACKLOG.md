# M63.3 Future IR / Tooling Backlog

Status: post-M63.3 backlog. None of these items are blockers for APF `v0.1.0-rc.1` release-candidate acceptance.

## Future IR candidates

- `FLOW.JOIN`: design canonical join semantics for source YAML and Semantic JSON IR. Current YAML can express practical joins, but not as a first-class canonical construct.
- `SHARED.TAIL.REFERENCE`: design reusable subflow/tail-reference semantics after join behavior is stable.

## Future CLI / tooling candidates

- `validate-factory-output`: remains APF-local or optional until parent CLI semantics are designed.
- `TEMPLATE.MOCK_RENDER`: candidate for future generic template tooling.
- `TEMPLATE.RECIPE`: candidate for standard template-layer documentation and possibly future validation support.
- Generic review-layer support for `NODE.REVIEW`, `BRANCH.REVIEW`, and `SUBTREE.REVIEW` after multiple applied modules use the pattern.

## APF-local / standard applied-module patterns

- `INPUT.POLICY`, `OUTPUT.CANDIDATE.CATALOG`, `TERMINAL.OUTPUT.BIND`, and `TREE.AUTHOR.PROGRESSIVE` remain usable inside APF rc.1 without requiring parent runtime migration.
- `TREE.NORMALIZE` and `DIALOGUE.EXTRACT` remain adapter / AI-assisted extraction patterns, not deterministic opcodes.
- `VALIDATION.HANDOFF.TAIL` is documented as a reusable applied-module tail, not hardcoded into language core.
