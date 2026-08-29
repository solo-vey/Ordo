# Anti-pattern wiring contract v1

Status: accepted integration contract; node wiring not yet applied.

## Purpose

This contract makes anti-pattern enforcement an explicit part of an Ordo/APF node or transition instead of an implicit runtime overlay.

Canonical hook schema:

```text
language/schemas/antipattern_wiring_hook.schema.json
```

Canonical adapter and profile:

```text
language/integration/antipattern_gate_adapter.py
language/integration/antipattern_activation_profile.apf.v1.json
```

## Execution order

```text
node input / current state
→ optional node state update
→ build declared state projection
→ AntipatternGateAdapter.evaluate_gate(...)
→ persist GATE.REPORT and ANTIPATTERN.FINDING records
→ apply decision policy
→ continue transition OR route to repair
```

No transition protected by a hook may execute before the gate decision is persisted.

## Required hook fields

Each hook declares:

- stable `hook_id`;
- execution `phase`;
- canonical adapter/profile;
- one activated `context_type`;
- stable `source_id`;
- explicit state projection and required-signal policy;
- report/findings/status/evidence state bindings;
- deterministic decision policy;
- explicit repair target for blocking findings.

## Decision semantics

| Adapter decision | Required behavior |
|---|---|
| `block` | Stop the transition and route to the declared repair target. |
| `allow_with_advisory` | Continue, but persist findings and evidence references. |
| `allow` | Continue and persist the gate report. |
| `inconclusive` | Escalate to `block` when a blocking rule lacks required signals. |

Severity alone does not determine routing. Enforcement is authoritative:

```text
blocking → block
advisory → allow_with_advisory
```

`critical` findings must always be blocking.

## Evidence requirements

Every invocation must persist:

- complete `GATE.REPORT`;
- all produced `ANTIPATTERN.FINDING` records;
- gate decision and gate id;
- activation profile id;
- source node/transition id;
- evidence references or source hash when available.

## Prohibited behavior

- Calling detectors without persisting their report.
- Logging a blocking finding while continuing the protected transition.
- Treating missing required signals as automatic success.
- Replacing the activation profile with prompt-only instructions.
- Claiming integration merely because detectors and tests exist.

## Boundary

This document defines the wiring contract only. Specific APF node hooks, repair routes, state fields, and end-to-end enforcement are implemented in later integration steps.
