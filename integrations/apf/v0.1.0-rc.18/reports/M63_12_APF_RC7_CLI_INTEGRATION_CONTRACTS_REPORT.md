# M63.12 / APF rc.7 — CLI Integration Contracts Confirmed

Status: ready / go.

## Scope

APF-only. This patch confirms external Ordo CLI integration contracts and readiness semantics for package/playbook creation. It does not implement Ordo CLI commands and does not modify the Ordo language package.

## Confirmed

```text
APF-RC7-01 CLI capability discovery placement
APF-RC7-02 package profile → required CLI checks matrix
APF-RC7-03 runtime-capable blocking semantics without required CLI evidence
APF-RC7-04 source/design deferred CLI evidence semantics
APF-RC7-05 standard evidence path reports/cli_evidence/
APF-RC7-06 node/gate naming convention
APF-RC7-07 APF_PACKAGE_CREATION_HARDENING_GATE as aggregator
```

## Gate wiring update

```text
PACKAGE_PROFILE_GATE
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
```

## Hardening gate role

`APF_PACKAGE_CREATION_HARDENING_GATE` is an umbrella/aggregator gate. Specialized CLI/release/render/evidence gates own their checks and are not duplicated inside the aggregator.

## Remaining boundary

APF consumes Ordo CLI checks as deterministic evidence when available. CLI implementation belongs to the Ordo language package.
