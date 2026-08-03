# Validation evidence and package integrity

BL-ORDO-091 binds every JSON report written under a package `reports/` directory
to a physical source identity and a current-run identity. A PASS therefore
records the canonical relative path, package version, file size, modification
time, SHA-256 digest, run ID, timestamp, validation-layer statuses and an
explicit `current_run` scope. A report whose source changed or whose required
layer is missing is blocked as stale or incomplete; historical reports are not
counted as current evidence.

BL-ORDO-090 verifies that a package is one coherent versioned snapshot. It
checks the manifest version, canonical source, required files, package-local
and generated `SHA256SUMS.txt` entries, build-manifest content, and current
report identities. Mixed versions, missing files, stale report identity, or
checksum drift are blocking findings. The package builder runs this check before
it writes an archive.

Standalone checks:

```text
PYTHONPATH=cli python -m ordo.cli validate-canonical-source packages/example
PYTHONPATH=cli python -m ordo.cli validate-package-integrity packages/example
PYTHONPATH=cli python -m ordo.cli validate-evidence packages/example reports/lint_report.json --required-layers parse,schema,graph
PYTHONPATH=cli python -m ordo.cli verify-reproducible-build first-build.zip second-build.zip
```

These checks are read-only; generated reports are evidence and never become a
replacement for the canonical source.
