# APF anti-pattern runtime integration

Status: integrated; pending final closure gate.

## Runtime flow

```text
critical APF node
→ antipattern hook
→ activation profile APF_ANTIPATTERN_CORE_V1
→ signal projection
→ detector runtime
→ gate adapter
→ allow | allow_with_advisory | block
```

A blocking or inconclusive result for a blocking rule stops the normal transition and routes execution to the hook's `repair_target`. Advisory findings preserve the normal transition and are stored with evidence.

## Integration surface

- 10 critical APF nodes
- 13 explicit hooks
- 6/6 canonical anti-pattern rules
- state, finding, gate-report and evidence contracts
- fail-closed runtime behavior
- repair routing and blocked-target preservation

## Canonical rules

1. `PROMPT_AS_IMPLEMENTATION`
2. `PACKAGE_VALIDATION_WITHOUT_COMPLETENESS_VALIDATION`
3. `MANDATORY_BRANCH_SHORT_CIRCUIT`
4. `FINAL_LABEL_OVERCLAIM`
5. `SCOPE_CONFIRMATION_AS_IMPLEMENTATION_AUTHORIZATION`
6. `COMPLEXITY_ROUTING_AND_EXECUTION_IN_ONE_NODE`

## Evidence

- `reports/APF_ANTIPATTERN_RULE_COVERAGE_REPORT.json`
- `reports/APF_ANTIPATTERN_RUNTIME_BEHAVIOR_REPORT.json`
- `reports/APF_ANTIPATTERN_STATE_EVIDENCE_CONTRACT_REPORT.json`
- `reports/APF_ANTIPATTERN_EXTENDED_E2E_TEST_REPORT.json`
- `reports/APF_ANTIPATTERN_INTEGRATION_CLOSURE_REPORT.json`

## Visual graph

`visuals/antipattern_runtime_integration/apf_antipattern_runtime_integration.svg`

This graph is an integration view. It does not replace the canonical APF process graph.
