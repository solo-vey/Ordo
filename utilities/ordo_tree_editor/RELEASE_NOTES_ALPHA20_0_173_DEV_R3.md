# ORDO Tree Editor 0.2.0-alpha.20.0.173-dev

- Portable startup bootstrap: no machine-specific Python paths.
- Detects Python 3.10+ across common versioned commands and macOS/Homebrew locations.
- If PyYAML is missing, creates a local `utilities/ordo_tree_editor/.venv` and installs runtime dependencies from `requirements-runtime.txt`.
- Explicit `ORDO_PYTHON` remains supported.
