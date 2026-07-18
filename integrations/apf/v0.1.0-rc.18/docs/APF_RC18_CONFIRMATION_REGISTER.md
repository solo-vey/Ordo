# APF rc.18 Confirmation Register

## Confirmed baseline

`v0.1.0-rc.18-csg-language-baseline-aligned-confirmed-closure`

## Decision

Status: `accepted-confirmed-baseline`

The process owner explicitly confirmed APF v0.1.0-rc.18 on 2026-07-11.

## Accepted scope

- CSG-A1 language baseline schema alignment;
- canonical `DEVIATION.CLASSIFY` record structure;
- canonical confidence enum and escalation counter scopes;
- canonical package binding and `decision_status`;
- canonical generated-playbook CSG artifact names;
- dedicated CSG trace-events artifact;
- CSG-A2 regression validation and release hygiene.

## Preserved boundaries

- APF internal CSG remains disabled.
- Generated playbooks must enable CSG explicitly.
- Safety and valid process-control intents must not be blocked.
- Mini-prompt, Execution Trace, and Atomic Step Review capabilities remain unchanged.
- Ordo core is not modified by APF.
