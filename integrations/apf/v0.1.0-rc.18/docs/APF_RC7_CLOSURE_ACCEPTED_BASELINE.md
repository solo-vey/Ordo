# APF rc.7 Closure — Accepted CLI Integration Contracts Baseline

## Status

```text
module_id: ordo.applied_project_factory
closure_version: v0.1.0-rc.7-closure
closed_baseline: v0.1.0-rc.7-cli-integration-contracts-confirmed
status: accepted-baseline / ready-for-next-apf-patch
blocking_issues: 0
scope_boundary: APF package/playbook creation process only; no Ordo language package changes
```

## Purpose

This closure freezes APF rc.7 as the accepted baseline for Ordo CLI integration contracts in the APF package/playbook creation process.

The closure does not implement Ordo CLI commands. It records how APF will consume external Ordo CLI evidence when those commands become available from the language/tooling package.

## Confirmed decisions

```text
APF-RC7-01 — CLI_CAPABILITY_DISCOVERY_GATE is placed immediately after PACKAGE_PROFILE_GATE.
APF-RC7-02 — package profile → required CLI checks matrix is accepted, including conditional render-smoke-test rule.
APF-RC7-03 — runtime-capable package cannot be runtime-release ready/go without required CLI evidence.
APF-RC7-04 — source/design/reference package may use explicit passed-with-deferred-cli-evidence status.
APF-RC7-05 — reports/cli_evidence/ is the standard APF evidence path.
APF-RC7-06 — graph/process node IDs use N_SHARED_TAIL_* form; reports use short *_GATE names.
APF-RC7-07 — APF_PACKAGE_CREATION_HARDENING_GATE is an umbrella/aggregator gate.
```

## Final accepted tail

```text
FINAL_COMPLETION_ARTIFACTS_GENERATION
→ PROGRAM_LEVEL_CONTRACT_REVIEW
→ PROGRAM_LEVEL_CONTRACT_APPROVAL_GATE
→ COMPILE_UTILITY_DISCOVERY_GATE
→ PACKAGE_PROFILE_GATE
→ CLI_CAPABILITY_DISCOVERY_GATE
→ DERIVED_ARTIFACT_SYNC_GATE
→ DELTA_BACKLOG_CONVENTION_GATE
→ SVG_GRAPH_GENERATOR_PACKAGING_GATE
→ START_PROMPT_PACKAGING_GATE
→ README_STARTUP_SECTION_GATE
→ RELEASE_HYGIENE_CLI_GATE
→ ANALYST_START_SMOKE_CLI_GATE
→ RENDER_SMOKE_CLI_GATE
→ INSPECT_RELEASE_ZIP_CLI_GATE
→ APF_PACKAGE_CREATION_HARDENING_GATE
→ EXTERNAL_CHECK_EVIDENCE_GATE
→ PACKAGE_COMPOSITION_GATE
→ FINAL_ARCHIVE_ASSEMBLY
```

## Boundary

```text
APF owns:
- package/playbook creation process;
- gate wiring;
- evidence contracts;
- confirmation registers;
- readiness classification.

Ordo language/tooling package owns:
- actual CLI command implementation;
- compiler/runtime/language features;
- language-level schema/opcode adoption.
```

## Closure decision

APF rc.7 is closed as accepted. Future APF work must use this closure as baseline unless a later APF patch explicitly supersedes it.
