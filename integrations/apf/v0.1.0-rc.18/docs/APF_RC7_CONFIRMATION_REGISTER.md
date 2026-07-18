# APF rc.7 Confirmation Register

Status: confirmed
Scope: APF package/playbook creation process only
Language package changes: none

## APF-RC7-01 — CLI capability discovery placement

```text
CONFIRMED:
CLI_CAPABILITY_DISCOVERY_GATE is placed immediately after PACKAGE_PROFILE_GATE.
```

Reason: package profile determines required external checks.

## APF-RC7-02 — Package profile → required CLI checks matrix

```yaml
source_authoring:
  inspect-release-zip: required
  render-smoke-test: required_if_rendered_templates_present

compiled_runtime:
  clean-runtime: required
  release-hygiene: required
  analyst-start-smoke-test: required
  inspect-release-zip: required
  render-smoke-test: required_if_rendered_templates_present

hybrid:
  clean-runtime: required
  release-hygiene: required
  analyst-start-smoke-test: required
  inspect-release-zip: required
  render-smoke-test: required_if_rendered_templates_present

handoff:
  inspect-release-zip: required
  release-hygiene: recommended
  render-smoke-test: required_if_rendered_templates_present

reference_only:
  inspect-release-zip: recommended
  render-smoke-test: not_applicable_unless_rendered_templates_present
```

## APF-RC7-03 — Runtime-capable package readiness

```text
Runtime-capable package cannot receive runtime-release ready/go without required CLI evidence.
```

Status rules:

```text
required CLI exists + check passed → passed
required CLI exists + check failed → blocked
required CLI missing because language tooling unavailable → pending-language-tooling / blocked-pending-language-tooling
runtime-capable package without required CLI evidence → no-go-for-runtime-release
```

## APF-RC7-04 — Source/design deferred evidence

```text
Source/design/reference package may receive ready/go with explicit passed-with-deferred-cli-evidence if deferred CLI checks are non-blocking for the declared package profile and the package is not claimed as runtime-release ready.
```

## APF-RC7-05 — CLI evidence path

```text
reports/cli_evidence/
```

Standard evidence files:

```text
cli_capability_discovery_result.json
release_hygiene_result.json
clean_runtime_result.json
analyst_start_smoke_result.json
render_smoke_result.json
inspect_release_zip_result.json
```

## APF-RC7-06 — Node/gate naming

```text
N_SHARED_TAIL_CLI_CAPABILITY_DISCOVERY_GATE → CLI_CAPABILITY_DISCOVERY_GATE
N_SHARED_TAIL_RELEASE_HYGIENE_CLI_GATE → RELEASE_HYGIENE_CLI_GATE
N_SHARED_TAIL_ANALYST_START_SMOKE_CLI_GATE → ANALYST_START_SMOKE_CLI_GATE
N_SHARED_TAIL_RENDER_SMOKE_CLI_GATE → RENDER_SMOKE_CLI_GATE
N_SHARED_TAIL_INSPECT_RELEASE_ZIP_CLI_GATE → INSPECT_RELEASE_ZIP_CLI_GATE
N_SHARED_TAIL_EXTERNAL_CHECK_EVIDENCE_GATE → EXTERNAL_CHECK_EVIDENCE_GATE
```

## APF-RC7-07 — APF package creation hardening gate role

```text
APF_PACKAGE_CREATION_HARDENING_GATE remains an umbrella/aggregator gate.
Specialized release/render/CLI/evidence checks are separate gates and must not be duplicated inside the aggregator.
```

Aggregator duties:

```text
- collect specialized gate results;
- classify passed / failed / pending-language-tooling / not-applicable;
- decide whether the package can move to evidence and composition gates;
- prevent false green when required external evidence is missing.
```
