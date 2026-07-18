# APF anti-pattern wiring contract

Status: activation profile connected; critical-node wiring pending.

APF consumes the canonical language contract:

```text
language/integration/ANTIPATTERN_WIRING_CONTRACT.md
language/schemas/antipattern_wiring_hook.schema.json
```

## APF hook rule

A protected APF node or transition must declare an `antipattern_check` object conforming to `ordo.antipattern_wiring_hook.v1`.

The hook runs at one of these boundaries:

```text
before_node_execution
after_state_update_before_transition
before_repository_mutation
before_package_finalization
before_final_status_claim
```

Default APF state bindings:

```text
antipattern_gate_report
antipattern_findings
antipattern_gate_status
antipattern_evidence_refs
```

Blocking behavior:

```text
blocking finding or blocking inconclusive
→ do not execute next transition
→ set antipattern_repair_required = true
→ route to the hook's explicit repair_target
```

Advisory behavior:

```text
persist report/findings
→ continue transition
```

## Context selection

Use the activation profile context that matches the protected boundary:

- conversational authorization: `conversation`;
- process/node transition: `runtime_state` or `process_trace`;
- package completion: `package_state`;
- evidence claims: `evidence_state`;
- repository mutation: `repository_state`.

## Current integration state

The contract is explicit and machine-validatable. The APF runtime now binds the canonical activation profile through:

```text
integration/antipattern_runtime_binding.apf.v1.json
integration/antipattern_runtime_binding.py
ordo.runtime.json.antipattern_enforcement
```

The binding validates profile identity, active status, all six contexts, required components, and fail-closed behavior. No claim is made yet that APF critical nodes are wired; that belongs to the critical-node wiring step.
