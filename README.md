# Ordo — AI Process Language and Applied Runtime Framework

Ordo is a language and framework for designing, validating, executing, testing, and improving structured AI-assisted processes. The repository contains the language specification, runtime contracts, Applied Process Factory (APF), reference playbooks, command-line tooling, tests, documentation, books, and empirical evidence.

> Latest canonical packaged baseline: `ordo-2026.07.17-rc.10`  
> Language: `0.14.0-rc.1` · Framework: `0.6.0-rc.1`
>
> The `main` branch may contain validated documentation and tooling changes merged after that packaged baseline. Release identity files and gate reports remain the source of truth for packaged releases.

## Quickstart

The primary first-use path is a language-model chat. Python is optional.

1. Download the [`chat-first starter ZIP`](examples/chat_first_playbook_starter/ORDO_CHAT_FIRST_PLAYBOOK_STARTER.zip).
2. Upload the ZIP to a new language-model chat.
3. Paste the [`starter prompt`](examples/chat_first_playbook_starter/source/START_PROMPT.md).
4. Answer the model's short clarification sequence and approve the first playbook draft.
5. Ask the model to test the playbook, explain any failures, and improve it before returning the final package.

No local installation is required for this route. The starter uses a small weekly-status process to demonstrate `create → validate → dry-run → improve → package` in one chat.

See [`docs/QUICKSTART.md`](docs/QUICKSTART.md) for the complete chat walkthrough and the optional CLI validation path.

## Documentation

Use [`docs/README.md`](docs/README.md) as the canonical documentation map.

The main routes are:

- [Quickstart](docs/QUICKSTART.md)
- [Frequently asked questions](docs/FAQ.md)
- [Glossary](docs/GLOSSARY.md)
- [Citation metadata](CITATION.cff)
- [Language and runtime](docs/README.md#language-and-runtime)
- [Packages and authoring](docs/README.md#packages-and-authoring)
- [CLI and validation](docs/README.md#cli-and-validation)
- [Repository hygiene](docs/REPOSITORY_HYGIENE.md)
- [Evidence and releases](docs/README.md#evidence-and-releases)
- [Security](SECURITY.md)
- [Support](SUPPORT.md)
- [Governance](GOVERNANCE.md)
- [Contributing](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)

## Community and security

Use public issues for reproducible bugs, documentation problems, and feature proposals. See [`SUPPORT.md`](SUPPORT.md) for the correct route.

Do not disclose suspected vulnerabilities in public issues, discussions, pull requests, or social media. Use GitHub private vulnerability reporting as described in [`SECURITY.md`](SECURITY.md).

## Repository hygiene

The unified development/release contract is documented in [`docs/REPOSITORY_HYGIENE.md`](docs/REPOSITORY_HYGIENE.md). Local generated outputs belong under `.ordo-generated/`; tracked forbidden metadata and polluted release exports fail closed.

## What is included

- `language/` — language schemas, registries, runtime semantics, migration and integration layers.
- `integrations/apf/` — Applied Process Factory modules and assembly definitions.
- `packages/` — reference process and playbook packages.
- `cli/` — command-line implementation, examples, scripts, and regression tests.
- `book/` — English and Ukrainian source and compiled book materials.
- `empirical_evidence/` — normalized evidence records plus immutable raw evidence.
- `benchmarks/` — benchmark datasets, schemas, taxonomy, and evaluation artifacts.
- `docs/` — canonical documentation map, quickstart, concepts, design decisions, testing, publication, handoff, and audit documentation.
- `manifests/` and `reports/` — release identity, backlog, checksums, validation, and closure evidence.

## Packaged release verification

The RC10 packaged baseline was produced by the sanctioned release builder and passed:

- 596 tests, 0 failures;
- 4 of 4 package lints;
- release manifest synchronization;
- root hygiene checks;
- clean post-unpack checksum verification for 4,698 files.

These figures describe the packaged RC10 baseline, not every later commit on `main`.

See [`reports/delivery/current/DELIVERY_GATE_REPORT.json`](reports/delivery/current/DELIVERY_GATE_REPORT.json), [`reports/self-check/current/FINAL_PACKAGE_SELF_CHECK_REPORT.json`](reports/self-check/current/FINAL_PACKAGE_SELF_CHECK_REPORT.json), and [`manifests/RELEASE_IDENTITY.json`](manifests/RELEASE_IDENTITY.json).

To verify a downloaded package:

1. Verify the external SHA-256 file supplied with the archive.
2. Extract the archive into a clean directory.
3. Verify every entry in `SHA256SUMS.txt`.
4. Review `reports/delivery/current/DELIVERY_GATE_REPORT.json` and `reports/self-check/current/FINAL_PACKAGE_SELF_CHECK_REPORT.json`.
5. Confirm release versions in `manifests/VERSION_STATE.json` and `manifests/RELEASE_IDENTITY.json`.

```bash
sha256sum -c ORDO_ARF_CANONICAL_ORDO_2026_07_17_RC10.zip.sha256
unzip ORDO_ARF_CANONICAL_ORDO_2026_07_17_RC10.zip
cd ORDO_ARF_CANONICAL_ORDO_2026_07_17_RC10
sha256sum -c SHA256SUMS.txt
```

## Development and validation

The release gate is defined by [`docs/policies/DELIVERY_POLICY.md`](docs/policies/DELIVERY_POLICY.md). The sanctioned archive builder is [`tools/build_release_archive.py`](tools/build_release_archive.py). Local generated outputs belong under `.ordo-generated/` and must not be committed.

## Evidence integrity

Files under `empirical_evidence/raw_evidence/` may be immutable source artifacts. Their original language and byte identity are intentionally preserved. Canonical indexes, manifests, normalized records, and reports provide English metadata and SHA-256 provenance.

## License

The project is distributed under the PolyForm Noncommercial License 1.0.0. See [`LICENSE.md`](LICENSE.md), [`COMMERCIAL_LICENSE.md`](COMMERCIAL_LICENSE.md), and [`NOTICE.md`](NOTICE.md). Commercial use requires a separate commercial license.

## Project status

This repository is an active release-candidate codebase. Use release identity and gate reports as the source of truth for packaged releases. Historical transfer folders and archived milestone reports are retained for provenance and are not the current project front door.
