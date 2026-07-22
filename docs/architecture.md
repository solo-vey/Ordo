# Ordo architecture

Core pipeline:

```text
Ordo Source YAML
→ lint
→ compile
→ Semantic JSON IR
→ tests / coverage
→ helper runner / guided intake
→ reports / package
```

Key contours:

- `language/` — normative specification.
- `cli/` — minimal toolchain.
- `packages/` — validated Ordo packages.
- `book/` — learning documentation.


## M42 lean root note

Legacy registry-site, dashboard, publication and old playbook artifacts were removed from the lean workspace; the current source of truth is `language/`, `packages/`, `cli/`, `docs/`, and `book/`.
