# APF Language Pattern Candidates

Status: `classification-only`

This document records language/process-model concepts observed during APF alpha.14 review. M62.0 does not implement them as opcodes or IR objects.

## High priority candidates

| Candidate | Proposed initial home | Rationale |
|---|---|---|
| `INPUT.POLICY` | APF schema convention → language pattern | Inputs can be required, optional, absent, deferred, or produced later. |
| `OUTPUT.CANDIDATE.CATALOG` | APF schema convention | Output artifacts may be known, partial, AI-proposed, deferred, or absent. |
| `TERMINAL.OUTPUT.BIND` | APF reusable subflow | Terminal path readiness depends on explicit output decision. |
| `TERMINAL.READY.CHECK` | APF reusable subflow → future lint candidate | Terminal path is not complete without output/template readiness. |
| `OUTPUT.MOCK.EXAMPLE` | template review artifact standard | Templates need mock-filled examples for human review. |
| `TREE.AUTHOR.PROGRESSIVE` | APF authoring model | User can provide root-only, shallow subtree, deep subtree, or free-form logic. |
| `CURRENT.NODE.DISPLAY.BLOCK` | runtime/review rendering standard | Review mode must show mode, node, gates, state, outputs, siblings, and expected decision. |
| `FLOW.JOIN` / `SHARED.TAIL.REFERENCE` | language pattern candidate | Avoid duplicated validation/handoff tails. |
| `YAML.PATCH.SCOPED` | package authoring policy | Apply scoped patches after review closure; run minimal validation before full validation. |

## Classification rule

Do not promote a candidate directly to IR/opcode just because APF needs it.

Use this ladder:

```text
APF local subflow
→ reusable package authoring pattern
→ schema convention / lint candidate
→ formal language construct
→ runtime/IR object only when proven stable
```

## M62.0 decision

All candidates remain backlog/classification items. M62.1 imports APF as-is with integration notes. M62.3 can start extraction planning after the package is present in the current workspace.

---

# M62.3 classification update

M62.3 keeps all APF language candidates outside runtime core. The detailed classification is now maintained in:

- `docs/apf/legacy-root/APF_LANGUAGE_PATTERN_EXTRACTION_PLAN.md`
- `docs/apf/legacy-root/APF_PATTERN_CLASSIFICATION_MATRIX.md`
- `reports/apf/legacy-root/APF_PATTERN_CLASSIFICATION_MATRIX.csv`
- `reports/apf/legacy-root/APF_PATTERN_CLASSIFICATION_MATRIX.json`

Summary:

```text
Documentation / rendering / policy standards: safe to document now.
APF reusable subflows: drive future APF branch-review patch planning.
Schema conventions: define state/status vocabulary before linting.
Lint candidates: defer until APF metadata is implemented.
Future IR candidates: FLOW.JOIN and SHARED.TAIL.REFERENCE only; no M62.3 IR promotion.
```

M62.3 decision: no candidate becomes an opcode or runtime-core construct in this milestone.
