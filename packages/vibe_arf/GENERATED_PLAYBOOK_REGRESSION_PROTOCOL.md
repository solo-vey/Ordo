# Generated Playbook Regression Protocol — alpha.30

## Authority
Canonical Ordo language is the only semantic source of truth.

## Verification layers
- `ordo_language_regression`: invalid Ordo must fail independent of runtime adapter.
- `vibe_authoring_regression`: information/authority/projection quality and safe-generation defaults; valid Ordo may still be profile-nonconformant.
- `auto_answers_and_scenario_regression`: fixture sequencing, retry/path and required behavioral-family coverage; never force business-state workarounds into the playbook.
- `runtime_simulation_regression`: exact-candidate execution against a pinned adapter runtime with analyst/model fixtures.
- `editor_conformance_regression`: canonical Ordo fixtures that Editor must execute correctly. Failures are Editor defects.
- `editor_adapter_regression`: Editor-specific package/UI/replay/transport compatibility.

## Status taxonomy
- `ORDO_INVALID`
- `ORDO_VALID_VIBE_PROFILE_NONCONFORMANT`
- `AUTO_ANSWERS_INVALID`
- `SIMULATION_FIXTURE_INCOMPLETE`
- `ORDO_VALID_ADAPTER_INCOMPATIBLE`
- `PASS`

No adapter-specific result may be promoted to `ORDO_INVALID` without a canonical-language basis.

## Information/authority regression contracts
Vibe-generated candidates must prove:
- authoring information-model validity before graph synthesis;
- bidirectional AIM ↔ Ordo traceability;
- review bundles reference valid AIM groups/objects and minimize analyst burden;
- proposal state is quarantined from canonical truth;
- approval history is persistent/revisioned;
- human authority updates are followed by local persistence gates;
- gate postconditions are ordered after their evidence producers;
- recovery targets the nearest causal remediation point when known;
- authority-derived semantic sources are declared as explicit inputs.

## Behavioral truth contracts
Aggregate PASS/complete/VERIFIED claims do not establish coverage. Required scenario families are explicit and machine-checked. Critical runtime gate PASS must contain non-vacuous execution evidence/check results. Simulation must identify the exact candidate hash, pinned kit/runtime baseline, scenario result and fixture closure.

## Defect ownership
Every simulation failure is classified as playbook/source, fixture/model-quality, language/tooling, or runtime-adapter defect. Runtime-adapter defects must not be hidden by playbook workarounds. Historical failures remain as domain-neutral negative fixtures even after their owner is fixed.

## Pinned simulation dependency
The Simulation Kit is a runtime-adapter dependency, not a language authority. Its runtime core must be explicitly versioned/rebased. PASS proves fixture-based runtime compatibility only; it is not real-provider/LLM acceptance.


## Simulation Kit 0.1.5 behavior
Pinned runtime baseline: `0.2.0-alpha.20.0.166-dev`. Native semantic-recovery fixture points are authoritative for static fixture synthesis. A runtime `fixture_incomplete` result is an expected discovery state when the call depends on runtime state; preserve the exact missing-fixture contract, extend fixtures, and rerun. `SOURCE_PROFILE_EXECUTOR_ADAPTED` confirms an explicit generated-playbook profile adapter projection; it does not extend canonical Ordo.


## Semantic execution regression inheritance (alpha.44 candidate)

Generated stateful playbooks must include generic regression coverage for: Model Mode terminal reference trace before strict-runtime equivalence claims; merge-by-diff state preservation; current-node re-entry after authority/repair loops; declared gate `on_fail` recovery; absence of runtime-workaround business/Data-Layer fields; exhaustive same-group human-authority discovery with stable `decision_id`; partial-answer no-reask behavior; and at least one end-to-end `FAIL → repair → recompute/rematerialize → PASS` recovery loop.

## Deterministic-first architecture regression

Every generated playbook should include positive/negative fixtures for producer-boundary rejection, stale StatePatch rejection, lifecycle downgrade rejection, deterministic recovery resume, stable-ID completeness accounting, and evidence hydration hash/allowlist mismatch.


## Candidate Development / Regression Governance (alpha.45)

For every material candidate change: define the protected invariant and regression first; capture reproducible pre-change non-PASS evidence (or explicit machine-checkable NOT_APPLICABLE); apply the minimal change; prove the exact regression GREEN; run directly impacted checks; keep `REGRESSION_PROOF` separate from `LIVE_PROOF`. Real failures remain permanent regression memory. Candidate validation is targeted/impacted; the full accumulated regression/scenario/profile suite is a RELEASE gate unless explicitly requested earlier.
