# CSG-2 — Strictness, Response, and Escalation Policy

Status: completed

Implemented:

- four canonical strictness modes;
- canonical redirect actions and required response parts;
- active-node-scoped escalation with reset rules;
- controlled pause, exit, and suspension behavior;
- safety and process-control bypass requirements;
- blocking conditions for unsafe or incomplete policies;
- generated-playbook policy decision template.

APF internal Conversation Scope Guard remains disabled. No runtime guard is implemented by APF; APF produces the design contract and package artifacts for generated playbooks.

Next stage: CSG-3 — state-protection and process-control contract.
