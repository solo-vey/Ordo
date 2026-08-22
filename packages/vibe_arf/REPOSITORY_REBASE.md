# Vibe ARF repository rebase

This package is the repository-native Vibe ARF source for release `0.1.2`.

The upstream `0.1.1` archive was an autonomous snapshot. Its embedded Ordo
language and CLI are intentionally not versioned here: they would become a
second semantic authority. The release builder stages the current repository
`language/` directory and `cli/ordo/` package at build time instead.

The package-local `canonical_support/guides/` and `canonical_support/output_templates/`
remain because they are Vibe authoring contracts, not an Ordo-language fork.

Generated reports, compiled/runtime output, editor artifacts, caches, and
binary dependency snapshots are excluded from Git source. A release therefore
records exactly which repository revision supplied the language and CLI.

## Distribution profiles

- `EDIT`: full authoring source, templates, patterns, validators, current Ordo language, and CLI.
- `CLI_RUN`: runtime-capable projection with the same current Ordo language and CLI.
- `MODEL_RUN`: chat-oriented projection without embedded CLI runtime.

Use `python tools/build_vibe_arf.py --output-dir dist/vibe_arf` from the
repository root to build all three deterministic ZIP artifacts.
