# Authoring tooling
Use `python tools/ordo_authoring.py lint <package>` and `compile <package>` for applied playbooks. Runtime of Vibe itself uses `./cli_embedded/ordo`. Canonical references are in `canonical_support/`.


## alpha.10 closure contour
For a candidate applied playbook, Vibe leads verification, builds current editor Auto Answers,
collects editor live-run evidence, performs post-run self-audit and re-verifies before readiness.
Use `python tools/build_editor_auto_answers.py <mapping.json> <answers.zip>` for editor-compatible
Auto Answers. Use `python tools/verify_playbook_laws.py <generated-playbook-root>` to enforce
verbatim laws propagation. Independent dry-check is optional and final-stage only.


## alpha.12 executable verification
Generate a mandatory baseline profile for an applied playbook:
`python tools/generate_verification_profile.py <playbook-root>`

Validate it:
`python tools/validate_verification_profile.py <playbook-root>/verification_profile.json`

Run deterministic checks through a phase:
`python tools/run_verification_profile.py <playbook-root> --through PRE_EDITOR`

After editor evidence has been returned as `reports/EDITOR_RUN_EVIDENCE.json`, run through RELEASE.
The machine-readable result is written to `reports/VERIFICATION_EVIDENCE_SUMMARY.json`.


### Mandatory runner contract
`validate_verification_profile.py` rejects a profile that omits mandatory runners. Custom deterministic
validators use `python_script` and must live inside the applied package. `POST_EDITOR` fails until actual
machine-readable editor evidence is returned; `RELEASE` depends on that evidence.


## Generated-playbook inheritance (alpha.16)

After a generated playbook has `source/program.ordo.yaml`:

```bash
python tools/materialize_generated_playbook_verification.py <generated-playbook-root>
```

This installs governing laws, generates the baseline verification profile, creates the invariant register and
an exact executable-element responsibility-map scaffold, and installs the package-local responsibility validator.

The scaffold intentionally fails until Vibe classifies every executable element and provides required mechanisms,
semantic reasons, authority ownership and evidence contracts.

Then run:

```bash
python tools/verify_execution_responsibility_map.py <generated-playbook-root>
python tools/run_verification_profile.py <generated-playbook-root> --through PRE_EDITOR
```


## Artifact materialization contract (alpha.16)

Each generated source output must be represented in:
`verification/ARTIFACT_MATERIALIZATION_REGISTRY.json`.

Validate with:
`python tools/validate_artifact_materialization_registry.py <playbook-root>`

This is a mandatory PRE_EDITOR check.


## Trusted factory regression runner (alpha.18)

Vibe's own `tools/test_alpha*.py` regressions use `trusted_python_regression` and execute in-process to avoid
host Python subprocess startup/daemon contention. This runner is restricted to Vibe-owned `tools/test_alpha*.py`.

Generated/applied playbook package-local Python validators continue to use `python_script` subprocess isolation
with path containment and timeout. Do not use the trusted runner for generated domain code.


## Information-first authoring (alpha.24)
Initialize the design-time model **before** Ordo graph synthesis:

```bash
python tools/init_information_first_authoring.py <generated-playbook-root>
```

Populate `authoring/information_object_catalog.yaml`, `information_group_catalog.yaml`, `artifact_catalog.yaml`, `information_flow_graph.yaml`, and `interaction_projection.yaml`. Then run:

```bash
python tools/validate_authoring_information_model.py <generated-playbook-root>
```

Only after this gate passes should Vibe synthesize the process graph. Materialize `authoring/ordo_projection.yaml` while generating ordinary Ordo IDs. Once source exists, run:

```bash
python tools/validate_information_projection.py <generated-playbook-root> --playbook <generated-playbook-root>/source/program.ordo.yaml --require-bound
```

`materialize_generated_playbook_verification.py` installs these package-local validators and preserves any already-populated AIM files. Generated verification profiles execute both checks in PRE_EDITOR.

