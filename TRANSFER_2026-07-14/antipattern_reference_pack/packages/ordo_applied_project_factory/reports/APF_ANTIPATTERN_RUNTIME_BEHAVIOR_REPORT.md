# APF anti-pattern runtime behavior report

Status: implemented and focused-validation passed.

Implemented behavior:

- `block` stops the normal transition and routes to the hook's `repair_target`;
- `allow_with_advisory` continues the normal transition and persists findings/evidence;
- `allow` continues and persists the gate report;
- adapter/runtime failure is fail-closed and routes to repair;
- findings are deduplicated by `finding_id`;
- evidence references are persisted with stable evidence ids;
- the blocked original transition target is preserved for diagnostics;
- multiple hooks in one phase stop after the first blocking result.

Runtime wiring:

- `after_state_update_before_transition` is dispatched automatically by the deterministic runner;
- all other declared phases are supported by `execute_node_hooks(...)` and are available to repository/package/final-status call sites.

Validation:

- 5 focused runtime behavior tests passed;
- 6/6 canonical rule coverage remains passed;
- real adapter smoke at `N_FACTORY_MODE_SELECTION` returned `allow`, continued to `N_APPLIED_PROJECT_GOAL`, and persisted one evidence reference;
- Python syntax validation passed for parent and embedded runners.

This report does not claim final BL-ORDO-020 integration closure. Remaining steps include dedicated state/evidence contract validation, negative/regression/E2E tests, graph/docs update, and final closure gate.
