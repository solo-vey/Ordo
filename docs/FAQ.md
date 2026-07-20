# Ordo Frequently Asked Questions

This page answers common questions about the current Ordo repository. For normative behavior, follow the linked language, runtime, package, and release sources.

## What is Ordo?

Ordo is a language and runtime framework for designing, validating, executing, testing, and improving structured AI-assisted processes. The repository includes the language specification, runtime contracts, Applied Process Factory (APF), reference playbooks, command-line tooling, tests, documentation, benchmarks, and empirical evidence.

Start with the [repository overview](../README.md) and the [documentation map](README.md).

## Is Ordo a programming language, workflow format, or prompt framework?

Ordo is a process language with schemas, runtime semantics, validation rules, execution modes, and package contracts. It can represent instructions and workflows, but its repository contract is broader than a collection of prompts or a generic YAML format.

See the [language and runtime documentation](README.md#language-and-runtime).

## What problem does Ordo solve?

Ordo makes AI-assisted processes explicit and testable. It provides structured process definitions, validation gates, execution contracts, trace and evidence mechanisms, and versioned packages so that a process can be reviewed and reproduced instead of remaining an undocumented prompt sequence.

## Does Ordo require a specific model or provider?

The repository does not define one model provider as a universal requirement. Individual integrations, benchmarks, or playbooks may declare their own execution requirements.

## What is APF?

The Applied Process Factory (APF) is the framework layer used to assemble and improve Ordo processes and playbooks from reusable modules and contracts.

See the [APF integration directory](../integrations/apf/) and the [standard module guide](../APF_STANDARD_MODULE_GUIDE.md).

## What is the difference between `main` and the packaged release?

The latest canonical packaged baseline is identified by the release manifests and gate reports. The `main` branch may contain validated documentation and tooling changes merged after that package was built.

See the [release identity](../manifests/RELEASE_IDENTITY.json) and [version state](../manifests/VERSION_STATE.json).

## Is Ordo open source?

Ordo is publicly available, but it is distributed under the PolyForm Noncommercial License 1.0.0 rather than an OSI-approved open-source license. Commercial use requires a separate commercial license.

See [LICENSE.md](../LICENSE.md) and [COMMERCIAL_LICENSE.md](../COMMERCIAL_LICENSE.md).

## Where should generated outputs go?

Local generated outputs belong under `.ordo-generated/` or temporary directories and must not be committed. Release candidates are checked against the stricter release-tree hygiene scope.

See [Repository Hygiene](REPOSITORY_HYGIENE.md).

## How are Ordo packages validated?

The CLI provides lint, compile, test, coverage, repository-check, and release-gate workflows. The quickstart uses the same golden-example runner enforced by CI.

See the [quickstart](QUICKSTART.md) and [CLI documentation](../cli/README.md).

## Where should I report a bug or propose a change?

Use public GitHub issues for reproducible bugs, documentation problems, and feature proposals. Follow [SUPPORT.md](../SUPPORT.md) to choose the correct route.

Do not report suspected vulnerabilities publicly. Use the private process described in [SECURITY.md](../SECURITY.md).
