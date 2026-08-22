# Vibe ARF 0.1.2 — Three-Profile Distribution + Standard Hardening/Optimization Subprocesses

Status: `STABLE_RELEASE_0.1.2`.

## Semantic authority
Canonical Ordo under `canonical_support/language/` is the sole language/runtime semantic source of truth. Vibe authoring models, Auto Answers, Simulation Kit and Editor are design/test layers or runtime adapters; none may redefine valid Ordo.

## Information-first, authority-first authoring
Before synthesizing an executable process graph, Vibe must:

1. discover required outcomes/artifacts;
2. decompose artifacts into information objects and typed dependencies;
3. define semantic groups, provenance, lifecycle and authority boundaries;
4. compile **analyst-minimal review bundles** from AIM rather than exposing all groups verbatim;
5. keep model proposals quarantined from canonical truth until an approved projection is created;
6. persist human authority in an append-only/revisioned approval ledger and verify it locally after each apply;
7. derive recovery from the nearest causal remediation point in AIM;
8. validate the information model deterministically;
9. synthesize ordinary Ordo only after that model is valid;
10. prove bidirectional AIM ↔ Ordo traceability.

## Analyst-minimal review
Review bundles are distinct from semantic information groups. They are derived from dependencies, authority, uncertainty and cognitive load. Analyst-visible interaction should emphasize `authority_fields` and `uncertain_fields`; supported/derived fields remain silent unless context is required.

## Simulation before analyst visibility
For runnable generated playbooks, the **exact candidate ZIP** must be inspected and exercised with the pinned `ORDO_PLAYBOOK_SIMULATION_KIT` before analyst-ready handoff when the simulation dependency applies. Simulation is runtime-adapter qualification, not Ordo semantic authority.

The preflight contour is:

`AIM → Ordo → deterministic PRE_EDITOR gates → scenario/fixture synthesis → pinned-runtime simulation → defect ownership → internal repair or adapter handoff → analyst visibility`.

Simulation failures are classified by owner. Runtime-adapter defects must not produce playbook workarounds. Fixture defects repair fixtures. Playbook/source defects return to internal root-cause repair.


## Simulation Kit 0.1.5 binding (alpha.30)
The pinned offline runtime adapter is `ORDO_PLAYBOOK_SIMULATION_KIT 0.1.5`, rebased on shared Editor/runtime `0.2.0-alpha.20.0.166-dev`. Vibe supports both flat-root and legacy single-root dependency ZIP layouts. Native `semantic_recovery_fixture_points` are consumed from `simulation_contract.json`; runtime-discovered recovery calls are preserved via `missing_fixtures.json` and `missing_model_responses.template.yaml` and are repaired as fixture work, not misclassified as playbook defects. The kit's generated-playbook `package_tool` support is an explicit compiler adapter and never canonical Ordo semantics.

## Truthful behavioral verification
A generic PASS is insufficient. Behavioral coverage comes from an explicit scenario matrix. Critical runtime gates cannot count as PASS with empty evidence/check results. State phases such as VERIFIED/APPROVED/MATERIALIZED cannot be required before their producer/evidence gate executes.

## Alpha.29 pre-simulation contract hardening
Before pinned-runtime simulation, Vibe now blocks three classes of defects deterministically:

- **strict route closure** — every static route must resolve to a declared element/external terminal or canonical reserved `STOP`; convenience words such as `block` are not implicit terminals;
- **deterministic execution contract completeness** — package-tool/materialization nodes require explicit executor, tool reference, effect/output and route; mechanical gates require executable condition/assert semantics plus fail-closed routing;
- **artifact/archive registry completeness** — first-class outputs require materialization identity, producer, builder/template, validator contract, and archives additionally require explicit membership and hash validation contracts.

Simulation Kit `0.1.5` remains the runtime backstop and must still fail closed on any `profile_contract_gap`; alpha.30 simply catches machine-detectable profile omissions earlier so they do not consume an analyst-visible or runtime-debug cycle.

## Main tooling
- `tools/init_information_first_authoring.py`
- `tools/compile_review_bundles.py`
- `tools/derive_behavioral_scenario_matrix.py`
- `tools/validate_authoring_information_model.py`
- `tools/validate_information_projection.py`
- alpha.26+ validators under `tools/validate_*`
- `tools/run_simulation_preflight.py`
- `tools/build_portable_candidate_zip.py`
- `tools/run_verification_profile.py`

## Verification layers
Language conformance, Vibe authoring profile, Auto Answers/scenarios and runtime-adapter qualification remain separate. Adapter failure must never be promoted to `ORDO_INVALID` without a canonical-language basis.

## One-line chat bootstrap
After uploading the archive to a clean chat, the user may say only:

`Read the archive, find START_PROMPT.md in the package root, and follow it.`

`START_PROMPT.md` is bootstrap-only and must route into Runtime Mode; it is never the analyst intake questionnaire.

## Runtime entry artifacts
Runtime-mode instructions: `START_HERE_RUNTIME_MODE.md` and `START_PROMPT_RUNTIME_MODE.md`. Canonical source is `source/program.ordo.yaml`; `compiled/program.ir.json` is derived runtime IR and is never the authoring source of truth.

## Self-hosted information model
Vibe itself carries `authoring/` AIM artifacts and is validated by the same information-model and bidirectional projection Python gates used for generated playbooks. Alpha.29 self-describes its review/proposal/approval/simulation and deterministic-contract contour; the Vibe executable graph remains a projection of persisted design-time information state.


## Simulation Kit 0.1.5 artifact validation binding (alpha.30)
The pinned runtime adapter is Simulation Kit `0.1.5` on shared runtime `0.2.0-alpha.20.0.166-dev`. Deterministic artifact/archive validation is consumed only through the explicit generated-playbook profile adapter. Missing required archive membership/hash declarations are preserved as `profile_contract_gaps.json`, classified as an authoring-profile contract gap, repaired internally, and rerun before analyst visibility. Mechanical gates never fall through to LLM semantic recovery, and none of these adapter capabilities redefine canonical Ordo semantics.


## Self-hosted Source Data Flow publication (alpha.30)

Vibe now publishes its own canonical `authoring/` AIM through an Editor-discoverable `design/MODEL_BUNDLE.yaml` and `design/DATA_FLOW_PACKAGE.zip`. The `design/` files are generated views, never a second source of truth. `tools/validate_self_data_flow_publication.py` blocks stale or divergent publication before Editor handoff.


## Alpha.45 candidate development subprocesses

VIBE now carries two reusable authoring subprocesses: **Quality Hardening Loop** (RED → minimal repair → GREEN → impacted regressions) and **Performance & Token Optimization Loop** (stable quality baseline → telemetry → hotspot → one optimization → semantic-equivalence/performance comparison). The model routes explicit debugging/performance requests and evidence into these standard loops rather than inventing an ad-hoc method.
