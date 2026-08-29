# alpha.20.0.116-dev

- `Export JSON` exports the complete discovered Data Flow as a machine-readable report.
- It includes all entities, visible relations, semantic layers, final artifacts, isolated entities, diagnostics/messages, producer/consumer execution nodes and candidate unresolved resource references.
- `All` is the default graph view.
- `Issues` shows every node with a Data Flow diagnostic plus its direct incoming/outgoing neighbours as minimal context.
- A Data Flow issue indicates uncertain or missing discovered lineage; it is not by itself proof that the playbook is invalid.
