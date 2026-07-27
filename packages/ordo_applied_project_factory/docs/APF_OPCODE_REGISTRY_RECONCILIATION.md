# APF opcode registry reconciliation

The APF compiler emits four lowering operations for shared-tail flow reuse:

| Opcode | Role |
|---|---|
| `FLOW.JOIN.DEF` | Synthetic join node for converging branches. |
| `FLOW.EDGE` | Explicit lowered control-flow edge. |
| `SHARED.TAIL.DEF` | Definition of a reusable validation/handoff tail. |
| `SHARED.TAIL.REFERENCE.RESOLVED` | Resolved reference from a source tail to its canonical lowered target. |

These names are now present in both the repository canonical opcode catalog and
the embedded APF opcode catalog. They describe compiler lowering and IR
provenance; they do not promote `FLOW.JOIN` or `SHARED.TAIL.REFERENCE` into new
authoring-language syntax.

The reconciliation is enforced by a contract test that compiles the active APF
source and verifies that every emitted opcode is registered in both catalogs.
Unknown emitted operations remain blocking errors.

Older APF classification and milestone documents may still describe the
pre-reconciliation candidate status. Those records are retained as historical
provenance; this document and the active README/source contracts define the
current status.
