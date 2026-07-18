# Packaging Profiles

This Ordo package supports three build profiles:

- `dev` — full editable package for development/audit.
- `runtime` — clean guided-execution package using `compiled/program.ir.json`.
- `evidence` — validation/provenance reports only.

Use:

```bash
ordo package . --profile dev --out dist/dev.zip
ordo package . --profile runtime --out dist/runtime.zip
ordo package . --profile evidence --out dist/evidence.zip
```

Runtime packages intentionally exclude `source/`, `tests/`, `run_inputs/`, `domain/`, generated outputs, release zips, and state snapshots.
