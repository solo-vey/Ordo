# alpha.20.0.109-dev — Show Data Flow

Adds a read-only logical data-lineage view separate from execution control flow.

- New top-level `Show Data Flow` workspace.
- Projects analyst-provided state, derived/internal state, documents, artifacts and archives.
- Derives relationships from declared state reads/writes, output/rematerialization contracts, bindings/templates and package resource references.
- Selecting an entity highlights its complete upstream/downstream lineage and dims unrelated entities.
- Right-side inspector shows current runtime value when available plus producing/consuming execution nodes.
- Execution-node links jump back to Show Tree.
- `Explain with model` starts a focused read-only conversation about the selected variable/document/artifact.
- This projection never becomes executable control flow and does not change playbook semantics.
