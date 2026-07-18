# APF rc.6 reasoning and decisions

Decision: language-package planning work was stopped for this assistant scope. The assistant is responsible only for APF, the process that creates playbook/package-generating playbooks.

Applied APF-only patch: `0.1.0-rc.6-apf-process-hardening`.

Included APF-level changes:

1. package profile + startup standard strengthening;
2. derived artifact sync strengthening;
3. delta backlog preservation;
4. prompt registry packaging checks;
5. graph/SVG provenance checks;
6. release hygiene + clean runtime gate design;
7. real-module testcase generation backlog item;
8. output-template rendering smoke/hardening checks.

Explicitly not included:

- Ordo language package changes;
- compiler/runtime/core CLI changes;
- PROGRAM.DEF or INTERACTION.MODEL as language primitives;
- FLOW.JOIN / SHARED.TAIL.REFERENCE adoption.


## rc.7 decision — APF consumes Ordo CLI checks, does not implement them

APF rc.7 adds integration contracts for future/external Ordo CLI checks. The Ordo language package owns the implementation of those commands. APF owns gate placement, command contract, evidence retention, and readiness semantics.


## APF rc.7 confirmed decisions

See `docs/APF_RC7_CONFIRMATION_REGISTER.md`. `APF_PACKAGE_CREATION_HARDENING_GATE` is confirmed as umbrella/aggregator; specialized release/render/CLI/evidence checks remain separate gates.
