# Ordo Documentation

This file is the canonical map for current Ordo documentation. Start with the quickstart, then follow the route that matches your task. Historical transfer packages and milestone reports are retained for provenance but are not the documentation front door.

## Start here

- [`QUICKSTART.md`](QUICKSTART.md) — install Ordo and run the three CI-backed golden examples.
- [`FAQ.md`](FAQ.md) — answers to common project, licensing, package, and support questions.
- [`GLOSSARY.md`](GLOSSARY.md) — short definitions and links for core Ordo terminology.
- [`../CITATION.cff`](../CITATION.cff) — canonical repository citation metadata.
- [`../README.md`](../README.md) — repository overview, release distinction, and top-level entry points.
- [`../SUPPORT.md`](../SUPPORT.md) — choose the correct route for bugs, questions, proposals, security reports, and conduct concerns.
- [`../CONTRIBUTING.md`](../CONTRIBUTING.md) — contribution workflow and repository expectations.

## Security, support, and governance

- [`../SECURITY.md`](../SECURITY.md) — supported versions, private vulnerability reporting, scope, and disclosure process.
- [`../SUPPORT.md`](../SUPPORT.md) — public and private support routes.
- [`../GOVERNANCE.md`](../GOVERNANCE.md) — decision authority, review expectations, and governance changes.
- [`../CODE_OF_CONDUCT.md`](../CODE_OF_CONDUCT.md) — behavior expectations and private conduct reporting route.
- [`../CONTRIBUTING.md`](../CONTRIBUTING.md) — contribution requirements and pull-request expectations.

## Language and runtime

- [`../language/`](../language) — canonical language schemas, registries, runtime semantics, and migration layers.
- [`../language/RUNTIME_CHECKPOINTS.md`](../language/RUNTIME_CHECKPOINTS.md) — one-node, one-contract runtime checkpoint discipline.
- [`../LANGUAGE_POLICY.md`](../LANGUAGE_POLICY.md) — repository language policy.
- [`../language/ENGLISH_ONLY_REPOSITORY_POLICY_GATE.md`](../language/ENGLISH_ONLY_REPOSITORY_POLICY_GATE.md) — English-only policy gate and migration-aware enforcement.

## Packages and authoring

- [`../packages/`](../packages) — reference process and playbook packages.
- [`../integrations/apf/`](../integrations/apf) — Applied Process Factory modules and assembly definitions.
- [`../STABLE_PACKAGE_INDEX.md`](../STABLE_PACKAGE_INDEX.md) — stable package index.
- [`../APF_STANDARD_MODULE_GUIDE.md`](apf/legacy-root/APF_STANDARD_MODULE_GUIDE.md) — standard APF module guidance.

## CLI and validation

- [`../cli/README.md`](../cli/README.md) — CLI command reference and root-relative usage.
- [`REPOSITORY_HYGIENE.md`](REPOSITORY_HYGIENE.md) — development and release hygiene scopes, forbidden paths, and duplicate-nesting rules.
- [`../DELIVERY_POLICY.md`](../DELIVERY_POLICY.md) — release and delivery gate policy.
- [`../tools/run_golden_examples.py`](../tools/run_golden_examples.py) — CI-backed golden-example runner.
- [`../examples/golden_examples.json`](../examples/golden_examples.json) — machine-readable golden-example source of truth.

## Evidence and releases

- [`../manifests/RELEASE_IDENTITY.json`](../manifests/RELEASE_IDENTITY.json) — packaged release identity.
- [`../manifests/VERSION_STATE.json`](../manifests/VERSION_STATE.json) — current version state.
- [`../DELIVERY_GATE_REPORT.json`](../DELIVERY_GATE_REPORT.json) — delivery gate evidence.
- [`../FINAL_PACKAGE_SELF_CHECK_REPORT.json`](../FINAL_PACKAGE_SELF_CHECK_REPORT.json) — packaged self-check evidence.
- [`../empirical_evidence/`](../empirical_evidence) — normalized and immutable empirical evidence.
- [`../benchmarks/`](../benchmarks) — benchmark datasets, schemas, and evaluation artifacts.

## Books

- [`../book/`](../book) — English and Ukrainian source and compiled book materials.

## Documentation status rules

Current documentation should describe present behavior without milestone chronology in user-facing headings. Historical identifiers may remain where they are required for provenance. Generated reports belong under `.ordo-generated/` or temporary directories and must not become documentation entry points.
