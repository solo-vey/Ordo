# APF Package Creation Hardening Gate — Aggregator Policy

## Decision

After rc.7 confirmation, `APF_PACKAGE_CREATION_HARDENING_GATE` is an aggregator gate, not a monolithic implementation gate.

## Specialized gates

The following gates own their own checks:

```text
CLI_CAPABILITY_DISCOVERY_GATE
RELEASE_HYGIENE_CLI_GATE
ANALYST_START_SMOKE_CLI_GATE
RENDER_SMOKE_CLI_GATE
INSPECT_RELEASE_ZIP_CLI_GATE
EXTERNAL_CHECK_EVIDENCE_GATE
```

## Aggregator responsibilities

`APF_PACKAGE_CREATION_HARDENING_GATE` must:

```text
1. read outputs from specialized gates;
2. classify each check as passed, failed, not-run, pending-language-tooling, or not-applicable;
3. apply package-profile readiness semantics;
4. prevent ready/go false positives;
5. forward blocking findings to PACKAGE_COMPOSITION_GATE and GO_NO_GO_REPORT.
```

## Non-responsibilities

The aggregator must not:

```text
- implement Ordo CLI commands;
- simulate CLI results with narrative text;
- duplicate release hygiene, render smoke, smoke start, or zip inspection logic;
- mark missing CLI evidence as passed;
- override runtime-capable no-go status when required evidence is absent.
```

## Clean-runtime note

`clean-runtime` is a required external check for compiled runtime and hybrid profiles. Until a separate APF gate is explicitly approved, it is represented as a required check result under the release hygiene / external evidence model and recorded in:

```text
reports/cli_evidence/clean_runtime_result.json
```
