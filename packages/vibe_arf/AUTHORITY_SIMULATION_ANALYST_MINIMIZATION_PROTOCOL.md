# Authority, Simulation & Analyst-Minimization Protocol — alpha.27

## Goal
Keep machine-detectable authoring/runtime defects behind the analyst-visibility barrier and reserve analyst interaction for consequential human authority.

## Standard contour
`source materials → AIM → review bundles → proposals → human authority where required → approved projection → Ordo synthesis → deterministic verification → scenario matrix → exact-candidate simulation → defect ownership → internal repair/adapter handoff → analyst-ready candidate`.

## Analyst-minimal review
1. Derive as much as possible from supplied evidence.
2. Separate supported/derived fields from authority/uncertain fields.
3. Review only the smallest coherent bundles needed for human authority.
4. Persist decisions in a revisioned approval ledger.
5. Verify persistence immediately; never wait for a distant final gate to discover an overwritten approval.

## Simulation-first qualification
- Inspect the exact candidate ZIP using the pinned Simulation Kit.
- Synthesize fixtures from `simulation_contract.json` plus the required scenario matrix.
- Use native `semantic_recovery_fixture_points` from the Simulation Kit inspect contract; when runtime discovers an additional state-dependent call, preserve `missing_fixtures.json` and its ready-to-fill template, extend fixtures, and rerun.
- Execute required scenarios and persist trace, errors, state, fixture usage and runtime gate evidence.
- Treat fixture-based PASS as runtime-conformance evidence only, not live-model acceptance.

## Defect ownership
- **Playbook/source defect** → internal root-cause repair and re-run.
- **Fixture defect** → repair fixtures only.
- **Model-quality defect** → improve semantic fixture/prompt design without falsifying deterministic state.
- **Runtime-adapter conformance defect** → create evidence-rich adapter handoff; do not mutate canonical-valid playbook as workaround.
- **Language violation** → fix Vibe/generated source against canonical Ordo.

## Truthfulness
- No critical gate PASS with empty checks/evidence.
- No coverage PASS unless all required scenario families are actually covered.
- No VERIFIED/APPROVED/MATERIALIZED postcondition before its producer/evidence gate runs.
- No readiness claim when simulation or ownership evidence required by the target is missing.

## TDD memory
Every defect class discovered in dogfood becomes a domain-neutral negative regression fixture before the implementation fix. The regression stays after the defect is repaired so the class cannot return silently.
