# Canonical source identity

Every Ordo package has one authoritative playbook source: the path declared by
the package's `ordo.yml` `source` field (normally
`source/program.ordo.yaml`). The declared path is the only source accepted for
linting, compilation, export, and runtime confirmation.

Every package load, including compile, test, release, and package-export routes,
runs the canonical-source identity check before reading the YAML. `ordo lint
<package>` exposes the same check in its report. A PASS records the verified
relative path, package version, file size, UTC modification time, and SHA-256
digest. A caller that supplies a different path, an expected digest from a stale
copy, or a different expected version is blocked. A second file with the
canonical source filename is also blocked so an attachment/cache copy cannot
silently become authoritative.

For a standalone check:

```text
PYTHONPATH=cli python -m ordo.canonical_source packages/example
```

Use `--expected-sha256` and `--expected-version` when importing a previously
recorded identity. Use `--out report.json` to persist the read-only result.
Generated reports must be treated as evidence, never as a replacement source.
