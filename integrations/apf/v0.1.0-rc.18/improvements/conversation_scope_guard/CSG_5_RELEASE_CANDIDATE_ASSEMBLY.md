# CSG-5 — Release Candidate Assembly and Confirmation Preparation

Status: completed

Conversation Scope Guard integration is assembled as APF v0.1.0-rc.17 release candidate.

## Included capability

- optional CSG design phase for generated playbooks;
- canonical deviation classification;
- advisory, guided_redirect, strict_redirect, and locked_process modes;
- node-scoped escalation and reset rules;
- state-protection assertions;
- pause, resume, and controlled incomplete exit semantics;
- conditional package artifacts;
- validation and regression requirements;
- Execution Trace hooks when trace is enabled.

## Preserved boundaries

- APF internal CSG remains disabled;
- CSG is never enabled implicitly;
- generated-playbook business logic is not changed automatically;
- safety and valid process-control intents cannot be blocked;
- unrelated or unclassifiable input cannot complete a node or mutate confirmed state;
- Ordo core is not modified by this APF package.

## Release result

- release candidate: `v0.1.0-rc.17-conversation-scope-guard-support-release-candidate`;
- blocking issues: 0;
- human confirmation required before confirmed-baseline closure.
