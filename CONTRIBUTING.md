# Contributing to Ordo

Thank you for considering a contribution to Ordo.

Ordo is a language, framework, runtime, evidence, and documentation project for auditable AI-assisted processes. Contributions must preserve explicit human authority, evidence provenance, deterministic behavior where required, and release integrity.

Read [`GOVERNANCE.md`](GOVERNANCE.md), [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md), [`SUPPORT.md`](SUPPORT.md), and [`SECURITY.md`](SECURITY.md) before contributing.

## Repository Language Policy

All repository files must be written in English.

The sole documentation exception is the Ukrainian translation of the authoritative English Ordo book. The Ukrainian edition must not introduce independent normative requirements.

Immutable raw evidence may preserve source-language content when translation would alter the submitted artifact or invalidate its checksum. Such evidence must be accompanied by an English inventory, normalized record, or exception report.

## Before You Start

1. Search existing issues and backlog items.
2. Reference an issue or backlog item for significant changes.
3. Keep the change narrowly scoped.
4. Do not mix unrelated cleanup with functional work.
5. Never describe a candidate, partial gate, inherited gate, or stale report as canonical.
6. Never put suspected vulnerabilities or sensitive conduct reports in public issues or pull requests.

## Contribution Categories

### Code and tooling

Provide focused tests, regression coverage, deterministic output where required, and safe temporary-file handling.

### Language and schema changes

Provide compatibility analysis, version-impact assessment, updated schemas, validators, examples, positive and negative tests, migration notes, and authoritative English documentation.

### Framework and ARF changes

Document affected stages, input/output contracts, human-authority boundaries, failure behavior, generated artifacts, and regression coverage.

### Evidence submissions

Provide:

- immutable source package;
- exact SHA-256;
- provenance and collection method;
- model and evaluator identity;
- author-assistance declaration;
- internal-access and unpublished-material declarations;
- scoring methodology;
- bounded claims;
- privacy review;
- independence level and verification status.

Do not modify raw evidence to improve formatting or language.

## Development and Testing

Follow the setup instructions in the root README.

Run focused tests first, then the complete sanctioned release or delivery gate defined by the package.

A focused PASS does not make a change release-ready.

## Generated Files

Do not commit `.ordo-generated/`.

Canonical generated artifacts may be committed only when the repository explicitly requires them. Record generator identity, update checksums, and verify reproducibility.

## Versioning

State impact on:

- language version;
- framework version;
- schema version;
- playbook `built_with`;
- evidence dataset version;
- release identity.

## Checksums and Canonical Archives

For release-bound work:

1. complete all source and derived-file updates;
2. run the full sanctioned gate;
3. generate current-run reports;
4. generate `SHA256SUMS.txt` last;
5. freeze staging;
6. build the archive;
7. unpack into a clean directory;
8. verify checksums and release identity.

## Security and Privacy

Do not submit credentials, private keys, unauthorized personal information, private repository URLs, confidential customer data, or unredacted conversations containing personal information.

Report vulnerabilities only through the private process in [`SECURITY.md`](SECURITY.md).

## Pull Requests

Use the repository pull-request template.

A pull request must reference related work, explain behavior changes, identify affected artifacts, list tests, declare version impact, disclose evidence/privacy impact, and describe migration or rollback behavior.

## Licensing

The repository uses PolyForm Noncommercial License 1.0.0 unless a file states otherwise.

By contributing, you confirm that you have the right to submit the contribution under the applicable repository license. Commercial use is not granted by the public repository license.

## Acceptance

Submission does not guarantee acceptance. Maintainers may reject or defer changes that are outside scope, insufficiently tested, unsafe, unsupported by evidence, or incompatible with release-integrity requirements.
