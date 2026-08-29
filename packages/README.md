# Reference packages

This directory contains runnable or reference Ordo process packages. Each package
owns its source, inputs, tests, and package-local documentation.

The recommended playbook-authoring package is [`vibe_arf/`](vibe_arf/). The
older [`arf_playbook_kit/`](arf_playbook_kit/) is a lower-level compatibility
package and is scheduled for deprecation.

- [`benchmark_creation_playbook/README.md`](benchmark_creation_playbook/README.md) —
  versioned benchmark-creation playbook package.
- [`vibe_arf/README.md`](vibe_arf/README.md) — recommended Vibe ARF authoring
  package with chat, CLI, and model-run profiles.
- [`arf_playbook_kit/README.md`](arf_playbook_kit/README.md) — legacy lower-level
  ARF Playbook Kit source retained for compatibility and engineering use.
- [`history_event_guided_intake/README.md`](history_event_guided_intake/README.md) —
  guided intake for a historical event contract.
- [`ordo_applied_project_factory/README.md`](ordo_applied_project_factory/README.md) —
  authoring and improvement of applied Ordo projects.
- [`ordo_hybrid_executor/README.md`](ordo_hybrid_executor/README.md) — reference hybrid
  execution contract.
- [`ordo_project_builder/README.md`](ordo_project_builder/README.md) — reference
  project-building process.
- [`playbook_regression/README.md`](playbook_regression/README.md) — candidate
  regression orchestration playbook that controls PRH.

Accepted external baselines belong in [`../integrations/README.md`](../integrations/README.md).
