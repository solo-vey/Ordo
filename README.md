# Ordo — AI Process Language and Applied Runtime Framework

Ordo is a language and framework for designing, validating, executing, testing, and improving structured AI-assisted processes. The repository contains the language specification, runtime contracts, Applied Process Factory (APF), reference playbooks, command-line tooling, tests, documentation, books, and empirical evidence.

> Current canonical baseline: `ordo-2026.07.17-rc.10`  
> Language: `0.14.0-rc.1` · Framework: `0.6.0-rc.1`

[Українська версія](README_UK.md)

## What is included

- `language/` — language schemas, registries, runtime semantics, migration and integration layers.
- `integrations/apf/` — Applied Process Factory modules and assembly definitions.
- `packages/` — reference process and playbook packages.
- `cli/` — command-line implementation, examples, scripts, and regression tests.
- `book/` — English and Ukrainian source and compiled book materials.
- `empirical_evidence/` — normalized evidence records plus immutable raw evidence.
- `benchmarks/` — benchmark datasets, schemas, taxonomy, and evaluation artifacts.
- `docs/` — concepts, design decisions, testing, publication, handoff, and audit documentation.
- `manifests/` and `reports/` — release identity, backlog, checksums, validation, and closure evidence.

## Verified release status

The RC10 canonical baseline was produced by the sanctioned release builder and passed:

- 596 tests, 0 failures;
- 4 of 4 package lints;
- release manifest synchronization;
- root hygiene checks;
- clean post-unpack checksum verification for 4,698 files.

See [`DELIVERY_GATE_REPORT.json`](DELIVERY_GATE_REPORT.json), [`FINAL_PACKAGE_SELF_CHECK_REPORT.json`](FINAL_PACKAGE_SELF_CHECK_REPORT.json), and [`manifests/RELEASE_IDENTITY.json`](manifests/RELEASE_IDENTITY.json).

## Verify a downloaded package

1. Verify the external SHA-256 file supplied with the archive.
2. Extract the archive into a clean directory.
3. Verify every entry in `SHA256SUMS.txt`.
4. Review `DELIVERY_GATE_REPORT.json` and `FINAL_PACKAGE_SELF_CHECK_REPORT.json`.
5. Confirm release versions in `manifests/VERSION_STATE.json` and `manifests/RELEASE_IDENTITY.json`.

Example:

```bash
sha256sum -c ORDO_ARF_CANONICAL_ORDO_2026_07_17_RC10.zip.sha256
unzip ORDO_ARF_CANONICAL_ORDO_2026_07_17_RC10.zip
cd ORDO_ARF_CANONICAL_ORDO_2026_07_17_RC10
sha256sum -c SHA256SUMS.txt
```

## Quickstart

From the repository root, create an isolated environment, install the CLI, and run the canonical package-validation example:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ./cli
python tools/run_golden_examples.py --example package-validation
```

The command runs the same documented example enforced by CI. See [`docs/QUICKSTART.md`](docs/QUICKSTART.md) for the Process Rail and end-to-end examples.

## Development and validation

The release gate is defined by [`DELIVERY_POLICY.md`](DELIVERY_POLICY.md). The sanctioned archive builder is [`tools/build_release_archive.py`](tools/build_release_archive.py). Local generated outputs belong under `.ordo-generated/` and must not be committed.

## Evidence integrity

Files under `empirical_evidence/raw_evidence/` may be immutable source artifacts. Their original language and byte identity are intentionally preserved. Canonical indexes, manifests, normalized records, and reports provide English metadata and SHA-256 provenance.

## License

The project is distributed under the PolyForm Noncommercial License 1.0.0. See [`LICENSE.md`](LICENSE.md), [`COMMERCIAL_LICENSE.md`](COMMERCIAL_LICENSE.md), and [`NOTICE.md`](NOTICE.md). Commercial use requires a separate commercial license.

## Project status

This repository is an active release-candidate codebase. Use the release identity and gate reports as the source of truth; historical transfer folders and archived milestone reports are retained for provenance and are not the current project front door.
