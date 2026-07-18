# Ordo architecture

Базовий ланцюжок:

```text
Ordo Source YAML
→ lint
→ compile
→ Semantic JSON IR
→ tests / coverage
→ helper runner / guided intake
→ reports / package
```

Ключові рівні:

- `language/` — нормативна специфікація.
- `cli/` — мінімальний toolchain.
- `packages/` — перевірювані Ordo-пакети.
- `book/` — навчальна документація.


## M42 lean root note

Legacy registry-site, dashboard, publication and old playbook artifacts were removed from the lean workspace; the current source of truth is `language/`, `packages/`, `cli/`, `docs/`, and `book/`.