## Self-hosted information model (alpha.25)
Vibe itself carries `authoring/` AIM artifacts and is validated by the same information-model and bidirectional projection Python gates used for generated playbooks. The Vibe executable graph is therefore treated as a projection of its own persisted information model, not as a special graph-first exception.

## Authority-first / simulation-first authoring (alpha.26)
After AIM grouping, derive review bundles and scenario families:

```bash
python tools/compile_review_bundles.py <generated-playbook-root>
python tools/derive_behavioral_scenario_matrix.py <generated-playbook-root>
```

Generated packages receive package-local alpha.26 validators for review bundles, proposal/canonical separation, approval persistence, local persistence gates, state-phase ordering, recovery locality, semantic input parity, behavioral coverage, simulation evidence, fixture closure, runtime gate evidence and defect ownership.

For runnable candidates, Vibe uses its pinned Simulation Kit dependency to inspect/run the **exact candidate ZIP** before analyst-ready handoff:

```bash
python tools/run_simulation_preflight.py <candidate.zip> --package-root <vibe-root> --inspect-only
python tools/run_simulation_preflight.py <candidate.zip> --package-root <vibe-root> --scenario-dir <scenario-dir>
```

The simulator is adapter qualification only. Adapter defects generate an adapter handoff; they do not justify mutating canonical-valid Ordo. Simulation fixtures/evidence are stored with the generated package/report set so its PRE_EDITOR evidence validators can verify them.

### Portable candidate ZIP freshness (alpha.26)
Build final runnable candidate ZIPs with:

```bash
python tools/build_portable_candidate_zip.py <package-root> <candidate.zip>
```

The builder writes `compiled/` members after editable source. This prevents sequential extractors that do not restore archive mtimes from making `source/program.ordo.yaml` appear newer than its derived IR solely because of extraction order. Always re-extract the final ZIP and rerun portable/PRE_EDITOR checks.


## Simulation Kit 0.1.5 upgrade (alpha.30)
The pinned dependency is `dependencies/ORDO_PLAYBOOK_SIMULATION_KIT_0.1.5.zip` with runtime baseline `0.2.0-alpha.20.0.166-dev`. `run_simulation_preflight.py` accepts both flat-root and one-root-directory kit archives. Use native inspect `semantic_recovery_fixture_points`. When runtime returns `fixture_incomplete`, preserve `missing_fixtures.json` and `missing_model_responses.template.yaml`, extend the model/recovery fixture, and rerun until closure or a real defect is identified.


## Self-hosted Data Flow publication (alpha.30)

Publish Vibe's own AIM for Editor Source Data Flow with:

`python tools/publish_authoring_data_flow.py .`

Then verify canonical equivalence with:

`python tools/validate_self_data_flow_publication.py .`

Always mutate `authoring/` first. Never hand-edit the generated `design/` projection.


## Context / Runtime Efficiency (alpha.45 candidate)

Generated playbooks should treat model-visible context as a measured runtime surface. Prefer active-node targeted source reads, lazy prompt/knowledge loading, consumer-aware package projections, compact evidence references and hash-bound deltas. Use `tools/audit_context_runtime_efficiency.py` for baseline evidence and `tools/validate_context_runtime_efficiency.py` for the framework contract. Estimated tokens must be labeled; platform/system/tool-schema overhead is tracked separately from playbook-controlled context.

## Deterministic-first architecture

Generated playbooks classify every executable responsibility before graph synthesis. Mechanical work is deterministic. Model-owned state changes use `state_patch_v1`; deterministic tools use `state_updates_v1`. Producer writes validate before persistence, lifecycle closure is monotonic, recovery resume is deterministic, finite completeness is ID-accounted, and deterministic evidence hydration is hash/allowlist-bound.


## Development / Regression governance

`tools/build_development_regression_plan.py` creates the pre-change evidence plan and `tools/validate_development_regression_governance.py` validates post-change candidate evidence. Material candidate changes use the reusable `DEVELOPMENT_REGRESSION_GOVERNANCE` template; full accumulated verification is deferred to RELEASE by default.
