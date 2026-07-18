# APF to Ordo Language Pattern Mapping

Status: `classification / no direct opcode promotion`

## Purpose

Map improvements discovered during APF work into possible homes in the Ordo language package.

## Mapping table

| APF / process discovery | Language-level candidate | Initial home | Future promotion condition |
|---|---|---|---|
| Explicit execution mode declaration | `execution_mode` / runtime profile | schema convention | promote after multiple modules use same enum and validation |
| Hybrid mode preferred | `HYBRID_EXECUTION.MODEL` | package/runtime profile standard | promote if compiler/runtime need first-class semantics |
| Runtime compilation gate | deterministic validation evidence rule | package validation standard | promote to CLI contract if reused broadly |
| Derived artifact sync gate | derived artifact freshness model | package validation standard | promote to manifest/IR hash checks if stable |
| Delta backlog convention | improvement intake metadata | release/package discipline | keep as package standard unless runtime needs it |
| Packaged SVG utility | graph artifact standard | companion utility standard | promote only graph metadata/provenance, not renderer implementation |
| Compile/start prompt gates | package startup contract | package standard | promote to full-package schema/lint rule |
| Program-level metadata prompt | `PROGRAM.DEF`, `INTERACTION.MODEL`, `PROCESS_RAIL.DEF`, `CONVERSATION.SEMANTICS` | P0 schema convention | after APF implementation proves stable |
| Shared APF tail duplication | `FLOW.JOIN`, `SHARED.TAIL.REFERENCE` | future IR candidate | requires separate compiler/IR design milestone |
| Real module confusion tests | testcase generation utility standard | companion testing tool | promote if accepted as language QA line |
| Complex output templates | two-tier rendering model | renderer capability standard | already suitable for docs/language guide; runtime promotion depends on renderer implementation |
| YAML attribute confusion | schema documentation contract | book/schema docs | should become mandatory docs rule before runtime change |

## Rule

A useful APF pattern is not automatically an opcode.

Promotion should happen only when:

```text
- it appears in more than one package/module;
- the package-standard form is stable;
- lint validation can define it clearly;
- runtime/IR needs it for execution, not just documentation;
- migration impact is understood.
```
