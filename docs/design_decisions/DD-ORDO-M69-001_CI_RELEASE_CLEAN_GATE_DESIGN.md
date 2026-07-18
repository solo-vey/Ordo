# DD-ORDO-M69-001 — CI / Release Clean Gate Design

Status: accepted

## Decision

Use the existing `repo-check --clean` command as the only hygiene decision engine for CI and release gates.

CI/release integrations may orchestrate command execution and retain evidence, but may not reimplement clean-check logic.

## Accepted defaults

- pull request: `standard`, warnings allowed;
- main branch: `standard`, warnings block;
- release candidate: `strict`, warnings block;
- release: `strict`, warnings block.

## Boundary

M69.0 is design-only. Workflow files and release integration are deferred to later milestones and require separate implementation approval.
