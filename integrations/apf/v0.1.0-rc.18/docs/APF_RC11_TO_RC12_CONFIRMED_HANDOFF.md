# APF rc.11 → rc.12 confirmed handoff

## Source baseline

Use:

`APF_TRANSFER_PACKAGE_CURRENT_STATE_RC11_CONFIRMED_CLOSURE.zip`

## Preserved rc.11 contract

The next APF patch must preserve:

- `CONCRETE_PLAYBOOK_STARTUP_GATE` as an APF packaging/readiness gate;
- the authoring protocol, startup manifest, skeleton, and readiness report as reusable templates;
- strict separation between APF patch mode and concrete playbook authoring mode;
- prohibition on mutating the APF baseline during future concrete playbook authoring;
- prohibition on Ordo language-package changes inside APF work;
- the fact that no real playbook package was created in rc.11.

## Recommended next APF topic

`APF rc.12 — Concrete playbook intake contract and requirement-capture standard`

This recommendation remains APF-only: define reusable intake contracts, schemas, templates, and validation rules without running a real intake or producing a real playbook package.
