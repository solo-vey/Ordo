# M79.5 — Real playbook template tooling integration

Status: **PASS**

Integrated playbook: `history_event_analysis_package_factory v0.8.28`.

Integrated templates:

1. `history_event.passport` — `model_rendered`, strict review, controlled model job and provenance.
2. `history_event.validation_report` — `deterministic`, strict review, JSON artifact.

The existing authoritative templates and business process logic were not replaced. A generic tooling layer was added through registry contracts and `generic_template_tooling` bindings in both `ordo.yml` and `source/program.ordo.yaml`.

Full integration cycle passed:

`validate → registry-check → render → review → diff`

A real integration exposed and fixed a generic renderer issue: boolean and null scalar values are now serialized as JSON-compatible lowercase literals.
