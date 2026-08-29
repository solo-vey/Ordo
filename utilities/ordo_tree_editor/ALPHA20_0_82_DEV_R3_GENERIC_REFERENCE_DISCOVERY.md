# alpha.20.0.82-dev — generic package reference discovery

Inspector-only R3 hardening.

- References are discovered recursively across the whole node/gate source record.
- Structured package paths in fields such as `allowed_tools`, `knowledge_refs`, contracts, schemas, templates, and future extension fields are surfaced automatically.
- File-like paths mentioned inside prose/commands are surfaced only when they resolve to a real package resource.
- Duplicate references from multiple semantic origins are collapsed into one file entry while preserving origin roles.
- Python resources retain Preview + Explain with model; Markdown retains Preview / Source.
- Generated/output paths that do not exist in the source package are not falsely surfaced from prose mentions.

No playbook or runtime execution semantics changed.
