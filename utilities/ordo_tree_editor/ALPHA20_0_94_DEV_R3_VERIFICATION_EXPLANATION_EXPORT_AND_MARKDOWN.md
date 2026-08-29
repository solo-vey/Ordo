# alpha.20.0.94-dev — Verification explanation export and Markdown

- Verification model explanations render as Markdown.
- Verification explanations are persisted into Export results JSON per check.
- Export schema bumped to `ordo.editor.verification_results.v2`.
- Each saved model explanation includes classification, model/provider metadata, locale/language, usage, and generation timestamp.
- Classification enum: `playbook_graph_defect`, `package_release_defect`, `missing_runtime_evidence_context`, `verification_tool_defect`, `inconclusive`.

No playbook/runtime execution semantics changed.
