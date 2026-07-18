# APF Conversation Scope Guard — Strictness, Response, and Escalation Policy

## Scope

This policy applies only to Conversation Scope Guard capabilities designed by APF for generated playbooks. APF does not enable the guard for its own authoring process by default.

## Mode selection

The playbook owner must explicitly select one canonical mode:

- `advisory`: brief external answer is allowed, followed by redirect;
- `guided_redirect`: acknowledge, explain the boundary, and repeat the active question;
- `strict_redirect`: issue only a scope notice and repeat the active question;
- `locked_process`: accept only declared process and control intents.

APF must not infer or silently strengthen the mode.

## Redirect behavior

A redirect response may acknowledge the message, state the active process boundary, show the current node or question, and offer return, pause, or exit actions. It must not complete a node, invent an answer, change path or confirmed state, discard collected state, or terminate the run implicitly.

## Escalation

Default escalation is scoped to the active node:

1. `gentle_redirect`;
2. `explicit_scope_reminder`;
3. `offer_pause_or_exit`;
4. `suspend_until_process_choice`.

The counter resets after a valid process answer, node transition, or process resume. A process-wide counter is allowed only when explicitly selected and justified.

## Safety and process control

Safety or emergency messages override normal scope handling. Pause, resume, exit, correction, backtracking, requirement change, clarification, and process-meta questions must not be rejected as unrelated topics.

## Human confirmation boundary

Before package assembly, APF must present the selected mode, response templates, escalation scope, reset rules, and pause/resume/exit behavior for human confirmation. Changes that make the guard stricter or alter suspension/exit behavior require renewed confirmation.
