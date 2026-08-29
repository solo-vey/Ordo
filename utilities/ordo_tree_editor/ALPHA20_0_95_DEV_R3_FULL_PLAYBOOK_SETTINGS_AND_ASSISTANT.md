# alpha.20.0.95-dev — Full Playbook Settings + AI Settings Assistant

- Playbook Settings is a full-width workspace; the graph/tree is hidden.
- The setting list is driven by Ordo language schemas plus value registries, not only by fields present in the source.
- Language-defined settings absent from the playbook are visible as `Not specified`.
- Allowed values and English meanings are shown when the language registry declares them.
- Package-specific settings remain visible but are explicitly marked package-defined.
- A read-only AI Settings Assistant can analyze the current settings in the playbook language and discuss desired changes.
- The assistant can emit a proposed YAML settings block for the user to copy manually.
- The assistant never mutates playbook source/state.
