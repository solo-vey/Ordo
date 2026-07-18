# APF rc.17 Confirmation Register

## Confirmed baseline

`v0.1.0-rc.17-conversation-scope-guard-support-confirmed-closure`

## Decision

Status: `accepted-confirmed-baseline`

The process owner explicitly confirmed APF v0.1.0-rc.17 on 2026-07-11.

## Accepted scope

- CSG-0 through CSG-5 Conversation Scope Guard integration;
- deviation classification contract;
- strictness, response and escalation policy;
- state-protection and process-control contracts;
- generated-playbook authoring flow and package artifacts;
- validation and regression requirements.

## Preserved boundaries

- APF internal CSG remains disabled.
- Generated playbooks must enable CSG explicitly.
- Safety and valid process-control intents must not be blocked.
- Ordo core is not modified by APF.
