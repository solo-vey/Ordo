# M46.7 Pre-release candidate consolidation

Status: passed.

Scope: consolidate the M46 pre-release candidate after M46.1–M46.6 without adding new language semantics.

## What changed

- Kept M46.1–M46.6 functionality intact.
- Added source archive hygiene checks to `ordo repo-check`.
- Removed generated package artifacts from the source archive.
- Kept only `.gitkeep` placeholders inside package `compiled/`, `reports/`, `runtime/`, and `generated_outputs/` directories.
- Updated README, CHANGELOG, CLI docs and book Markdown only.
- Did not regenerate the book PDF.

## Why

Generated package artifacts can make a pre-release archive look validated even when the files are stale. M46.7 makes the source package cleaner: package reports, compiled IR, runtime traces and generated outputs must be produced by the current CLI run.

## Validation summary

- `repo-check`: passed.
- CLI unit tests: passed.
- Active package `lint/compile/test/coverage`: passed.
- History Event output flow: passed through `go-no-go`.

## Known limitations

- `go-no-go` remains a deterministic helper and does not execute an AI model.
- Rendered artifact validation checks declared contract values and required mappings, not arbitrary business semantics.
- Generated artifacts are excluded from the source archive but can be regenerated from package inputs.
