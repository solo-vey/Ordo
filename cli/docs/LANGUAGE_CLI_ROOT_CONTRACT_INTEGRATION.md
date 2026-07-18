# Language / CLI Root Contract Integration

M70.2 adds a read-only `root_contract` treatment for repository roots that are release-critical but are not Ordo package roots.

The contract supports:
- required path existence;
- YAML parsing by glob;
- JSON parsing by glob;
- Python syntax parsing by glob through `ast.parse`.

It does not create package manifests, compile runtime artifacts, mutate sources, or scan delegated applied packages.

Production policy now treats `language/` and `cli/` as release-blocking `root_contract` roots. The canonical CLI example remains an optional package-level `clean-check` root, while `packages/` remains delegated.
