# Ordo Tree Editor 0.2.0-alpha.20.0.172-dev

- Fix Source Data Flow / Variable Passports model assistant wiring.
- `Explain with model` now resolves the active entity from the selected Data Flow mode instead of always reading reconstructed lineage selection.
- Source authoring topology passes its own incoming/outgoing relation context to the existing Data Flow assistant endpoint.
- Assistant controls remain available in Source Data Flow when a model is configured.
- Switching source entities clears stale assistant context.
- Canonical Ordo, compiler semantics, and runtime semantics are unchanged.

## Portable launcher fix
- Removed machine-specific default `ORDO_PYTHON` path from distribution defaults.
- Launcher now auto-detects a usable Python 3.10+ interpreter with PyYAML (`python3`, then `python`) unless `ORDO_PYTHON` is explicitly set.
- Explicit invalid `ORDO_PYTHON` fails with a focused diagnostic instead of silently falling back.
