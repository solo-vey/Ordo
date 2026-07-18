# BL-ORDO-027 — ARF Deterministic Process Control Model

Status: `in_progress`  
Scope: general ARF process control only.

## Plan

1. **Control-model contract**
   - define `EXECUTION_MODE`, `DESIGN_MODE`, `AUTHORIZED_MAINTENANCE_MODE`;
   - define explicit entry/exit authorization and forbid implicit switching;
   - define `blocked_missing_instruction`.

2. **Node contract profiles**
   - define minimum contracts for executable, routing, capture and validator nodes;
   - require atomic responsibility, prerequisites, allowlisted actions, outputs, gates, transitions, forbidden actions, invalidation and authorization boundary where relevant.

3. **Instruction precedence**
   - formalize precedence from confirmed user decision through node contract, authoritative sources, confirmed state, rendering and independent validation;
   - define conflict handling as blocking, never best-judgement fallback.

4. **Runtime enforcement**
   - bind current mode and active-node allowlist to runtime;
   - block undefined actions and implicit transitions;
   - require explicit authorization for maintenance mutations.

5. **Independent validation**
   - separate artifact generation from validation;
   - prevent self-declared pass status;
   - validate composite executable outputs at the smallest declared executable unit.

6. **State and invalidation**
   - add mode, authorization, blocked-reason and validation-evidence state;
   - invalidate downstream confirmations after relevant upstream changes.

7. **Anti-pattern integration**
   - map violations to existing fundamental rules;
   - add subpatterns/detector cases only; no new fundamental rule without owner approval.

8. **Tests**
   - positive flows for each mode;
   - negative tests for unauthorized mutation, editorial compression, invented instructions, implicit transitions and self-validation;
   - backward-compatibility and end-to-end ARF generation tests.

9. **Graph, docs and closure**
   - update ARF graph and runtime documentation;
   - issue integration and final closure reports.

## Explicit exclusions

Manual QA test-case fields, fixture mutation workflows, endpoint reconstruction and History Event-specific contracts are excluded.
